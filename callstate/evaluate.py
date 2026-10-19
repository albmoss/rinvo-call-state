import json
from pathlib import Path

from .transcript import fold, load
from .verify import TYPES, QuoteIndex

FIELDS = ["state", "owner", "date", "condition", "approvers", "limit"]


def _spans(item: dict, qi: QuoteIndex | None) -> list[tuple[int, int, int]]:
    out = []
    for e in item.get("evidence") or []:
        if e.get("verification") == "not_found":
            continue
        span, line = e.get("span"), e.get("line")
        if not span and qi is not None:
            loc = qi.locate(e["quote"], e.get("speaker"))
            if loc["status"] == "not_found":
                continue
            span, line = loc["span"], loc["line"]
        if span:
            out.append((line, span[0], span[1]))
    return out


def _overlap(a: list, b: list) -> float:
    inter = sum(max(0, min(x2, y2) - max(x1, y1)) for (la, x1, x2) in a for (lb, y1, y2) in b if la == lb)
    total = min(sum(x2 - x1 for _, x1, x2 in a), sum(y2 - y1 for _, y1, y2 in b))
    return inter / total if total else 0.0


def _dates(w: dict | None) -> set:
    if not w:
        return set()
    return {d for d in (w.get("start"), w.get("end")) if d}


def _names(xs) -> set:
    return {fold(x.split()[-1] if x.lower().startswith(("pan ", "pani ")) else x.split()[0]) for x in xs or [] if x}


def compare(g: dict, p: dict) -> dict:
    res = {}
    res["state"] = g["state"] == p["state"]
    go, po = g.get("owner") or {}, p.get("owner") or {}
    res["owner"] = go.get("party") == po.get("party") and (not go.get("person") or _names([go["person"]]) == _names([po.get("person")]))
    res["date"] = _dates(g.get("when")) == _dates(p.get("when"))
    res["condition"] = bool(g.get("condition")) == bool(p.get("condition"))
    res["approvers"] = _names(g.get("approvers")) == _names(p.get("approvers"))
    gl, pl = (g.get("limit") or {}).get("max_count"), (p.get("limit") or {}).get("max_count")
    res["limit"] = gl == pl if gl else True
    res["revised"] = bool(g.get("revised")) == bool(p.get("revised"))
    res["known"] = (g.get("known") or {}).get("status", "new") == (p.get("known") or {}).get("status", "new")
    return res


def match(gold: list[dict], pred: list[dict], qi: QuoteIndex) -> list[tuple[dict, dict, float]]:
    gs = [(g, _spans(g, qi)) for g in gold]
    ps = [(p, _spans(p, None)) for p in pred if not p.get("quarantined")]
    pairs = []
    for g, gsp in gs:
        for p, psp in ps:
            ov = _overlap(gsp, psp)
            if ov >= 0.2:
                pairs.append((ov + (0.25 if g["type"] == p["type"] else 0.0), ov, g, p))
    pairs.sort(key=lambda x: -x[0])
    used_g, used_p, out = set(), set(), []
    for score, ov, g, p in pairs:
        if g["id"] in used_g or p["id"] in used_p:
            continue
        used_g.add(g["id"])
        used_p.add(p["id"])
        out.append((g, p, round(ov, 3)))
    return out


def _pr(tp: int, fp: int, fn: int) -> tuple:
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
    return p, r, f


