import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls (id TEXT PRIMARY KEY, customer TEXT, date TEXT, transcript TEXT, source TEXT, meta TEXT);
CREATE TABLE IF NOT EXISTS people (customer TEXT, name TEXT, side TEXT, role TEXT, email TEXT, present INTEGER, evidence TEXT, call TEXT,
    PRIMARY KEY (customer, name));
CREATE TABLE IF NOT EXISTS authority (customer TEXT, key TEXT, decision TEXT, approvers TEXT, not_authorized TEXT, evidence TEXT, call TEXT,
    PRIMARY KEY (customer, key));
CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, key TEXT, subject TEXT, value TEXT, status TEXT,
    evidence TEXT, call TEXT, superseded_by INTEGER);
CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, customer TEXT, call TEXT, type TEXT, state TEXT, assignee TEXT, data TEXT);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, item_id TEXT, kind TEXT, at TEXT, by TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS conflicts (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, call TEXT, previous_id TEXT, item_id TEXT,
    description TEXT, evidence TEXT);
"""

CLOSING_EVENTS = {"received": "closed", "done": "closed", "condition_met": "open", "reopened": "open", "cancelled": "closed"}


def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def ingest(db: sqlite3.Connection, customer: str, call: dict, account: dict, items: list[dict],
           previous_updates: list[dict], conflicts: list[dict], account_quarantine: dict) -> None:
    cid = call["date"]
    with db:
        old = [r["id"] for r in db.execute("SELECT id FROM items WHERE customer=? AND call=?", (customer, cid))]
        db.executemany("DELETE FROM events WHERE item_id=?", [(i,) for i in old])
        db.execute("DELETE FROM items WHERE customer=? AND call=?", (customer, cid))
        db.execute("DELETE FROM facts WHERE customer=? AND call=?", (customer, cid))
        db.execute("DELETE FROM conflicts WHERE customer=? AND call=?", (customer, cid))
        db.execute("UPDATE facts SET status='current', superseded_by=NULL WHERE customer=? AND superseded_by IS NOT NULL "
                   "AND superseded_by NOT IN (SELECT id FROM facts)", (customer,))
        db.execute("INSERT OR REPLACE INTO calls VALUES (?,?,?,?,?,?)",
                   (cid, customer, cid, call["transcript"], call["extraction"], json.dumps(call, ensure_ascii=False)))
        for n, p in enumerate(account["people"]):
            if f"account.people[{n}]" in account_quarantine:
                continue
            db.execute("INSERT OR REPLACE INTO people VALUES (?,?,?,?,?,?,?,?)",
                       (customer, p["name"], p["side"], p["role"], p["email"], int(p["present"]), json.dumps(p["evidence"], ensure_ascii=False), cid))
        for n, a in enumerate(account["authority"]):
            if f"account.authority[{n}]" in account_quarantine:
                continue
            db.execute("INSERT OR REPLACE INTO authority VALUES (?,?,?,?,?,?,?)",
                       (customer, a["key"], a["decision"], json.dumps(a["approvers"], ensure_ascii=False),
                        json.dumps(a["not_authorized"], ensure_ascii=False), json.dumps(a["evidence"], ensure_ascii=False), cid))
        new_ids: dict[str, list[int]] = {}
        for n, f in enumerate(account["facts"]):
            if f"account.facts[{n}]" in account_quarantine:
                continue
            cur = db.execute("INSERT INTO facts (customer, key, subject, value, status, evidence, call) VALUES (?,?,?,?,?,?,?)",
                             (customer, f["key"], f["subject"], f["value"], f["status"], json.dumps(f["evidence"], ensure_ascii=False), cid))
            new_ids.setdefault(f["key"], []).append((cur.lastrowid, f["status"], min(e["line"] for e in f["evidence"])))
        for key, rows in new_ids.items():
            live = [r for r in rows if r[1] != "superseded"]
            if not live:
                continue
            target = max(live, key=lambda r: r[2])[0]
            for rid, status, _ in rows:
                if status == "superseded":
                    db.execute("UPDATE facts SET superseded_by=? WHERE id=?", (target, rid))
            db.execute("UPDATE facts SET status='superseded', superseded_by=? WHERE customer=? AND key=? AND call<>? AND status<>'superseded'",
                       (target, customer, key, cid))
        for u in previous_updates:
            _update_item(db, u["previous_id"], u["new_state"], {"update_note": u["note"], "updated_by_call": cid, "update_evidence": u["evidence"]})
        for it in items:
            db.execute("INSERT INTO items VALUES (?,?,?,?,?,?,?)",
                       (it["id"], customer, cid, it["type"], it["state"], it["assignee"], json.dumps(it, ensure_ascii=False)))
            if it.get("previous_id") and not it.get("quarantined"):
                _update_item(db, it["previous_id"], "superseded", {"superseded_by": it["id"]})
        for c in conflicts:
            local = next((i["id"] for i in items if i["local_id"] == c["local_id"]), None)
            db.execute("INSERT INTO conflicts (customer, call, previous_id, item_id, description, evidence) VALUES (?,?,?,?,?,?)",
                       (customer, cid, c["previous_id"], local, c["description"], json.dumps(c["evidence"], ensure_ascii=False)))


def _update_item(db, item_id: str, state: str, extra: dict) -> None:
    row = db.execute("SELECT data FROM items WHERE id=?", (item_id,)).fetchone()
    if not row:
        return
    data = json.loads(row["data"])
    data["state"] = state
    data.update(extra)
    db.execute("UPDATE items SET state=?, data=? WHERE id=?", (state, json.dumps(data, ensure_ascii=False), item_id))


def items(db, customer: str) -> list[dict]:
    out = []
    for r in db.execute("SELECT data FROM items WHERE customer=? ORDER BY id", (customer,)):
        it = json.loads(r["data"])
        it["events"] = [dict(e) for e in db.execute("SELECT kind, at, by, note FROM events WHERE item_id=? ORDER BY id", (it["id"],))]
        out.append(it)
    return out


def item(db, item_id: str) -> dict | None:
    r = db.execute("SELECT data FROM items WHERE id=?", (item_id,)).fetchone()
    if not r:
        return None
    it = json.loads(r["data"])
    it["events"] = [dict(e) for e in db.execute("SELECT kind, at, by, note FROM events WHERE item_id=? ORDER BY id", (item_id,))]
    return it


def record_event(db, item_id: str, kind: str, at: str, by: str = "", note: str = "") -> None:
    with db:
        db.execute("INSERT INTO events (item_id, kind, at, by, note) VALUES (?,?,?,?,?)", (item_id, kind, at, by, note))
        if kind in CLOSING_EVENTS:
            _update_item(db, item_id, CLOSING_EVENTS[kind], {f"{kind}_at": at})


def account(db, customer: str) -> dict:
    people = [dict(r) | {"evidence": json.loads(r["evidence"])} for r in db.execute("SELECT * FROM people WHERE customer=? ORDER BY side, name", (customer,))]
    auth = [dict(r) | {"approvers": json.loads(r["approvers"]), "not_authorized": json.loads(r["not_authorized"]),
                       "evidence": json.loads(r["evidence"])} for r in db.execute("SELECT * FROM authority WHERE customer=? ORDER BY key", (customer,))]
    facts = [dict(r) | {"evidence": json.loads(r["evidence"])} for r in db.execute("SELECT * FROM facts WHERE customer=? ORDER BY key, id", (customer,))]
    return {"people": people, "authority": auth, "facts": facts}


def calls(db, customer: str) -> list[dict]:
    return [dict(r) | {"meta": json.loads(r["meta"])} for r in db.execute("SELECT * FROM calls WHERE customer=? ORDER BY date", (customer,))]


def conflicts(db, customer: str) -> list[dict]:
    return [dict(r) | {"evidence": json.loads(r["evidence"])} for r in db.execute("SELECT * FROM conflicts WHERE customer=? ORDER BY id", (customer,))]


def customers(db) -> list[str]:
    return [r["customer"] for r in db.execute("SELECT DISTINCT customer FROM calls ORDER BY customer")]


def previous_record(db, customer: str, before: str) -> dict | None:
    prior = [c for c in calls(db, customer) if c["date"] < before]
    if not prior:
        return None
    acc = account(db, customer)
    live = [i for i in items(db, customer) if i["call"] < before and not i.get("quarantined")
            and i["state"] not in ("closed", "rejected", "superseded", "noted")]
    return {"last_call": prior[-1]["date"], "authority": acc["authority"], "facts": acc["facts"], "items": live}
