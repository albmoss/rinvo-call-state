import shutil
from pathlib import Path

import pytest

from callstate import pipeline, render, store, views

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT = ROOT / "transcripts" / "tama_2026-10-06.md"
EXTRACTION = ROOT / "tests" / "fixtures" / "tama_2026-10-06.extraction.json"
C = "grupa_auto_tama"


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("run")
    pipeline.run(str(TRANSCRIPT), str(tmp / "t.db"), str(tmp / "out"), str(EXTRACTION), log=lambda *_: None)
    conn = store.connect(tmp / "t.db")
    yield conn
    conn.close()
    shutil.rmtree(tmp, ignore_errors=True)


def items(db):
    return [i for i in store.items(db, C) if not i.get("quarantined")]


def cites(it, *lines):
    return any(e["line"] in lines for e in it["evidence"])


def find(db, *lines, types=None, states=None, text=None):
    out = [i for i in items(db) if cites(i, *lines) and (not types or i["type"] in types) and (not states or i["state"] in states)]
    if text:
        out = [i for i in out if text.lower() in blob(i).lower()]
    return out


def one(db, *lines, **kw):
    hits = find(db, *lines, **kw)
    assert hits, f"no item cites lines {lines} with {kw}"
    return hits[0]


def blob(it):
    v = it.get("value") or {}
    return " ".join(str(x) for x in (it["title"], it["action"], (it.get("condition") or {}).get("text"), v.get("target"), v.get("current"),
                                     v.get("requested"), " ".join(it.get("ambiguities", [])), it.get("if_others_ask")))


def quoting(db, fragment, types=None, states=None):
    out = [i for i in items(db) if any(fragment in e["quote"] for e in i["evidence"])
           and (not types or i["type"] in types) and (not states or i["state"] in states)]
    assert out, f"no item quotes {fragment!r} with types={types} states={states}"
    return out


def facts(db):
    return store.account(db, C)["facts"]


def area(db, it):
    auth = {a["key"]: a for a in store.account(db, C)["authority"]}
    return {p for k in it["authority_keys"] for p in auth.get(k, {}).get("approvers", [])}


def approvers_of(db, key):
    return next(a for a in store.account(db, C)["authority"] if a["key"] == key)


def test_01_calling_window_and_salon_hours_are_specs_not_applied(db):
    cw = one(db, 234, 232, types=["config_change"], text="19")
    assert "15" in blob(cw) and cw["state"] == "open" and not cw["events"]
    sat = one(db, 236, types=["config_change"])
    assert "15" in blob(sat)
    addr = one(db, 82, 80, types=["config_change"], text="Toruńska 120")
    assert addr["state"] == "open"
    assert any("18" in f["value"] and f["status"] == "current" for f in facts(db) if any(e["line"] == 82 for e in f["evidence"]))
    old = [f for f in facts(db) if f["status"] == "superseded" and "14" in f["value"]]
    assert old and all(f["superseded_by"] for f in old)
    assert "APPLY after review" in render.change_specs(db, C)


def test_02_intro_ab_test(db):
    ab = one(db, 58, 60, types=["config_change"], states=["conditional"])
    assert ab["launch"]
    assert not views.can_start(ab, items(db), "2026-10-08")[0]
    assert not views.can_start(ab, items(db), "2026-10-20")[0]
    assert views.can_start(ab, items(db), "2026-10-12")[0]
    texts = one(db, 58, types=["commitment"])
    assert texts["owner"]["party"] == "customer" and views.due_date(texts) == "2026-10-08"
    rem = next(i for i in items(db) if i["type"] == "follow_up" and i["watches"] == texts["id"])
    assert rem["limit"]["max_count"] == 1
    assert not any(e["item"]["id"] == rem["id"] for es in views.today(db, C, "2026-10-07").values() for e in es)
    assert any(e["item"]["id"] == rem["id"] for es in views.today(db, C, "2026-10-08").values() for e in es)
    assert "Kasia" in area(db, ab) and "Paweł" not in area(db, ab) and ab["approvers"] == []
    assert "Paweł" in approvers_of(db, ab["authority_keys"][0])["not_authorized"] or not any(
        r["authorized"] for r in views.check_request(db, C, "Paweł", "Zatwierdzam tekst wstępu", "2026-10-09"))


