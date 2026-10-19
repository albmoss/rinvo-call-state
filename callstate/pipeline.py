import datetime as dt
import json
import os
import re
from pathlib import Path

from . import llm, render, store
from .schema import validate
from .transcript import fold, load
from .verify import QuoteIndex, cross_checks, normalize, semantic_errors


class NeedsExtraction(Exception):
    pass


class ValidationFailed(Exception):
    pass


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", fold(text or "call")).strip("_") or "call"


def _check(text: str, qi: QuoteIndex) -> tuple[dict | None, list[str], dict]:
    try:
        raw = llm.parse_json(text)
    except llm.LLMError as e:
        return None, [str(e)], {}
    errs = validate(raw)
    if errs:
        return raw, errs, {}
    return raw, [], semantic_errors(raw, qi)


def run(transcript_path: str, db_path: str = "callstate.db", out_root: str = "out", extraction: str | None = None,
        call_date: str | None = None, log=print) -> Path:
    t = load(transcript_path, dt.date.fromisoformat(call_date) if call_date else None)
    if t.call_date is None:
        raise SystemExit("No call date in the transcript header. Pass --date YYYY-MM-DD.")
    if not t.turns:
        raise SystemExit("No speaker turns found. Expected lines like '**Name:** text'.")
    customer = slug(t.customer or Path(transcript_path).stem)
    out = Path(out_root) / customer / t.call_date.isoformat()
    (out / "drafts").mkdir(parents=True, exist_ok=True)
    db = store.connect(db_path)
    prev = store.previous_record(db, customer, t.call_date.isoformat())
    log(f"call {t.call_date} · {t.customer} · {len(t.turns)} turns · previous record: {prev['last_call'] if prev else 'none'}")
    prompt = llm.build_prompt(t, prev)
    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    qi = QuoteIndex(t)

    if extraction:
        text = Path(extraction).read_text(encoding="utf-8")
        source = f"replayed: {extraction}"
    else:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise NeedsExtraction(str(out / "prompt.md"))
        log("extracting ...")
        text = llm.complete(prompt)
        source = f"anthropic:{os.environ.get('CALLSTATE_MODEL', llm.DEFAULT_MODEL)}"
    (out / "raw_response.json").write_text(text, encoding="utf-8")
    raw, schema_errs, sem = _check(text, qi)
    if (schema_errs or sem) and not extraction:
        listed = schema_errs + [e for v in sem.values() for e in v]
        log(f"{len(listed)} validation errors, one repair pass")
        text2 = llm.complete(llm.repair_prompt(prompt, text, listed))
        (out / "raw_response_repair.json").write_text(text2, encoding="utf-8")
        raw, schema_errs, sem = _check(text2, qi)
        source += " + repair pass"
    if schema_errs:
        (out / "validation_errors.json").write_text(json.dumps(schema_errs, ensure_ascii=False, indent=2), encoding="utf-8")
        raise ValidationFailed(f"{len(schema_errs)} schema errors, nothing ingested; see {out / 'validation_errors.json'}:\n" + "\n".join(schema_errs[:15]))

    item_q = {k: v for k, v in sem.items() if not k.startswith("account.")}
    acc_q = {k: v for k, v in sem.items() if k.startswith("account.")}
    call_id = t.call_date.isoformat()
    account, items = normalize(raw, t, qi, item_q, call_id)
    cross_checks([i for i in items if not i["quarantined"]])
    call = {"date": call_id, "customer": t.customer, "transcript": str(transcript_path).replace("\\", "/"), "extraction": source,
            "customer_contact": raw["call"]["customer_contact"], "customer_contact_vocative_pl": raw["call"]["customer_contact_vocative_pl"],
            "rinvo_contact": raw["call"]["rinvo_contact"], "account_quarantine": acc_q}
    store.ingest(db, customer, call, account, items, raw["previous_updates"], raw["conflicts"], acc_q)
    write_outputs(db, customer, out, call_id)
    nq = sum(i["quarantined"] for i in items)
    log(f"{len(items)} items, {nq} quarantined · account: {len(account['people'])} people, {len(account['authority'])} authority, "
        f"{len(account['facts'])} facts, {len(acc_q)} quarantined entries")
    log(f"output: {out}")
    return out


def write_outputs(db, customer: str, out: Path, day: str) -> None:
    call_items = [i for i in store.items(db, customer) if i["call"] == out.name]
    (out / "items.json").write_text(json.dumps({"call": store.calls(db, customer)[-1]["meta"], "items": call_items}, ensure_ascii=False, indent=2), encoding="utf-8")
    ledger = {"customer": customer, "calls": store.calls(db, customer), "account": store.account(db, customer),
              "items": store.items(db, customer), "conflicts": store.conflicts(db, customer)}
    (out / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / f"review_{day}.md").write_text(render.review_md(db, customer, day), encoding="utf-8")
    (out / "client.md").write_text(render.client_md(db, customer), encoding="utf-8")
    (out / "change_specs.md").write_text(render.change_specs(db, customer), encoding="utf-8")
    (out / "dev_tickets.md").write_text(render.dev_tickets(db, customer), encoding="utf-8")
    (out / "backlog.md").write_text(render.backlog(db, customer), encoding="utf-8")
    (out / "next_call_brief.md").write_text(render.next_call_brief(db, customer, day), encoding="utf-8")
    for mid, text in render.meeting_briefs(db, customer).items():
        (out / f"meeting_brief_{mid.split('/')[-1]}.md").write_text(text, encoding="utf-8")
    (out / "drafts" / "recap_email_pl.md").write_text(render.recap_email(db, customer), encoding="utf-8")
    (out / "drafts" / "messages_pl.md").write_text(render.messages_md(db, customer, day), encoding="utf-8")
