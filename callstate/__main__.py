import argparse
import json
import sys
from pathlib import Path

from . import llm, render, store, views
from .pipeline import NeedsExtraction, ValidationFailed, run

COMMANDS = {"serve", "review", "event", "check", "eval"}


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    if not argv or argv[0] not in COMMANDS:
        ap = argparse.ArgumentParser(prog="python -m callstate", description="Process a call transcript into the client ledger.")
        ap.add_argument("transcript")
        ap.add_argument("--db", default="callstate.db")
        ap.add_argument("--out", default="out")
        ap.add_argument("--extraction", help="replay a saved model response instead of calling the API")
        ap.add_argument("--date", help="call date YYYY-MM-DD if the header has none")
        a = ap.parse_args(argv)
        try:
            run(a.transcript, a.db, a.out, a.extraction, a.date)
        except NeedsExtraction as e:
            print(f"ANTHROPIC_API_KEY is not set. Set it, or give the prompt at {e} to a model and rerun with --extraction <response.json>.", file=sys.stderr)
            return 2
        except (ValidationFailed, llm.LLMError) as e:
            print(f"failed: {e}", file=sys.stderr)
            return 1
        return 0
    cmd, rest = argv[0], argv[1:]
    ap = argparse.ArgumentParser(prog=f"python -m callstate {cmd}")
    ap.add_argument("--db", default="callstate.db")
    ap.add_argument("--customer", help="customer slug (default: the only one in the database)")
    ap.add_argument("--day", help="YYYY-MM-DD, Europe/Warsaw (default: today)")
    if cmd == "serve":
        ap.add_argument("--port", type=int, default=8765)
        a = ap.parse_args(rest)
        from .web import serve
        serve(a.db, a.port, a.day)
        return 0
    if cmd == "eval":
        from .evaluate import evaluate, to_markdown
        ap.add_argument("gold")
        ap.add_argument("items")
        ap.add_argument("--out")
        a = ap.parse_args(rest)
        m = evaluate(a.gold, a.items)
        out = Path(a.out or Path(a.items).parent)
        out.mkdir(parents=True, exist_ok=True)
        (out / "metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        md = to_markdown(m)
        (out / "metrics.md").write_text(md, encoding="utf-8")
        print(md.split("## Errors")[0])
        return 0
    if cmd == "event":
        ap.add_argument("item_id")
        ap.add_argument("kind", choices=["done", "received", "sent", "condition_met", "reopened", "cancelled"])
        ap.add_argument("--note", default="")
    if cmd == "check":
        ap.add_argument("--sender", required=True)
        ap.add_argument("--text", required=True)
    a = ap.parse_args(rest)
    from .web import today_iso
    db = store.connect(a.db)
    customer = a.customer or (store.customers(db) or [None])[0]
    if not customer:
        print("no calls ingested", file=sys.stderr)
        return 1
    day = a.day or today_iso()
    if cmd == "review":
        print(render.review_md(db, customer, day))
    elif cmd == "event":
        store.record_event(db, a.item_id, a.kind, day, note=a.note)
        print(f"{a.item_id}: {a.kind} on {day}")
    elif cmd == "check":
        res = views.check_request(db, customer, a.sender, a.text, day)
        if not res:
            print("no hold or constraint matches")
        for r in res:
            print(f"{r['item']['id']} {r['item']['title']}\n  {r['verdict']}\n  rule: {r['rule']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
