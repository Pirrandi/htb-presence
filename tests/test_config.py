import pytest

from htb_presence.config import (
    DEFAULT_CLIENT_ID,
    DEFAULT_INTERVAL,
    MIN_INTERVAL,
    ConfigError,
    config_path,
    load_settings,
    read_config_file,
    write_config_file,
)


@pytest.fixture
def cfg(tmp_path):
    path = tmp_path / "config.env"

    def write(text):
        path.write_text(text, encoding="utf-8")
        return path

    return write


def test_defaults_with_token_from_file(cfg):
    settings = load_settings(env={}, path=cfg("HTB_API_TOKEN=abc\n"))

    assert settings.token == "abc"
    assert settings.lang == "en"
    assert settings.client_id == DEFAULT_CLIENT_ID
    assert settings.interval == DEFAULT_INTERVAL


def test_env_overrides_file(cfg):
    path = cfg("HTB_API_TOKEN=file\nHTB_PRESENCE_LANG=en\nHTB_PRESENCE_INTERVAL=60\n")
    env = {"HTB_API_TOKEN": "env", "HTB_PRESENCE_LANG": "ES", "DISCORD_CLIENT_ID": "42"}

    settings = load_settings(env=env, path=path)

    assert settings.token == "env"
    assert settings.lang == "es"
    assert settings.client_id == "42"
    assert settings.interval == 60


def test_empty_env_value_does_not_hide_file_value(cfg):
    settings = load_settings(env={"HTB_API_TOKEN": "  "}, path=cfg("HTB_API_TOKEN=file\n"))

    assert settings.token == "file"


def test_missing_file_and_env_raises(tmp_path):
    with pytest.raises(ConfigError):
        load_settings(env={}, path=tmp_path / "missing.env")


def test_placeholder_token_is_rejected(cfg):
    with pytest.raises(ConfigError):
        load_settings(env={}, path=cfg("HTB_API_TOKEN=INSERT_YOUR_API_KEY\n"))


def test_placeholder_token_reads_as_unset_when_not_required(cfg):
    path = cfg("HTB_API_TOKEN=INSERT_YOUR_API_KEY\n")

    assert load_settings(env={}, path=path, require_token=False).token == ""


def test_unknown_language_falls_back_to_english(cfg):
    settings = load_settings(env={"HTB_PRESENCE_LANG": "fr"}, path=cfg("HTB_API_TOKEN=t\n"))

    assert settings.lang == "en"


def test_system_language_variable_is_ignored(cfg):
    env = {"LANGUAGE": "es_ES:es", "LANG": "es_ES.UTF-8"}

    assert load_settings(env=env, path=cfg("HTB_API_TOKEN=t\n")).lang == "en"


def test_interval_is_clamped_to_minimum(cfg):
    settings = load_settings(env={"HTB_PRESENCE_INTERVAL": "1"}, path=cfg("HTB_API_TOKEN=t\n"))

    assert settings.interval == MIN_INTERVAL


def test_invalid_interval_raises(cfg):
    with pytest.raises(ConfigError):
        load_settings(env={"HTB_PRESENCE_INTERVAL": "soon"}, path=cfg("HTB_API_TOKEN=t\n"))


def test_load_does_not_touch_os_environ(cfg, monkeypatch):
    monkeypatch.delenv("HTB_API_TOKEN", raising=False)

    load_settings(env={}, path=cfg("HTB_API_TOKEN=secret\n"))

    import os

    assert "HTB_API_TOKEN" not in os.environ


@pytest.mark.parametrize(
    "platform, env, expected_tail",
    [
        ("linux", {"XDG_CONFIG_HOME": "/xdg"}, ("xdg", "htb-presence", "config.env")),
        ("win32", {"APPDATA": "/appdata"}, ("appdata", "htb-presence", "config.env")),
        ("darwin", {}, ("Application Support", "htb-presence", "config.env")),
    ],
)
def test_config_path_per_platform(platform, env, expected_tail):
    assert config_path(platform, env).parts[-3:] == expected_tail


def test_config_path_linux_defaults_to_dot_config(monkeypatch, tmp_path):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    assert config_path("linux", {}) == tmp_path / ".config" / "htb-presence" / "config.env"


def test_write_then_read_round_trip(tmp_path):
    path = tmp_path / "sub" / "config.env"
    write_config_file(path, {"HTB_API_TOKEN": "eyJ.abc-_", "OTHER": "has space"})

    assert read_config_file(path) == {"HTB_API_TOKEN": "eyJ.abc-_", "OTHER": "has space"}
    if __import__("os").name == "posix":
        assert path.stat().st_mode & 0o777 == 0o600
