import datetime as dt
import json
import re
from pathlib import Path

from . import llm, render
from .transcript import Transcript, fold, load
from .verify import QuoteIndex, check_item, cross_checks


class NeedsExtraction(Exception):
    pass


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", fold(text or "call")).strip("_") or "call"


def find_previous(out_root: Path, customer_slug: str, call_date: dt.date) -> Path | None:
    best = None
    for p in (out_root / customer_slug).glob("*/ledger.json"):
        try:
            d = dt.date.fromisoformat(json.loads(p.read_text(encoding="utf-8"))["call"]["date"])
        except (ValueError, KeyError, json.JSONDecodeError):
            continue
        if d < call_date and (best is None or d > best[0]):
            best = (d, p)
    return best[1] if best else None


def _errors_for_repair(items: list[dict]) -> list[str]:
    errs = []
    for it in items:
        for i in it.get("issues", []):
            if i["severity"] == "error":
                errs.append(f"{it.get('local_id')}: {i['message']}")
    return errs


def _check_all(raw: dict, t: Transcript) -> list[dict]:
    qi = QuoteIndex(t)
    items = []
    for n, it in enumerate(raw.get("items") or [], start=1):
        it = dict(it)
        it["id"] = f"I{n:02d}"
        items.append(check_item(it, qi, t))
    id_map = {it.get("local_id"): it["id"] for it in items if it.get("local_id")}
    for it in items:
        it["related"] = [id_map.get(r, r) for r in it.get("related") or []]
    return items


def _link_previous(items: list[dict], previous: dict | None, updates: list[dict], call_date: str) -> tuple[list[dict], list[dict]]:
    if not previous:
        return items, []
    prev_items = {p["id"]: p for p in previous["items"]}
    continued = set()
    for it in items:
        pid = it.get("previous_id")
        if pid and pid in prev_items:
            continued.add(pid)
            it["known"] = {"status": "known_previous_call", "basis": f"continues {pid}"}
        elif pid:
            it.setdefault("issues", []).append({"severity": "warn", "code": "unknown_previous_id", "message": f"previous_id {pid} is not in the previous ledger"})
            it["previous_id"] = None
        if not it.get("previous_id"):
            words = set(re.findall(r"\w{4,}", fold(it["title"])))
            for p in prev_items.values():
                pw = set(re.findall(r"\w{4,}", fold(p["title"])))
                if words and pw and len(words & pw) / len(words | pw) >= 0.5 and p["type"] == it["type"]:
                    it.setdefault("issues", []).append({"severity": "warn", "code": "possible_previous_match",
                                                        "message": f"title resembles previous item {p['id']} ({p['title']}); link or confirm it is new"})
    upd = {u.get("previous_id"): u for u in updates or [] if u.get("previous_id") in prev_items}
    carried = []
    for pid, p in prev_items.items():
        if pid in continued:
            continue
        c = dict(p)
        if pid in upd:
            c["state"] = upd[pid].get("new_state") or c["state"]
            c["update_note"] = upd[pid].get("note")
        w = c.get("when") or {}
        if c["type"] == "constraint" and c["state"] == "active" and w.get("end") and w["end"] < call_date:
            c["state"] = "closed"
            c["update_note"] = f"window ended {w['end']}"
        if c["state"] in ("closed", "rejected", "noted"):
            continue
        c["carried"] = True
        carried.append(c)
    return items, carried


def _ledger_entry(it: dict, call_date: str) -> dict:
    keep = ("type", "state", "title", "owner", "action", "when", "condition", "limit", "approvers", "value", "known", "customer_visible")
    e = {k: it.get(k) for k in keep}
    e["id"] = it["id"] if "/" in it["id"] else f"{call_date}/{it['id']}"
    e["source_call"] = it.get("source_call", call_date)
    e["evidence"] = [{k: ev.get(k) for k in ("speaker", "line", "quote", "role")} for ev in it["evidence"] if ev.get("verification") != "not_found"]
    return e


def _stats(items: list[dict]) -> dict:
    evs = [e for i in items for e in i["evidence"]]
    ws = [i["when"] for i in items if i.get("when")]
    claims = [c for i in items for c in i.get("claims", [])]
    return {
        "items": len(items), "quarantined": sum(1 for i in items if i.get("quarantined")),
        "quotes_total": len(evs), "verified": sum(e["verification"] == "verified" for e in evs),
        "normalized": sum(e["verification"] == "verified_normalized" for e in evs),
        "repaired": sum(e["verification"] == "repaired" for e in evs),
        "speaker_fixed": sum(e["verification"] == "speaker_mismatch" for e in evs),
        "not_found": sum(e["verification"] == "not_found" for e in evs),
        "dates_rule": sum(w["resolution"] == "rule" for w in ws), "dates_model": sum(w["resolution"] == "model" for w in ws),
        "dates_conflict": sum(w["resolution"] == "conflict" for w in ws), "dates_unresolved": sum(w["resolution"] == "unresolved" for w in ws),
        "claims": len(claims), "claims_checked": sum(c["check"] != "not_checked" for c in claims),
        "claims_unchecked": sum(c["check"] == "not_checked" for c in claims),
    }


