from . import store, views
from .dates import pl_date, pl_when

OPEN_LIKE = ("open", "conditional")


def _first_line(it: dict) -> int:
    return min((e["line"] for e in it["evidence"]), default=10**6)


def q(e: dict) -> str:
    return f"> „{e['quote']}” ({e['speaker']}, line {e['line']}, {e['role']})"


def when_txt(it: dict) -> str:
    w = it.get("when")
    if not w:
        return ""
    if w["kind"] == "by":
        d = f"by {w['end']}"
    elif w["kind"] == "not_before":
        d = f"not before {w['start']}"
    elif w.get("start") and w.get("end") and w["start"] != w["end"]:
        d = f"{w['start']}..{w['end']}"
    else:
        d = w.get("start") or w.get("end") or "unresolved"
    return f"{d}{' ' + w['time'] if w.get('time') else ''} (\"{w['phrase']}\", {w['resolution']})"


def item_block(it: dict, extra: list[str] | None = None) -> list[str]:
    out = [f"### {it['id']} · {it['title']}", "",
           f"- {it['type']} · {it['state']} · owner {it['owner'].get('person') or it['owner']['party']} · assignee {it['assignee'] or '-'}"]
    if it.get("action"):
        out.append(f"- {it['action']}")
    if it.get("when"):
        out.append(f"- When: {when_txt(it)}")
    if it.get("condition"):
        out.append(f"- Condition: {it['condition']['text']}")
    if it.get("approvers"):
        out.append(f"- Waiting for sign-off from: {', '.join(it['approvers'])}")
    if it.get("authority_keys"):
        out.append(f"- Decision area: {', '.join(it['authority_keys'])}")
    if it.get("if_others_ask"):
        out.append(f"- If someone else asks: {it['if_others_ask']}")
    out += extra or []
    out.append("")
    out += [q(e) for e in it["evidence"]]
    out.append("")
    return out


def recap_email(db, customer: str) -> str:
    call = store.calls(db, customer)[-1]
    meta = call["meta"]
    items = [i for i in store.items(db, customer) if i["call"] == call["date"] and not i.get("quarantined")
             and i.get("customer_visible") and i.get("recap_pl")]
    items.sort(key=_first_line)

    def line(it):
        w = it.get("when")
        d = pl_when(w) if w and w["kind"] != "past" and w["resolution"] in ("rule", "anchor") else ""
        txt = it["recap_pl"].strip()
        days = [x for x in ((w or {}).get("start"), (w or {}).get("end")) if x]
        already = days and all(str(int(x[-2:])) in txt for x in days) and pl_date(days[0]).split()[1] in txt
        return f"- {txt}" + (f" ({d})" if d and not already else "")

    groups = [
        ("Po naszej stronie", [i for i in items if i["owner"]["party"] == "rinvo" and i["state"] in OPEN_LIKE and i["type"] in views.RINVO_WORK]),
        ("Po Twojej stronie", [i for i in items if i["owner"]["party"] == "customer" and i["state"] in OPEN_LIKE and i["type"] == "commitment"]),
        ("Wstrzymane albo czekające na decyzję", [i for i in items if i["state"] in views.HOLDS and i["type"] != "constraint"]),
        ("Zapisane jako propozycje rozwoju produktu, bez obiecanego terminu", [i for i in items if i["type"] == "feature_request" and i["state"] in OPEN_LIKE]),
        ("Zasady, których się trzymamy", [i for i in items if i["type"] == "constraint" and i["state"] == "active"]),
    ]
    contact = next((p for p in store.account(db, customer)["people"] if p["name"].split()[0] == (meta.get("customer_contact") or "").split()[0]), {})
    out = ["<!-- Draft. Not sent. -->", "", f"**Do:** {contact.get('email') or meta.get('customer_contact')}  ",
           f"**Temat:** Podsumowanie rozmowy z {pl_date(call['date'])}", "",
           f"Cześć {meta.get('customer_contact_vocative_pl') or meta.get('customer_contact')},", "",
           f"poniżej ustalenia z naszej rozmowy z {pl_date(call['date'])}.", ""]
    for title, group in groups:
        if group:
            out += [f"**{title}**", ""] + [line(i) for i in group] + [""]
    out += ["Jeśli coś się nie zgadza, daj znać.", "", "Pozdrawiam,", meta.get("rinvo_contact") or ""]
    return "\n".join(out) + "\n"


