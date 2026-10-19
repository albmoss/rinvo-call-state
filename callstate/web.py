import datetime as dt
import html
import itertools
import os
import re
import threading
import urllib.parse
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import llm, store, views
from .dates import WEEKDAY_PL, pl_date
from .pipeline import NeedsExtraction, ValidationFailed, run, slug
from .transcript import fold, load

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Warsaw")
except Exception:
    TZ = None

CSS = """body{font:15px/1.45 system-ui,sans-serif;margin:0;color:#1d1d1f;background:#fafafa}
nav{display:flex;gap:18px;align-items:center;padding:12px 24px;background:#fff;border-bottom:1px solid #e5e5e5;position:sticky;top:0;flex-wrap:wrap}
nav a{color:#333;text-decoration:none}nav a.on{font-weight:600;color:#0a58ca}nav form{margin-left:auto;display:flex;gap:8px;align-items:center}
main{max-width:1000px;margin:0 auto;padding:20px 24px}h1{font-size:22px;margin-bottom:4px}h2{font-size:17px;margin-top:28px}
.lead{color:#666;margin-top:0}.card{background:#fff;border:1px solid #e5e5e5;border-radius:8px;padding:12px 14px;margin:8px 0}
.meta{color:#666;font-size:13px}.tag{display:inline-block;font-size:12px;padding:1px 7px;border-radius:10px;background:#eef;margin-right:4px}
.late{background:#fdecea}.warn{background:#fff4e5}.err{background:#fdecea}.ok{background:#eaf6ec}
blockquote{margin:6px 0;padding-left:10px;border-left:3px solid #ccc;color:#444;font-size:13px}
pre{white-space:pre-wrap;background:#f4f4f4;padding:10px;border-radius:6px;font:inherit}summary{cursor:pointer;color:#0a58ca;font-size:13px}
button{cursor:pointer;transition:transform 120ms ease-out}button:active{transform:scale(0.97)}
input,textarea,select{font:inherit}table{border-collapse:collapse}td,th{padding:4px 10px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
textarea{width:100%;box-sizing:border-box;font-size:13px;font-family:ui-monospace,Consolas,monospace}.add label{display:block;margin:12px 0 4px;font-weight:600}
[id]{scroll-margin-top:70px}.sum{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.sum a{background:#fff;border:1px solid #e5e5e5;border-radius:8px;padding:5px 10px;color:#333;text-decoration:none;font-size:13px}
.sum a b{font-size:16px;margin-right:5px;color:#1d1d1f}.sum a.hot{background:#fdecea}.sum a.hot b{color:#b3261e}
.ln{font-size:14px;padding:1px 4px;white-space:pre-wrap}.ln a{display:inline-block;width:38px;color:#999;text-decoration:none;font-size:12px}.ln:target{background:#fff4c2}"""

OPEN_HASH = "<script>function o(){var d=location.hash&&document.getElementById(location.hash.slice(1));if(d&&d.tagName=='DETAILS')d.open=true}addEventListener('hashchange',o);o()</script>"

PAGES = [("today", "Na dziś", "Co trzeba dziś zrobić, osobno dla każdej osoby."),
         ("waiting", "Czekamy na klienta", "Co klient obiecał nam przysłać i kiedy wolno mu przypomnieć."),
         ("drafts", "Do wysłania", "Gotowe teksty. System niczego nie wysyła: skopiuj, sprawdź, wyślij, kliknij „Wysłane”."),
         ("client", "Klient", "Wszystko o kliencie: kto decyduje, aktualne ustawienia, wstrzymane sprawy i zasady."),
         ("review", "Przegląd dnia", "Jedno miejsce do przejrzenia raz dziennie: co wysłać, co na dziś, co wymaga decyzji."),
         ("add", "+ Dodaj rozmowę", "Wgraj transkrypt nowej rozmowy. Model wyciąga z niego sprawy, a panel od razu je pokazuje.")]

STATE_PL = {"open": "do zrobienia", "conditional": "czeka na warunek", "pending_approval": "czeka na zgodę",
            "deferred": "wstrzymane", "blocked": "zablokowane", "active": "obowiązuje", "closed": "zamknięte",
            "superseded": "zastąpione", "rejected": "odrzucone", "noted": "informacja"}
TYPE_PL = {"bug": "błąd", "config_change": "zmiana konfiguracji", "feature_request": "prośba o funkcję",
           "commitment": "zobowiązanie", "follow_up": "przypomnienie", "billing": "rozliczenia",
           "constraint": "zasada", "account_signal": "sygnał o kliencie"}


def e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def today_iso() -> str:
    return (dt.datetime.now(TZ) if TZ else dt.datetime.now()).date().isoformat()


