import datetime as dt

from .dates import next_working_day, pl_date, pl_when

OPEN_LIKE = ("open", "conditional")
HOLD = ("deferred", "pending_approval", "blocked")


def _first_line(it: dict) -> int:
    lines = [e["line"] for e in it["evidence"] if e.get("line")]
    return min(lines) if lines else 10**6


def _when_text(it: dict) -> str:
    w = it.get("when")
    if not w or not (w.get("start") or w.get("end")):
        return ""
    span = w["start"] if w["start"] == w["end"] else " .. ".join(x or "?" for x in (w.get("start"), w.get("end")))
    if w["kind"] == "by":
        span = f"by {w['end']}"
    elif w["kind"] == "not_before":
        span = f"not before {w['start']}"
    tm = f" {w['time']}" if w.get("time") else ""
    return f"{span}{tm} (\"{w['phrase']}\", {w['resolution']}: {w.get('basis') or 'n/a'})"


def _quote(e: dict) -> str:
    mark = {"verified": "verified", "verified_normalized": "verified (normalized)", "repaired": "repaired to verbatim",
            "speaker_mismatch": "verified, speaker corrected", "not_found": "NOT FOUND"}[e["verification"]]
    return f"> „{e['quote']}” ({e['speaker']}, line {e.get('line', '?')}, {e['role']}, {mark})"


def _who(it: dict) -> str:
    o = it["owner"]
    return f"{o.get('person') or '-'} ({o.get('party')})"


def report(call: dict, items: list[dict], carried: list[dict]) -> str:
    out = [f"# Call items: {call['customer']}, {call['date']}", "",
           f"Transcript: `{call['transcript']}`. {len(items)} items from this call"
           + (f", {len(carried)} carried from {call['previous']}" if carried else "") + ".", ""]
    for it in sorted(items, key=_first_line):
        out.append(f"## {it['id']} · {it['type']} · {it['state']} · {it['title']}")
        out.append("")
        rows = [("Owner", _who(it)), ("Action", it.get("action") or ""), ("When", _when_text(it))]
        if it.get("condition"):
            rows.append(("Condition", f"{it['condition'].get('text')} (\"{it['condition'].get('phrase')}\")"))
        if it.get("approvers"):
            rows.append(("Approvers", ", ".join(it["approvers"])))
        if it.get("limit") and it["limit"].get("max_count"):
            rows.append(("Limit", f"max {it['limit']['max_count']}" + (f" via {it['limit']['channel']}" if it["limit"].get("channel") else "")))
        if it.get("value"):
            rows.append(("Value", f"{it['value'].get('current') or '?'} → {it['value'].get('requested') or '?'}"))
        k = it.get("known") or {}
        rows.append(("Known", k.get("status", "new") + (f": {k['basis']}" if k.get("basis") else "")))
        rows.append(("Revised", "yes, final state shown; superseded quotes kept below" if it.get("revised") else "no"))
        for label, val in rows:
            if val:
                out.append(f"- **{label}:** {val}")
        out.append("")
        out.extend(_quote(e) for e in it["evidence"])
        out.append("")
        if it.get("claims"):
            out.append("Claims:")
            out.extend(f"- {c['text']} [{c['source']}: {c['check']}, {c['detail']}]" for c in it["claims"])
            out.append("")
        if it.get("ambiguities"):
            out.append("Ambiguities:")
            out.extend(f"- {a}" for a in it["ambiguities"])
            out.append("")
        issues = [i for i in it.get("issues", []) if i["severity"] != "info"]
        if issues:
            out.append("Checks:")
            out.extend(f"- {i['severity']}: {i['message']}" for i in issues)
            out.append("")
    if carried:
        out.append(f"## Carried from {call['previous']}")
        out.append("")
        out.extend(f"- {c['id']} [{c['type']}/{c['state']}] {c['title']}" for c in carried)
        out.append("")
    return "\n".join(out)