def messages_md(db, customer: str, day: str) -> str:
    out = [f"# Message drafts (as of {day})", "", "Polish drafts. Nothing is sent by the system.", ""]
    for d in views.drafts(db, customer, day):
        if d["kind"] != "message":
            continue
        it = d["item"]
        out += [f"## {it['id']} · {it['title']}", "", f"- To: {d['to']}" + (f" <{d['to_email']}>" if d.get("to_email") else ""),
                f"- Status: {d['status']}", f"- Subject: {d['subject']}", "", "> " + d["body"].replace("\n", "\n> "), ""]
    return "\n".join(out)


def change_specs(db, customer: str) -> str:
    items = store.items(db, customer)
    out = ["# Configuration change specs", "",
           "For a person to apply by hand. The system has no write access to the agent configuration.", ""]
    for it in sorted([i for i in items if i["type"] == "config_change" and not i.get("quarantined")], key=_first_line):
        v = it.get("value") or {}
        if it["state"] == "open":
            status = "APPLY after review"
        elif it["state"] == "conditional":
            status = "HOLD until the condition holds"
        else:
            status = f"DO NOT APPLY ({it['state']})"
        extra = [f"- Status: **{status}**"]
        if v:
            extra += [f"- Setting: {v.get('target') or '-'}", f"- Current: {v.get('current') or '-'}", f"- New: {v.get('requested') or '-'}"]
        if it.get("launch"):
            sw = views.start_window(it, items)
            extra.append(f"- Earliest start: {sw['earliest']}; blocked: " + (", ".join(f"{b['from']}..{b['to']} ({b['by']})" for b in sw["blocked"]) or "none"))
        out += item_block(it, extra)
    return "\n".join(out)


def dev_tickets(db, customer: str) -> str:
    out = ["# Dev tickets", ""]
    for it in sorted([i for i in store.items(db, customer) if i["type"] == "bug" and not i.get("quarantined")], key=_first_line):
        extra = []
        for c in it.get("claims", []):
            extra.append(f"- Reported: {c['text']}" + (f" (date {c['date']})" if c.get("date") else "") + f" [to verify in {c['source']}]")
        out += item_block(it, extra)
    return "\n".join(out)


def backlog(db, customer: str) -> str:
    out = ["# Product backlog entries", ""]
    for it in sorted([i for i in store.items(db, customer) if i["type"] == "feature_request" and not i.get("quarantined")], key=_first_line):
        extra = [f"- Success metric named by the client: {it.get('success_metric') or 'none named'}",
                 f"- Deadline promised: {'no' if it.get('no_deadline_promised') else 'YES, check the quote'}",
                 f"- Known: {it['known']['status']}" + (f" ({it['known']['basis']})" if it['known'].get('basis') else "")]
        out += item_block(it, extra)
    return "\n".join(out)


def meeting_briefs(db, customer: str) -> dict[str, str]:
    items = store.items(db, customer)
    byid = {i["id"]: i for i in items}
    acc = store.account(db, customer)
    meetings: dict[str, list] = {}
    for it in items:
        for m in it.get("brief_for", []):
            meetings.setdefault(m, []).append(it)
    out = {}
    for mid, agenda in meetings.items():
        m = byid.get(mid)
        if not m:
            continue
        auth = {a["key"]: a for a in acc["authority"]}
        attendees = {p for k in m.get("authority_keys", []) for p in auth.get(k, {}).get("approvers", [])} | set(m.get("approvers", []))
        lines = [f"# Meeting brief: {m['title']}", "", f"When: {when_txt(m)}", f"Precondition: {(m.get('condition') or {}).get('text') or 'none'}", ""]
        lines += ["## On the agenda", ""]
        for it in sorted(agenda, key=_first_line):
            lines += item_block(it)
        pend = [i for i in views._live(items) if i["state"] == "pending_approval" and i not in agenda and set(i.get("approvers", [])) & attendees]
        if pend:
            lines += ["## Decisions waiting for the attendee", ""]
            for it in pend:
                lines += item_block(it)
        nopromise = [i for i in views._live(items) if i["type"] == "feature_request" and i.get("no_deadline_promised")]
        if nopromise:
            lines += ["## Do not promise dates for", ""] + [f"- {i['title']}" for i in nopromise] + [""]
        facts = [f for f in acc["facts"] if f["status"] != "superseded"]
        lines += ["## Client facts", ""] + [f"- {f['subject']}: {f['value']}" for f in facts] + [""]
        out[mid] = "\n".join(lines)
    return out


