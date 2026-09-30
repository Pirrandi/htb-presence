from pypresence.exceptions import DiscordNotFound, PipeClosed

from htb_presence.rpc import DiscordRPC


class FakePresence:
    def __init__(self, fail_connect=None, fail_update=None):
        self.fail_connect = fail_connect
        self.fail_update = fail_update
        self.closed = False
        self.updates = []

    def connect(self):
        if self.fail_connect:
            raise self.fail_connect

    def update(self, **payload):
        if self.fail_update:
            raise self.fail_update
        self.updates.append(payload)

    def clear(self):
        pass

    def close(self):
        self.closed = True


def test_connect_failure_is_reported_not_raised():
    fake = FakePresence(fail_connect=DiscordNotFound())
    rpc = DiscordRPC("1", factory=lambda cid: fake)

    assert rpc.connect() is False
    assert rpc.connected is False
    assert fake.closed


def test_connection_refused_is_handled():
    rpc = DiscordRPC("1", factory=lambda cid: FakePresence(fail_connect=ConnectionRefusedError()))

    assert rpc.connect() is False


def test_update_failure_disconnects():
    fake = FakePresence(fail_update=PipeClosed())
    rpc = DiscordRPC("1", factory=lambda cid: fake)
    assert rpc.connect()

    assert rpc.update({"details": "x"}) is False
    assert rpc.connected is False


def test_update_passes_payload():
    fake = FakePresence()
    rpc = DiscordRPC("1", factory=lambda cid: fake)
    rpc.connect()

    assert rpc.update({"details": "x"}) is True
    assert fake.updates == [{"details": "x"}]
