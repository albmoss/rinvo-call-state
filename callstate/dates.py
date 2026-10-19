import datetime as dt
import re

from .transcript import fold

WEEKDAYS = {
    0: ["poniedzialek", "poniedzialku", "poniedzialkiem", "poniedzialki"],
    1: ["wtorek", "wtorku", "wtorkiem", "wtorki"],
    2: ["sroda", "srode", "srody", "srodzie", "sroda"],
    3: ["czwartek", "czwartku", "czwartkiem", "czwartki"],
    4: ["piatek", "piatku", "piatkiem", "piatki"],
    5: ["sobota", "sobote", "soboty", "sobocie"],
    6: ["niedziela", "niedziele", "niedzieli"],
}
WEEKDAY_WORD = {w: i for i, ws in WEEKDAYS.items() for w in ws}
WEEKDAY_PL = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"]

MONTH_WORD = {}
for n, forms in enumerate([
    ["styczen", "stycznia", "styczniu"], ["luty", "lutego", "lutym"], ["marzec", "marca", "marcu"],
    ["kwiecien", "kwietnia", "kwietniu"], ["maj", "maja", "maju"], ["czerwiec", "czerwca", "czerwcu"],
    ["lipiec", "lipca", "lipcu"], ["sierpien", "sierpnia", "sierpniu"], ["wrzesien", "wrzesnia", "wrzesniu"],
    ["pazdziernik", "pazdziernika", "pazdzierniku"], ["listopad", "listopada", "listopadzie"],
    ["grudzien", "grudnia", "grudniu"]], start=1):
    for f in forms:
        MONTH_WORD[f] = n
MONTH_GEN_PL = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia",
                "września", "października", "listopada", "grudnia"]

UNITS = {"pierwsz": 1, "drugi": 2, "trzeci": 3, "czwart": 4, "piat": 5, "szost": 6, "siodm": 7, "osm": 8, "dziewiat": 9}
TEENS = {"dziesiat": 10, "jedenast": 11, "dwunast": 12, "trzynast": 13, "czternast": 14, "pietnast": 15,
         "szesnast": 16, "siedemnast": 17, "osiemnast": 18, "dziewietnast": 19}
TENS = {"dwudziest": 20, "trzydziest": 30}
DAY_ENDINGS = ("ego", "y", "i")
HOUR_ENDINGS = ("ej", "a")

NEXT_WORDS = {"przyszly", "przyszlym", "przyszlego", "przyszla", "przyszlej", "przyszla", "nastepny", "nastepnym",
              "nastepnego", "nastepna", "nastepnej"}
LAST_WORDS = {"zeszly", "zeszlym", "zeszlego", "zeszla", "zeszlej", "ubiegly", "ubieglym", "ubieglego", "ubiegla",
              "ubieglej", "poprzedni", "poprzednim", "poprzedniego"}
THIS_WORDS = {"ten", "tym", "tego", "ta", "te", "tej"}
TODAY_PATTERNS = [r"\bdzis\b", r"\bdzisiaj\b", r"\bdzisiejsz", r"\bpo callu\b", r"\bpo spotkaniu\b",
                  r"\bpo rozmowie\b", r"\bzaraz po\b", r"\bjeszcze dzis"]


def _stem_value(tok: str, table: dict, endings: tuple) -> int | None:
    for stem, val in table.items():
        if tok.startswith(stem) and tok[len(stem):] in endings:
            return val
    return None


def _word_day_numbers(tokens: list[str]) -> list[int]:
    out = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        tens = _stem_value(tok, TENS, DAY_ENDINGS)
        if tens:
            unit = _stem_value(tokens[i + 1], UNITS, DAY_ENDINGS) if i + 1 < len(tokens) else None
            if unit:
                out.append(tens + unit)
                i += 2
                continue
            out.append(tens)
        else:
            v = _stem_value(tok, TEENS, DAY_ENDINGS) or _stem_value(tok, UNITS, ("ego",))
            if v:
                out.append(v)
        i += 1
    return out


def _hour(tokens: list[str], text: str) -> str | None:
    m = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text) or re.search(r"\b(?:o|godz\.?)\s*([01]?\d|2[0-3])\.([0-5]\d)\b", text)
    if m:
        return f"{int(m[1]):02d}:{m[2]}"
    for i, tok in enumerate(tokens):
        prev = tokens[i - 1] if i else ""
        tens = _stem_value(tok, {"dwudziest": 20}, HOUR_ENDINGS)
        v = tens or _stem_value(tok, TEENS, HOUR_ENDINGS) or _stem_value(tok, UNITS, HOUR_ENDINGS)
        if v and (prev == "o" or tok.endswith("a")) and 6 <= v <= 23:
            return f"{v:02d}:00"
    return None


