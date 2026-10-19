import datetime as dt
import difflib
import re
import unicodedata

from . import dates
from .transcript import Transcript, fold

TYPES = ["bug", "config_change", "feature_request", "commitment", "follow_up", "billing", "constraint", "account_signal"]
STATES = ["open", "conditional", "pending_approval", "deferred", "blocked", "rejected", "active", "closed", "noted"]
KINDS = ["by", "on", "not_before", "range", "window", "past"]
ROLES = ["origin", "superseded", "revision", "final", "condition", "confirmation"]
KNOWN = ["new", "known_previous_call", "known_other_customers", "known_backlog"]
ACTIONABLE_ROLES = {"origin", "revision", "final", "condition", "confirmation"}

QUOTE_MAP = {"„": '"', "”": '"', "“": '"', "«": '"', "»": '"', "″": '"', "‚": "'", "‘": "'", "’": "'", "ʼ": "'",
             "–": "-", "—": "-", "‑": "-", "−": "-", "\u00a0": " "}


def _norm_map(text: str) -> tuple[str, list[int]]:
    out: list[str] = []
    idx: list[int] = []
    prev_space = True
    for i, ch in enumerate(unicodedata.normalize("NFC", text)):
        if ch == "…":
            for c in "...":
                out.append(c)
                idx.append(i)
            prev_space = False
            continue
        ch = QUOTE_MAP.get(ch, ch)
        if ch.isspace():
            if prev_space:
                continue
            ch = " "
            prev_space = True
        else:
            prev_space = False
        out.append(ch)
        idx.append(i)
    while out and out[-1] == " ":
        out.pop()
        idx.pop()
    return "".join(out), idx


def norm(text: str) -> str:
    return _norm_map(text)[0].strip()


class QuoteIndex:
    def __init__(self, t: Transcript):
        self.t = t
        self.turns = []
        for turn in t.turns:
            n, m = _norm_map(turn.text)
            self.turns.append((turn, n, m, n.lower()))

    def _same_speaker(self, a: str, b: str) -> bool:
        return bool(a and b) and fold(a.split()[0]) == fold(b.split()[0])

    def _find_parts(self, parts: list[str], hay: str, low: str) -> tuple[int, int, bool] | None:
        for haystack, needles, case in ((hay, parts, False), (low, [p.lower() for p in parts], True)):
            pos, first = 0, None
            ok = True
            for p in needles:
                j = haystack.find(p, pos)
                if j < 0:
                    ok = False
                    break
                first = j if first is None else first
                pos = j + len(p)
            if ok:
                return first, pos, case
        return None

    def locate(self, quote: str, speaker: str | None) -> dict:
        q = norm(quote or "").strip()
        if len(q) < 3:
            return {"status": "not_found", "reason": "empty quote"}
        variants = [q]
        trimmed = q.rstrip(".,;:!?\"' ").lstrip("\"' ")
        if trimmed and trimmed != q:
            variants.append(trimmed)
        ordered = sorted(self.turns, key=lambda x: not self._same_speaker(x[0].speaker, speaker or ""))
        for v in variants:
            parts = [p.strip() for p in v.split("...") if p.strip()]
            for turn, n, m, low in ordered:
                hit = self._find_parts(parts, n, low)
                if hit:
                    a, b, case = hit
                    verbatim = turn.text[m[a]:m[b - 1] + 1]
                    same = self._same_speaker(turn.speaker, speaker or "")
                    status = "verified" if same else "speaker_mismatch"
                    if same and (case or len(parts) > 1):
                        status = "verified_normalized"
                    return {"status": status, "line": turn.line, "turn": turn.index, "speaker": turn.speaker,
                            "verbatim": verbatim, "span": [m[a], m[b - 1] + 1]}
        best = (0.0, None)
        words_q = q.split()
        for turn, n, m, low in ordered:
            if not self._same_speaker(turn.speaker, speaker or ""):
                continue
            words = n.split(" ")
            offsets, pos = [], 0
            for w in words:
                offsets.append(pos)
                pos += len(w) + 1
            for size in range(max(1, len(words_q) - 2), len(words_q) + 3):
                for s in range(0, max(1, len(words) - size + 1)):
                    cand = " ".join(words[s:s + size])
                    r = difflib.SequenceMatcher(None, q.lower(), cand.lower()).ratio()
                    if r > best[0]:
                        a = offsets[s]
                        b = a + len(cand)
                        best = (r, (turn, a, b, m))
        if best[1] and best[0] >= 0.9:
            turn, a, b, m = best[1]
            return {"status": "repaired", "line": turn.line, "turn": turn.index, "speaker": turn.speaker,
                    "verbatim": turn.text[m[a]:m[b - 1] + 1], "span": [m[a], m[b - 1] + 1], "similarity": round(best[0], 3)}
        return {"status": "not_found", "similarity": round(best[0], 3)}

    def phrase_exists(self, phrase: str) -> dict | None:
        r = self.locate(phrase, None)
        return r if r["status"] != "not_found" else None


