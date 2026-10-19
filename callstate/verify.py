import re
import unicodedata

from . import dates
from .schema import TYPES
from .transcript import Transcript, fold

QUOTE_MAP = {"„": '"', "”": '"', "“": '"', "«": '"', "»": '"', "″": '"', "‚": "'", "‘": "'", "’": "'", "ʼ": "'",
             "–": "-", "—": "-", "‑": "-", "−": "-", "\u00a0": " ", "…": "..."}
HOLD_STATES = ("deferred", "pending_approval", "blocked")
APPROVAL_TYPES = ("config_change", "feature_request", "billing", "commitment")
APPROVAL_STATES = ("pending_approval", "deferred")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = "".join(QUOTE_MAP.get(c, c) for c in text)
    text = text.replace("**", "").replace("*", "")
    return re.sub(r"\s+", " ", text).strip()


def _same(a: str, b: str) -> bool:
    return bool(a and b) and fold(a.split()[0]) == fold(b.split()[0])


class QuoteIndex:
    def __init__(self, t: Transcript):
        self.t = t
        self.lines: dict[int, tuple[str, str, str]] = {}
        turn_lines = {tu.line: tu for tu in t.turns}
        for n, raw in enumerate(t.lines, start=1):
            if n in turn_lines:
                tu = turn_lines[n]
                self.lines[n] = (tu.speaker, tu.text, norm(tu.text))
            elif raw.strip() and (not t.turns or n < t.turns[0].line):
                text = re.sub(r"^[#\-\s]+", "", raw)
                self.lines[n] = ("context", text, norm(text))

    def check(self, ev: dict) -> str:
        q = norm(ev.get("quote", ""))
        if len(q) < 3:
            return "empty quote"
        entry = self.lines.get(ev.get("line"))
        if not entry:
            return f"line {ev.get('line')} has no text"
        speaker, _, text = entry
        if not (_same(speaker, ev.get("speaker", "")) or (speaker == "context" and fold(ev.get("speaker", "")) == "context")):
            return f"line {ev['line']} is said by {speaker}, not {ev.get('speaker')}"
        parts = [p.strip() for p in q.split("...") if p.strip()]
        pos = 0
        for p in parts:
            j = text.find(p, pos)
            if j < 0:
                return f"quote not found on line {ev['line']} ({speaker}): {ev.get('quote')!r}"
            pos = j + len(p)
        return ""

    def span(self, ev: dict) -> list[int] | None:
        entry = self.lines.get(ev.get("line"))
        if not entry:
            return None
        q = norm(ev["quote"]).split("...")[0].strip()
        j = entry[2].find(q)
        return [j, j + len(norm(ev["quote"]))] if j >= 0 else None

    def phrase_on_any_line(self, phrase: str) -> bool:
        p = norm(phrase)
        return bool(p) and any(p.lower() in v[2].lower() for v in self.lines.values())


def check_evidence(evs: list, qi: QuoteIndex, where: str) -> list[str]:
    errs = []
    if not evs:
        errs.append(f"{where}: no evidence")
    for e in evs:
        msg = qi.check(e)
        if msg:
            errs.append(f"{where}: {msg}")
        else:
            e["span"] = qi.span(e)
    return errs


