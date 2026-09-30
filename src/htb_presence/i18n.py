"""Strings shown in the Discord presence, per language."""

from __future__ import annotations

DEFAULT_LANGUAGE = "en"

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "machine_prefix": "Machine: ",
        "connected": "Connected to Hack The Box",
        "waiting": "State: Waiting",
        "button_label": "Get this Rich Presence",
    },
    "es": {
        "machine_prefix": "Máquina: ",
        "connected": "Conectado a Hack The Box",
        "waiting": "Estado: Esperando",
        "button_label": "Obtén este Rich Presence",
    },
}

SUPPORTED_LANGUAGES = tuple(STRINGS)


def translate(lang: str, key: str) -> str:
    """Return the string for ``key`` in ``lang``, falling back to English."""
    return STRINGS.get(lang, {}).get(key) or STRINGS[DEFAULT_LANGUAGE][key]
