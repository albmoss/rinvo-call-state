import datetime as dt
import re

from . import store
from .transcript import fold

RINVO_WORK = ("bug", "config_change", "commitment", "billing")
HOLDS = ("deferred", "pending_approval", "blocked")
LIVE = ("open", "conditional", "pending_approval", "deferred", "blocked", "active")


def due_date(it: dict) -> str | None:
    w = it.get("when") or {}
    if w.get("kind") in ("by", "on", "window", "range"):
        return w.get("end") or w.get("start")
    return None


def sent_count(it: dict) -> int:
    return sum(1 for e in it.get("events", []) if e["kind"] == "sent")


def _by_id(items: list[dict]) -> dict:
    return {i["id"]: i for i in items}


def _live(items):
    return [i for i in items if not i.get("quarantined") and i["state"] in LIVE]


def reminder_status(it: dict, items_by_id: dict, today: str) -> dict:
    watched = items_by_id.get(it.get("watches") or "")
    deadline = due_date(it)
    limit = (it.get("limit") or {}).get("max_count") or 0
    sent = sent_count(it)
    if watched and watched["state"] == "closed":
        status = "not needed: the awaited item arrived"
    elif sent >= limit:
        status = f"done: sent {sent} of {limit}"
    elif deadline and today < deadline:
        status = f"scheduled for {deadline}"
    elif deadline:
        status = "due today" if today == deadline else f"overdue since {deadline}"
    else:
        status = "no date"
    return {"deadline": deadline, "max_count": limit, "sent": sent, "status": status,
            "due": status.startswith(("due", "overdue")), "watches": watched["id"] if watched else None}


def freeze_windows(items: list[dict]) -> list[dict]:
    return [i for i in _live(items) if i["type"] == "constraint" and i.get("freeze") and i.get("when")
            and i["when"].get("start") and i["when"].get("end")]


def start_window(it: dict, items: list[dict]) -> dict:
    w = it.get("when") or {}
    earliest = max(x for x in (it["call"], w.get("start") if w.get("kind") == "not_before" else None) if x)
    blocked = [(f["when"]["start"], f["when"]["end"], f["id"]) for f in freeze_windows(items)]
    if w.get("kind") == "not_before" and w.get("start"):
        blocked.append((it["call"], (dt.date.fromisoformat(w["start"]) - dt.timedelta(days=1)).isoformat(), it["id"]))
    d = dt.date.fromisoformat(earliest)
    for _ in range(400):
        iso = d.isoformat()
        hit = next((b for b in blocked if b[0] <= iso <= b[1]), None)
        if not hit:
            break
        d = dt.date.fromisoformat(hit[1]) + dt.timedelta(days=1)
    return {"earliest": d.isoformat(), "blocked": [{"from": a, "to": b, "by": c} for a, b, c in sorted(blocked)]}


def can_start(it: dict, items: list[dict], day: str) -> tuple[bool, str]:
    sw = start_window(it, items)
    if day < sw["earliest"]:
        return False, f"not before {sw['earliest']}"
    hit = next((b for b in sw["blocked"] if b["from"] <= day <= b["to"]), None)
    if hit:
        return False, f"blocked {hit['from']}..{hit['to']} by {hit['by']}"
    return True, "allowed"


def today(db, customer: str, day: str, person: str | None = None) -> dict:
    items = store.items(db, customer)
    byid = _by_id(items)
    meetings = {m for i in items for m in i.get("brief_for", [])}
    out: dict[str, list] = {}

    def add(who, entry):
        if person and fold(who or "") != fold(person):
            return
        out.setdefault(who or "unassigned", []).append(entry)

    for it in _live(items):
        d = due_date(it)
        if it["type"] == "follow_up":
            rs = reminder_status(it, byid, day)
            if rs["due"]:
                add(it["assignee"], {"kind": "reminder", "item": it, "reminder": rs, "draft": it.get("message")})
            continue
        if it["id"] in meetings and d == day:
            add(it["assignee"], {"kind": "meeting", "item": it})
        elif it["owner"]["party"] == "rinvo" and it["type"] in RINVO_WORK and it["state"] in ("open", "conditional") and d and d <= day:
            kind = ("due" if d == day else "overdue") if it["state"] == "open" else "due if condition holds"
            add(it["assignee"], {"kind": kind, "item": it, "draft": it.get("message")})
        elif it["owner"]["party"] == "customer" and it["state"] in ("open", "conditional") and d and d < day:
            add(it["assignee"], {"kind": "client_late", "item": it})
    return out


def waiting_on_client(db, customer: str, day: str) -> list[dict]:
    items = store.items(db, customer)
    byid = _by_id(items)
    rows = []
    for it in _live(items):
        if it["owner"]["party"] != "customer" or it["state"] not in ("open", "conditional"):
            continue
        rem = [reminder_status(f, byid, day) | {"id": f["id"]} for f in items if f["type"] == "follow_up" and f.get("watches") == it["id"]]
        rows.append({"item": it, "due": due_date(it), "reminders": rem})
    return sorted(rows, key=lambda r: r["due"] or "9999")


