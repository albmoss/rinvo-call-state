import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .dates import WEEKDAY_PL
from .schema import OUTPUT
from .transcript import Transcript

TEMPLATE = Path(__file__).with_name("prompt_template.md")
API_BASE = "https://api.anthropic.com"
RETRY_WAITS = [2, 8]
DEFAULT_MODEL = "claude-opus-5-5"


class LLMError(RuntimeError):
    pass


def call_metadata(t: Transcript) -> str:
    rows = [f"- Call date: {t.call_date.isoformat()} ({WEEKDAY_PL[t.call_date.weekday()]}), time zone Europe/Warsaw",
            f"- Customer: {t.customer or 'unknown'}", f"- Title: {t.title}"]
    present = [p for p in t.people if p.present]
    absent = [p for p in t.people if not p.present]
    rows.append("- On the call: " + "; ".join(f"{p.name} ({', '.join(x for x in (p.role, p.org, p.email) if x)})" for p in present))
    if absent:
        rows.append("- Mentioned, not on the call: " + "; ".join(f"{p.name} ({p.role})" if p.role else p.name for p in absent))
    return "\n".join(rows)


def previous_block(prev: dict | None) -> str:
    if not prev:
        return "None. This is the first processed call for this client."
    lines = [f"Record built from calls up to {prev['last_call']}."]
    lines.append("Authority:")
    lines += [f"- {a['key']}: {a['decision']}; approvers {', '.join(a['approvers']) or '-'}"
              + (f"; not authorized {', '.join(a['not_authorized'])}" if a["not_authorized"] else "") for a in prev["authority"]]
    lines.append("Current facts:")
    lines += [f"- {f['key']} ({f['status']}): {f['value']}" for f in prev["facts"] if f["status"] != "superseded"]
    lines.append("Items still open, on hold or in force:")
    for it in prev["items"]:
        w = it.get("when") or {}
        span = " to ".join(x for x in (w.get("start"), w.get("end")) if x)
        lines.append(f"- {it['id']} [{it['type']}/{it['state']}] {it['title']}. Owner: {it['owner'].get('person') or it['owner']['party']}."
                     + (f" When: {span}." if span else "")
                     + (f" Condition: {it['condition']['text']}" if it.get("condition") else ""))
    return "\n".join(lines)


def build_prompt(t: Transcript, prev: dict | None) -> str:
    return (TEMPLATE.read_text(encoding="utf-8")
            .replace("{{CALL_METADATA}}", call_metadata(t))
            .replace("{{PREVIOUS_LEDGER}}", previous_block(prev))
            .replace("{{TRANSCRIPT}}", t.numbered()))


def parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"model output is not valid JSON: {e}") from None


def _stream(req: urllib.request.Request) -> tuple[str, str | None]:
    parts: list[str] = []
    stop = None
    with urllib.request.urlopen(req, timeout=900) as resp:
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
    return "".join(parts), stop


def complete(prompt: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise LLMError("ANTHROPIC_API_KEY is not set")
    body = {"model": os.environ.get("CALLSTATE_MODEL", DEFAULT_MODEL), "max_tokens": 128000, "stream": True,
            "messages": [{"role": "user", "content": prompt}],
            "output_config": {"format": {"type": "json_schema", "schema": OUTPUT}}}
    url = os.environ.get("ANTHROPIC_BASE_URL", API_BASE).rstrip("/") + "/v1/messages"
    data = json.dumps(body).encode("utf-8")
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    for wait in RETRY_WAITS + [None]:
        try:
            text, stop = _stream(urllib.request.Request(url, data=data, method="POST", headers=headers))
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 529) and wait is not None:
                time.sleep(wait)
                continue
            raise LLMError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:2000]}") from None
        except (urllib.error.URLError, ConnectionResetError) as e:
            if wait is not None:
                time.sleep(wait)
                continue
            raise LLMError(f"cannot reach the API: {getattr(e, 'reason', e)}") from None
    if stop == "max_tokens":
        raise LLMError("model output hit max_tokens; the JSON is truncated")
    return text


def repair_prompt(prompt: str, previous: str, errors: list[str]) -> str:
    listed = "\n".join(f"- {e}" for e in errors[:80])
    return (prompt + "\n\n# Your previous answer\n\n" + previous + "\n\n# Problems found by the validator\n\n" + listed +
            "\n\nReturn the full corrected JSON object. Fix only these problems. Quotes must be copied character for character from the cited line.")