def semantic_errors(raw: dict, qi: QuoteIndex) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    acc = raw["account"]
    keys = {a["key"] for a in acc["authority"]}
    ids = {it["local_id"] for it in raw["items"]}
    for kind in ("people", "authority", "facts"):
        for n, e in enumerate(acc[kind]):
            errs = check_evidence(e["evidence"], qi, f"account.{kind}[{n}]")
            if errs:
                out[f"account.{kind}[{n}]"] = errs
    seen = set()
    for it in raw["items"]:
        lid = it["local_id"]
        errs = check_evidence(it["evidence"], qi, lid)
        if lid in seen:
            errs.append(f"{lid}: duplicate local_id")
        seen.add(lid)
        st, ty = it["state"], it["type"]
        if st in ("conditional", "deferred", "blocked") and not it["condition"]["text"]:
            errs.append(f"{lid}: state {st} needs condition.text")
        if st == "pending_approval" and not it["authority_keys"]:
            errs.append(f"{lid}: pending_approval needs authority_keys")
        for k in it["authority_keys"]:
            if k not in keys:
                errs.append(f"{lid}: authority key {k!r} is not in account.authority")
        if ty == "follow_up":
            if it["watches"] not in ids:
                errs.append(f"{lid}: follow_up must watch an existing local_id, got {it['watches']!r}")
            if it["max_count"] < 1:
                errs.append(f"{lid}: follow_up needs max_count >= 1")
            if it["when"]["kind"] == "none":
                errs.append(f"{lid}: follow_up needs the deadline it watches in when")
        if ty == "constraint" and st not in ("active", "closed", "rejected"):
            errs.append(f"{lid}: constraint state must be active, closed or rejected, got {st}")
        if ty == "account_signal" and it["customer_visible"]:
            errs.append(f"{lid}: account_signal cannot be customer_visible")
        if (st in HOLD_STATES or ty == "constraint") and not it["keywords"]:
            errs.append(f"{lid}: holds and constraints need keywords")
        if it["when"]["kind"] != "none" and not it["when"]["phrase"]:
            errs.append(f"{lid}: when.kind is set but when.phrase is empty")
        if it["when"]["anchor"] and it["when"]["anchor"] not in ids:
            errs.append(f"{lid}: when.anchor {it['when']['anchor']!r} is not a local_id")
        for r in it["related"] + it["brief_for"]:
            if r not in ids:
                errs.append(f"{lid}: reference {r!r} is not a local_id")
        sup = [e for e in it["evidence"] if e["role"] == "superseded"]
        later = [e for e in it["evidence"] if e["role"] in ("revision", "final")]
        if it["revised"] and not sup:
            errs.append(f"{lid}: revised=true needs a superseded quote")
        if sup and later and max(e["line"] for e in later) < min(e["line"] for e in sup):
            errs.append(f"{lid}: the revising quote comes before the superseded one")
        if sup and not it["revised"]:
            errs.append(f"{lid}: cites a superseded quote but revised=false")
        for c in it["claims"]:
            msg = qi.check({"speaker": qi.lines.get(c["line"], ("", "", ""))[0], "line": c["line"], "quote": c["quote"]})
            if msg:
                errs.append(f"{lid}: claim {c['text']!r}: {msg}")
        if errs:
            out[lid] = errs
    return out


def _resolve(w: dict, call, items_by_lid: dict, qi: QuoteIndex, issues: list, allow_anchor: bool = True) -> dict | None:
    if w["kind"] == "none":
        return None
    out = {"kind": w["kind"], "phrase": w["phrase"], "start": None, "end": None, "time": None, "resolution": "unresolved", "basis": ""}
    if w["phrase"] and not qi.phrase_on_any_line(w["phrase"]):
        issues.append({"severity": "warn", "code": "date_phrase_not_found", "message": f"date phrase not in the text: {w['phrase']!r}"})
    r = dates.resolve(w["phrase"], call, w["kind"], w["tense"])
    if r:
        out.update({k: r[k] for k in ("kind", "start", "end", "time", "basis")}, resolution="rule")
        for f in r["flags"]:
            issues.append({"severity": "warn", "code": "date_flag", "message": f})
    elif allow_anchor and w["anchor"] and w["anchor"] in items_by_lid:
        aw = items_by_lid[w["anchor"]].get("when")
        if aw and (aw.get("start") or aw.get("end")):
            out.update({"start": aw["start"], "end": aw["end"], "resolution": "anchor", "basis": f"same date as {items_by_lid[w['anchor']]['id']}"})
    elif w["anchor"]:
        return None
    if out["resolution"] == "unresolved":
        issues.append({"severity": "warn", "code": "date_unresolved", "message": f"no calendar date for {w['phrase']!r}"})
    return out


def _first(t: Transcript, name: str) -> str:
    p = t.person(name)
    return p.first if p else (name.split()[0] if name else name)


