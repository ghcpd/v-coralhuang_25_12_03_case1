from user_display.filters import filter_users, SimpleCriteriaFilter

users = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "Admin", "status": "Active"},
    {"id": 2, "name": "jane smith", "email": "jane@example.com", "role": "User", "status": "Inactive"},
]


def test_filter_case_insensitive_default():
    filtered = filter_users(users, {"name": "JANE"})
    assert len(filtered) == 1
    assert filtered[0]["id"] == 2


def test_filter_case_sensitive():
    filtered = filter_users(users, {"name": "JANE"}, case_insensitive=False)
    assert len(filtered) == 0


def test_filter_email_substring():
    filtered = filter_users(users, {"email": "example.com"})
    assert len(filtered) == 2


def test_custom_strategy_works():
    strat = SimpleCriteriaFilter()
    filtered = filter_users(users, {"role": "Admin"}, strategy=strat)
    assert len(filtered) == 1
    assert filtered[0]["id"] == 1