def _week_start(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def _add_months(d: dt.date, n: int) -> dt.date:
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    m += 1
    for day in (d.day, 30, 29, 28):
        try:
            return dt.date(y, m, day)
        except ValueError:
            continue
    raise ValueError(d)


def _month_end(d: dt.date) -> dt.date:
    return _add_months(d.replace(day=1), 1) - dt.timedelta(days=1)


def _day_in_context(day: int, month: int | None, call: dt.date, past: bool) -> dt.date | None:
    if month:
        year = call.year
        try:
            cand = dt.date(year, month, day)
        except ValueError:
            return None
        if past and cand > call:
            cand = cand.replace(year=year - 1)
        if not past and cand < call:
            cand = cand.replace(year=year + 1)
        return cand
    base = call.replace(day=1)
    for shift in ((0, -1) if past else (0, 1)):
        m = _add_months(base, shift)
        try:
            cand = m.replace(day=day)
        except ValueError:
            continue
        if (past and cand <= call) or (not past and cand >= call):
            return cand
    return None


def resolve(phrase: str, call: dt.date, kind: str | None = None, tense: str | None = None) -> dict | None:
    if not phrase or call is None:
        return None
    text = fold(phrase)
    tokens = re.findall(r"[a-z0-9]+", text)
    past = tense == "past" or kind == "past" or bool(re.search(r"\btemu\b", text))
    kind = kind or ("past" if past else "by")
    window = None
    day = None
    basis = []
    approximate = False
    flags = []

    m = re.search(r"\b(\w+|\d+)\s+(tydzien|tygodnie|tygodni)\s+temu\b", text)
    if re.search(r"\btydzien temu\b", text):
        day = call - dt.timedelta(days=7)
        basis.append("one week before the call")
        approximate = True
    elif m:
        n = {"dwa": 2, "trzy": 3, "cztery": 4}.get(m[1], int(m[1]) if m[1].isdigit() else None)
        if n:
            day = call - dt.timedelta(days=7 * n)
            basis.append(f"{n} weeks before the call")
            approximate = True
    if day is None:
        if re.search(r"\bpojutrze\b", text):
            day, _ = call + dt.timedelta(days=2), basis.append("day after tomorrow")
        elif re.search(r"\bjutr", text):
            day, _ = call + dt.timedelta(days=1), basis.append("tomorrow")
        elif re.search(r"\bprzedwczoraj\b", text):
            day, _ = call - dt.timedelta(days=2), basis.append("two days before the call")
        elif re.search(r"\bwczoraj", text):
            day, _ = call - dt.timedelta(days=1), basis.append("day before the call")
        elif any(re.search(p, text) for p in TODAY_PATTERNS):
            day, _ = call, basis.append("call date")

    month = next((MONTH_WORD[t] for t in tokens if t in MONTH_WORD), None)
    dm = re.search(r"(?<![\d:])(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?(?![\d:])", text)
    if dm and 1 <= int(dm[2]) <= 12 and not re.search(r"\b(o|godz|godzina|godzinie)\s*$", text[:dm.start()]):
        month = int(dm[2])
        numbers = [int(dm[1])]
        text = text[:dm.start()] + " " + text[dm.end():]
    else:
        numbers = [int(n) for n in re.findall(r"\b(\d{1,2})(?:\.|-?go\b|\b)(?!:)", text) if 1 <= int(n) <= 31]
        numbers = [n for n in numbers if not re.search(rf"\b{n}[:.]\d\d\b", text)]
    words = _word_day_numbers(tokens)
    weekday = next((WEEKDAY_WORD[t] for t in tokens if t in WEEKDAY_WORD), None)
    has_next = any(t in NEXT_WORDS for t in tokens)
    has_last = any(t in LAST_WORDS for t in tokens)
    day_numbers = words or numbers

    if day is None and re.search(r"\b(tydzien|tygodniu|tygodnia)\b", text):
        ws = _week_start(call)
        if has_next:
            ws += dt.timedelta(days=7)
            basis.append("next calendar week")
        elif has_last:
            ws -= dt.timedelta(days=7)
            basis.append("previous calendar week")
        elif re.search(r"\bza tydzien\b", text):
            day = call + dt.timedelta(days=7)
            basis.append("one week after the call")
            ws = None
        elif day_numbers or weekday is not None:
            ws = None
        else:
            basis.append("week of the call")
        if ws and day is None:
            window = (ws, ws + dt.timedelta(days=4), ws + dt.timedelta(days=6))
    if day is None and window is None and re.search(r"\b(miesiac|miesiacu|miesiaca)\b", text):
        ms = call.replace(day=1)
        if has_next:
            ms = _add_months(ms, 1)
            basis.append("next calendar month")
        elif has_last:
            ms = _add_months(ms, -1)
            basis.append("previous calendar month")
        else:
            basis.append("month of the call")
        end = _month_end(ms)
        window = (ms, end, end)
    if day is None and window is None and re.search(r"\bpol roku\b", text):
        day = _add_months(call, 6)
        basis.append("six months after the call")
        approximate = True

    if day is None and window is None and day_numbers:
        if len(day_numbers) >= 2 and re.search(r"\bod\b.*\bdo\b", text):
            a = _day_in_context(day_numbers[0], month, call, past)
            b = _day_in_context(day_numbers[1], month, a or call, past)
            if a and b:
                if b < a:
                    b = _day_in_context(day_numbers[1], month, a, False)
                window = (a, b, b)
                basis.append("explicit day numbers")
                kind = "range" if kind in ("by", "on", None) else kind
        else:
            day = _day_in_context(day_numbers[0], month, call, past)
            if day:
                basis.append("explicit day of month" + (" and month" if month else ", nearest matching month"))
                if weekday is not None and day.weekday() != weekday:
                    flags.append(f"weekday mismatch: phrase says {WEEKDAY_PL[weekday]}, {day.isoformat()} is {WEEKDAY_PL[day.weekday()]}")
                elif weekday is not None:
                    basis.append(f"weekday {WEEKDAY_PL[weekday]} agrees with the day of month")
    if day is None and window is None and weekday is not None:
        if has_next and not past:
            day = _week_start(call) + dt.timedelta(days=7 + weekday)
            basis.append(f"'{WEEKDAY_PL[weekday]}' of the next calendar week")
            nearest = call + dt.timedelta(days=(weekday - call.weekday()) % 7 or 7)
            if nearest != day:
                flags.append(f"'next {WEEKDAY_PL[weekday]}' can also mean {nearest.isoformat()} in Polish usage")
        elif past or has_last:
            delta = (call.weekday() - weekday) % 7 or 7
            day = call - dt.timedelta(days=delta)
            basis.append(f"most recent {WEEKDAY_PL[weekday]} before the call")
        else:
            delta = (weekday - call.weekday()) % 7 or 7
            day = call + dt.timedelta(days=delta)
            basis.append(f"next {WEEKDAY_PL[weekday]} after the call")
    if day is None and window is None and month and not day_numbers:
        ms = dt.date(call.year, month, 1)
        if past and ms > call:
            ms = ms.replace(year=ms.year - 1)
        if not past and _month_end(ms) < call:
            ms = ms.replace(year=ms.year + 1)
        end = _month_end(ms)
        window = (ms, end, end)
        basis.append("named month")

    if day is None and window is None:
        return None

    if window:
        start, work_end, cal_end = window
        if kind == "not_before":
            res_start, res_end = cal_end + dt.timedelta(days=1), None
            if call < start:
                res_start = start
            basis.append("not before the end of that period" if call >= start else "not before its start")
        elif kind == "by":
            res_start, res_end = None, work_end
        else:
            res_start, res_end = start, work_end
            if not past and start < call <= work_end:
                res_start = call
                basis.append("starting on the call date")
            if kind not in ("range", "window", "past"):
                kind = "window"
    else:
        if kind == "by":
            res_start, res_end = None, day
        elif kind == "not_before":
            res_start, res_end = day, None
        else:
            res_start, res_end = day, day
    return {
        "kind": kind,
        "start": res_start.isoformat() if res_start else None,
        "end": res_end.isoformat() if res_end else None,
        "time": _hour(tokens, text),
        "basis": "; ".join(basis),
        "approximate": approximate,
        "flags": flags,
    }


def next_working_day(d: dt.date) -> dt.date:
    d += dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def pl_date(iso: str | None) -> str:
    if not iso:
        return ""
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {MONTH_GEN_PL[d.month - 1]}"


def pl_when(when: dict | None) -> str:
    if not when:
        return ""
    s, e, k = when.get("start"), when.get("end"), when.get("kind")
    t = f", godz. {when['time']}" if when.get("time") else ""
    if k == "by" and e:
        return f"do {pl_date(e)}"
    if k == "not_before" and s:
        return f"nie wcześniej niż {pl_date(s)}"
    if s and e and s != e:
        a, b = dt.date.fromisoformat(s), dt.date.fromisoformat(e)
        if a.month == b.month:
            return f"{a.day}-{b.day} {MONTH_GEN_PL[b.month - 1]}"
        return f"{pl_date(s)} - {pl_date(e)}"
    if s or e:
        d = dt.date.fromisoformat(s or e)
        return f"{WEEKDAY_PL[d.weekday()]}, {pl_date(s or e)}{t}"
    return ""