def day_pl(iso: str | None) -> str:
    if not iso:
        return ""
    d = dt.date.fromisoformat(iso)
    return f"{WEEKDAY_PL[d.weekday()]}, {pl_date(iso)}"


class App:
    def __init__(self, db_path: str, fixed_day: str | None = None):
        self.db_path = db_path
        self.fixed_day = fixed_day
        self.root = Path(db_path).resolve().parent
        self.jobs: dict[int, dict] = {}
        self.ids = itertools.count(1)
        self.lock = threading.Lock()

    def db(self):
        return store.connect(self.db_path)


def _when(it: dict, day: str) -> str:
    d = views.due_date(it)
    w = it.get("when") or {}
    if w.get("kind") == "not_before" and w.get("start"):
        return f"nie wcześniej niż {pl_date(w['start'])}"
    if not d:
        return "bez terminu"
    tm = f", {w['time']}" if w.get("time") else ""
    if d < day and it["state"] in ("open", "conditional"):
        return f"<b style='color:#b3261e'>zaległe, minął {pl_date(d)}</b>"
    if d == day:
        return f"<b>dziś</b>{tm}"
    return f"{pl_date(d)}{tm}"


def _action(it: dict) -> tuple[str, str] | None:
    if it["state"] == "closed":
        return "reopened", "Cofnij: otwórz ponownie"
    if it["state"] in ("superseded", "rejected", "noted", "active", "deferred", "blocked", "pending_approval"):
        return None
    if it["type"] == "follow_up":
        return "sent", "Wysłałem przypomnienie"
    if it["owner"]["party"] == "customer":
        return "received", "Dostaliśmy"
    if it["state"] == "conditional":
        return "condition_met", "Warunek spełniony"
    if it.get("message") and views.sent_count(it) == 0:
        return "sent", "Wysłane"
    return "done", "Zrobione"


def card(it: dict, day: str, back: str, draft: bool = True, note: str = "") -> str:
    who = it["owner"].get("person") or ("Rinvo" if it["owner"]["party"] == "rinvo" else "klient")
    parts = [f"<div class=card><b>{e(it['title'])}</b><br>",
             f"<span class=tag>{e(STATE_PL.get(it['state'], it['state']))}</span><span class=tag>{e(TYPE_PL.get(it['type'], it['type']))}</span>"
             f"<span class=meta>odpowiada: <b>{e(who)}</b> · termin: {_when(it, day)}</span>"]
    if it.get("action"):
        parts.append(f"<div>{e(it['action'])}</div>")
    if note:
        parts.append(f"<div class=meta>{note}</div>")
    if it.get("condition"):
        parts.append(f"<div class=meta>Warunek: {e(it['condition']['text'])}</div>")
    if it.get("approvers"):
        parts.append(f"<div class=meta>Potrzebna zgoda: {e(', '.join(it['approvers']))}</div>")
    if it.get("if_others_ask"):
        parts.append(f"<div class=meta>Jeśli poprosi ktoś inny: {e(it['if_others_ask'])}</div>")
    m = it.get("message")
    if draft and m:
        parts.append(f"<div class=meta style='margin-top:8px'>Tekst do wysłania, do: <b>{e(m['to'])}</b>{' &lt;' + e(m.get('to_email')) + '&gt;' if m.get('to_email') else ''}, temat: {e(m['subject_pl'])}</div><pre>{e(m['body_pl'])}</pre>")
    call = it["id"].split("/")[0]
    quotes = "".join(f"<blockquote>„{e(x['quote'])}” · {e(x['speaker'])}, <a href='/transcript?call={e(call)}#L{x['line']}'>linia {x['line']}</a></blockquote>" for x in it["evidence"])
    parts.append(f"<details><summary>Skąd to wiemy: cytaty z rozmowy ({len(it['evidence'])})</summary>{quotes}</details>")
    act = _action(it)
    if act:
        kind, text = act
        parts.append(f"<form method=post action=/event style='margin-top:8px'><input type=hidden name=id value='{e(it['id'])}'>"
                     f"<input type=hidden name=kind value={kind}><input type=hidden name=day value={day}><input type=hidden name=back value='{e(back)}'>"
                     f"<button>{text}</button></form>")
    parts.append("</div>")
    return "".join(parts)


def section(title: str, cards: list[str], empty: str = "Nic.", anchor: str = "") -> str:
    return f"<h2 id='{anchor}'>{e(title)} ({len(cards)})</h2>" + ("".join(cards) if cards else f"<p class=meta>{e(empty)}</p>")


def folded(title: str, cards: list[str], anchor: str = "") -> str:
    if not cards:
        return ""
    return f"<details class=card id='{anchor}'><summary style='font-size:15px;color:#1d1d1f'><b>{e(title)}</b> ({len(cards)})</summary>{''.join(cards)}</details>"


