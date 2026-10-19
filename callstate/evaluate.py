import json
from pathlib import Path

from .schema import TYPES
from .transcript import fold, load
from .verify import QuoteIndex

FIELDS = ["state", "owner", "date", "condition", "approvers", "limit"]


def _spans(item: dict, qi: QuoteIndex) -> list[tuple[int, int, int]]:
    out = []
    for e in item.get("evidence") or []:
        sp = qi.span(e)
        if sp and sp[0] >= 0:
            out.append((e["line"], sp[0], sp[1]))
    return out


def _overlap(a: list, b: list) -> float:
    inter = sum(max(0, min(x2, y2) - max(x1, y1)) for (la, x1, x2) in a for (lb, y1, y2) in b if la == lb)
    total = min(sum(x2 - x1 for _, x1, x2 in a), sum(y2 - y1 for _, y1, y2 in b))
    return inter / total if total else 0.0


def _dates(w: dict | None) -> set:
    return {d for d in ((w or {}).get("start"), (w or {}).get("end")) if d}


def _names(xs) -> set:
    return {fold(x.split()[-1] if x.lower().startswith(("pan ", "pani ")) else x.split()[0]) for x in xs or [] if x}


def compare(g: dict, p: dict) -> dict:
    go, po = g.get("owner") or {}, p.get("owner") or {}
    gl, pl = (g.get("limit") or {}).get("max_count"), (p.get("limit") or {}).get("max_count")
    return {
        "state": g["state"] == p["state"] or p["state"] in g.get("alt_states", []),
        "owner": go.get("party") == po.get("party") and (not go.get("person") or _names([go["person"]]) == _names([po.get("person")])),
        "date": _dates(g.get("when")) == _dates(p.get("when")),
        "condition": bool(g.get("condition")) == bool(p.get("condition")),
        "approvers": _names(g.get("approvers")) == _names(p.get("approvers")),
        "limit": gl == pl if gl else True,
        "revised": bool(g.get("revised")) == bool(p.get("revised")),
        "known": (g.get("known") or {}).get("status", "new") == (p.get("known") or {}).get("status", "new"),
    }


def match(gold: list[dict], pred: list[dict], qi: QuoteIndex) -> list[tuple[dict, dict, float]]:
    gs = [(g, _spans(g, qi)) for g in gold]
    ps = [(p, _spans(p, qi)) for p in pred]
    pairs = []
    for g, gsp in gs:
        for p, psp in ps:
            ov = _overlap(gsp, psp)
            if ov >= 0.2:
                bonus = 0.25 if g["type"] == p["type"] else 0.15 if p["type"] in g.get("alt_types", []) else 0.0
                pairs.append((ov + bonus, ov, g, p))
    pairs.sort(key=lambda x: -x[0])
    used_g, used_p, out = set(), set(), []
    for _, ov, g, p in pairs:
        if g["id"] in used_g or p["id"] in used_p:
            continue
        used_g.add(g["id"])
        used_p.add(p["id"])
        out.append((g, p, round(ov, 3)))
    return out


def _pr(tp: int, npred: int, ngold: int) -> tuple:
    p = tp / npred if npred else None
    r = tp / ngold if ngold else None
    return p, r