def test_02b_reminder_not_surfaced_once_texts_arrived(db):
    texts = one(db, 58, types=["commitment"])
    rem = next(i for i in items(db) if i["type"] == "follow_up" and i["watches"] == texts["id"])
    store.record_event(db, texts["id"], "received", "2026-10-08")
    try:
        assert not any(e["item"]["id"] == rem["id"] for es in views.today(db, C, "2026-10-08").values() for e in es)
    finally:
        store.record_event(db, texts["id"], "reopened", "2026-10-08")


def test_03_fresh_leads(db):
    f = one(db, 134, types=["commitment"], text="")
    assert f["owner"]["party"] == "customer" and views.due_date(f) == "2026-10-12"
    rem = next(i for i in items(db) if i["type"] == "follow_up" and i["watches"] == f["id"])
    assert rem["limit"]["max_count"] == 1
    assert any(e["item"]["id"] == rem["id"] for es in views.today(db, C, "2026-10-12").values() for e in es)
    store.record_event(db, rem["id"], "sent", "2026-10-12")
    assert not any(e["item"]["id"] == rem["id"] for es in views.today(db, C, "2026-10-13").values() for e in es)
    assert quoting(db, "nie przysyłaj mi wzoru pliku", types=["constraint"], states=["active"])
    assert quoting(db, "Starej bazy drugi raz nie puszczajcie", types=["constraint"], states=["active"])
    camp = one(db, 134, 136, types=["config_change"], states=["conditional"])
    assert any(w in blob(camp).lower() for w in ("opel", "opla"))


def test_04_opel_hold_call_kasia_first(db):
    opel = one(db, 130, 132, states=["deferred", "pending_approval"])
    res = [r for r in views.check_request(db, C, "Paweł", "Paweł prosi, żeby włączyć Opla od jutra", "2026-10-14") if r["item"]["id"] == opel["id"]]
    assert res and not res[0]["authorized"] and "Kasia" in res[0]["verdict"]
    assert not opel["events"]


def test_05_after_hours(db):
    ah = one(db, 168, 172, 176, states=["deferred"])
    spec = blob(ah)
    for word in ("VIN", "BOK"):
        assert word.lower() in spec.lower()
    assert quoting(db, "nie podpinajcie", types=["constraint"], states=["active"])
    assert quoting(db, "nie wierzcie", types=["constraint"], states=["active"])
    res = views.check_request(db, C, "Ola", "Kasia mówiła, że po godzinach od wtorku", "2026-10-13")
    assert res and not any(r["authorized"] for r in res)


def test_06_freeze(db):
    fr = next(i for i in find(db, 228, 230, types=["constraint"]) if i["freeze"])
    assert fr["freeze"] and fr["when"]["start"] == "2026-10-19" and fr["when"]["end"] == "2026-10-23"
    assert approvers_of(db, "emergency_contact")["approvers"] == ["Paweł"] or any(
        "Paweł" in a["approvers"] and "emerg" in a["key"] for a in store.account(db, C)["authority"])
    for r in views.check_request(db, C, "Paweł", "Włączcie Opla", "2026-10-20"):
        assert not r["authorized"]


def test_07_contact_rules(db):
    assert one(db, 144, types=["constraint"], states=["active"])
    assert one(db, 138, 240, types=["bug"], states=["blocked", "conditional"])
    assert one(db, 60, 38, types=["bug"], states=["blocked"])


def test_08_redial_bug(db):
    bug = one(db, 90, types=["bug"])
    text = render.dev_tickets(db, C)
    for s in ("16:40", "14", "2026-10-05"):
        assert s in text
    assert any("5" in f["value"] for f in facts(db) if "retry" in f["key"]) or find(db, 94, types=["constraint"])
    assert one(db, 186, types=["billing"], states=["conditional"])
    assert one(db, 184, 186, types=["billing"], text="minut") or one(db, 186, types=["billing"])
    assert one(db, 188, 190, types=["commitment"])
    assert bug["state"] == "open"


def test_09_filter_bug_and_column(db):
    assert one(db, 146, 148, types=["bug"])
    assert one(db, 150, 152, states=["conditional"])