def recap_email(call: dict, items: list[dict]) -> str:
    informal = call.get("informal", True)
    visible = [i for i in sorted(items, key=_first_line) if i.get("customer_visible") and not i.get("quarantined") and i.get("recap_pl")]

    def line(it: dict) -> str:
        w = it.get("when")
        date = pl_when(w) if w and w.get("kind") != "past" and w.get("resolution") in ("rule", "model") else ""
        txt = it["recap_pl"].strip()
        return f"- {txt}" + (f" ({date})" if date and date not in txt else "")

    ours = [i for i in visible if i["owner"]["party"] == "rinvo" and i["state"] in OPEN_LIKE and i["type"] in ("bug", "config_change", "commitment", "billing")]
    yours = [i for i in visible if i["owner"]["party"] == "customer" and i["state"] in OPEN_LIKE and i["type"] == "commitment"]
    hold = [i for i in visible if i["state"] in HOLD and i["type"] != "constraint"]
    product = [i for i in visible if i["type"] == "feature_request" and i["state"] in OPEN_LIKE]
    rules = [i for i in visible if i["type"] == "constraint" and i["state"] == "active"]
    contact = call.get("customer_contact") or {}
    rinvo = call.get("rinvo_contact") or {}
    greet = f"Cześć {contact.get('vocative_pl') or contact.get('name') or ''}," if informal else "Dzień dobry,"
    out = ["<!-- DRAFT. Not sent. A person must review and send it. -->", "",
           f"**Do:** {contact.get('email') or '(brak adresu w transkrypcji)'}  ",
           f"**Temat:** Podsumowanie rozmowy z {pl_date(call['date'])}", "", greet, "",
           f"poniżej ustalenia z naszej rozmowy z {pl_date(call['date'])}.", ""]
    sections = [("Po naszej stronie", ours),
                ("Po Twojej stronie" if informal else "Po Państwa stronie", yours),
                ("Wstrzymane do decyzji", hold),
                ("Zapisane jako propozycje rozwoju produktu (bez terminu)", product),
                ("Zasady, których się trzymamy", rules)]
    for title, group in sections:
        if group:
            out.append(f"**{title}**")
            out.append("")
            out.extend(line(i) for i in group)
            out.append("")
    out.append("Jeśli coś się nie zgadza, daj znać." if informal else "Jeśli coś się nie zgadza, proszę o informację.")
    out.append("")
    out.append("Pozdrawiam,")
    out.append(rinvo.get("name") or "")
    return "\n".join(out)


def reminders(call: dict, items: list[dict], constraints: list[dict]) -> list[dict]:
    out = []
    for it in sorted(items, key=_first_line):
        if it["type"] != "follow_up" or it["state"] not in OPEN_LIKE or it.get("quarantined"):
            continue
        w = it.get("when") or {}
        deadline = w.get("end") or w.get("start")
        send = next_working_day(dt.date.fromisoformat(deadline)).isoformat() + "T09:00" if deadline else None
        watch = [r for r in it.get("related") or []]
        conflicts = [i["message"] for i in it.get("issues", []) if i["code"] == "inside_constraint_window"]
        out.append({
            "id": f"REM-{it['id']}", "item": it["id"], "status": "proposed, not scheduled",
            "to": (call.get("customer_contact") or {}).get("email"),
            "watches_deadline": deadline, "proposed_send_at": send,
            "trigger": (it.get("condition") or {}).get("text"),
            "pre_send_check": "Confirm the awaited item has not arrived (inbox, shared drive). If it arrived, cancel.",
            "max_count": (it.get("limit") or {}).get("max_count"), "channel": (it.get("limit") or {}).get("channel"),
            "draft_pl": it.get("draft_pl"), "related_items": watch, "constraint_conflicts": conflicts,
            "evidence": [{"speaker": e["speaker"], "line": e["line"], "quote": e["quote"]} for e in it["evidence"] if e["verification"] != "not_found"],
        })
    return out


