import pytest

from user_display.store import UserStore


@pytest.fixture
def sample_users():
    return [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "Admin", "status": "Active", "join_date": "2023-01-15", "last_login": "2025-11-26"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "User", "status": "Inactive", "join_date": "2023-06-20", "last_login": "2025-11-20"},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "Moderator", "status": "Active", "join_date": "2024-02-10", "last_login": "2025-11-25"},
    ]


@pytest.fixture
def store(sample_users):
    return UserStore(users=sample_users)
