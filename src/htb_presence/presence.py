"""Pure functions that turn HTB state into a Discord presence payload.

A payload is a dict of keyword arguments for ``pypresence.Presence.update``;
``None`` means the presence should be cleared.
"""

from __future__ import annotations

from typing import Any

from htb_presence.i18n import translate
from htb_presence.models import Machine, MachineActivity, User

Payload = dict[str, Any]

HTB_LOGO_URL = (
    "https://yt3.googleusercontent.com/ytc/"
    "AOPolaR5R7bueWAUHc7ctRNCy5r63xddkeL17RDHOwxAlw=s900-c-k-c0x00ffffff-no-rj"
)
LARGE_TEXT = "Hack The Box"
REPO_URL = "https://github.com/Pirrandi/htb-presence"
FLAG_OWNED = "🟢"
FLAG_MISSING = "🔴"


def flag(owned: bool) -> str:
    return FLAG_OWNED if owned else FLAG_MISSING


def machine_presence(
    lang: str, user: User, machine: Machine, activity: MachineActivity, start: int | None
) -> Payload:
    payload = {
        "details": translate(lang, "machine_prefix") + machine.name,
        "state": f"User: {flag(activity.user_owned)} | Root: {flag(activity.root_owned)}",
        "large_image": activity.avatar_url or machine.avatar_url or HTB_LOGO_URL,
        **_common(lang, user),
    }
    if start:
        payload["start"] = start
    return payload


def waiting_presence(lang: str, user: User) -> Payload:
    return {
        "details": translate(lang, "connected"),
        "state": translate(lang, "waiting"),
        "large_image": HTB_LOGO_URL,
        **_common(lang, user),
    }


def build_presence(
    lang: str,
    user: User,
    machine: Machine | None,
    activity: MachineActivity | None,
    vpn_connected: bool,
    start: int | None,
) -> Payload | None:
    """Pick the presence for the current state: machine, waiting, or cleared."""
    if machine is not None:
        return machine_presence(lang, user, machine, activity or MachineActivity(), start)
    if vpn_connected:
        return waiting_presence(lang, user)
    return None


def _common(lang: str, user: User) -> Payload:
    payload: Payload = {
        "large_text": LARGE_TEXT,
        "small_text": user.name,
        "buttons": [{"label": translate(lang, "button_label"), "url": REPO_URL}],
    }
    if user.avatar_url:
        payload["small_image"] = user.avatar_url
    return payload