def test_10_invoice_handoff_to_michal(db):
    inv = one(db, 180, 182, types=["billing"])
    assert inv["owner"]["person"] == "Michał"
    assert "Auto Tama Toruń" in blob(inv)
    assert inv["when"]["end"] == "2026-10-16" and inv["when"]["start"] in (None, "2026-10-12")
    assert any(x["code"] == "handoff" for x in inv["issues"])


def test_11_sms(db):
    price = one(db, 198, types=["commitment"])
    assert views.due_date(price) == "2026-10-09"
    sms = one(db, 192, 194, 196, types=["config_change", "feature_request"])
    assert "Paweł" in sms["approvers"] or sms["type"] == "feature_request"
    assert "Kasia" in approvers_of(db, next(a["key"] for a in store.account(db, C)["authority"] if "Kasia" in a["approvers"] and any(e["line"] == 196 for e in a["evidence"])))["approvers"]


def test_12_meeting_with_pawel(db):
    m = next(i for i in find(db, 210, types=["commitment"]) if i.get("when"))
    assert m["when"]["start"] == "2026-10-15" and m["when"]["time"] == "10:00"
    assert m["state"] in ("pending_approval", "conditional")
    d = [x for x in views.drafts(db, C, "2026-10-07") if x["item"] and x["item"]["id"] == m["id"]]
    assert not d or d[0]["status"] != "ready"
    briefs = render.meeting_briefs(db, C)
    brief = briefs.get(m["id"]) or "\n".join(briefs.values())
    for s in ("208", "VoiceDesk"):
        assert s in brief
    cs = one(db, 118, 120, types=["constraint"])
    assert "Paweł" in area(db, cs) and cs["approvers"] == []


def test_13_cheat_sheet_and_training(db):
    assert one(db, 222, 218, types=["commitment"], states=["open"])
    tr = one(db, 220, states=["deferred"])
    assert "Kasia" in tr["approvers"]


def test_14_holds_separate(db):
    assert one(db, 142, states=["deferred"])
    assert one(db, 124, 126, states=["deferred"])


def test_15_standing_rules(db):
    assert one(db, 224, 226, types=["constraint"], states=["active"])
    assert one(db, 110, 112, types=["constraint"], states=["active"])


def test_16_backlog_no_dates(db):
    for lines in ((62, 68), (146, 148), (154, 156), (204, 206)):
        fr = one(db, *lines, types=["feature_request"])
        assert fr["no_deadline_promised"]
    ab = one(db, 62, 68, types=["feature_request"])
    assert ab["success_metric"]


def test_17_address_fix_message_no_recording(db):
    msg = one(db, 86, 88, types=["commitment"])
    assert msg["message"] and msg["message"]["to"].startswith("Kasia")
    assert any(e["line"] == 84 and e["role"] == "superseded" for e in msg["evidence"])


def test_18_bad_quotes_are_quarantined_and_bad_schema_fails(tmp_path):
    import json
    raw = json.loads(EXTRACTION.read_text(encoding="utf-8"))
    raw["items"][0]["evidence"][0]["quote"] = "Tego zdania nie ma w rozmowie."
    raw["items"][1]["evidence"][0]["speaker"] = "Marek" if raw["items"][1]["evidence"][0]["speaker"] != "Marek" else "Kasia"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    pipeline.run(str(TRANSCRIPT), str(tmp_path / "q.db"), str(tmp_path / "out"), str(bad), log=lambda *_: None)
    conn = store.connect(tmp_path / "q.db")
    got = {i["local_id"]: i for i in store.items(conn, C)}
    assert got[raw["items"][0]["local_id"]]["quarantined"] and got[raw["items"][1]["local_id"]]["quarantined"]
    ids = {got[raw["items"][k]["local_id"]]["id"] for k in (0, 1)}
    assert not any(d["item"] and d["item"]["id"] in ids for d in views.drafts(conn, C, "2026-10-06"))
    assert {i["id"] for i in views.review(conn, C, "2026-10-06")["quarantined"]} >= ids
    conn.close()
    del raw["items"][2]["state"]
    bad.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(pipeline.ValidationFailed):
        pipeline.run(str(TRANSCRIPT), str(tmp_path / "f.db"), str(tmp_path / "out2"), str(bad), log=lambda *_: None)
