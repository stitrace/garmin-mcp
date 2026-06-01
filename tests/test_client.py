from unittest.mock import MagicMock

import pytest

import garmin_mcp_server.client as client_mod
from garmin_mcp_server.client import GarminAuthError, GarminClient
from garmin_mcp_server.config import GarminConfig


def make_config(tmp_path, with_creds=False):
    return GarminConfig(
        email="user@example.com" if with_creds else None,
        password="secret" if with_creds else None,
        tokenstore=str(tmp_path / "tokens"),
        is_cn=False,
    )


def test_no_tokens_no_credentials_raises(tmp_path):
    c = GarminClient(make_config(tmp_path, with_creds=False))
    with pytest.raises(GarminAuthError):
        _ = c.raw


def test_credential_login_caches_tokens(tmp_path, monkeypatch):
    fake = MagicMock()
    created = {}

    def fake_garmin(*args, **kwargs):
        created["kwargs"] = kwargs
        return fake

    monkeypatch.setattr(client_mod, "Garmin", fake_garmin)

    c = GarminClient(make_config(tmp_path, with_creds=True))
    got = c.raw

    assert got is fake
    # garminconnect's own login(tokenstore) handles loading/persisting tokens.
    fake.login.assert_called_once_with(c._config.tokenstore)
    assert created["kwargs"]["email"] == "user@example.com"


def test_token_login_used_when_tokens_present(tmp_path, monkeypatch):
    tokendir = tmp_path / "tokens"
    tokendir.mkdir(parents=True)
    (tokendir / "oauth1_token.json").write_text("{}")

    fake = MagicMock()
    monkeypatch.setattr(client_mod, "Garmin", lambda *a, **k: fake)

    c = GarminClient(make_config(tmp_path, with_creds=False))
    got = c.raw

    assert got is fake
    fake.login.assert_called_once_with(str(tokendir))


def test_call_retries_once_on_auth_error(tmp_path, monkeypatch):
    # Use the exact class object the client module references, so the test is
    # immune to any name re-binding between import time and test time.
    auth_error = client_mod.GarminConnectAuthenticationError("expired")

    fake = MagicMock()
    method = MagicMock(side_effect=[auth_error, {"ok": True}])
    fake.get_stats = method

    monkeypatch.setattr(client_mod, "Garmin", lambda *a, **k: fake)

    c = GarminClient(make_config(tmp_path, with_creds=True))
    result = c.call("get_stats", "2024-01-01")

    assert result == {"ok": True}
    assert method.call_count == 2


def test_profile_number_resolution(tmp_path, monkeypatch):
    fake = MagicMock()
    fake.get_user_profile.return_value = {"userProfileNumber": 12345}
    monkeypatch.setattr(client_mod, "Garmin", lambda *a, **k: fake)

    c = GarminClient(make_config(tmp_path, with_creds=True))
    assert c.profile_number() == "12345"
    assert c.profile_number() == "12345"  # cached
    fake.get_user_profile.assert_called_once()