def page_today(db, c, day, back):
    groups = views.today(db, c, day)
    out = []
    for who, entries in groups.items():
        rem = [x for x in entries if x["kind"] == "reminder"]
        due = [x for x in entries if x["kind"] in ("due", "overdue")]
        cond = [x for x in entries if x["kind"] == "due if condition holds"]
        late = [x for x in entries if x["kind"] == "client_late"]
        meet = [x for x in entries if x["kind"] == "meeting"]
        out.append(f"<h2 style='font-size:20px'>{e(who)}</h2>")
        if meet:
            out.append(section("Spotkania dziś", [card(x["item"], day, back) for x in meet], anchor="spotkania"))
        out.append(section("Przypomnienia do wysłania dziś", [card(x["item"], day, back, note=f"Wysłano {x['reminder']['sent']} z {x['reminder']['max_count']}. Wyślij tylko, jeśli klient jeszcze nie przysłał.") for x in rem], "Dziś nie ma przypomnień.", "przypomnienia"))
        out.append(section("Zadania na dziś i zaległe", [card(x["item"], day, back) for x in due], "Nic zaległego.", "zadania"))
        if cond:
            out.append(section("Zrób, jeśli warunek jest już spełniony", [card(x["item"], day, back) for x in cond], anchor="warunek"))
        if late:
            out.append(section("Klient się spóźnia", [card(x["item"], day, back) for x in late], anchor="spoznienia"))
    return "".join(out) or "<p class=meta>Na dziś nic nie ma.</p>"


def page_waiting(db, c, day, back):
    rows = views.waiting_on_client(db, c, day)
    cards = []
    for r in rows:
        if r["reminders"]:
            x = r["reminders"][0]
            if x["status"].startswith("not needed"):
                status = "niepotrzebne, już przyszło"
            elif x["status"].startswith("done"):
                status = f"wysłane {x['sent']} z {x['max_count']}"
            elif x["due"]:
                status = "wysłać dziś (zakładka Na dziś)"
            else:
                status = "jeszcze nie teraz"
            note = f"Przypomnienie: {e(pl_date(x['deadline']) or 'bez daty')}, najwyżej {x['max_count']} raz. Stan: {e(status)}."
        else:
            note = "Nie umawialiśmy przypomnienia: nie ponaglamy."
        cards.append(card(r["item"], day, back, draft=False, note=note))
    return section("Klient obiecał", cards, "Na nic nie czekamy.")


def page_drafts(db, c, day, back):
    ds = views.drafts(db, c, day)
    ready, later = [], []
    for d in ds:
        if d["kind"] == "recap":
            ready.insert(0, f"<div class=card><h3>Podsumowanie rozmowy z {e(pl_date(d['call']))}</h3><div class=meta>do: <b>{e(d['to'])}</b></div>"
                            f"<div class=todo>Mail po polsku ze wszystkimi ustaleniami. Plik: <code>out/{e(c)}/{e(d['call'])}/drafts/recap_email_pl.md</code></div></div>")
        elif d["status"] == "ready":
            ready.append(card(d["item"], day, back))
        else:
            later.append(card(d["item"], day, back))
    return section("Gotowe do wysłania", ready, "Nic do wysłania.") + folded("Czekają na warunek albo termin", later)