def reminders_md(rems: list[dict]) -> str:
    out = ["# Reminder drafts", "", "Nothing here is scheduled. Each reminder needs approval, and the pre-send check must pass on the day.", ""]
    for r in rems:
        out += [f"## {r['id']}", "",
                f"- Proposed send: {r['proposed_send_at']} (deadline watched: {r['watches_deadline']})",
                f"- Trigger: {r['trigger']}",
                f"- Maximum sends: {r['max_count'] if r['max_count'] else 'NOT SET, do not schedule'}" + (f", channel {r['channel']}" if r['channel'] else ""),
                f"- Pre-send check: {r['pre_send_check']}"]
        if r["constraint_conflicts"]:
            out.append("- Constraint warnings: " + "; ".join(r["constraint_conflicts"]))
        out += ["", "Draft (PL):", "", "> " + (r["draft_pl"] or "(no draft)").replace("\n", "\n> "), ""]
        out += [f"Source: „{e['quote']}” ({e['speaker']}, line {e['line']})" for e in r["evidence"]]
        out += ["", "- [ ] approve   - [ ] reject", ""]
    return "\n".join(out)


def change_requests(items: list[dict]) -> list[dict]:
    out = []
    for it in sorted(items, key=_first_line):
        if it["type"] != "config_change" or it.get("quarantined"):
            continue
        cust = [e for e in it["evidence"] if e["verification"] != "not_found"]
        if it["state"] == "open":
            status = "ready for review: execute after approval"
        elif it["state"] == "conditional":
            status = "hold: execute only when the condition holds, after approval"
        else:
            status = f"do not execute ({it['state']})"
        out.append({
            "id": f"CR-{it['id']}", "item": it["id"], "title": it["title"], "status": status, "state": it["state"],
            "current": (it.get("value") or {}).get("current"), "requested": (it.get("value") or {}).get("requested"),
            "action": it.get("action"), "due": it.get("when"), "condition": it.get("condition"),
            "approvers": ["Rinvo reviewer"] + it.get("approvers", []),
            "data_checks": it.get("claims", []),
            "warnings": [i["message"] for i in it.get("issues", []) if i["severity"] in ("warn", "error")],
            "evidence": [{"speaker": e["speaker"], "line": e["line"], "role": e["role"], "quote": e["quote"]} for e in cust],
        })
    return out


def change_requests_md(crs: list[dict]) -> str:
    out = ["# Configuration change requests", "",
           "Drafts only. The system has no write access to agent configuration. A person executes an approved request and records who approved it.", ""]
    for c in crs:
        out += [f"## {c['id']} · {c['title']}", "", f"- Status: **{c['status']}**",
                f"- Change: {c['current'] or '?'} → {c['requested'] or '?'}", f"- Action: {c['action']}"]
        if c["due"] and (c["due"].get("start") or c["due"].get("end")):
            out.append(f"- Due: {c['due'].get('kind')} {c['due'].get('start') or ''} {c['due'].get('end') or ''} (\"{c['due'].get('phrase')}\")")
        if c["condition"]:
            out.append(f"- Condition: {c['condition'].get('text')}")
        out.append(f"- Approvals needed: {', '.join(c['approvers'])}")
        for d in c["data_checks"]:
            out.append(f"- Data check: {d['text']} [{d['check']}: {d['detail']}]")
        for w in c["warnings"]:
            out.append(f"- Warning: {w}")
        out.append("")
        out += [f"> „{e['quote']}” ({e['speaker']}, line {e['line']}, {e['role']})" for e in c["evidence"]]
        out += ["", "- [ ] approve   - [ ] reject", ""]
    return "\n".join(out)


def tickets(items: list[dict]) -> list[dict]:
    queue = {"bug": "engineering", "feature_request": "product backlog", "billing": "finance", "commitment": "account tasks"}
    out = []
    for it in sorted(items, key=_first_line):
        if it["type"] not in queue or it.get("quarantined") or it["state"] in ("closed", "rejected"):
            continue
        if it["type"] == "commitment" and it["owner"]["party"] != "rinvo":
            continue
        out.append({"id": f"TKT-{it['id']}", "item": it["id"], "queue": queue[it["type"]], "title": it["title"],
                    "state": it["state"], "assignee": it["owner"].get("person"), "action": it.get("action"),
                    "due": it.get("when"), "condition": it.get("condition"), "known": it.get("known"),
                    "claims_to_verify": [c for c in it.get("claims", []) if c["check"] == "not_checked"],
                    "evidence": [{"speaker": e["speaker"], "line": e["line"], "quote": e["quote"]} for e in it["evidence"] if e["verification"] != "not_found"]})
    return out


