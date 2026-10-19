import argparse
import json
import sys
from pathlib import Path

from . import llm
from .evaluate import evaluate, to_markdown
from .pipeline import NeedsExtraction, run

USAGE = """python -m callstate TRANSCRIPT [options]       process a call
python -m callstate eval GOLD ITEMS [--out DIR]   score items.json against an annotation"""


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if argv and argv[0] == "eval":
        ap = argparse.ArgumentParser(prog="python -m callstate eval")
        ap.add_argument("gold")
        ap.add_argument("items")
        ap.add_argument("--out", help="directory for metrics.json and metrics.md (default: next to ITEMS)")
        a = ap.parse_args(argv[1:])
        m = evaluate(a.gold, a.items)
        out = Path(a.out or Path(a.items).parent)
        out.mkdir(parents=True, exist_ok=True)
        (out / "metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        md = to_markdown(m)
        (out / "metrics.md").write_text(md, encoding="utf-8")
        print(md.split("## Errors")[0])
        print(f"written: {out / 'metrics.md'}")
        return 0
    ap = argparse.ArgumentParser(prog="python -m callstate", usage=USAGE)
    ap.add_argument("transcript")
    ap.add_argument("--out", default="out", help="output root (default: out)")
    ap.add_argument("--extraction", help="use a saved model response instead of calling the API")
    ap.add_argument("--previous", default="auto", help="previous ledger.json; default: newest earlier call for the same customer under --out")
    ap.add_argument("--no-previous", action="store_true", help="ignore earlier calls")
    ap.add_argument("--date", help="call date YYYY-MM-DD if the header has none")
    a = ap.parse_args(argv)
    try:
        run(a.transcript, a.out, a.extraction, None if a.no_previous else a.previous, a.date)
    except NeedsExtraction as e:
        print(f"No API key found. Set ANTHROPIC_API_KEY (or OPENAI_API_KEY with CALLSTATE_MODEL),\n"
              f"or give the prompt at {e} to a model and rerun with --extraction <response.json>.", file=sys.stderr)
        return 2
    except llm.LLMError as e:
        print(f"model call failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
