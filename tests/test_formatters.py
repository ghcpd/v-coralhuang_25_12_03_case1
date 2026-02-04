from user_display.formatters import format_compact, format_verbose, format_json_like


def test_format_compact(sample_users):
    out = format_compact(sample_users[0])
    assert "John" in out


def test_format_verbose(sample_users):
    out = format_verbose(sample_users[0])
    assert "Name: John Doe" in out


def test_format_json_like(sample_users):
    out = format_json_like(sample_users[0])
    assert '"name": "John Doe"' in out
