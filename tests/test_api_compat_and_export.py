from user_display_optimized import display_users, get_user_by_id, filter_users, export_users_to_string
from user_display_original import sample_users as original_samples


def test_lookup_and_filter():
    users = original_samples
    res = get_user_by_id(users, 3)
    assert res and res["id"] == 3

    filtered = filter_users(users, {"role": "User", "status": "Active"})
    assert isinstance(filtered, list)


def test_export_contains_markers():
    users = original_samples
    out = export_users_to_string(users)
    assert "USER_EXPORT_START" in out
    assert "USER_EXPORT_END" in out