def tickets_md(tks: list[dict]) -> str:
    out = ["# Tickets and tasks (drafts)", ""]
    for q in ("engineering", "finance", "account tasks", "product backlog"):
        group = [t for t in tks if t["queue"] == q]
        if not group:
            continue
        out += [f"## {q.capitalize()}", ""]
        for t in group:
            due = t["due"] or {}
            when = f", due {due.get('end') or due.get('start')}" if (due.get("end") or due.get("start")) else ""
            out.append(f"### {t['id']} · {t['title']}")
            out.append("")
            out.append(f"- {t['state']}, assignee {t['assignee'] or '-'}{when}; known: {(t['known'] or {}).get('status', 'new')}")
            out.append(f"- {t['action']}")
            if t["condition"]:
                out.append(f"- Condition: {t['condition'].get('text')}")
            for c in t["claims_to_verify"]:
                out.append(f"- Verify: {c['text']} ({c['source']})")
            out += [f"> „{e['quote']}” ({e['speaker']}, line {e['line']})" for e in t["evidence"]]
            out.append("")
    return "\n".join(out)


def alerts(call: dict, items: list[dict], notes: list[dict]) -> list[dict]:
    out = []
    for it in sorted(items, key=_first_line):
        if it["type"] == "account_signal":
            out.append({"kind": "account_signal", "item": it["id"], "title": it["title"], "detail": it.get("action"),
                        "evidence": [f"„{e['quote']}” ({e['speaker']}, line {e['line']})" for e in it["evidence"] if e["verification"] != "not_found"]})
        for i in it.get("issues", []):
            if i["code"] in ("absent_owner", "quote_not_found", "unverified", "date_conflict", "final_is_superseded",
                             "revision_order", "claim_mismatch", "inside_constraint_window", "possible_duplicate", "missing_condition",
                             "missing_approver", "missing_limit", "unknown_person"):
                out.append({"kind": i["code"], "item": it["id"], "title": it["title"], "detail": i["message"]})
        for a in it.get("ambiguities") or []:
            out.append({"kind": "ambiguity", "item": it["id"], "title": it["title"], "detail": a})
    return out


def alerts_md(al: list[dict]) -> str:
    out = ["# Internal alerts", "", "Internal only. Never forwarded to the customer.", ""]
    order = ["account_signal", "absent_owner", "ambiguity", "date_conflict", "claim_mismatch", "inside_constraint_window",
             "final_is_superseded", "revision_order", "possible_duplicate", "quote_not_found", "unverified",
             "missing_condition", "missing_approver", "missing_limit", "unknown_person"]
    for kind in order:
        group = [a for a in al if a["kind"] == kind]
        if not group:
            continue
        out += [f"## {kind.replace('_', ' ')}", ""]
        for a in group:
            out.append(f"- **{a['item']}** {a['title']}: {a['detail']}")
            for e in a.get("evidence", []):
                out.append(f"  > {e}")
        out.append("")
    return "\n".join(out)


def constraints_md(call: dict, items: list[dict], carried: list[dict]) -> str:
    out = [f"# Constraint registry: {call['customer']}", "",
           "Every future change request, reminder, and draft is checked against this list. Carried into the next call until the window ends or the named approver lifts it.", ""]
    rows = [i for i in items if i["type"] == "constraint" and i["state"] == "active" and not i.get("quarantined")]
    rows += [c for c in carried if c["type"] == "constraint" and c["state"] == "active"]
    for c in sorted(rows, key=lambda x: x["id"]):
        w = c.get("when") or {}
        span = f" Valid {w.get('start') or ''}..{w.get('end') or ''}." if (w.get("start") or w.get("end")) else " No end date."
        lift = f" Only {', '.join(c['approvers'])} can lift it." if c.get("approvers") else ""
        src = c.get("source_call", call["date"])
        ev = next((e for e in c["evidence"] if e["role"] == "final"), c["evidence"][-1] if c["evidence"] else None)
        cite = f" „{ev['quote']}” ({ev['speaker']}, line {ev['line']}, call {src})" if ev else ""
        out.append(f"- **{c['id']}** {c['title']}. {c.get('action') or ''}{span}{lift}{cite}")
    return "\n".join(out) + "\n"