def page_client(db, c, day, back):
    cl = views.client(db, c)
    acc = cl["account"]
    out = ["<div class=card><b>Ktoś o coś prosi albo mówi, że ktoś się zgodził?</b> Sprawdź tu, zanim cokolwiek zmienisz.<br><br>"
           f"<form method=post action=/check><input type=hidden name=c value='{e(c)}'><input type=hidden name=day value={e(day)}>"
           "<input name=sender placeholder='Od kogo, np. Paweł' required> <input name=text size=50 placeholder='Treść, np. włączcie Opla od jutra' required> "
           "<button>Sprawdź</button></form></div>"]
    out.append("<h2>Kto o czym decyduje</h2><table><tr><th>Sprawa</th><th>Decyduje</th><th>Nie może decydować</th></tr>" + "".join(
        f"<tr><td>{e(a['decision'])}</td><td><b>{e(', '.join(a['approvers']) or '-')}</b></td><td>{e(', '.join(a['not_authorized']) or '-')}</td></tr>" for a in acc["authority"]) + "</table>")
    current = [f for f in acc["facts"] if f["status"] != "superseded"]
    old = [f for f in acc["facts"] if f["status"] == "superseded"]
    out.append("<h2>Ustawienia i fakty</h2><table><tr><th>Co</th><th>Wartość</th></tr>" + "".join(
        f"<tr><td>{e(f['subject'])}</td><td>{e(f['value'])}{' <span class=tag>do zmiany</span>' if f['status'] == 'pending_change' else ''}</td></tr>" for f in current) + "</table>")
    if old:
        out.append("<details><summary>Wcześniejsze wartości, poprawione w trakcie rozmowy</summary><table>" + "".join(
            f"<tr><td>{e(f['subject'])}</td><td><s>{e(f['value'])}</s></td></tr>" for f in old) + "</table></details>")
    out.append("<h2>Osoby</h2><table><tr><th>Kto</th><th>Rola</th><th>Na rozmowie</th><th>E-mail</th></tr>" + "".join(
        f"<tr><td>{e(p['name'])}{' (Rinvo)' if p['side'] == 'rinvo' else ''}</td><td>{e(p['role'])}</td><td>{'tak' if p['present'] else 'nie'}</td><td>{e(p['email'])}</td></tr>" for p in acc["people"]) + "</table>")
    out.append("<h2>Sprawy</h2>")
    for title, key in [("Nasze zobowiązania", "rinvo_commitments"), ("Czekamy na klienta", "waiting_on_client"), ("Wstrzymane: nie ruszać", "holds"),
                       ("Zasady, których się trzymamy", "constraints"), ("Prośby o nowe funkcje (bez obiecanego terminu)", "product"),
                       ("Ryzyka i sygnały", "risks"), ("Zamknięte", "closed"), ("Kwarantanna: cytat się nie zgadza", "quarantined")]:
        out.append(folded(title, [card(i, day, back, draft=False) for i in cl[key]], key))
    return "".join(out)


def page_review(db, c, day, back):
    r = views.review(db, c, day)
    out = []
    out.append("<h2>1. Wyślij gotowe teksty</h2>" + ("".join(
        f"<div class=card>{'Podsumowanie rozmowy z ' + e(pl_date(d['call'])) if d['kind'] == 'recap' else e(d['subject'])} → <b>{e(d['to'])}</b></div>" for d in r["drafts"]) or "<p class=meta>Nic.</p>")
        + f"<p><a href='/drafts?c={e(c)}&day={e(day)}'>Otwórz teksty →</a></p>")
    out.append("<h2>2. Sprawy na dziś</h2>" + ("".join(
        f"<div class=card><b>{e(w)}</b>: {len(xs)} spraw</div>" for w, xs in r["due"].items()) or "<p class=meta>Nic.</p>")
        + f"<p><a href='/today?c={e(c)}&day={e(day)}'>Otwórz listę na dziś →</a></p>")
    q = [f"<div class=card><b>{e(i['title'])}</b><div class=meta>{e('; '.join(i['quarantine_reasons']))}</div></div>" for i in r["quarantined"]]
    q += [f"<div class=card>{e(k)}<div class=meta>{e('; '.join(v))}</div></div>" for k, v in r["account_quarantine"].items()]
    out.append("<h2>3. Kwarantanna: model zacytował coś, czego nie ma w rozmowie</h2>" + ("".join(q) or "<p class=meta>Nic. Wszystkie cytaty się zgadzają.</p>"))
    conf = [f"<div class='card err'>{e(i['title'])}: {e(x['message'])}</div>" for i, x in r["constraint_conflicts"]]
    conf += [f"<div class='card err'>{e(x['description'])}</div>" for x in r["cross_call_conflicts"]]
    out.append("<h2>4. Konflikty z zasadami</h2>" + ("".join(conf) or "<p class=meta>Brak.</p>"))
    out.append("<h2>5. Niejasności do rozstrzygnięcia</h2>" + folded("Pokaż", [f"<div class=card><b>{e(i['title'])}</b><div>{e(a)}</div></div>" for i, a in r["ambiguities"]]))
    return "".join(out)


