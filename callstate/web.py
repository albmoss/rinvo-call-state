import datetime as dt
import html
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import store, views

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Warsaw")
except Exception:
    TZ = None

CSS = """body{font:15px/1.45 system-ui,sans-serif;margin:0;color:#1d1d1f;background:#fafafa}
nav{display:flex;gap:18px;align-items:center;padding:12px 24px;background:#fff;border-bottom:1px solid #e5e5e5;position:sticky;top:0}
nav a{color:#333;text-decoration:none}nav a.on{font-weight:600;color:#0a58ca}nav form{margin-left:auto;display:flex;gap:8px}
main{max-width:1000px;margin:0 auto;padding:20px 24px}h1{font-size:22px}h2{font-size:17px;margin-top:28px}
.card{background:#fff;border:1px solid #e5e5e5;border-radius:8px;padding:12px 14px;margin:8px 0}
.meta{color:#666;font-size:13px}.tag{display:inline-block;font-size:12px;padding:1px 7px;border-radius:10px;background:#eef;margin-right:4px}
.warn{background:#fff4e5}.err{background:#fdecea}blockquote{margin:6px 0;padding-left:10px;border-left:3px solid #ccc;color:#444;font-size:13px}
pre{white-space:pre-wrap;background:#f4f4f4;padding:10px;border-radius:6px}button{cursor:pointer}
input,textarea{font:inherit}table{border-collapse:collapse}td,th{padding:4px 10px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}"""

PAGES = [("today", "Today"), ("client", "Client"), ("waiting", "Waiting on client"), ("drafts", "Drafts"), ("review", "Daily review")]


def e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def today_iso() -> str:
    return (dt.datetime.now(TZ) if TZ else dt.datetime.now()).date().isoformat()


class App:
    def __init__(self, db_path: str, fixed_day: str | None = None):
        self.db_path = db_path
        self.fixed_day = fixed_day

    def db(self):
        return store.connect(self.db_path)


def _item_card(it: dict, day: str, extra: str = "", actions: bool = True) -> str:
    ev = "".join(f"<blockquote>„{e(x['quote'])}” <span class=meta>{e(x['speaker'])}, line {x['line']}</span></blockquote>" for x in it["evidence"][:4])
    d = views.due_date(it)
    cond = f"<div class=meta>Condition: {e(it['condition']['text'])}</div>" if it.get("condition") else ""
    who = f"<div class=meta>Waiting for sign-off from: {e(', '.join(it['approvers']))}</div>" if it.get("approvers") else ""
    ask = f"<div class=meta>If someone else asks: {e(it['if_others_ask'])}</div>" if it.get("if_others_ask") else ""
    btn = ""
    if actions and it["state"] not in ("closed", "superseded", "rejected"):
        kinds = ["done", "received", "sent", "condition_met"]
        btn = "".join(f"<form method=post action=/event style='display:inline'><input type=hidden name=id value='{e(it['id'])}'>"
                      f"<input type=hidden name=kind value={k}><input type=hidden name=day value={day}><button>{k.replace('_', ' ')}</button></form> " for k in kinds)
    return (f"<div class=card><b><a href='/item?id={urllib.parse.quote(it['id'])}&day={day}'>{e(it['id'])}</a> {e(it['title'])}</b><br>"
            f"<span class=tag>{e(it['type'])}</span><span class=tag>{e(it['state'])}</span>"
            f"<span class=meta>owner {e(it['owner'].get('person') or it['owner']['party'])} · assignee {e(it['assignee'])}{' · due ' + e(d) if d else ''}</span>"
            f"<div>{e(it.get('action'))}</div>{cond}{who}{ask}{extra}{ev}<div>{btn}</div></div>")


def _draft(m: dict | None) -> str:
    if not m:
        return ""
    return f"<details><summary>Draft to {e(m['to'])}: {e(m['subject_pl'])}</summary><pre>{e(m['body_pl'])}</pre></details>"