def next_call_brief(call: dict, items: list[dict], carried: list[dict]) -> str:
    allit = [i for i in items if not i.get("quarantined")] + carried
    out = [f"# Next call brief: {call['customer']}", "", f"Built from the call on {call['date']}.", ""]

    def due(i):
        w = i.get("when") or {}
        return w.get("end") or w.get("start") or "9999"

    groups = [
        ("Rinvo owes", [i for i in allit if i["owner"]["party"] == "rinvo" and i["state"] in OPEN_LIKE and i["type"] in ("bug", "config_change", "commitment", "billing")]),
        ("Waiting on the customer", [i for i in allit if i["owner"]["party"] == "customer" and i["state"] in OPEN_LIKE]),
        ("Pending approval", [i for i in allit if i["state"] == "pending_approval"]),
        ("Deferred: ask only if the reopen condition holds", [i for i in allit if i["state"] == "deferred"]),
        ("Blocked on input", [i for i in allit if i["state"] == "blocked"]),
    ]
    for title, group in groups:
        if not group:
            continue
        out += [f"## {title}", ""]
        for i in sorted(group, key=due):
            w = i.get("when") or {}
            d = w.get("end") or w.get("start")
            cond = f" Condition: {i['condition']['text']}" if i.get("condition") else ""
            who = i["owner"].get("person") or i["owner"]["party"]
            appr = f" Approver: {', '.join(i['approvers'])}." if i.get("approvers") and i["state"] in HOLD else ""
            out.append(f"- {i['id']} {i['title']} ({who}{', ' + d if d else ''}).{cond}{appr}")
        out.append("")
    cons = [i for i in allit if i["type"] == "constraint" and i["state"] == "active"]
    if cons:
        out += ["## Constraints in force", ""] + [f"- {c['id']} {c['title']}" for c in cons] + [""]
    amb = [(i["id"], a) for i in items for a in i.get("ambiguities") or []]
    if amb:
        out += ["## Open questions from the last call", ""] + [f"- {i}: {a}" for i, a in amb] + [""]
    return "\n".join(out)


def review_md(call: dict, items: list[dict], crs: list, rems: list, tks: list, al: list, stats: dict) -> str:
    out = [f"# Review checklist: {call['customer']}, {call['date']}", "",
           "Nothing below has been sent or executed. Approve each line before it leaves the system.", "",
           "## Verification", "",
           f"- Quotes: {stats['quotes_total']} cited, {stats['verified']} verified verbatim, {stats['normalized']} verified after normalization, "
           f"{stats['repaired']} repaired to the verbatim text, {stats['speaker_fixed']} with the speaker corrected, {stats['not_found']} not found.",
           f"- Items: {stats['items']} extracted, {stats['quarantined']} quarantined (no verifiable quote, excluded from every draft).",
           f"- Dates: {stats['dates_rule']} resolved by rule, {stats['dates_model']} taken from the model, {stats['dates_conflict']} rule/model conflicts, {stats['dates_unresolved']} unresolved.",
           f"- Claims: {stats['claims']} made in the call, {stats['claims_checked']} checked against available data, {stats['claims_unchecked']} need data that was not provided.",
           "", "## Approvals", "",
           f"- [ ] Recap email (`drafts/recap_email_pl.md`) to {(call.get('customer_contact') or {}).get('email') or 'customer'}",
           ]
    out += [f"- [ ] {c['id']} {c['title']} ({c['status']})" for c in crs]
    out += [f"- [ ] {r['id']} reminder, proposed {r['proposed_send_at']}, max {r['max_count']}" for r in rems]
    out += [f"- [ ] {t['id']} credit or invoice action: {t['title']}" for t in tks if t["queue"] == "finance"]
    out += [f"- [ ] Add {i['id']} to the constraint registry: {i['title']}" for i in items if i["type"] == "constraint" and not i.get("quarantined")]
    errs = [(i["id"], x) for i in items for x in i.get("issues", []) if x["severity"] == "error"]
    if errs:
        out += ["", "## Errors to resolve before approving", ""] + [f"- {i}: {x['message']}" for i, x in errs]
    return "\n".join(out) + "\n"
