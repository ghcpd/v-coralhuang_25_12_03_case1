import user_display_original as baseline
import user_display_optimized as opt


def test_display_users_matches_baseline(sample_users):
    expected = baseline.display_users(sample_users, show_all=True, verbose=False)
    actual = opt.display_users(sample_users, show_all=True, verbose=False)
    assert actual == expected


def test_get_user_by_id_matches_baseline(sample_users):
    expected = baseline.get_user_by_id(sample_users, 3)
    actual = opt.get_user_by_id(sample_users, 3)
    assert actual == expected


def test_filter_users_matches_baseline(sample_users):
    criteria = {"role": "User", "status": "Active"}
    expected = baseline.filter_users(sample_users, criteria)
    actual = opt.filter_users(sample_users, criteria)
    assert actual == expected


def test_export_users_to_string_matches_baseline(sample_users):
    expected = baseline.export_users_to_string(sample_users)
    actual = opt.export_users_to_string(sample_users)
    assert actual == expected
