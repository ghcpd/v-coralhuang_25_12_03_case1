import json
from user_display.formatters import format_user, format_users


sample = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "User",
    "status": "Active",
    "join_date": "2023-01-01",
    "last_login": "2025-11-26",
}


def test_format_compact():
    out = format_user(sample, mode="compact")
    assert "ID: 1" in out
    assert "Name: John Doe" in out


def test_format_verbose():
    out = format_user(sample, mode="verbose")
    assert out.startswith("User ID: 1")
    assert "Join Date: 2023-01-01" in out


def test_format_json():
    out = format_user(sample, mode="json")
    obj = json.loads(out)
    assert obj["name"] == "John Doe"


def test_format_users_include_exclude():
    users = [sample]
    out = format_users(users, mode="compact", include=["id", "name"])
    assert "Email" not in out