def drafts(db, customer: str, day: str) -> list[dict]:
    items = store.items(db, customer)
    byid = _by_id(items)
    out = []
    last = store.calls(db, customer)[-1]
    out.append({"kind": "recap", "item": None, "to": last["meta"].get("customer_contact"), "status": "ready",
                "path": "drafts/recap_email_pl.md", "call": last["date"]})
    for it in _live(items):
        m = it.get("message")
        if not m:
            continue
        if it["type"] == "follow_up":
            rs = reminder_status(it, byid, day)
            status = "ready" if rs["due"] else rs["status"]
        elif it["state"] == "open" and sent_count(it) == 0:
            status = "ready"
        else:
            status = f"waiting: {(it.get('condition') or {}).get('text') or it['state']}"
        out.append({"kind": "message", "item": it, "to": m["to"], "to_email": m.get("to_email"), "subject": m["subject_pl"],
                    "body": m["body_pl"], "status": status})
    return out


def client(db, customer: str) -> dict:
    items = store.items(db, customer)
    live = _live(items)
    return {
        "account": store.account(db, customer), "calls": store.calls(db, customer),
        "rinvo_commitments": [i for i in live if i["owner"]["party"] == "rinvo" and i["type"] in RINVO_WORK and i["state"] in ("open", "conditional")],
        "waiting_on_client": [i for i in live if i["owner"]["party"] == "customer" and i["state"] in ("open", "conditional")],
        "reminders": [i for i in live if i["type"] == "follow_up"],
        "holds": [i for i in live if i["state"] in HOLDS],
        "product": [i for i in live if i["type"] == "feature_request"],
        "risks": [i for i in live if i["type"] == "account_signal" or (i["type"] == "billing" and i["state"] in ("open", "conditional"))]
                 + [i for i in items if i["type"] == "account_signal" and i["state"] == "noted" and not i.get("quarantined")],
        "constraints": [i for i in live if i["type"] == "constraint"],
        "closed": [i for i in items if i["state"] in ("closed", "superseded", "rejected")],
        "quarantined": [i for i in items if i.get("quarantined")],
        "conflicts": store.conflicts(db, customer),
    }


def check_request(db, customer: str, sender: str, text: str, day: str) -> list[dict]:
    items = store.items(db, customer)
    auth = {a["key"]: a for a in store.account(db, customer)["authority"]}
    words = set(re.findall(r"\w+", fold(text)))
    out = []
    for it in items:
        if it.get("quarantined") or not (it["state"] in HOLDS or (it["type"] == "constraint" and it["state"] == "active")):
            continue
        kws = {fold(k) for k in it.get("keywords") or [] if k}
        hits = sorted(k for k in kws if (k in words if " " not in k else k in fold(text)))
        if not hits:
            continue
        approvers = sorted({p for k in it.get("authority_keys", []) for p in auth.get(k, {}).get("approvers", [])})
        barred = sorted({p for k in it.get("authority_keys", []) for p in auth.get(k, {}).get("not_authorized", [])})
        authorized = any(fold(p.split()[0]) == fold(sender.split()[0]) for p in approvers) if sender else False
        if authorized:
            verdict = "from an authorized person; still goes to the daily review before anything changes"
        else:
            who = ", ".join(approvers) or "the person named in the call"
            verdict = f"{sender or 'Sender'} cannot approve this. Confirm with {who} first. Do not change anything."
        out.append({"item": it, "matched": hits, "authorized": authorized, "approvers": approvers, "not_authorized": barred,
                    "verdict": verdict, "rule": it.get("if_others_ask") or "",
                    "freeze": [f["id"] for f in freeze_windows(items) if f["when"]["start"] <= day <= f["when"]["end"]]})
    return out


def review(db, customer: str, day: str) -> dict:
    items = store.items(db, customer)
    last = store.calls(db, customer)[-1]["date"]
    conflicts = [(i, x) for i in _live(items) for x in i.get("issues", []) if x["code"] == "constraint_conflict"]
    return {
        "day": day,
        "drafts": [d for d in drafts(db, customer, day) if d["status"] == "ready"],
        "due": today(db, customer, day),
        "quarantined": [i for i in items if i.get("quarantined")],
        "account_quarantine": store.calls(db, customer)[-1]["meta"].get("account_quarantine", {}),
        "ambiguities": [(i, a) for i in items if i["call"] == last and not i.get("quarantined") for a in i.get("ambiguities", [])],
        "constraint_conflicts": conflicts,
        "cross_call_conflicts": store.conflicts(db, customer),
        "warnings": [(i, x) for i in items if i["call"] == last for x in i.get("issues", []) if x["severity"] == "warn" and x["code"] != "constraint_conflict"],
    }