def evaluate(gold_path: str, pred_path: str) -> dict:
    gold = json.loads(Path(gold_path).read_text(encoding="utf-8"))
    pred = json.loads(Path(pred_path).read_text(encoding="utf-8"))
    t = load(gold["call"]["transcript"]) if Path(gold["call"]["transcript"]).exists() else load(pred["call"]["transcript"])
    qi = QuoteIndex(t)
    pitems = [p for p in pred["items"] if not p.get("quarantined")]
    pairs = match(gold["items"], pitems, qi)
    matched_g = {g["id"] for g, _, _ in pairs}
    matched_p = {p["id"] for _, p, _ in pairs}
    rows = {}
    for ty in TYPES + ["all"]:
        gi = [g for g in gold["items"] if ty == "all" or g["type"] == ty]
        pi = [p for p in pitems if ty == "all" or p["type"] == ty]
        tp_pairs = [(g, p) for g, p, _ in pairs if (ty == "all" or g["type"] == ty) and g["type"] == p["type"]]
        tp = len(tp_pairs)
        full = sum(all(compare(g, p)[f] for f in FIELDS) for g, p in tp_pairs)
        det = _pr(tp, len(pi) - tp, len(gi) - tp)
        st = _pr(full, len(pi) - full, len(gi) - full)
        rows[ty] = {"gold": len(gi), "pred": len(pi), "tp": tp, "precision": det[0], "recall": det[1], "f1": det[2],
                    "state_correct": full, "state_precision": st[0], "state_recall": st[1]}
    field_acc = {}
    same_type = [(g, p) for g, p, _ in pairs if g["type"] == p["type"]]
    for f in FIELDS + ["revised", "known"]:
        ok = sum(compare(g, p)[f] for g, p in same_type)
        field_acc[f] = {"correct": ok, "of": len(same_type)}
    errors = []
    for g in gold["items"]:
        if g["id"] not in matched_g:
            errors.append({"kind": "missed", "gold": g["id"], "type": g["type"], "title": g["title"]})
    for p in pitems:
        if p["id"] not in matched_p:
            errors.append({"kind": "invented", "pred": p["id"], "type": p["type"], "title": p["title"],
                           "first_quote": (p["evidence"] or [{}])[0].get("quote")})
    for g, p, ov in pairs:
        if g["type"] != p["type"]:
            errors.append({"kind": "wrong_type", "gold": g["id"], "pred": p["id"], "expected": g["type"], "got": p["type"], "title": g["title"]})
        c = compare(g, p)
        for f in FIELDS + ["revised", "known"]:
            if not c[f]:
                errors.append({"kind": f"wrong_{f}", "gold": g["id"], "pred": p["id"], "title": g["title"],
                               "expected": _show(g, f), "got": _show(p, f)})
    return {"gold": gold_path, "pred": pred_path, "per_type": rows, "fields": field_acc,
            "pairs": [{"gold": g["id"], "pred": p["id"], "overlap": ov, "gold_title": g["title"], "pred_title": p["title"]} for g, p, ov in pairs],
            "errors": errors}


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


def _fmt(x):
    return "n/a" if x is None else f"{x:.2f}"


def to_markdown(m: dict) -> str:
    out = ["# Metrics", "", f"Gold: `{m['gold']}`  ", f"Prediction: `{m['pred']}`", "",
           "Detection counts an item as found when it cites overlapping transcript spans and has the same type. "
           "State-correct also requires state, owner, date, condition presence, approvers, and reminder count to match.", "",
           "| Type | Gold | Pred | Found | Precision | Recall | F1 | State-correct | State P | State R |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for ty, r in m["per_type"].items():
        out.append(f"| {ty} | {r['gold']} | {r['pred']} | {r['tp']} | {_fmt(r['precision'])} | {_fmt(r['recall'])} | {_fmt(r['f1'])} | "
                   f"{r['state_correct']} | {_fmt(r['state_precision'])} | {_fmt(r['state_recall'])} |")
    out += ["", "| Field (on found items) | Correct |", "|---|---|"]
    for f, v in m["fields"].items():
        out.append(f"| {f} | {v['correct']}/{v['of']} |")
    out += ["", "## Errors", ""]
    for e in m["errors"]:
        ids = " / ".join(x for x in (e.get("gold"), e.get("pred")) if x)
        detail = f" expected {e['expected']!r}, got {e['got']!r}" if "expected" in e else ""
        out.append(f"- {e['kind']} [{ids}] {e['title']}.{detail}")
    out += ["", "## Matches", ""] + [f"- {p['gold']} ↔ {p['pred']} ({p['overlap']}): {p['gold_title']} / {p['pred_title']}" for p in m["pairs"]]
    return "\n".join(out) + "\n"
