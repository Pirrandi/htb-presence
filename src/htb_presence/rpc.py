"""Thin wrapper around pypresence that turns Discord failures into return values.

Discord is not required to be running: connection attempts simply fail and are
retried by the caller on the next cycle.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from pypresence import Presence
from pypresence.exceptions import PyPresenceException

log = logging.getLogger(__name__)

# DiscordNotFound, InvalidPipe, PipeClosed, DiscordError, timeouts... all derive
# from PyPresenceException; socket-level failures surface as OSError
# (ConnectionRefusedError, BrokenPipeError, ConnectionResetError...).
RPC_ERRORS = (PyPresenceException, OSError, asyncio.TimeoutError)


class DiscordRPC:
    def __init__(self, client_id: str, factory: Callable[[str], Any] = Presence) -> None:
        self._client_id = client_id
        self._factory = factory
        self._presence: Any | None = None

    @property
    def connected(self) -> bool:
        return self._presence is not None

    def connect(self) -> bool:
        if self._presence is not None:
            return True
        presence = None
        try:
            presence = self._factory(self._client_id)
            presence.connect()
        except RPC_ERRORS as exc:
            log.debug("Discord is not reachable: %s", exc)
            self._safe_close(presence)
            return False
        self._presence = presence
        log.info("Connected to Discord.")
        return True

    def update(self, payload: dict) -> bool:
        return self._call(lambda p: p.update(**payload))

    def clear(self) -> bool:
        return self._call(lambda p: p.clear())

    def close(self) -> None:
        presence, self._presence = self._presence, None
        self._safe_close(presence)

    def _call(self, action: Callable[[Any], Any]) -> bool:
        if self._presence is None:
            return False
        try:
            action(self._presence)
        except RPC_ERRORS as exc:
            log.warning("Lost connection to Discord: %s", exc)
            self.close()
            return False
        return True

    @staticmethod
    def _safe_close(presence: Any | None) -> None:
        if presence is None:
            return
        try:
            presence.close()
        except (*RPC_ERRORS, AttributeError, RuntimeError):
            pass
