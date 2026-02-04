import user_display_optimized as ud
import user_display_original as original

sample_users = [
    {"id": 1, "name": "John", "email": "john@example.com", "role": "Admin", "status": "Active", "join_date": "2023-01-01", "last_login": "2023-02-01"},
    {"id": 2, "name": "Jane", "email": "jane@example.com", "role": "User", "status": "Inactive", "join_date": "2023-01-02", "last_login": "2023-02-02"},
    {"id": 3, "name": "Jake", "email": "jake@example.com", "role": "User", "status": "Active", "join_date": "2023-01-03", "last_login": "2023-02-03"},
]


def test_display_users_api():
    original_out = original.display_users(sample_users, show_all=True)
    optimized_out = ud.display_users(sample_users, show_all=True)
    assert "Total users processed" in optimized_out
    assert isinstance(optimized_out, str)
    assert optimized_out.count("\n") >= len(sample_users)
    assert "Total users processed" in original_out


def test_get_user_by_id_api():
    assert ud.get_user_by_id(sample_users, 2)["name"] == "Jane"
    assert ud.get_user_by_id(sample_users, 99) is None


def test_filter_users_api():
    filtered = ud.filter_users(sample_users, {"role": "User", "status": "Active"})
    assert len(filtered) == 1
    assert filtered[0]["id"] == 3


def test_export_users_to_string_api():
    out = ud.export_users_to_string(sample_users)
    assert out.startswith("USER_EXPORT_START")
    assert out.strip().endswith("USER_EXPORT_END")