def summary(db, c: str, day: str) -> str:
    entries = [x for xs in views.today(db, c, day).values() for x in xs]
    n = lambda *kinds: sum(1 for x in entries if x["kind"] in kinds)
    ready = sum(1 for d in views.drafts(db, c, day) if d["status"] == "ready")
    cl = views.client(db, c)
    amb = len(views.review(db, c, day)["ambiguities"])
    q = f"c={e(c)}&day={e(day)}"
    chips = [(f"/today?{q}#spotkania", n("meeting"), "spotkania dziś", False),
             (f"/today?{q}#przypomnienia", n("reminder"), "przypomnienia do wysłania", True),
             (f"/today?{q}#zadania", n("due", "overdue"), f"zadania na dziś (zaległe: {n('overdue')})", n("overdue") > 0),
             (f"/today?{q}#warunek", n("due if condition holds"), "zrób, jeśli warunek spełniony", False),
             (f"/drafts?{q}", ready, "teksty do wysłania", False),
             (f"/today?{q}#spoznienia", n("client_late"), "klient się spóźnia", n("client_late") > 0),
             (f"/waiting?{q}", len(cl["waiting_on_client"]), "czekamy na klienta", False),
             (f"/client?{q}#holds", len(cl["holds"]), "wstrzymane", False),
             (f"/review?{q}", amb, "niejasności do przejrzenia", False)]
    out = "".join(f"<a class='{'hot' if hot and k else ''}' href='{h}'><b>{k}</b>{e(t)}</a>" for h, k, t, hot in chips if k or h.endswith(("zadania", "przypomnienia")))
    calls = " · ".join(f"rozmowa {e(pl_date(x['date']))}: <a href='/transcript?{q}&call={e(x['id'])}'>{e(x['transcript'])}</a>" for x in store.calls(db, c))
    return (f"<div class=sum>{out}</div><p class=meta style='margin:0 0 18px'>Źródła (transkrypty w rejestrze): {calls} · "
            f"<a href='/add?{q}'>+ dodaj nową rozmowę</a></p>")


def layout(db, c: str, day: str, page: str, body: str) -> str:
    title, lead = next(((t, ld) for p, t, ld in PAGES if p == page), ("", ""))
    nav = "".join(f"<a class='{'on' if p == page else ''}' href='/{p}?c={e(c)}&day={e(day)}'>{t}</a>" for p, t, _ in PAGES if c or p == "add")
    head = f"<h1>{e(title)}</h1><p class=lead>{e(lead)}</p>" if title else ""
    custs = store.customers(db)
    if len(custs) > 1:
        pick = "<select name=c onchange='this.form.submit()'>" + "".join(f"<option value='{e(x)}'{' selected' if x == c else ''}>{e(x.replace('_', ' ').title())}</option>" for x in custs) + "</select>"
    else:
        pick = f"<input type=hidden name=c value='{e(c)}'>"
    brand = e(c.replace('_', ' ').title()) if c else "Asystent konta"
    return (f"<!doctype html><html lang=pl><meta charset=utf-8><title>{e(title or 'Asystent konta')}</title><style>{CSS}</style>"
            f"<nav><b>{brand}</b>{nav}"
            f"<form>{pick}<span class=meta>Stan na: {e(day_pl(day))}</span><input type=date name=day value={e(day)}><button>Pokaż</button></form></nav>"
            f"<main>{summary(db, c, day) if c else ''}{head}{body}</main>{OPEN_HASH}</html>")


def transcript_page(app: App, db, c: str, day: str, call_id: str) -> str:
    row = next((x for x in store.calls(db, c) if x["id"] == call_id), None)
    if not row:
        return layout(db, c, day, "transcript", "<h1>Transkrypt</h1><p class=meta>Nie ma takiej rozmowy w rejestrze.</p>")
    path = Path(row["transcript"])
    if not path.is_absolute() and not path.exists():
        path = Path(app.db_path).resolve().parent / row["transcript"]
    if not path.exists():
        return layout(db, c, day, "transcript", f"<h1>Transkrypt</h1><p class=meta>Nie znalazłem pliku {e(row['transcript'])}.</p>")
    lines = path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    body = "".join(f"<div class=ln id=L{i}><a href='#L{i}'>{i}</a>{e(t) or '&nbsp;'}</div>" for i, t in enumerate(lines, 1))
    return layout(db, c, day, "transcript", f"<h1>Transkrypt rozmowy z {e(pl_date(row['date']))}</h1>"
                  f"<p class=lead>Plik: <code>{e(row['transcript'])}</code>. Numery linii są te same co w cytatach.</p><div class=card>{body}</div>")


def _day(raw: str | None, default: str) -> str:
    try:
        return dt.date.fromisoformat(raw).isoformat() if raw else default
    except ValueError:
        return default


UPLOAD_JS = ("<script>var f=document.getElementById('file');if(f)f.onchange=function(){var x=this.files[0];if(!x)return;"
             "document.getElementById('name').value=x.name;x.text().then(function(t){document.getElementById('text').value=t})}</script>")

FORMAT_HELP = """# Klient × Rinvo: tytuł rozmowy

20 października 2026, Google Meet.

## Uczestnicy

- **Kasia Malinowska**, BDC, Klient, kasia@firma.pl
- **Marek Rewoliński**, Rinvo, marek@rinvo.io

## Transkrypcja

**Kasia:** Dzień dobry.

**Marek:** Dzień dobry, to zaczynamy."""


