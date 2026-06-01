from unittest.mock import MagicMock

import pytest

import garmin_mcp_server.server as server


@pytest.fixture
def fake_client(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(server, "get_client", lambda: fake)
    return fake


def test_get_daily_summary_calls_get_stats(fake_client):
    fake_client.call.return_value = {"steps": 1000}
    out = server.get_daily_summary(date="2024-01-01")
    assert out == {"steps": 1000}
    fake_client.call.assert_called_once_with("get_stats", "2024-01-01")


def test_get_activities_passes_args(fake_client):
    fake_client.call.return_value = []
    server.get_activities(start=0, limit=5, activity_type="running")
    fake_client.call.assert_called_once_with("get_activities", 0, 5, "running")


def test_get_sleep_resolves_date(fake_client):
    fake_client.call.return_value = {"sleep": True}
    server.get_sleep(date="today")
    method, arg = fake_client.call.call_args[0]
    assert method == "get_sleep_data"
    assert len(arg) == 10 and arg[4] == "-"  # resolved to ISO date


def test_get_gear_uses_profile_number(fake_client):
    fake_client.profile_number.return_value = "999"
    fake_client.call.return_value = []
    server.get_gear()
    fake_client.call.assert_called_once_with("get_gear", "999")


def test_download_activity_rejects_bad_format(fake_client):
    with pytest.raises(ValueError):
        server.download_activity(activity_id=1, fmt="PDF")


def test_call_wraps_errors(fake_client):
    fake_client.call.side_effect = RuntimeError("boom")
    with pytest.raises(RuntimeError) as exc:
        server.get_daily_summary(date="2024-01-01")
    assert "get_stats" in str(exc.value)
