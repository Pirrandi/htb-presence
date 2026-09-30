"""Command-line interface: ``htb-presence [run|setup|install|uninstall|status]``."""

from __future__ import annotations

import argparse
import getpass
import logging
import logging.handlers
import signal
import sys
from collections.abc import Sequence

from htb_presence import __version__, app, autostart
from htb_presence.config import (
    ALL_KEYS,
    KEY_LANG,
    KEY_TOKEN,
    ConfigError,
    config_dir,
    config_path,
    load_settings,
    read_config_file,
    write_config_file,
)
from htb_presence.htb import HTBAuthError, HTBClient, HTBError
from htb_presence.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from htb_presence.lock import AlreadyRunningError, SingleInstanceLock

log = logging.getLogger("htb_presence")

TOKEN_HELP = "Create one on Hack The Box: Profile Settings -> App Tokens."


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    _setup_logging(args.verbose)
    return args.func(args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="htb-presence", description="Discord Rich Presence for Hack The Box."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug logs")
    parser.set_defaults(func=cmd_run)

    sub = parser.add_subparsers(title="commands", metavar="COMMAND")
    commands = [
        ("run", cmd_run, "run the presence in the foreground (default)"),
        ("setup", cmd_setup, "save your HTB App Token and language"),
        ("install", cmd_install, "start automatically when you log in"),
        ("uninstall", cmd_uninstall, "remove the automatic start"),
        ("status", cmd_status, "show configuration and autostart state"),
    ]
    for name, func, help_text in commands:
        cmd = sub.add_parser(name, help=help_text, description=help_text)
        cmd.add_argument("-v", "--verbose", action="store_true", default=argparse.SUPPRESS)
        cmd.set_defaults(func=func)
    return parser


def _setup_logging(verbose: bool) -> None:
    if sys.stderr is not None:
        handler: logging.Handler = logging.StreamHandler()
    else:  # pythonw.exe (Windows autostart) has no console
        config_dir().mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            config_dir() / "htb-presence.log", maxBytes=1_000_000, backupCount=1, encoding="utf-8"
        )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    if not verbose:
        logging.getLogger("urllib3").setLevel(logging.WARNING)


# --- run --------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        log.error("%s", exc)
        return app.EXIT_BAD_CONFIG

    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _raise_keyboard_interrupt)

    try:
        with SingleInstanceLock():
            return app.run(settings)
    except AlreadyRunningError as exc:
        log.error("%s", exc)
        return 1


def _raise_keyboard_interrupt(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


# --- setup ------------------------------------------------------------------


def cmd_setup(args: argparse.Namespace) -> int:
    path = config_path()
    existing = read_config_file(path)
    try:
        token = _prompt_token(existing.get(KEY_TOKEN, ""))
        lang = _prompt_lang(existing.get(KEY_LANG, DEFAULT_LANGUAGE))
    except (EOFError, KeyboardInterrupt):
        print("\nAborted; nothing was saved.")
        return 1

    try:
        user = HTBClient(token).get_user()
        print(f"Token OK: logged in as {user.name}.")
    except HTBAuthError as exc:
        print(f"{exc} Nothing was saved. {TOKEN_HELP}")
        return 1
    except HTBError as exc:
        print(f"Warning: could not verify the token right now ({exc}). Saving it anyway.")

    values = {**existing, KEY_TOKEN: token, KEY_LANG: lang}
    ordered = {k: values[k] for k in ALL_KEYS if k in values}
    ordered.update({k: v for k, v in values.items() if k not in ordered})
    try:
        write_config_file(path, ordered)
    except (ConfigError, OSError) as exc:
        print(f"Could not write {path}: {exc}")
        return 1
    print(f"Saved configuration to {path}")
    print("Next: run 'htb-presence install' to start it automatically at login.")
    return 0


def _prompt_token(current: str) -> str:
    print(f"HTB App Token. {TOKEN_HELP}")
    suffix = " (leave empty to keep the current one)" if current else ""
    while True:
        token = getpass.getpass(f"Token{suffix}: ").strip()
        if token:
            return token
        if current:
            return current
        print("The token cannot be empty.")


def _prompt_lang(current: str) -> str:
    options = "/".join(SUPPORTED_LANGUAGES)
    current = current.lower() if current.lower() in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    while True:
        lang = input(f"Language [{options}] (default {current}): ").strip().lower() or current
        if lang in SUPPORTED_LANGUAGES:
            return lang
        print(f"Choose one of: {options}.")


# --- install / uninstall / status -------------------------------------------


def cmd_install(args: argparse.Namespace) -> int:
    try:
        load_settings()
    except ConfigError as exc:
        print(f"{exc}\nRun 'htb-presence setup' first.")
        return 1
    try:
        print(autostart.install())
    except autostart.AutostartError as exc:
        print(f"Could not install autostart: {exc}")
        return 1
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    try:
        print(autostart.uninstall())
    except autostart.AutostartError as exc:
        print(f"Could not remove autostart: {exc}")
        return 1
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    path = config_path()
    print(f"Config file : {path} ({'found' if path.is_file() else 'missing'})")
    try:
        settings = load_settings(require_token=False)
    except ConfigError as exc:
        print(f"Config error: {exc}")
    else:
        print(f"Token       : {'set' if settings.token else 'NOT SET'}")
        print(f"Language    : {settings.lang}")
        print(f"Client ID   : {settings.client_id}")
        print(f"Interval    : {settings.interval}s")
    try:
        state = "installed" if autostart.is_installed() else "not installed"
        print(f"Autostart   : {state} - {autostart.describe()}")
    except autostart.AutostartError as exc:
        print(f"Autostart   : {exc}")
    hint = autostart.log_file_hint()
    if hint:
        print(f"Logs        : {hint}")
    return 0