def _issue(item: dict, severity: str, code: str, msg: str) -> None:
    item.setdefault("issues", []).append({"severity": severity, "code": code, "message": msg})


def _enum(item: dict, field: str, value, allowed: list, default=None):
    if value not in allowed:
        _issue(item, "error", "schema", f"{field}={value!r} is not one of {allowed}")
        return default
    return value


def check_item(item: dict, qi: QuoteIndex, t: Transcript) -> dict:
    item["type"] = _enum(item, "type", item.get("type"), TYPES, item.get("type"))
    item["state"] = _enum(item, "state", item.get("state"), STATES, item.get("state"))
    owner = item.get("owner") or {}
    if owner.get("party") not in ("rinvo", "customer"):
        _issue(item, "error", "schema", f"owner.party={owner.get('party')!r} must be rinvo or customer")
    item["owner"] = {"party": owner.get("party"), "person": owner.get("person")}
    item["approvers"] = [a for a in (item.get("approvers") or []) if a]

    verified = 0
    for ev in item.get("evidence") or []:
        ev["role"] = _enum(item, "evidence.role", ev.get("role"), ROLES, "confirmation")
        loc = qi.locate(ev.get("quote", ""), ev.get("speaker"))
        ev["verification"] = loc["status"]
        if loc["status"] == "not_found":
            _issue(item, "error", "quote_not_found",
                   f"quote by {ev.get('speaker')} not found in the transcript (best similarity {loc.get('similarity')}): {ev.get('quote')!r}")
            continue
        if loc["status"] == "speaker_mismatch":
            _issue(item, "warn", "speaker_mismatch",
                   f"quote attributed to {ev.get('speaker')} was said by {loc['speaker']} (line {loc['line']}); speaker corrected")
            ev["speaker_claimed"] = ev.get("speaker")
            ev["speaker"] = loc["speaker"]
        if loc["status"] == "repaired":
            _issue(item, "warn", "quote_repaired",
                   f"quote was not verbatim (similarity {loc['similarity']}); replaced with the transcript text")
            ev["quote_claimed"] = ev.get("quote")
            ev["quote"] = loc["verbatim"]
        if ev.get("line") != loc["line"]:
            if ev.get("line") is not None:
                ev["line_claimed"] = ev.get("line")
            ev["line"] = loc["line"]
        ev["turn"] = loc["turn"]
        ev["span"] = loc["span"]
        verified += 1
    item["evidence_verified"] = verified
    if not item.get("evidence"):
        _issue(item, "error", "no_evidence", "item has no evidence")
    elif verified == 0:
        _issue(item, "error", "unverified", "no quote of this item could be verified; item is quarantined")
    item["quarantined"] = verified == 0
    item["evidence"] = sorted(item.get("evidence") or [], key=lambda e: (e.get("line") or 10**6, (e.get("span") or [0])[0]))

    good = [e for e in item["evidence"] if e.get("verification") != "not_found"]
    if good:
        last = good[-1]
        if last["role"] == "superseded":
            _issue(item, "error", "final_is_superseded",
                   f"the latest quote (line {last['line']}) is marked superseded, so the final state may be outdated")
        sup = [e for e in good if e["role"] == "superseded"]
        rev = [e for e in good if e["role"] in ("revision", "final")]
        if sup and not item.get("revised"):
            item["revised"] = True
            _issue(item, "info", "revised_inferred", "a superseded quote is cited, so the item is marked revised")
        if item.get("revised"):
            if not sup:
                _issue(item, "warn", "revision_without_superseded", "revised=true but no superseded quote is cited")
            elif not rev or max(e["line"] for e in rev) < min(e["line"] for e in sup):
                _issue(item, "error", "revision_order", "the revising quote comes before the superseded one")

    state = item["state"]
    if state in ("conditional", "deferred", "blocked") and not item.get("condition"):
        _issue(item, "error", "missing_condition", f"state {state} requires a condition")
    if state == "pending_approval" and not item["approvers"]:
        _issue(item, "error", "missing_approver", "pending_approval requires approvers")
    if item["type"] == "follow_up":
        if not item.get("condition"):
            _issue(item, "error", "missing_condition", "follow_up requires a trigger condition")
        if not (item.get("limit") or {}).get("max_count"):
            _issue(item, "warn", "missing_limit", "follow_up has no max_count; the reminder count is unbounded")
    if item["type"] == "account_signal" and item.get("customer_visible"):
        item["customer_visible"] = False
        _issue(item, "info", "forced_internal", "account signals are never customer visible")
    if item["type"] == "constraint" and state not in ("active", "closed", "rejected"):
        _issue(item, "warn", "constraint_state", f"constraint in state {state}")

    for role, name in (("owner", owner.get("person")),) + tuple(("approver", a) for a in item["approvers"]):
        if not name:
            continue
        p = t.person(name)
        if p is None:
            _issue(item, "warn", "unknown_person", f"{role} {name!r} is not a participant or a mentioned person")
        elif not p.present:
            code = "absent_owner" if role == "owner" else "absent_approver"
            _issue(item, "warn" if role == "owner" else "info", code,
                   f"{role} {p.name} was not on the call" + ("; the commitment was made on their behalf and needs their confirmation" if role == "owner" else ""))

    cond = item.get("condition")
    if cond and cond.get("phrase"):
        if not qi.phrase_exists(cond["phrase"]):
            _issue(item, "warn", "condition_phrase_not_found", f"condition phrase not in transcript: {cond['phrase']!r}")

    _resolve_when(item, qi, t)
    _check_claims(item, t)
    for field in ("recap_pl", "draft_pl"):
        txt = item.get(field)
        if txt and re.search(r"[–—]", txt):
            item[field] = re.sub(r"\s*[–—]\s*", ", ", txt)
            _issue(item, "info", "dash_removed", f"{field}: dashes used as punctuation were replaced")
    k = item.get("known") or {}
    if k.get("status") not in KNOWN:
        item["known"] = {"status": "new", "basis": k.get("basis", "")}
    return item


