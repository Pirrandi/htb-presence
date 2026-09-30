import pytest
import requests

from htb_presence.htb import (
    BASE_URL,
    HTBAuthError,
    HTBClient,
    HTBError,
    absolute_url,
    parse_activity,
)


class FakeResponse:
    def __init__(self, status=200, data=None, invalid_json=False):
        self.status_code = status
        self.ok = 200 <= status < 400
        self._data = data
        self._invalid = invalid_json

    def json(self):
        if self._invalid:
            raise ValueError("not json")
        return self._data


class FakeSession:
    def __init__(self, routes):
        self.routes = routes
        self.headers = {}
        self.calls = []

    def get(self, url, timeout=None):
        self.calls.append((url, timeout))
        route = self.routes[url.replace(BASE_URL, "")]
        if isinstance(route, Exception):
            raise route
        return route

    def close(self):
        pass


def client(routes):
    session = FakeSession(routes)
    return HTBClient("tok", session=session), session


def test_sends_bearer_token_user_agent_and_timeout():
    htb, session = client({"/api/v4/user/connection/status": FakeResponse(data={"status": True})})

    assert htb.is_vpn_connected() is True
    assert session.headers["Authorization"] == "Bearer tok"
    assert session.headers["User-Agent"].startswith("htb-presence/")
    assert session.calls == [(f"{BASE_URL}/api/v4/user/connection/status", 10)]


def test_get_user_makes_avatar_absolute():
    data = {"info": {"id": 7, "name": "neo", "avatar": "/storage/avatars/neo.png"}}
    htb, _ = client({"/api/v4/user/info": FakeResponse(data=data)})

    user = htb.get_user()

    assert (user.id, user.name) == (7, "neo")
    assert user.avatar_url == f"{BASE_URL}/storage/avatars/neo.png"


def test_get_user_without_info_raises():
    htb, _ = client({"/api/v4/user/info": FakeResponse(data={"info": None})})

    with pytest.raises(HTBError):
        htb.get_user()


@pytest.mark.parametrize("data", [{"info": None}, {}, None, [], {"info": {"name": None}}])
def test_no_active_machine(data):
    htb, _ = client({"/api/v4/machine/active": FakeResponse(data=data)})

    assert htb.get_active_machine() is None


def test_active_machine():
    data = {"info": {"name": "Lame", "avatar": "https://cdn/lame.png"}}
    htb, _ = client({"/api/v4/machine/active": FakeResponse(data=data)})

    machine = htb.get_active_machine()

    assert machine.name == "Lame"
    assert machine.avatar_url == "https://cdn/lame.png"


@pytest.mark.parametrize("data", [{"status": False}, {}, {"status": "true"}, None])
def test_vpn_not_connected(data):
    htb, _ = client({"/api/v4/user/connection/status": FakeResponse(data=data)})

    assert htb.is_vpn_connected() is False


def test_machine_activity_uses_v5_endpoint():
    records = {"data": [{"name": "Lame", "type": "user"}, {"name": "Lame", "type": "root"}]}
    path = "/api/v5/user/profile/activity/7?per_page=5"
    htb, _ = client({path: FakeResponse(data=records)})

    activity = htb.get_machine_activity(7, "Lame")

    assert activity.user_owned and activity.root_owned


@pytest.mark.parametrize("status", [401, 403])
def test_auth_errors_are_distinct(status):
    htb, _ = client({"/api/v4/user/info": FakeResponse(status=status)})

    with pytest.raises(HTBAuthError):
        htb.get_user()


@pytest.mark.parametrize(
    "response",
    [
        FakeResponse(status=500),
        FakeResponse(status=429),
        FakeResponse(invalid_json=True),
        requests.ConnectionError("down"),
        requests.Timeout("slow"),
    ],
)
def test_other_failures_raise_htb_error(response):
    htb, _ = client({"/api/v4/machine/active": response})

    with pytest.raises(HTBError) as info:
        htb.get_active_machine()
    assert not isinstance(info.value, HTBAuthError)


def test_parse_activity_flags_and_avatar():
    records = [
        {"name": "Other", "type": "root", "avatar": "/other.png"},
        {"name": "Lame", "type": "user", "avatar": "/lame.png"},
        "garbage",
        {"type": "root"},
    ]

    activity = parse_activity(records, "Lame")

    assert activity.user_owned is True
    assert activity.root_owned is False
    assert activity.avatar_url == f"{BASE_URL}/lame.png"


@pytest.mark.parametrize("records", [None, {}, "x", []])
def test_parse_activity_tolerates_bad_input(records):
    activity = parse_activity(records, "Lame")

    assert not activity.user_owned and not activity.root_owned and activity.avatar_url is None


def test_absolute_url():
    assert absolute_url(None) is None
    assert absolute_url("") is None
    assert absolute_url("https://a/b.png") == "https://a/b.png"
    assert absolute_url("/x.png") == f"{BASE_URL}/x.png"
    assert absolute_url("x.png") == f"{BASE_URL}/x.png"
