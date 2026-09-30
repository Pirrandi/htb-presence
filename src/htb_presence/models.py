"""Domain data shared by the HTB client, the presence builder and the app loop."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    avatar_url: str | None = None


@dataclass(frozen=True)
class Machine:
    name: str
    avatar_url: str | None = None


@dataclass(frozen=True)
class MachineActivity:
    """Flags the user owns on a machine, taken from their recent activity."""

    user_owned: bool = False
    root_owned: bool = False
    avatar_url: str | None = None
