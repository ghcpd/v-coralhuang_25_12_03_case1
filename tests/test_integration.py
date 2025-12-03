from user_display.user_display_optimized import display_users, get_user_by_id, filter_users, export_users_to_string


def test_display_and_export(sample_users):
    text = display_users(sample_users, show_all=True)
    assert "Total users processed" in text
    out = export_users_to_string(sample_users)
    assert "USER_EXPORT_START" in out


def test_filter_multi_criteria(sample_users):
    res = filter_users(sample_users, {"role": "User", "status": "Inactive"})
    assert len(res) == 1


def test_case_sensitivity():
    from user_display.store import UserStore
    s = UserStore(users=[{"id":1, "name":"John"}], case_sensitive=True)
    res = s.filter_users({"name":"john"})
    assert len(res) == 0