def _resolve_when(item: dict, qi: QuoteIndex, t: Transcript) -> None:
    w = item.get("when")
    if not w:
        item["when"] = None
        return
    kind = w.get("kind")
    if kind not in KINDS:
        _issue(item, "warn", "schema", f"when.kind={kind!r} unknown; treated as 'by'")
        kind = "by"
    phrase = w.get("phrase") or ""
    model = {"start": w.get("model_start"), "end": w.get("model_end")}
    out = {"kind": kind, "phrase": phrase, "start": None, "end": None, "time": w.get("time"),
           "resolution": None, "basis": "", "model": model}
    if phrase and not qi.phrase_exists(phrase):
        _issue(item, "warn", "date_phrase_not_found", f"date phrase not in transcript: {phrase!r}")
    r = dates.resolve(phrase, t.call_date, kind, w.get("tense")) if t.call_date else None
    if r:
        out.update({"kind": r["kind"], "start": r["start"], "end": r["end"], "time": r["time"] or w.get("time"),
                    "basis": r["basis"], "resolution": "rule", "approximate": r["approximate"]})
        for f in r["flags"]:
            _issue(item, "warn", "date_flag", f)
        ms, me = model.get("start"), model.get("end")
        if (ms or me) and ((ms and ms != r["start"] and ms != r["end"]) or (me and me != r["end"] and me != r["start"])):
            out["resolution"] = "conflict"
            _issue(item, "warn", "date_conflict",
                   f"rule resolved {phrase!r} to {r['start']}..{r['end']}, model said {ms}..{me}; rule value kept, needs review")
    elif model.get("start") or model.get("end"):
        out.update({"start": model.get("start"), "end": model.get("end"), "resolution": "model",
                    "basis": "model resolution; the phrase carries no date the rules can read"})
        _issue(item, "info", "date_from_model", f"date for {phrase!r} comes from the model, not from a rule")
    else:
        out["resolution"] = "unresolved"
        _issue(item, "warn", "date_unresolved", f"no calendar date for {phrase!r}")
    for key in ("start", "end"):
        v = out.get(key)
        if v:
            try:
                dt.date.fromisoformat(v)
            except ValueError:
                _issue(item, "error", "schema", f"when.{key}={v!r} is not an ISO date")
                out[key] = None
    item["when"] = out


