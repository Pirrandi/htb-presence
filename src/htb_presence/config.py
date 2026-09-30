"""Settings loading.

Values come from environment variables first, then from the per-user config
file, then from defaults. ``os.environ`` is never modified.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

from htb_presence.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

log = logging.getLogger(__name__)

APP_NAME = "htb-presence"
CONFIG_FILENAME = "config.env"

KEY_TOKEN = "HTB_API_TOKEN"
KEY_LANG = "HTB_PRESENCE_LANG"
KEY_CLIENT_ID = "DISCORD_CLIENT_ID"
KEY_INTERVAL = "HTB_PRESENCE_INTERVAL"
ALL_KEYS = (KEY_TOKEN, KEY_LANG, KEY_CLIENT_ID, KEY_INTERVAL)

TOKEN_PLACEHOLDER = "INSERT_YOUR_API_KEY"
DEFAULT_CLIENT_ID = "1125543074861432864"
DEFAULT_INTERVAL = 30
MIN_INTERVAL = 15

_SAFE_VALUE = re.compile(r"^[A-Za-z0-9._~+/=:-]*$")


class ConfigError(Exception):
    """Raised when the settings are missing or invalid."""


@dataclass(frozen=True)
class Settings:
    token: str
    lang: str = DEFAULT_LANGUAGE
    client_id: str = DEFAULT_CLIENT_ID
    interval: int = DEFAULT_INTERVAL


def config_dir(platform: str | None = None, env: Mapping[str, str] | None = None) -> Path:
    """Return the per-user configuration directory for this platform."""
    platform = platform or sys.platform
    env = os.environ if env is None else env
    home = Path.home()
    if platform == "win32":
        base = env.get("APPDATA")
        return (Path(base) if base else home / "AppData" / "Roaming") / APP_NAME
    if platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    base = env.get("XDG_CONFIG_HOME")
    return (Path(base) if base else home / ".config") / APP_NAME


def config_path(platform: str | None = None, env: Mapping[str, str] | None = None) -> Path:
    return config_dir(platform, env) / CONFIG_FILENAME


def read_config_file(path: Path) -> dict[str, str]:
    """Parse a dotenv-style file without touching ``os.environ``."""
    if not path.is_file():
        return {}
    return {k: v for k, v in dotenv_values(path).items() if v is not None}


def load_settings(
    env: Mapping[str, str] | None = None,
    path: Path | None = None,
    require_token: bool = True,
) -> Settings:
    """Build :class:`Settings` from environment variables and the config file.

    With ``require_token=False`` a missing token yields ``Settings.token == ""``.
    """
    env = os.environ if env is None else env
    path = config_path(env=env) if path is None else path
    file_values = read_config_file(path)

    def get(key: str) -> str:
        value = env.get(key)
        if value is None or not value.strip():
            value = file_values.get(key, "")
        return value.strip()

    token = get(KEY_TOKEN)
    if token == TOKEN_PLACEHOLDER:
        token = ""
    if not token and require_token:
        raise ConfigError(f"{KEY_TOKEN} is not set. Run 'htb-presence setup' or set it in {path}.")

    return Settings(
        token=token,
        lang=_parse_lang(get(KEY_LANG)),
        client_id=get(KEY_CLIENT_ID) or DEFAULT_CLIENT_ID,
        interval=_parse_interval(get(KEY_INTERVAL)),
    )


def _parse_lang(raw: str) -> str:
    if not raw:
        return DEFAULT_LANGUAGE
    lang = raw.lower()
    if lang not in SUPPORTED_LANGUAGES:
        log.warning("Unsupported language %r, falling back to %r.", raw, DEFAULT_LANGUAGE)
        return DEFAULT_LANGUAGE
    return lang


def _parse_interval(raw: str) -> int:
    if not raw:
        return DEFAULT_INTERVAL
    try:
        interval = int(raw)
    except ValueError:
        raise ConfigError(
            f"{KEY_INTERVAL} must be a whole number of seconds, got {raw!r}."
        ) from None
    if interval < MIN_INTERVAL:
        log.warning("%s=%d is too low, using %d seconds.", KEY_INTERVAL, interval, MIN_INTERVAL)
        return MIN_INTERVAL
    return interval


def write_config_file(path: Path, values: Mapping[str, str]) -> None:
    """Write ``values`` as a dotenv file readable only by the current user."""
    lines = []
    for key, value in values.items():
        lines.append(f"{key}={_quote(key, value)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    if os.name == "posix":
        os.chmod(path, 0o600)


def _quote(key: str, value: str) -> str:
    if _SAFE_VALUE.match(value):
        return value
    if "'" in value or "\n" in value:
        raise ConfigError(f"{key} contains characters that cannot be stored.")
    return f"'{value}'"
