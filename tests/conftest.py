import pytest

from user_display_original import sample_users as baseline_users


def make_users(n: int):
    return [
        {
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "role": "Admin" if i % 3 == 0 else ("Moderator" if i % 3 == 1 else "User"),
            "status": "Active" if i % 2 == 0 else "Inactive",
            "join_date": "2023-01-01",
            "last_login": "2025-11-26",
        }
        for i in range(1, n + 1)
    ]


@pytest.fixture
def sample_users():
    return list(baseline_users)


@pytest.fixture
def many_users():
    return make_users(1000)


@pytest.fixture
def malformed_users():
    return [
        {"name": "No ID"},
        {"id": 1, "name": "Missing email"},
        {"id": 2, "name": "Valid", "email": "valid@example.com", "role": "User", "status": "Active", "join_date": "2023-01-01", "last_login": "2025-11-26"},
    ]