def next_call_brief(db, customer: str, day: str) -> str:
    c = views.client(db, customer)
    out = [f"# Pre-call brief: {customer} (state on {day})", ""]
    sections = [("Rinvo owes", c["rinvo_commitments"]), ("Waiting on the client", c["waiting_on_client"]),
                ("Holds: do not act, ask only if the reopen condition holds", c["holds"]), ("Constraints in force", c["constraints"]),
                ("Risks", c["risks"])]
    for title, group in sections:
        if not group:
            continue
        out += [f"## {title}", ""]
        for it in sorted(group, key=lambda i: views.due_date(i) or "9999"):
            d = views.due_date(it)
            cond = f" Condition: {it['condition']['text']}" if it.get("condition") else ""
            who = f" Waiting for {', '.join(it['approvers'])}." if it.get("approvers") else ""
            out.append(f"- {it['id']} {it['title']} ({it['owner'].get('person') or it['owner']['party']}{', ' + d if d else ''}).{cond}{who}")
        out.append("")
    amb = [(i["id"], a) for i in store.items(db, customer) for a in i.get("ambiguities", []) if i["state"] in views.LIVE]
    if amb:
        out += ["## Open questions", ""] + [f"- {i}: {a}" for i, a in amb] + [""]
    return "\n".join(out)


def review_md(db, customer: str, day: str) -> str:
    r = views.review(db, customer, day)
    out = [f"# Daily review: {customer}, {day}", "", "The only human step. Everything else is already filed.", "", "## Drafts ready to send", ""]
    for d in r["drafts"]:
        if d["kind"] == "recap":
            out.append(f"- [ ] Recap email for the call on {d['call']} to {d['to']} (`drafts/recap_email_pl.md`)")
        else:
            out.append(f"- [ ] {d['item']['id']} to {d['to']}: {d['subject']}")
    out += ["", "## Due today, per assignee", ""]
    for who, entries in r["due"].items():
        out.append(f"**{who}**")
        for e in entries:
            it = e["item"]
            tail = f" ({e['reminder']['status']}, sent {e['reminder']['sent']} of {e['reminder']['max_count']})" if e["kind"] == "reminder" else ""
            out.append(f"- [{e['kind']}] {it['id']} {it['title']}{tail}")
        out.append("")
    if not r["due"]:
        out += ["Nothing due.", ""]
    out += ["## Quarantined", ""]
    for it in r["quarantined"]:
        out.append(f"- {it['id']} {it['title']}: " + "; ".join(it["quarantine_reasons"]))
    for k, v in r["account_quarantine"].items():
        out.append(f"- {k}: " + "; ".join(v))
    if not r["quarantined"] and not r["account_quarantine"]:
        out.append("None.")
    out += ["", "## Ambiguities", ""] + [f"- {i['id']} {i['title']}: {a}" for i, a in r["ambiguities"]]
    out += ["", "## Constraint conflicts", ""] + [f"- {i['id']} {i['title']}: {x['message']}" for i, x in r["constraint_conflicts"]]
    out += [f"- {c['item_id'] or c['previous_id']}: {c['description']}" for c in r["cross_call_conflicts"]]
    if not r["constraint_conflicts"] and not r["cross_call_conflicts"]:
        out.append("None.")
    if r["warnings"]:
        out += ["", "## Other warnings", ""] + [f"- {i['id']}: {x['message']}" for i, x in r["warnings"]]
    return "\n".join(out) + "\n"


def client_md(db, customer: str) -> str:
    c = views.client(db, customer)
    acc = c["account"]
    out = [f"# Client: {customer}", "", "## People", ""]
    out += [f"- {p['name']} ({p['side']}, {p['role'] or '-'}, {'on the call' if p['present'] else 'not on the call'}{', ' + p['email'] if p['email'] else ''})" for p in acc["people"]]
    out += ["", "## Who decides what", ""]
    for a in acc["authority"]:
        bar = f"; not: {', '.join(a['not_authorized'])}" if a["not_authorized"] else ""
        ev = a["evidence"][0] if a["evidence"] else None
        out.append(f"- **{a['key']}**: {a['decision']}. Decides: {', '.join(a['approvers']) or '-'}{bar}." + (f" „{ev['quote']}” (line {ev['line']})" if ev else ""))
    out += ["", "## Facts", ""]
    for f in acc["facts"]:
        ev = f["evidence"][0] if f["evidence"] else None
        mark = "" if f["status"] == "current" else f" [{f['status']}{', replaced by #' + str(f['superseded_by']) if f['superseded_by'] else ''}]"
        out.append(f"- #{f['id']} {f['subject']}: {f['value']}{mark}" + (f" „{ev['quote']}” (line {ev['line']})" if ev else ""))
    for title, key in [("Rinvo commitments", "rinvo_commitments"), ("Waiting on client", "waiting_on_client"), ("Reminders", "reminders"),
                       ("Holds", "holds"), ("Product requests", "product"), ("Risks", "risks"), ("Constraints", "constraints")]:
        if c[key]:
            out += ["", f"## {title}", ""]
            for it in sorted(c[key], key=_first_line):
                out += item_block(it)
    return "\n".join(out) + "\n"
