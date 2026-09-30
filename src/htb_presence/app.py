"""Main polling loop: HTB state in, Discord presence out."""

from __future__ import annotations

import logging
import time
from typing import Callable

from htb_presence.config import Settings
from htb_presence.htb import HTBAuthError, HTBClient, HTBError
from htb_presence.models import User
from htb_presence.presence import Payload, build_presence
from htb_presence.rpc import DiscordRPC

log = logging.getLogger(__name__)

EXIT_OK = 0
# Configuration problems (missing/rejected token). The systemd unit does not
# restart on this code because retrying cannot fix it.
EXIT_BAD_CONFIG = 2

_UNSET = object()


class PresenceApp:
    def __init__(
        self,
        settings: Settings,
        htb: HTBClient,
        rpc: DiscordRPC,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._settings = settings
        self._htb = htb
        self._rpc = rpc
        self._clock = clock
        self._sleep = sleep
        self._user: User | None = None
        self._machine_name: str | None = None
        self._machine_start: int | None = None
        self._last_payload: object = _UNSET

    def run(self) -> int:
        """Poll until interrupted. Returns the process exit code."""
        log.info("htb-presence started (polling every %ss).", self._settings.interval)
        try:
            while True:
                self.tick()
                self._sleep(self._settings.interval)
        except HTBAuthError as exc:
            log.error("%s Check your HTB App Token (run 'htb-presence setup').", exc)
            return EXIT_BAD_CONFIG
        except KeyboardInterrupt:
            log.info("Stopping.")
            return EXIT_OK
        finally:
            self.shutdown()

    def tick(self) -> None:
        """Run one poll cycle. Raises HTBAuthError if the token is rejected."""
        if not self._rpc.connect():
            log.debug("Discord is not running; retrying later.")
            self._last_payload = _UNSET
            return
        try:
            payload = self._fetch_payload()
        except HTBAuthError:
            raise
        except HTBError as exc:
            log.warning("Could not fetch HTB state: %s", exc)
            return
        self._publish(payload)

    def shutdown(self) -> None:
        if self._rpc.connected:
            self._rpc.clear()
        self._rpc.close()

    def _fetch_payload(self) -> Payload | None:
        if self._user is None:
            self._user = self._htb.get_user()
            log.info("Logged in to HTB as %s.", self._user.name)
        user = self._user

        machine = self._htb.get_active_machine()
        if machine is None:
            self._machine_name = self._machine_start = None
            vpn = self._htb.is_vpn_connected()
            return build_presence(self._settings.lang, user, None, None, vpn, None)

        if machine.name != self._machine_name:
            log.info("Active machine: %s", machine.name)
            self._machine_name = machine.name
            self._machine_start = int(self._clock())
        activity = self._htb.get_machine_activity(user.id, machine.name)
        return build_presence(
            self._settings.lang, user, machine, activity, True, self._machine_start
        )

    def _publish(self, payload: Payload | None) -> None:
        if payload == self._last_payload:
            return
        ok = self._rpc.clear() if payload is None else self._rpc.update(payload)
        if ok:
            log.debug("Presence updated: %s", payload)
            self._last_payload = payload
        else:
            self._last_payload = _UNSET


def run(settings: Settings) -> int:
    htb = HTBClient(settings.token)
    try:
        return PresenceApp(settings, htb, DiscordRPC(settings.client_id)).run()
    finally:
        htb.close()
