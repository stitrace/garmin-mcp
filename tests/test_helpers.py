from datetime import date, timedelta

import pytest

from garmin_mcp_server.helpers import resolve_date, resolve_range, trim


def test_resolve_date_today_variants():
    today = date.today().isoformat()
    assert resolve_date(None) == today
    assert resolve_date("") == today
    assert resolve_date("today") == today
    assert resolve_date("TODAY") == today


def test_resolve_date_relative():
    assert resolve_date("yesterday") == (date.today() - timedelta(days=1)).isoformat()
    assert resolve_date("-7") == (date.today() - timedelta(days=7)).isoformat()
    assert resolve_date("3") == (date.today() + timedelta(days=3)).isoformat()


def test_resolve_date_iso():
    assert resolve_date("2024-01-31") == "2024-01-31"


def test_resolve_date_invalid():
    with pytest.raises(ValueError):
        resolve_date("not-a-date")
    with pytest.raises(ValueError):
        resolve_date("2024-13-40")


def test_resolve_range_defaults():
    s, e = resolve_range(None, None, default_days=7)
    assert e == date.today().isoformat()
    assert s == (date.today() - timedelta(days=7)).isoformat()


def test_resolve_range_swaps_when_reversed():
    s, e = resolve_range("2024-02-10", "2024-02-01")
    assert s == "2024-02-01"
    assert e == "2024-02-10"


def test_trim_lists():
    out = trim(list(range(100)), max_items=10)
    assert len(out) == 11  # 10 items + truncation marker
    assert "_truncated" in out[-1]


def test_trim_strings():
    out = trim("x" * 10_000, max_str=100)
    assert out.startswith("x" * 100)
    assert "truncated" in out


def test_trim_nested_dict_passthrough():
    data = {"a": 1, "b": [1, 2, 3], "c": {"d": "short"}}
    assert trim(data) == data
