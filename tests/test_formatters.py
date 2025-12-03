from user_display.formatters import format_user, format_users

user = {"id": 1, "name": "John", "email": "john@example.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2023-02-01"}


def test_format_user_compact():
    s = format_user(user, mode="compact")
    assert "ID: 1" in s
    assert "Name: John" in s


def test_format_user_verbose():
    s = format_user(user, mode="verbose")
    assert "Id: 1" in s
    assert "Name: John" in s
    assert "Email: john@example.com" in s


def test_format_user_json():
    s = format_user(user, mode="json")
    assert s.startswith("{") and "\"id\"" in s


def test_format_users_include_exclude():
    s = format_users([user], mode="compact", include=["id", "name"], exclude=["id"])
    assert "Name: John" in s
    assert "ID:" not in s