def run(transcript_path: str, out_root: str = "out", extraction: str | None = None, previous: str | None = "auto",
        call_date: str | None = None, log=print) -> Path:
    t = load(transcript_path, dt.date.fromisoformat(call_date) if call_date else None)
    if t.call_date is None:
        raise SystemExit("No call date found in the transcript header. Pass --date YYYY-MM-DD.")
    if not t.turns:
        raise SystemExit("No speaker turns found. Expected lines like '**Name:** text' or 'Name: text'.")
    root = Path(out_root)
    cust = slug(t.customer or Path(transcript_path).stem)
    out = root / cust / t.call_date.isoformat()
    (out / "drafts").mkdir(parents=True, exist_ok=True)

    prev_path = None
    if previous == "auto":
        prev_path = find_previous(root, cust, t.call_date)
    elif previous:
        prev_path = Path(previous)
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path else None
    log(f"call {t.call_date} · {t.customer} · {len(t.turns)} turns · previous ledger: {prev_path or 'none'}")

    prompt = llm.build_prompt(t, prev)
    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    provider = None
    if extraction:
        text = Path(extraction).read_text(encoding="utf-8")
        source = f"replayed from {extraction}"
    else:
        provider = llm.provider_from_env()
        if not provider:
            raise NeedsExtraction(str(out / "prompt.md"))
        log(f"extracting with {provider[0]}:{provider[1]} ...")
        text = llm.complete(prompt, provider)
        source = f"{provider[0]}:{provider[1]}"
    (out / "raw_response.json").write_text(text, encoding="utf-8")
    raw = llm.parse_json(text)
    items = _check_all(raw, t)
    errors = _errors_for_repair(items)
    if errors and provider:
        log(f"{len(errors)} validation errors, asking the model for one repair pass")
        text2 = llm.complete(llm.repair_prompt(prompt, text, errors), provider)
        (out / "raw_response_repair.json").write_text(text2, encoding="utf-8")
        try:
            raw2 = llm.parse_json(text2)
            items2 = _check_all(raw2, t)
            if len(_errors_for_repair(items2)) < len(errors):
                raw, items, source = raw2, items2, source + " + repair pass"
        except (llm.LLMError, json.JSONDecodeError) as e:
            log(f"repair pass unusable: {e}")
    notes = cross_checks(items)
    items, carried = _link_previous(items, prev, raw.get("previous_updates") or [], t.call_date.isoformat())

    head = "\n".join(t.lines[t.turns[0].line - 1:t.turns[0].line + 6]) if t.turns else ""
    rc = raw.get("call") or {}
    call = {
        "customer": t.customer or rc.get("customer") or cust, "date": t.call_date.isoformat(),
        "transcript": str(transcript_path).replace("\\", "/"), "extraction": source,
        "previous": str(prev_path).replace("\\", "/") if prev_path else None,
        "customer_contact": rc.get("customer_contact") or {}, "rinvo_contact": rc.get("rinvo_contact") or {},
        "informal": not re.search(r"\b(Pan|Pani|Państwo)\b", head) or bool(re.search(r"\b(Cześć|Hej)\b", head)),
    }
    for who in ("customer_contact", "rinvo_contact"):
        p = t.person(call[who].get("name"))
        if p and p.email and not call[who].get("email"):
            call[who]["email"] = p.email
    stats = _stats(items)
    crs = render.change_requests(items)
    rems = render.reminders(call, items, [i for i in items if i["type"] == "constraint"])
    tks = render.tickets(items)
    al = render.alerts(call, items, notes)

    def dump(name, obj):
        (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    dump("items.json", {"call": call, "stats": stats, "items": items})
    dump("ledger.json", {"call": call, "items": [_ledger_entry(i, call["date"]) for i in items if not i.get("quarantined")] + carried})
    dump("drafts/actions.json", {"change_requests": crs, "reminders": rems, "tickets": tks, "alerts": al})
    (out / "report.md").write_text(render.report(call, items, carried), encoding="utf-8")
    (out / "review.md").write_text(render.review_md(call, items, crs, rems, tks, al, stats), encoding="utf-8")
    (out / "constraints.md").write_text(render.constraints_md(call, items, carried), encoding="utf-8")
    (out / "next_call_brief.md").write_text(render.next_call_brief(call, items, carried), encoding="utf-8")
    (out / "drafts/recap_email_pl.md").write_text(render.recap_email(call, items), encoding="utf-8")
    (out / "drafts/reminders.md").write_text(render.reminders_md(rems), encoding="utf-8")
    (out / "drafts/change_requests.md").write_text(render.change_requests_md(crs), encoding="utf-8")
    (out / "drafts/tickets.md").write_text(render.tickets_md(tks), encoding="utf-8")
    (out / "drafts/internal_alerts.md").write_text(render.alerts_md(al), encoding="utf-8")
    log(f"{stats['items']} items ({stats['quarantined']} quarantined) · quotes {stats['quotes_total']}: "
        f"{stats['verified'] + stats['normalized']} verified, {stats['repaired']} repaired, {stats['speaker_fixed']} speaker fixed, {stats['not_found']} not found")
    log(f"{len(crs)} change requests · {len(rems)} reminders · {len(tks)} tickets · {len(al)} alerts · {len(carried)} carried items")
    log(f"output: {out}")
    return out
