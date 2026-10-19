import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from .dates import WEEKDAY_PL
from .transcript import Transcript

TEMPLATE = Path(__file__).with_name("prompt_template.md")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_ANTHROPIC_MODEL = "claude-opus-5-5"


class LLMError(RuntimeError):
    pass


def call_metadata(t: Transcript) -> str:
    rows = [f"- Call date: {t.call_date.isoformat()} ({WEEKDAY_PL[t.call_date.weekday()]})" if t.call_date else "- Call date: unknown"]
    rows.append(f"- Customer: {t.customer or 'unknown'}")
    rows.append(f"- Title: {t.title}")
    present = [p for p in t.people if p.present]
    absent = [p for p in t.people if not p.present]
    rows.append("- On the call: " + "; ".join(
        f"{p.name} ({', '.join(x for x in (p.role, p.org, p.email) if x)})" for p in present))
    if absent:
        rows.append("- Mentioned, not on the call: " + "; ".join(
            f"{p.name} ({p.role})" if p.role else p.name for p in absent))
    return "\n".join(rows)


def previous_block(ledger: dict | None) -> str:
    if not ledger:
        return "None. This is the first processed call for this customer."
    lines = [f"Ledger from the call on {ledger['call']['date']}. Items still open or in force:"]
    for it in ledger["items"]:
        if it["state"] in ("closed", "rejected", "noted"):
            continue
        when = it.get("when") or {}
        span = " to ".join(x for x in (when.get("start"), when.get("end")) if x)
        lines.append(f"- {it['id']} [{it['type']}/{it['state']}] {it['title']}. Owner: {it['owner'].get('person') or it['owner'].get('party')}."
                     + (f" When: {span}." if span else "")
                     + (f" Condition: {it['condition']['text']}" if it.get("condition") else ""))
    return "\n".join(lines)


def build_prompt(t: Transcript, ledger: dict | None) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    return (text.replace("{{CALL_METADATA}}", call_metadata(t))
                .replace("{{PREVIOUS_LEDGER}}", previous_block(ledger))
                .replace("{{TRANSCRIPT}}", t.numbered()))


def parse_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence and not text.startswith("{"):
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise LLMError("model output contains no JSON object")
    return json.loads(text[start:end + 1])


def _post(url: str, headers: dict, body: dict, stream: bool):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=900)
    except urllib.error.HTTPError as e:
        raise LLMError(f"HTTP {e.code} from {url}: {e.read().decode('utf-8', 'replace')[:2000]}") from None
    except urllib.error.URLError as e:
        raise LLMError(f"cannot reach {url}: {e.reason}") from None


def _anthropic(prompt: str, model: str, key: str, url: str) -> str:
    body = {"model": model, "max_tokens": 64000, "stream": True,
            "messages": [{"role": "user", "content": prompt}]}
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    parts: list[str] = []
    stop = None
    with _post(url, headers, body, True) as resp:
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            event = json.loads(line[5:])
            kind = event.get("type")
            if kind == "content_block_delta" and event["delta"].get("type") == "text_delta":
                parts.append(event["delta"]["text"])
            elif kind == "message_delta":
                stop = event.get("delta", {}).get("stop_reason", stop)
            elif kind == "error":
                raise LLMError(f"stream error: {event.get('error')}")
    if stop == "max_tokens":
        raise LLMError("model output hit max_tokens; the JSON is truncated")
    return "".join(parts)


def _openai(prompt: str, model: str, key: str, url: str) -> str:
    body = {"model": model, "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": prompt}]}
    headers = {"authorization": f"Bearer {key}", "content-type": "application/json"}
    with _post(url, headers, body, False) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choice = data["choices"][0]
    if choice.get("finish_reason") == "length":
        raise LLMError("model output hit the length limit; the JSON is truncated")
    return choice["message"]["content"]


def provider_from_env() -> tuple[str, str, str, str] | None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return ("anthropic", os.environ.get("CALLSTATE_MODEL", DEFAULT_ANTHROPIC_MODEL),
                os.environ["ANTHROPIC_API_KEY"], os.environ.get("ANTHROPIC_BASE_URL", ANTHROPIC_URL))
    if os.environ.get("OPENAI_API_KEY"):
        model = os.environ.get("CALLSTATE_MODEL")
        if not model:
            raise LLMError("OPENAI_API_KEY is set but CALLSTATE_MODEL is not; name the model to use")
        base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        return ("openai", model, os.environ["OPENAI_API_KEY"], base + "/chat/completions")
    return None


def complete(prompt: str, provider: tuple[str, str, str, str]) -> str:
    name, model, key, url = provider
    if name == "anthropic":
        return _anthropic(prompt, model, key, url)
    return _openai(prompt, model, key, url)


def repair_prompt(prompt: str, previous: str, errors: list[str]) -> str:
    listed = "\n".join(f"- {e}" for e in errors[:60])
    return (prompt + "\n\n# Your previous answer\n\n" + previous +
            "\n\n# Problems found by the validator\n\n" + listed +
            "\n\nReturn the full corrected JSON object. Fix only these problems. Quotes must be copied character for character from the numbered transcript.")
