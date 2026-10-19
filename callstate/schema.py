TYPES = ["bug", "config_change", "feature_request", "commitment", "follow_up", "billing", "constraint", "account_signal"]
STATES = ["open", "conditional", "pending_approval", "deferred", "blocked", "rejected", "active", "closed", "noted"]
KINDS = ["none", "by", "on", "not_before", "range", "window", "past"]
ROLES = ["origin", "superseded", "revision", "final", "condition", "confirmation"]
KNOWN = ["new", "known_previous_call", "known_other_customers", "known_backlog"]
SOURCES = ["config", "knowledge_base", "call_log", "invoice", "contract", "calendar", "crm", "other"]
FACT_STATUS = ["current", "pending_change", "superseded"]


def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


S = {"type": "string"}
B = {"type": "boolean"}
I = {"type": "integer"}


def _arr(x: dict) -> dict:
    return {"type": "array", "items": x}


def _enum(values: list) -> dict:
    return {"type": "string", "enum": values}


EVIDENCE = _obj({"speaker": S, "line": I, "quote": S, "role": _enum(ROLES)})
WHEN = _obj({"kind": _enum(KINDS), "phrase": S, "tense": _enum(["future", "past"]), "anchor": S})

ITEM = _obj({
    "local_id": S, "type": _enum(TYPES), "state": _enum(STATES), "title": S,
    "owner_party": _enum(["rinvo", "customer"]), "owner_person": S, "action": S,
    "when": WHEN,
    "condition": _obj({"text": S, "phrase": S}),
    "authority_keys": _arr(S), "if_others_ask": S, "keywords": _arr(S),
    "launch": B, "freeze": B, "watches": S, "max_count": I, "channel": S,
    "target": S, "current_value": S, "new_value": S,
    "success_metric": S, "no_deadline_promised": B,
    "evidence": _arr(EVIDENCE), "revised": B,
    "known": _enum(KNOWN), "known_basis": S, "customer_visible": B,
    "claims": _arr(_obj({"text": S, "source": _enum(SOURCES), "line": I, "quote": S, "time_phrase": S})),
    "ambiguities": _arr(S), "related": _arr(S), "brief_for": _arr(S), "previous_id": S,
    "recap_pl": S,
    "message": _obj({"to": S, "subject_pl": S, "body_pl": S}),
})

OUTPUT = _obj({
    "call": _obj({"customer": S, "customer_contact": S, "customer_contact_vocative_pl": S, "rinvo_contact": S}),
    "account": _obj({
        "people": _arr(_obj({"name": S, "side": _enum(["rinvo", "customer"]), "role": S, "present": B, "email": S, "evidence": _arr(EVIDENCE)})),
        "authority": _arr(_obj({"key": S, "decision": S, "approvers": _arr(S), "not_authorized": _arr(S), "evidence": _arr(EVIDENCE)})),
        "facts": _arr(_obj({"key": S, "subject": S, "value": S, "status": _enum(FACT_STATUS), "evidence": _arr(EVIDENCE)})),
    }),
    "items": _arr(ITEM),
    "previous_updates": _arr(_obj({"previous_id": S, "new_state": _enum(STATES), "note": S, "evidence": _arr(EVIDENCE)})),
    "conflicts": _arr(_obj({"previous_id": S, "local_id": S, "description": S, "evidence": _arr(EVIDENCE)})),
})

PY = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}


def validate(value, schema: dict = OUTPUT, path: str = "$") -> list[str]:
    errors: list[str] = []
    t = schema["type"]
    if t == "integer" and isinstance(value, bool) or not isinstance(value, PY[t]):
        return [f"{path}: expected {t}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if t == "object":
        for k in schema["required"]:
            if k not in value:
                errors.append(f"{path}: missing field {k!r}")
        for k, v in value.items():
            if k not in schema["properties"]:
                errors.append(f"{path}: unexpected field {k!r}")
            else:
                errors += validate(v, schema["properties"][k], f"{path}.{k}")
    elif t == "array":
        for i, v in enumerate(value):
            errors += validate(v, schema["items"], f"{path}[{i}]")
    return errors
