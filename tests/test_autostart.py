import plistlib
from pathlib import Path

from htb_presence.autostart import launchd_plist, systemd_unit


def test_systemd_unit_runs_module_and_skips_restart_on_bad_config():
    unit = systemd_unit("/home/me/.local/pipx/venvs/htb-presence/bin/python")

    assert (
        "ExecStart=/home/me/.local/pipx/venvs/htb-presence/bin/python -m htb_presence run" in unit
    )
    assert "Restart=on-failure" in unit
    assert "RestartPreventExitStatus=2" in unit
    assert "WantedBy=default.target" in unit


def test_systemd_unit_quotes_and_escapes_paths():
    unit = systemd_unit("/opt/my apps/100%/python")

    assert 'ExecStart="/opt/my apps/100%%/python" -m htb_presence run' in unit


def test_launchd_plist():
    data = plistlib.loads(launchd_plist("/usr/bin/python3", Path("/tmp/h.log")))

    assert data["ProgramArguments"] == ["/usr/bin/python3", "-m", "htb_presence", "run"]
    assert data["RunAtLoad"] is True