def _check_claims(item: dict, t: Transcript) -> None:
    checked = []
    for c in item.get("claims") or []:
        src = c.get("source") or "other"
        res = {"text": c.get("text"), "source": src, "quote": c.get("quote")}
        if src == "calendar" and t.call_date:
            r = dates.resolve(c.get("quote") or c.get("text") or "", t.call_date, "on", None)
            if r and r["flags"]:
                res["check"] = "mismatch"
                res["detail"] = "; ".join(r["flags"])
                _issue(item, "warn", "claim_mismatch", f"calendar claim does not hold: {res['detail']}")
            elif r:
                res["check"] = "consistent"
                res["detail"] = f"{r['start']} ({r['basis']})"
            else:
                res["check"] = "not_checked"
                res["detail"] = "no date found in the claim"
        else:
            res["check"] = "not_checked"
            res["detail"] = f"needs {src} data; none was provided"
        checked.append(res)
    item["claims"] = checked


def cross_checks(items: list[dict]) -> list[dict]:
    notes = []
    windows = [(it, it["when"]) for it in items if it["type"] == "constraint" and it.get("when")
               and it["when"].get("start") and it["when"].get("end") and it["when"]["kind"] in ("range", "window")]
    for it in items:
        if it["type"] not in ("config_change", "follow_up", "commitment") or it["owner"].get("party") != "rinvo":
            continue
        w = it.get("when") or {}
        for c, cw in windows:
            for key in ("start", "end"):
                d = w.get(key)
                if d and cw["start"] <= d <= cw["end"]:
                    msg = f"{key} date {d} falls inside constraint {c['id']} ({c['title']}, {cw['start']}..{cw['end']})"
                    _issue(it, "warn", "inside_constraint_window", msg)
                    notes.append({"item": it["id"], "constraint": c["id"], "message": msg})
                    break

    def spans(it):
        return [(e["line"], e["span"][0], e["span"][1]) for e in it["evidence"]
                if e.get("span") and e.get("role") not in ("confirmation", "superseded")]

    for n, a in enumerate(items):
        sa = spans(a)
        for b in items[n + 1:]:
            if a["type"] != b["type"]:
                continue
            sb = spans(b)
            inter = sum(max(0, min(x2, y2) - max(x1, y1)) for (la, x1, x2) in sa for (lb, y1, y2) in sb if la == lb)
            total = min(sum(x2 - x1 for _, x1, x2 in sa), sum(y2 - y1 for _, y1, y2 in sb))
            if total and inter / total >= 0.5:
                _issue(b, "warn", "possible_duplicate", f"most of its evidence is also cited by {a['id']} with the same type")
                notes.append({"item": b["id"], "other": a["id"], "message": "possible duplicate"})
    return notes