def _save_transcript(app: App, stem: str, text: str) -> Path:
    folder = app.root / "transcripts"
    folder.mkdir(exist_ok=True)
    base = re.sub(r"[^a-z0-9-]+", "_", fold(stem)).strip("_-") or "rozmowa"
    path, n = folder / f"{base}.md", 2
    while path.exists() and path.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
        path, n = folder / f"{base}_{n}.md", n + 1
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _rel(path: Path) -> str:
    try:
        return os.path.relpath(path).replace("\\", "/")
    except ValueError:
        return str(path)


def start_job(app: App, path: str, date: str | None, extraction: str | None = None) -> int | None:
    with app.lock:
        if any(j["state"] == "running" for j in app.jobs.values()):
            return None
        job = {"id": next(app.ids), "state": "running", "log": [], "path": path, "date": date, "error": "", "prompt": "", "customer": "", "call": ""}
        app.jobs[job["id"]] = job

    def work():
        try:
            out = run(path, app.db_path, str(app.root / "out"), extraction, date, log=job["log"].append)
            job.update(state="done", customer=out.parent.name, call=out.name)
        except NeedsExtraction as ex:
            job.update(state="manual", prompt=str(ex))
        except (ValidationFailed, llm.LLMError, SystemExit) as ex:
            job.update(state="error", error=str(ex))
        except Exception as ex:
            job.update(state="error", error=f"{type(ex).__name__}: {ex}")

    threading.Thread(target=work, daemon=True).start()
    return job["id"]


def job_view(job: dict, c: str, day: str) -> str:
    log = "".join(f"<div class=meta>{e(x)}</div>" for x in job["log"])
    src = f"<p class=meta>Transkrypt zapisany jako <code>{e(job['path'])}</code>.</p>"
    if job["state"] == "running":
        return (f"<div class='card warn'><b>Przetwarzam rozmowę…</b> Model czyta transkrypt, zwykle trwa to 1-3 minuty. Strona odświeża się sama.</div>{src}{log}"
                "<script>setTimeout(function(){location.reload()},3000)</script>")
    if job["state"] == "done":
        q = f"c={e(job['customer'])}&day={e(job['call'])}"
        return (f"<div class='card ok'><b>Gotowe.</b> Rozmowa z {e(pl_date(job['call']))} jest w rejestrze.</div>{src}{log}"
                f"<p><a href='/today?{q}'>Zobacz sprawy na dzień rozmowy →</a> · <a href='/review?{q}'>Przegląd dnia →</a> · "
                f"<a href='/transcript?{q}&call={e(job['call'])}'>Transkrypt →</a></p>")
    if job["state"] == "manual":
        prompt = Path(job["prompt"]).read_text(encoding="utf-8")
        return (f"<div class='card warn'><b>Brak klucza API, więc zrób ten krok ręcznie.</b> Transkrypt jest zapisany i sprawdzony.</div>{src}"
                "<form method=post action=/add/response class='card add'>"
                "<label>1. Skopiuj prompt i wklej go w Claude</label>"
                f"<textarea id=prompt rows=8 readonly>{e(prompt)}</textarea>"
                "<button type=button onclick=\"navigator.clipboard.writeText(document.getElementById('prompt').value);this.textContent='Skopiowane'\">Kopiuj prompt</button>"
                "<label>2. Wklej tutaj całą odpowiedź modelu (JSON)</label>"
                "<textarea name=response rows=8 required></textarea>"
                f"<input type=hidden name=job value={job['id']}><input type=hidden name=c value='{e(c)}'><input type=hidden name=day value='{e(day)}'>"
                "<p><button>Przetwórz odpowiedź</button></p></form>")
    return (f"<div class='card err'><b>Nie udało się.</b> Nic nie zostało dodane do rejestru.<pre>{e(job['error'])}</pre></div>{src}{log}"
            f"<p><a href='/add?c={e(c)}&day={e(day)}'>← Spróbuj jeszcze raz</a></p>")


