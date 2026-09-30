"""Minimal Hack The Box API client.

Only the endpoints needed for the presence are used, and responses are parsed
defensively: anything unexpected becomes :class:`HTBError` or an empty value.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests

from htb_presence import __version__
from htb_presence.models import Machine, MachineActivity, User

BASE_URL = "https://labs.hackthebox.com"
TIMEOUT_SECONDS = 10
USER_AGENT = f"htb-presence/{__version__} (+https://github.com/Pirrandi/htb-presence)"
ACTIVITY_PAGE_SIZE = 5


class HTBError(Exception):
    """The HTB API could not be reached or returned an unusable response."""


class HTBAuthError(HTBError):
    """The HTB API rejected the token (HTTP 401/403)."""


def absolute_url(value: Any, base_url: str = BASE_URL) -> str | None:
    """Turn HTB's relative asset paths into absolute URLs."""
    if not value or not isinstance(value, str):
        return None
    if value.startswith(("http://", "https://")):
        return value
    if not value.startswith("/"):
        value = "/" + value
    return f"{base_url}{value}"


def parse_activity(records: Any, machine_name: str, base_url: str = BASE_URL) -> MachineActivity:
    """Extract user/root ownership for ``machine_name`` from activity records."""
    user_owned = root_owned = False
    avatar_url = None
    for record in _dicts(records):
        if record.get("name") != machine_name:
            continue
        avatar_url = absolute_url(record.get("avatar"), base_url) or avatar_url
        if record.get("type") == "root":
            root_owned = True
        elif record.get("type") == "user":
            user_owned = True
    return MachineActivity(user_owned=user_owned, root_owned=root_owned, avatar_url=avatar_url)


class HTBClient:
    def __init__(
        self,
        token: str,
        session: requests.Session | None = None,
        base_url: str = BASE_URL,
        timeout: float = TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            }
        )

    def close(self) -> None:
        self._session.close()

    def get_user(self) -> User:
        info = _as_dict(self._get("/api/v4/user/info").get("info"))
        user_id, name = info.get("id"), info.get("name")
        if user_id is None or not name:
            raise HTBError("User info response is missing 'id' or 'name'.")
        return User(id=user_id, name=str(name), avatar_url=self._url(info.get("avatar")))

    def get_active_machine(self) -> Machine | None:
        info = _as_dict(self._get("/api/v4/machine/active").get("info"))
        name = info.get("name")
        if not name:
            return None
        return Machine(name=str(name), avatar_url=self._url(info.get("avatar")))

    def is_vpn_connected(self) -> bool:
        return self._get("/api/v4/user/connection/status").get("status") is True

    def get_machine_activity(self, user_id: int, machine_name: str) -> MachineActivity:
        path = f"/api/v5/user/profile/activity/{user_id}?per_page={ACTIVITY_PAGE_SIZE}"
        return parse_activity(self._get(path).get("data"), machine_name, self._base_url)

    def _url(self, value: Any) -> str | None:
        return absolute_url(value, self._base_url)

    def _get(self, path: str) -> dict:
        url = f"{self._base_url}{path}"
        try:
            response = self._session.get(url, timeout=self._timeout)
        except requests.RequestException as exc:
            raise HTBError(f"Request to {path} failed: {exc}") from exc
        if response.status_code in (401, 403):
            raise HTBAuthError(f"HTB rejected the API token (HTTP {response.status_code}).")
        if not response.ok:
            raise HTBError(f"HTB returned HTTP {response.status_code} for {path}.")
        try:
            data = response.json()
        except ValueError as exc:
            raise HTBError(f"HTB returned invalid JSON for {path}.") from exc
        return _as_dict(data)


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _dicts(value: Any) -> Iterable[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
