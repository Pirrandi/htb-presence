"""Start htb-presence automatically when the user logs in.

- Linux: a systemd user service (no root, runs in the user's session).
- Windows: a value under HKCU\\...\\Run launched with pythonw.exe (no console).
- macOS: a LaunchAgent in ~/Library/LaunchAgents.
"""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

from htb_presence.config import config_dir

SERVICE_NAME = "htb-presence"
LAUNCHD_LABEL = "com.github.pirrandi.htb-presence"
WINDOWS_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_ARGS = ["-m", "htb_presence", "run"]


class AutostartError(Exception):
    """Autostart could not be installed, removed or queried."""


def install() -> str:
    """Install and start the autostart entry. Returns a human-readable summary."""
    return _backend().install()


def uninstall() -> str:
    return _backend().uninstall()


def is_installed() -> bool:
    return _backend().is_installed()


def describe() -> str:
    return _backend().describe()


def _backend():
    if sys.platform.startswith("linux"):
        return SystemdUser()
    if sys.platform == "win32":
        return WindowsRun()
    if sys.platform == "darwin":
        return LaunchAgent()
    raise AutostartError(
        f"Autostart is not supported on {sys.platform}; run 'htb-presence' manually."
    )


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    if shutil.which(cmd[0]) is None:
        raise AutostartError(f"'{cmd[0]}' was not found on this system.")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise AutostartError(f"'{' '.join(cmd)}' failed: {detail}")
    return result


# --- Linux ------------------------------------------------------------------


def systemd_unit(python: str) -> str:
    exec_start = " ".join(_systemd_quote(arg) for arg in [python, *RUN_ARGS])
    return f"""[Unit]
Description=Discord Rich Presence for Hack The Box
Documentation=https://github.com/Pirrandi/htb-presence

[Service]
ExecStart={exec_start}
Restart=on-failure
RestartSec=30
# Exit code 2 means the HTB token was rejected: restarting will not help.
RestartPreventExitStatus=2

[Install]
WantedBy=default.target
"""


def _systemd_quote(arg: str) -> str:
    # '%' starts a systemd specifier and '$' a variable expansion.
    arg = arg.replace("%", "%%").replace("$", "$$")
    if arg and not any(c in arg for c in " \t\"'\\"):
        return arg
    escaped = arg.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class SystemdUser:
    def unit_path(self) -> Path:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
        return Path(base) / "systemd" / "user" / f"{SERVICE_NAME}.service"

    def install(self) -> str:
        path = self.unit_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(systemd_unit(sys.executable), encoding="utf-8")
        _run(["systemctl", "--user", "daemon-reload"])
        _run(["systemctl", "--user", "enable", "--now", f"{SERVICE_NAME}.service"])
        return (
            f"Installed systemd user service at {path}.\n"
            f"Logs: journalctl --user -u {SERVICE_NAME} -f"
        )

    def uninstall(self) -> str:
        path = self.unit_path()
        if not path.exists():
            return "The systemd user service is not installed."
        _run(["systemctl", "--user", "disable", "--now", f"{SERVICE_NAME}.service"], check=False)
        path.unlink()
        _run(["systemctl", "--user", "daemon-reload"], check=False)
        return f"Removed {path}."

    def is_installed(self) -> bool:
        return self.unit_path().exists()

    def describe(self) -> str:
        return f"systemd user service ({self.unit_path()})"


# --- Windows ----------------------------------------------------------------


def windows_command(python: str) -> str:
    exe = Path(python)
    pythonw = exe.with_name("pythonw.exe")
    launcher = pythonw if pythonw.exists() else exe
    return subprocess.list2cmdline([str(launcher), *RUN_ARGS])


class WindowsRun:
    def _key(self, access: int):
        import winreg

        return winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, WINDOWS_RUN_KEY, 0, access)

    def install(self) -> str:
        import winreg

        command = windows_command(sys.executable)
        with self._key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, SERVICE_NAME, 0, winreg.REG_SZ, command)
        subprocess.Popen(
            command,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
            close_fds=True,
        )
        return (
            f"Registered '{command}' to run at login and started it.\n"
            f"Logs: {config_dir() / 'htb-presence.log'}"
        )

    def uninstall(self) -> str:
        import winreg

        try:
            with self._key(winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, SERVICE_NAME)
        except FileNotFoundError:
            return "The login entry is not installed."
        return "Removed the login entry. A running instance keeps going until you log out."

    def is_installed(self) -> bool:
        import winreg

        try:
            with self._key(winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, SERVICE_NAME)
        except FileNotFoundError:
            return False
        return True

    def describe(self) -> str:
        return f"HKCU\\{WINDOWS_RUN_KEY}\\{SERVICE_NAME}"


# --- macOS ------------------------------------------------------------------


def launchd_plist(python: str, log_path: Path) -> bytes:
    return plistlib.dumps(
        {
            "Label": LAUNCHD_LABEL,
            "ProgramArguments": [python, *RUN_ARGS],
            "RunAtLoad": True,
            "KeepAlive": {"SuccessfulExit": False},
            "ThrottleInterval": 60,
            "StandardOutPath": str(log_path),
            "StandardErrorPath": str(log_path),
        }
    )


class LaunchAgent:
    def plist_path(self) -> Path:
        return Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"

    def log_path(self) -> Path:
        return Path.home() / "Library" / "Logs" / "htb-presence.log"

    def _domain(self) -> str:
        return f"gui/{os.getuid()}"

    def install(self) -> str:
        path = self.plist_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path().parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(launchd_plist(sys.executable, self.log_path()))
        # Reload if a previous version is loaded; ignore "not loaded" errors.
        _run(["launchctl", "bootout", self._domain(), str(path)], check=False)
        _run(["launchctl", "bootstrap", self._domain(), str(path)])
        return f"Installed LaunchAgent at {path}.\nLogs: {self.log_path()}"

    def uninstall(self) -> str:
        path = self.plist_path()
        if not path.exists():
            return "The LaunchAgent is not installed."
        _run(["launchctl", "bootout", self._domain(), str(path)], check=False)
        path.unlink()
        return f"Removed {path}."

    def is_installed(self) -> bool:
        return self.plist_path().exists()

    def describe(self) -> str:
        return f"LaunchAgent ({self.plist_path()})"


def log_file_hint() -> str | None:
    """Where logs go for the autostarted process on this platform, if known."""
    if sys.platform.startswith("linux"):
        return f"journalctl --user -u {SERVICE_NAME} -f"
    if sys.platform == "win32":
        return str(config_dir() / "htb-presence.log")
    if sys.platform == "darwin":
        return str(LaunchAgent().log_path())
    return None
