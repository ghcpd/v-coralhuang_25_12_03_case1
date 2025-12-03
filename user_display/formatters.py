import json


def format_compact(user: dict, fields=None):
    parts = []
    if fields is None:
        fields = ["id", "name", "email", "role", "status", "join_date", "last_login"]
    for f in fields:
        parts.append(f"{str(user.get(f, ''))}")
    return " | ".join(parts)


def format_verbose(user: dict, fields=None):
    lines = []
    if fields is None:
        fields = ["id", "name", "email", "role", "status", "join_date", "last_login"]
    for f in fields:
        lines.append(f"{f.capitalize()}: {user.get(f, '')}")
    return "\n".join(lines)


def format_json_like(user: dict, fields=None):
    if fields is None:
        return json.dumps(user, ensure_ascii=False)
    return json.dumps({k: user.get(k) for k in fields}, ensure_ascii=False)