def evaluate(gold_path: str, pred_path: str) -> dict:
    gold = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    pred = json.loads(Path(pred_path).read_text(encoding="utf-8"))
    qi = QuoteIndex(load(gold["call"]["transcript"]))
    pitems = [p for p in pred["items"] if not p.get("quarantined")]
    pairs = match(gold["items"], pitems, qi)
    tol_type = {p["id"]: p["type"] for p in pitems}
    tol_type.update({p["id"]: g["type"] for g, p, _ in pairs if p["type"] in g.get("alt_types", [])})
    rows = {}
    for ty in TYPES + ["all"]:
        gi = [g for g in gold["items"] if ty in ("all", g["type"])]
        strict = [(g, p) for g, p, _ in pairs if ty in ("all", g["type"]) and g["type"] == p["type"]]
        tolerant = [(g, p) for g, p, _ in pairs if ty in ("all", g["type"]) and (g["type"] == p["type"] or p["type"] in g.get("alt_types", []))]
        np_strict = sum(1 for p in pitems if ty in ("all", p["type"]))
        np_tol = sum(1 for p in pitems if ty in ("all", tol_type[p["id"]]))
        alt_credit = [(g, p) for g, p in tolerant if g["type"] != p["type"]]
        full_s = sum(all(compare(g, p)[f] for f in FIELDS) for g, p in strict)
        full_t = sum(all(compare(g, p)[f] for f in FIELDS) for g, p in tolerant)
        rows[ty] = {"gold": len(gi), "pred": np_strict,
                    "strict": dict(zip(("precision", "recall"), _pr(len(strict), np_strict, len(gi))), tp=len(strict)),
                    "tolerant": dict(zip(("precision", "recall"), _pr(len(tolerant), np_tol, len(gi))), tp=len(tolerant),
                                     via_alt_type=len(alt_credit)),
                    "state_strict": dict(zip(("precision", "recall"), _pr(full_s, np_strict, len(gi))), tp=full_s),
                    "state_tolerant": dict(zip(("precision", "recall"), _pr(full_t, np_tol, len(gi))), tp=full_t)}
    tol_pairs = [(g, p) for g, p, _ in pairs if g["type"] == p["type"] or p["type"] in g.get("alt_types", [])]
    fields = {f: {"correct": sum(compare(g, p)[f] for g, p in tol_pairs), "of": len(tol_pairs)} for f in FIELDS + ["revised", "known"]}
    matched_g = {g["id"] for g, _, _ in pairs}
    matched_p = {p["id"] for _, p, _ in pairs}
    errors = [{"kind": "missed", "gold": g["id"], "type": g["type"], "title": g["title"]} for g in gold["items"] if g["id"] not in matched_g]
    errors += [{"kind": "invented", "pred": p["id"], "type": p["type"], "title": p["title"]} for p in pitems if p["id"] not in matched_p]
    for g, p, ov in pairs:
        if g["type"] != p["type"]:
            errors.append({"kind": "alt_type" if p["type"] in g.get("alt_types", []) else "wrong_type", "gold": g["id"], "pred": p["id"],
                           "title": g["title"], "expected": g["type"], "got": p["type"]})
        c = compare(g, p)
        for f in FIELDS + ["revised", "known"]:
            if not c[f]:
                errors.append({"kind": f"wrong_{f}", "gold": g["id"], "pred": p["id"], "title": g["title"], "expected": _show(g, f), "got": _show(p, f)})
    return {"gold": gold_path, "pred": pred_path, "quarantined": sum(1 for p in pred["items"] if p.get("quarantined")),
            "per_type": rows, "fields": fields, "errors": errors,
            "pairs": [{"gold": g["id"], "pred": p["id"], "overlap": ov, "gold_title": g["title"], "pred_title": p["title"]} for g, p, ov in pairs]}


def _show(it: dict, f: str):
    if f == "owner":
        return it.get("owner")
    if f == "date":
        w = it.get("when") or {}
        return {"kind": w.get("kind"), "start": w.get("start"), "end": w.get("end")} if w else None
    if f == "condition":
        return (it.get("condition") or {}).get("text")
    if f == "limit":
        return (it.get("limit") or {}).get("max_count")
    if f == "known":
        return (it.get("known") or {}).get("status")
    return it.get(f)


def _f(x):
    return "n/a" if x is None else f"{x:.2f}"


def to_markdown(m: dict) -> str:
    out = ["# Metrics", "", f"Gold: `{m['gold']}`  ", f"Prediction: `{m['pred']}` ({m['quarantined']} quarantined items excluded)", "",
           "Found = cites overlapping transcript spans and has the gold type (strict) or a type listed as an acceptable alternative in "
           "`annotation/notes.md` (tolerant). State-correct additionally requires state, owner, date, condition presence, approvers "
           "and reminder count to match.", "",
           "| Type | Gold | Pred | Strict P | Strict R | Tolerant P | Tolerant R | via alt type | State-correct strict P / R | State-correct tolerant P / R |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for ty, r in m["per_type"].items():
        s, t, ss, st = r["strict"], r["tolerant"], r["state_strict"], r["state_tolerant"]
        out.append(f"| {ty} | {r['gold']} | {r['pred']} | {_f(s['precision'])} | {_f(s['recall'])} | {_f(t['precision'])} | {_f(t['recall'])} | "
                   f"{t['via_alt_type']} | {_f(ss['precision'])} / {_f(ss['recall'])} | {_f(st['precision'])} / {_f(st['recall'])} |")
    out += ["", "| Field (tolerant matches) | Correct |", "|---|---|"] + [f"| {f} | {v['correct']}/{v['of']} |" for f, v in m["fields"].items()]
    out += ["", "## Errors", ""]
    for e in m["errors"]:
        ids = " / ".join(x for x in (e.get("gold"), e.get("pred")) if x)
        detail = f" expected {e['expected']!r}, got {e['got']!r}" if "expected" in e else ""
        out.append(f"- {e['kind']} [{ids}] {e['title']}.{detail}")
    out += ["", "## Matches", ""] + [f"- {p['gold']} ↔ {p['pred']} ({p['overlap']}): {p['gold_title']} / {p['pred_title']}" for p in m["pairs"]]
    return "\n".join(out) + "\n"
