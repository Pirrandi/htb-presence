import pytest

from htb_presence.app import EXIT_BAD_CONFIG, PresenceApp
from htb_presence.config import Settings
from htb_presence.htb import HTBAuthError, HTBError
from htb_presence.models import Machine, MachineActivity, User


class FakeHTB:
    def __init__(self):
        self.user_calls = 0
        self.machine = None
        self.vpn = False
        self.activity = MachineActivity()
        self.error = None

    def get_user(self):
        self.user_calls += 1
        return User(1, "neo")

    def get_active_machine(self):
        if self.error:
            raise self.error
        return self.machine

    def is_vpn_connected(self):
        return self.vpn

    def get_machine_activity(self, user_id, name):
        return self.activity


class FakeRPC:
    def __init__(self):
        self.available = True
        self.connected = False
        self.updates = []
        self.clears = 0

    def connect(self):
        self.connected = self.available
        return self.connected

    def update(self, payload):
        self.updates.append(payload)
        return True

    def clear(self):
        self.clears += 1
        return True

    def close(self):
        self.connected = False


@pytest.fixture
def parts():
    htb, rpc, now = FakeHTB(), FakeRPC(), [1000.0]
    app = PresenceApp(Settings(token="t"), htb, rpc, clock=lambda: now[0], sleep=lambda s: None)
    return app, htb, rpc, now


def test_updates_only_when_payload_changes(parts):
    app, htb, rpc, _ = parts
    htb.vpn = True

    app.tick()
    app.tick()

    assert len(rpc.updates) == 1
    assert htb.user_calls == 1


def test_machine_start_is_kept_while_machine_stays_active(parts):
    app, htb, rpc, now = parts
    htb.machine = Machine("Lame")

    app.tick()
    now[0] = 2000.0
    htb.activity = MachineActivity(user_owned=True)
    app.tick()

    assert [u["start"] for u in rpc.updates] == [1000, 1000]


def test_machine_change_resets_timer(parts):
    app, htb, rpc, now = parts
    htb.machine = Machine("Lame")
    app.tick()
    now[0] = 3000.0
    htb.machine = Machine("Jerry")
    app.tick()

    assert rpc.updates[-1]["start"] == 3000


def test_clears_when_nothing_active(parts):
    app, htb, rpc, _ = parts
    htb.vpn = True
    app.tick()
    htb.vpn = False
    app.tick()

    assert rpc.clears == 1


def test_skips_htb_when_discord_is_closed(parts):
    app, htb, rpc, _ = parts
    rpc.available = False

    app.tick()

    assert htb.user_calls == 0
    assert rpc.updates == []


def test_resends_after_discord_reconnects(parts):
    app, htb, rpc, _ = parts
    htb.vpn = True
    app.tick()
    rpc.available = False
    rpc.connected = False
    app.tick()
    rpc.available = True
    app.tick()

    assert len(rpc.updates) == 2


def test_transient_htb_error_keeps_presence(parts):
    app, htb, rpc, _ = parts
    htb.vpn = True
    app.tick()
    htb.error = HTBError("down")
    app.tick()

    assert rpc.clears == 0
    assert len(rpc.updates) == 1


def test_run_exits_on_invalid_token_and_clears(parts):
    app, htb, rpc, _ = parts
    htb.error = HTBAuthError("rejected")

    assert app.run() == EXIT_BAD_CONFIG
    assert rpc.clears == 1


def test_run_stops_on_keyboard_interrupt(parts):
    _, htb, rpc, _ = parts

    def interrupt(seconds):
        raise KeyboardInterrupt

    htb.vpn = True
    app = PresenceApp(Settings(token="t"), htb, rpc, sleep=interrupt)

    assert app.run() == 0
    assert len(rpc.updates) == 1
    assert rpc.clears == 1  # presence cleared on shutdown