def normalize(raw: dict, t: Transcript, qi: QuoteIndex, quarantine: dict[str, list[str]], call_id: str) -> tuple[dict, list[dict]]:
    acc = raw["account"]
    auth = {a["key"]: a for a in acc["authority"]}
    rinvo = raw["call"]["rinvo_contact"]
    by_lid: dict[str, dict] = {}
    items = []
    for n, it in enumerate(raw["items"], start=1):
        lid = it["local_id"]
        x = {
            "id": f"{call_id}/I{n:02d}", "local_id": lid, "call": call_id, "type": it["type"], "state": it["state"],
            "title": it["title"], "owner": {"party": it["owner_party"], "person": it["owner_person"] or None},
            "assignee": _first(t, it["owner_person"] if it["owner_party"] == "rinvo" and it["owner_person"] else rinvo),
            "action": it["action"], "condition": it["condition"] if it["condition"]["text"] else None,
            "authority_keys": it["authority_keys"],
            "approvers": sorted({p for k in it["authority_keys"] for p in auth.get(k, {}).get("approvers", [])})
                         if it["type"] in APPROVAL_TYPES and it["state"] in APPROVAL_STATES else [],
            "if_others_ask": it["if_others_ask"], "keywords": it["keywords"], "launch": it["launch"], "freeze": it["freeze"],
            "limit": {"max_count": it["max_count"], "channel": it["channel"]} if it["max_count"] else None,
            "value": {"target": it["target"], "current": it["current_value"], "requested": it["new_value"]}
                     if (it["target"] or it["current_value"] or it["new_value"]) else None,
            "success_metric": it["success_metric"], "no_deadline_promised": it["no_deadline_promised"],
            "evidence": it["evidence"], "revised": it["revised"],
            "known": {"status": it["known"], "basis": it["known_basis"]}, "customer_visible": it["customer_visible"],
            "claims": it["claims"], "ambiguities": it["ambiguities"], "previous_id": it["previous_id"] or None,
            "recap_pl": it["recap_pl"], "message": it["message"] if it["message"]["body_pl"] else None,
            "issues": [], "quarantined": lid in quarantine, "quarantine_reasons": quarantine.get(lid, []),
            "_when": it["when"], "_related": it["related"], "_brief_for": it["brief_for"], "_watches": it["watches"],
        }
        by_lid[lid] = x
        items.append(x)
    for _ in range(2):
        for x in items:
            if x.get("when") is None or x["when"].get("resolution") == "unresolved":
                issues: list = []
                x["when"] = _resolve(x["_when"], t.call_date, by_lid, qi, issues, allow_anchor=x["state"] != "conditional")
                x["_date_issues"] = issues
    for x in items:
        x["issues"] += x.pop("_date_issues", [])
        x["related"] = [by_lid[r]["id"] for r in x.pop("_related") if r in by_lid]
        x["brief_for"] = [by_lid[r]["id"] for r in x.pop("_brief_for") if r in by_lid]
        w = x.pop("_watches")
        x["watches"] = by_lid[w]["id"] if w in by_lid else None
        x.pop("_when")
        for c in x["claims"]:
            r = dates.resolve(c["time_phrase"], t.call_date, "past", "past") if c["time_phrase"] else None
            c["date"] = r["start"] if r else None
        if x["message"]:
            p = t.person(x["message"]["to"])
            x["message"]["to_email"] = p.email if p else None
        for k in x["authority_keys"]:
            for p in auth.get(k, {}).get("approvers", []):
                person = t.person(p)
                if person and not person.present:
                    x["issues"].append({"severity": "info", "code": "absent_approver", "message": f"needs {p}, who was not on the call"})
        if x["owner"]["person"]:
            person = t.person(x["owner"]["person"])
            if person and not person.present:
                x["issues"].append({"severity": "warn", "code": "handoff", "message": f"owner {person.name} was not on the call: this is a handoff that needs their confirmation"})
        for f in ("recap_pl",):
            if re.search(r"[–—]", x[f] or ""):
                x["issues"].append({"severity": "warn", "code": "dash", "message": f"{f} uses a dash as punctuation"})
        if x["message"] and re.search(r"[–—]", x["message"]["body_pl"]):
            x["issues"].append({"severity": "warn", "code": "dash", "message": "message body uses a dash as punctuation"})
    return acc, items


def cross_checks(items: list[dict]) -> None:
    freezes = [c for c in items if c["type"] == "constraint" and c["freeze"] and c["state"] == "active"
               and c.get("when") and c["when"].get("start") and c["when"].get("end")]
    for it in items:
        if not it["launch"]:
            continue
        w = it.get("when") or {}
        for c in freezes:
            for key in ("start", "end"):
                d = w.get(key)
                if d and c["when"]["start"] <= d <= c["when"]["end"]:
                    it["issues"].append({"severity": "warn", "code": "constraint_conflict",
                                         "message": f"{key} {d} falls inside freeze {c['id']} ({c['when']['start']}..{c['when']['end']})"})
                    break
    for n, a in enumerate(items):
        sa = [(e["line"], *e["span"]) for e in a["evidence"] if e.get("span") and e["role"] == "origin"]
        for b in items[n + 1:]:
            if a["type"] != b["type"]:
                continue
            sb = [(e["line"], *e["span"]) for e in b["evidence"] if e.get("span") and e["role"] == "origin"]
            inter = sum(max(0, min(x2, y2) - max(x1, y1)) for (la, x1, x2) in sa for (lb, y1, y2) in sb if la == lb)
            total = min(sum(x2 - x1 for _, x1, x2 in sa), sum(y2 - y1 for _, y1, y2 in sb))
            if total and inter / total >= 0.5:
                b["issues"].append({"severity": "warn", "code": "possible_duplicate", "message": f"most of its evidence is also cited by {a['id']}"})


__all__ = ["QuoteIndex", "semantic_errors", "normalize", "cross_checks", "TYPES"]