def add_page(app: App, db, c: str, day: str, qs: dict, values: dict | None = None, notice: str = "") -> str:
    jid = qs.get("job", [""])[0]
    if jid.isdigit() and int(jid) in app.jobs:
        return layout(db, c, day, "add", job_view(app.jobs[int(jid)], c, day))
    v = values or {}
    if os.environ.get("ANTHROPIC_API_KEY"):
        status = "<div class='card ok'>Klucz API jest ustawiony: po kliknięciu model sam przeczyta rozmowę.</div>"
    else:
        status = ("<div class='card warn'><b>Panel działa bez klucza API.</b> Rozmowę i tak dodasz: panel da Ci prompt do wklejenia w Claude i pole na odpowiedź. "
                  "Żeby działało samo, uruchom panel z ustawionym <code>ANTHROPIC_API_KEY</code>.</div>")
    calls = "".join(f"<li>{e(x['customer'].replace('_', ' ').title())}, {e(pl_date(x['date']))}: <code>{e(x['transcript'])}</code></li>"
                    for cu in store.customers(db) for x in store.calls(db, cu))
    body = (f"{status}{notice}<form method=post action=/add class='card add'>"
            "<label>1. Wybierz plik z transkryptem (.md lub .txt)</label><input type=file id=file accept='.md,.txt,text/plain,text/markdown'>"
            "<label>albo wklej treść</label>"
            f"<textarea id=text name=text rows=12 required>{e(v.get('text', ''))}</textarea>"
            f"<input type=hidden id=name name=name value='{e(v.get('name', ''))}'>"
            "<label>2. Data rozmowy <span class=meta style='font-weight:400'>(tylko jeśli nie ma jej w nagłówku)</span></label>"
            f"<input type=date name=date value='{e(v.get('date', ''))}'>{v.get('confirm', '')}"
            f"<input type=hidden name=c value='{e(c)}'><input type=hidden name=day value='{e(day)}'>"
            "<p><button>Przetwórz rozmowę</button></p></form>"
            f"<details><summary>Jak ma wyglądać transkrypt</summary><pre>{e(FORMAT_HELP)}</pre></details>"
            f"<h2>Rozmowy w rejestrze</h2><ul class=meta>{calls or '<li>Jeszcze żadnej.</li>'}</ul>"
            f"<p class=meta>Nowe transkrypty trafiają do folderu <code>transcripts/</code>, a wyniki do <code>out/</code>.</p>{UPLOAD_JS}")
    return layout(db, c, day, "add", body)


def add_submit(app: App, form: dict) -> tuple[int, str]:
    db = app.db()
    custs = store.customers(db)
    c = form.get("c", [""])[0]
    c = c if c in custs else (custs[0] if custs else "")
    day = _day(form.get("day", [None])[0], app.fixed_day or today_iso())
    text = form.get("text", [""])[0].replace("\r\n", "\n")
    name, date = form.get("name", [""])[0], form.get("date", [""])[0] or None
    values = {"text": text, "name": name, "date": date or ""}

    def again(msg: str, cls: str = "err") -> tuple[int, str]:
        return 200, add_page(app, db, c, day, {}, values, f"<div class='card {cls}'>{msg}</div>")

    if not text.strip():
        return again("Brak treści transkryptu.")
    if date and _day(date, "") != date:
        return again("Zła data rozmowy.")
    tmp = app.root / "transcripts" / ".upload.md"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(text, encoding="utf-8", newline="\n")
    try:
        t = load(str(tmp), dt.date.fromisoformat(date) if date else None)
    finally:
        tmp.unlink()
    if t.call_date is None:
        return again("Nie znalazłem daty rozmowy w nagłówku. Wpisz ją w polu „Data rozmowy”.")
    if not t.turns:
        return again("Nie znalazłem wypowiedzi. Każda musi zaczynać się od imienia w gwiazdkach, np. <code>**Kasia:** Dzień dobry.</code>")
    customer, call = slug(t.customer or Path(name or "rozmowa").stem), t.call_date.isoformat()
    if any(x["id"] == call for x in store.calls(db, customer)) and not form.get("confirm"):
        values["confirm"] = ("<div class='card warn'><label style='font-weight:400'><input type=checkbox name=confirm value=1> "
                             "Tak, przetwórz ponownie. Sprawy z tej rozmowy i kliknięte przy nich zdarzenia zostaną zastąpione.</label></div>")
        return again(f"Rozmowa z {e(pl_date(call))} dla klienta {e(customer.replace('_', ' ').title())} już jest w rejestrze. Zaznacz potwierdzenie niżej, jeśli chcesz ją przetworzyć jeszcze raz.", "warn")
    path = _save_transcript(app, Path(name).stem if name else f"{customer}_{call}", text)
    jid = start_job(app, _rel(path), date)
    if jid is None:
        return again("Trwa przetwarzanie innej rozmowy. Poczekaj, aż się skończy.", "warn")
    return 303, f"/add?job={jid}&c={urllib.parse.quote(c)}&day={day}"


def add_response(app: App, form: dict) -> tuple[int, str]:
    jid = form.get("job", [""])[0]
    job = app.jobs.get(int(jid)) if jid.isdigit() else None
    c, day = form.get("c", [""])[0], form.get("day", [""])[0]
    if not job or job["state"] != "manual":
        return 303, f"/add?c={urllib.parse.quote(c)}&day={day}"
    resp = Path(job["prompt"]).parent / "pasted_response.json"
    resp.write_text(form.get("response", [""])[0], encoding="utf-8")
    new = start_job(app, job["path"], job["date"], str(resp))
    return 303, f"/add?job={new or job['id']}&c={urllib.parse.quote(c)}&day={day}"


