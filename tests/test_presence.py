from htb_presence.models import Machine, MachineActivity, User
from htb_presence.presence import (
    FLAG_MISSING,
    FLAG_OWNED,
    HTB_LOGO_URL,
    REPO_URL,
    build_presence,
)

USER = User(id=1, name="neo", avatar_url="https://labs.hackthebox.com/storage/avatars/neo.png")
MACHINE = Machine(name="Lame", avatar_url="https://labs.hackthebox.com/storage/avatars/lame.png")


def test_machine_presence_shows_flags_and_timer():
    activity = MachineActivity(user_owned=True, root_owned=False)
    payload = build_presence("en", USER, MACHINE, activity, True, 1700000000)

    assert payload["details"] == "Machine: Lame"
    assert payload["state"] == f"User: {FLAG_OWNED} | Root: {FLAG_MISSING}"
    assert payload["start"] == 1700000000
    assert payload["large_image"] == MACHINE.avatar_url
    assert payload["small_text"] == "neo"
    assert payload["small_image"] == USER.avatar_url
    assert payload["buttons"] == [{"label": "Get this Rich Presence", "url": REPO_URL}]


def test_machine_presence_prefers_activity_avatar_and_translates():
    activity = MachineActivity(user_owned=True, root_owned=True, avatar_url="https://x/a.png")
    payload = build_presence("es", USER, MACHINE, activity, False, 5)

    assert payload["details"] == "Máquina: Lame"
    assert payload["state"] == f"User: {FLAG_OWNED} | Root: {FLAG_OWNED}"
    assert payload["large_image"] == "https://x/a.png"


def test_machine_presence_falls_back_to_logo_without_avatar():
    payload = build_presence("en", User(1, "neo"), Machine("Lame"), None, True, None)

    assert payload["large_image"] == HTB_LOGO_URL
    assert payload["state"] == f"User: {FLAG_MISSING} | Root: {FLAG_MISSING}"
    assert "start" not in payload
    assert "small_image" not in payload


def test_waiting_presence_when_vpn_connected_without_machine():
    payload = build_presence("en", USER, None, None, True, None)

    assert payload["details"] == "Connected to Hack The Box"
    assert payload["state"] == "State: Waiting"
    assert payload["large_image"] == HTB_LOGO_URL
    assert "start" not in payload


def test_presence_cleared_when_disconnected_and_no_machine():
    assert build_presence("en", USER, None, None, False, None) is None