def render_page(app: App, page: str, qs: dict) -> str:
    db = app.db()
    custs = store.customers(db)
    if not custs:
        return "<p>No calls ingested yet. Run <code>python -m callstate TRANSCRIPT</code>.</p>"
    c = qs.get("c", [custs[0]])[0]
    day = qs.get("day", [app.fixed_day or today_iso()])[0]
    nav = "".join(f"<a class='{'on' if p == page else ''}' href='/{p}?c={c}&day={day}'>{t}</a>" for p, t in PAGES)
    nav += f"<form><input type=hidden name=c value={e(c)}><input type=date name=day value={e(day)}><button>Set day</button></form>"
    body = ""
    if page == "today":
        person = qs.get("person", [None])[0]
        groups = views.today(db, c, day, person)
        body = f"<h1>Today, {e(day)}</h1>"
        people = sorted(groups)
        body += "<p class=meta>Assignees: " + " ".join(f"<a href='/today?c={c}&day={day}&person={e(p)}'>{e(p)}</a>" for p in people) + "</p>"
        for who, entries in groups.items():
            body += f"<h2>{e(who)}</h2>"
            for x in entries:
                extra = f"<div class=meta>[{e(x['kind'])}]" + (f" {e(x['reminder']['status'])}, sent {x['reminder']['sent']} of {x['reminder']['max_count']}" if x["kind"] == "reminder" else "") + "</div>"
                body += _item_card(x["item"], day, extra + _draft(x.get("draft")))
        if not groups:
            body += "<p>Nothing due.</p>"
    elif page == "client":
        cl = views.client(db, c)
        acc = cl["account"]
        body = f"<h1>{e(c)}</h1><h2>People</h2><table>" + "".join(
            f"<tr><td>{e(p['name'])}</td><td>{e(p['side'])}</td><td>{e(p['role'])}</td><td>{'present' if p['present'] else 'absent'}</td><td>{e(p['email'])}</td></tr>" for p in acc["people"]) + "</table>"
        body += "<h2>Who decides what</h2><table>" + "".join(
            f"<tr><td><b>{e(a['key'])}</b></td><td>{e(a['decision'])}</td><td>{e(', '.join(a['approvers']))}</td><td class=meta>{'not: ' + e(', '.join(a['not_authorized'])) if a['not_authorized'] else ''}</td></tr>" for a in acc["authority"]) + "</table>"
        body += "<h2>Facts</h2><table>" + "".join(
            f"<tr class='{'' if f['status'] == 'current' else 'warn'}'><td>{e(f['subject'])}</td><td>{e(f['value'])}</td><td class=meta>{e(f['status'])}</td></tr>" for f in acc["facts"]) + "</table>"
        body += ("<h2>Check an incoming request</h2><form method=post action=/check>"
                 f"<input type=hidden name=c value={e(c)}><input type=hidden name=day value={e(day)}>"
                 "<input name=sender placeholder='From (name)'> <input name=text size=60 placeholder='Message text'> <button>Check</button></form>")
        for title, key in [("Rinvo commitments", "rinvo_commitments"), ("Waiting on client", "waiting_on_client"), ("Holds", "holds"),
                           ("Product requests", "product"), ("Risks", "risks"), ("Constraints", "constraints"), ("Quarantined", "quarantined")]:
            if cl[key]:
                body += f"<h2>{title}</h2>" + "".join(_item_card(i, day, actions=key != "quarantined") for i in cl[key])
    elif page == "waiting":
        body = f"<h1>Waiting on client, {e(day)}</h1>"
        for r in views.waiting_on_client(db, c, day):
            rem = "".join(f"<div class=meta>Reminder {e(x['id'])}: {e(x['status'])}, max {x['max_count']}</div>" for x in r["reminders"]) or "<div class=meta>No reminder agreed.</div>"
            body += _item_card(r["item"], day, rem)
    elif page == "drafts":
        body = f"<h1>Drafts, {e(day)}</h1><p class=meta>Nothing is sent by the system. Copy, check, send, then mark as sent.</p>"
        for d in views.drafts(db, c, day):
            if d["kind"] == "recap":
                body += f"<div class=card><b>Recap email</b> to {e(d['to'])} · {e(d['status'])}<div class=meta>{e(d['path'])} in the output folder</div></div>"
            else:
                body += _item_card(d["item"], day, f"<div class=meta>Status: {e(d['status'])} · to {e(d['to'])} {e(d.get('to_email') or '')}</div>" + _draft(d["item"]["message"]))
    elif page == "review":
        r = views.review(db, c, day)
        body = f"<h1>Daily review, {e(day)}</h1><h2>Drafts ready to send</h2>"
        body += "".join(f"<div class=card>{'Recap email for ' + e(d['call']) if d['kind'] == 'recap' else e(d['item']['id']) + ' ' + e(d['subject'])} → {e(d['to'])}</div>" for d in r["drafts"])
        body += "<h2>Due today</h2>" + ("".join(f"<div class=card><b>{e(w)}</b>: " + ", ".join(f"{e(x['item']['id'])} {e(x['item']['title'])} [{e(x['kind'])}]" for x in xs) + "</div>" for w, xs in r["due"].items()) or "<p>Nothing due.</p>")
        body += "<h2>Quarantined</h2>" + ("".join(f"<div class='card err'>{e(i['id'])} {e(i['title'])}<div class=meta>{e('; '.join(i['quarantine_reasons']))}</div></div>" for i in r["quarantined"])
                                           + "".join(f"<div class='card err'>{e(k)}<div class=meta>{e('; '.join(v))}</div></div>" for k, v in r["account_quarantine"].items()) or "<p>None.</p>")
        body += "<h2>Ambiguities</h2>" + "".join(f"<div class='card warn'>{e(i['id'])} {e(i['title'])}: {e(a)}</div>" for i, a in r["ambiguities"])
        body += "<h2>Constraint conflicts</h2>" + ("".join(f"<div class='card err'>{e(i['id'])}: {e(x['message'])}</div>" for i, x in r["constraint_conflicts"])
                                                   + "".join(f"<div class='card err'>{e(x['item_id'] or x['previous_id'])}: {e(x['description'])}</div>" for x in r["cross_call_conflicts"]) or "<p>None.</p>")
    elif page == "item":
        it = store.item(db, qs["id"][0])
        body = _item_card(it, day) + "<h2>Events</h2>" + ("".join(f"<div class=meta>{e(x['at'])} {e(x['kind'])} {e(x['note'])}</div>" for x in it["events"]) or "<p class=meta>None.</p>")
        body += _draft(it.get("message")) + f"<h2>Raw</h2><pre>{e(it)}</pre>"
    return f"<!doctype html><meta charset=utf-8><title>Rinvo account assistant</title><style>{CSS}</style><nav><b>{e(c)}</b>{nav}</nav><main>{body}</main>"