def render_page(app: App, page: str, qs: dict) -> str:
    db = app.db()
    custs = store.customers(db)
    if page == "add" or not custs:
        c = qs.get("c", [custs[0] if custs else ""])[0]
        return add_page(app, db, c if c in custs else (custs[0] if custs else ""), _day(qs.get("day", [None])[0], app.fixed_day or today_iso()), qs)
    c = qs.get("c", [custs[0]])[0]
    if c not in custs:
        c = custs[0]
    day = _day(qs.get("day", [None])[0], app.fixed_day or today_iso())
    if page == "transcript":
        return transcript_page(app, db, c, day, qs.get("call", [""])[0])
    back = f"/{page}?c={c}&day={day}"
    fn = {"today": page_today, "waiting": page_waiting, "drafts": page_drafts, "client": page_client, "review": page_review}[page]
    return layout(db, c, day, page, fn(db, c, day, back))


def check_page(app: App, form: dict) -> str:
    db = app.db()
    custs = store.customers(db)
    c = form.get("c", [""])[0]
    if c not in custs:
        return render_page(app, "client", {})
    day = _day(form.get("day", [None])[0], app.fixed_day or today_iso())
    sender, text = form.get("sender", [""])[0].strip(), form.get("text", [""])[0].strip()
    res = views.check_request(db, c, sender, text, day)
    back = f"/client?c={c}&day={day}"
    body = [f"<p>Od <b>{e(sender)}</b>: „{e(text)}”</p>"]
    if not res:
        body.append("<div class='card warn'>Nie znalazłem wstrzymanej sprawy ani zasady, która pasuje do tej prośby. "
                    f"Zanim coś zmienisz, sprawdź w tabeli <a href='{e(back)}'>Kto o czym decyduje</a>, czy {e(sender or 'ta osoba')} może o tym decydować.</div>")
    denied = [r for r in res if not r["authorized"]]
    if denied:
        who = ", ".join(dict.fromkeys(a for r in denied for a in r["approvers"])) or "osobą wskazaną w rozmowie"
        body.append(f"<div class='card err'><b>{e(sender)} nie może tego zatwierdzić.</b> Najpierw potwierdź z: <b>{e(who)}</b>. Niczego nie zmieniaj.</div>")
    elif res:
        body.append(f"<div class='card ok'><b>{e(sender)} może o tym decydować.</b> Zmianę i tak wprowadza człowiek po przeglądzie.</div>")
    for f in views.freeze_windows(store.items(db, c)):
        if f["when"]["start"] <= day <= f["when"]["end"]:
            body.append(f"<div class='card warn'><b>Teraz obowiązuje:</b> {e(f['title'])} ({e(pl_date(f['when']['start']))} - {e(pl_date(f['when']['end']))}). {e(f.get('action') or '')}</div>")
    if res:
        body.append("<h2>Na podstawie</h2>" + "".join(card(r["item"], day, back, draft=False) for r in res))
    body.append(f"<p><a href='{e(back)}'>← Wróć do klienta</a></p>")
    return layout(db, c, day, "check", "<h1>Sprawdzenie prośby</h1>" + "".join(body))


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
            if page not in [p for p, _, _ in PAGES] + ["transcript"]:
                return self._send(404, "not found")
            self._send(200, render_page(app, page, urllib.parse.parse_qs(u.query)))

        def do_POST(self):
            form = urllib.parse.parse_qs(self.rfile.read(int(self.headers.get("content-length", 0))).decode("utf-8"))
            if self.path == "/event":
                kind = form.get("kind", [""])[0]
                if kind not in ("done", "received", "sent", "condition_met", "reopened", "cancelled"):
                    return self._send(400, "bad event kind")
                try:
                    store.record_event(app.db(), form.get("id", [""])[0], kind, _day(form.get("day", [None])[0], app.fixed_day or today_iso()))
                except KeyError:
                    return self._send(404, "unknown item")
                back = form.get("back", ["/today"])[0]
                return self._send(303, "", back if back.startswith("/") and not back.startswith("//") else "/today")
            if self.path == "/check":
                return self._send(200, check_page(app, form))
            if self.path in ("/add", "/add/response"):
                code, body = (add_submit if self.path == "/add" else add_response)(app, form)
                return self._send(code, "", body) if code == 303 else self._send(code, body)
            self._send(404, "not found")

        def log_message(self, *a):
            pass

    print(f"http://127.0.0.1:{port}/today")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
