from user_display.store import UserStore
from user_display.formatters import format_users


def test_compact_formatter_fields(sample_users):
    store = UserStore(sample_users)
    output = store.display_users(show_all=False, verbose=False, formatter="compact")
    # Should contain ID and Name labels in compact style
    assert "ID:" in output
    assert "Name:" in output
    assert "| Email:" in output


def test_verbose_formatter(sample_users):
    out = format_users(sample_users, formatter="verbose")
    # Multi-line per user
    assert "ID:" in out.split("\n")[0]


def test_json_formatter(sample_users):
    out = format_users(sample_users, formatter="json")
    assert out.strip().startswith("[") and out.strip().endswith("]")


def test_include_fields(sample_users):
    store = UserStore(sample_users)
    output = store.display_users(show_all=False, formatter="compact", include_fields=["id", "name"])
    lines = output.split("\n")
    assert all("Email" not in line for line in lines if line)


def test_exclude_fields(sample_users):
    store = UserStore(sample_users)
    output = store.display_users(show_all=False, formatter="compact", exclude_fields=["email"])
    assert "Email" not in output


def test_export_formatter_structure(sample_users):
    store = UserStore(sample_users)
    output = store.export_users_to_string()
    assert output.startswith("USER_EXPORT_START\n=")
    assert output.strip().endswith("USER_EXPORT_END")