def check_page(app: App, form: dict) -> str:
    db = app.db()
    c, day = form["c"][0], form["day"][0]
    sender, text = form.get("sender", [""])[0], form.get("text", [""])[0]
    res = views.check_request(db, c, sender, text, day)
    body = f"<h1>Request check</h1><p>From <b>{e(sender)}</b>: „{e(text)}”</p>"
    if not res:
        body += "<p>No hold or constraint matches this message.</p>"
    for r in res:
        cls = "card" if r["authorized"] else "card err"
        body += (f"<div class='{cls}'><b>{e(r['verdict'])}</b><div class=meta>Rule from the call: {e(r['rule'])}</div>"
                 f"<div class=meta>Matched on: {e(', '.join(r['matched']))}{' · freeze in force: ' + e(', '.join(r['freeze'])) if r['freeze'] else ''}</div></div>")
        body += _item_card(r["item"], day, actions=False)
    return f"<!doctype html><meta charset=utf-8><style>{CSS}</style><main>{body}<p><a href='/client?c={c}&day={day}'>Back</a></p></main>"


def serve(db_path: str, port: int = 8765, fixed_day: str | None = None) -> None:
    app = App(db_path, fixed_day)

    class H(BaseHTTPRequestHandler):
        def _send(self, code: int, body: str, loc: str | None = None):
            data = body.encode("utf-8")
            self.send_response(code)
            if loc:
                self.send_header("Location", loc)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            page = u.path.strip("/") or "today"
            if page not in [p for p, _ in PAGES] + ["item"]:
                return self._send(404, "not found")
            self._send(200, render_page(app, page, urllib.parse.parse_qs(u.query)))

        def do_POST(self):
            form = urllib.parse.parse_qs(self.rfile.read(int(self.headers.get("content-length", 0))).decode("utf-8"))
            if self.path == "/event":
                store.record_event(app.db(), form["id"][0], form["kind"][0], form["day"][0], note=form.get("note", [""])[0])
                return self._send(303, "", f"/item?id={urllib.parse.quote(form['id'][0])}&day={form['day'][0]}")
            if self.path == "/check":
                return self._send(200, check_page(app, form))
            self._send(404, "not found")

        def log_message(self, *a):
            pass

    print(f"http://127.0.0.1:{port}/today")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
