<h1 align="center">htb-presence</h1>
<p align="center">Show what you are hacking on Hack The Box in your Discord status.<br/>A <b>non-official</b> project.</p>
<p align="center"><a href="README-ES.md">Leer en español</a></p>

| Waiting for a machine | Working on a machine | Flags captured |
|:---:|:---:|:---:|
| ![Waiting](https://i.imgur.com/lkAXh34.png) | ![Machine](https://i.imgur.com/Wvn9x3m.png) | ![Flags](https://i.imgur.com/yJrS94P.png) |

## Features

- **Waiting status** when you are connected to the HTB VPN but have no active machine.
- **Machine status** with the machine name, its avatar and a timer since you started it.
- **Flag tracking**: User and Root flags shown as 🟢 (owned) or 🔴 (pending).
- **Runs in the background** on Linux, Windows and macOS, and survives Discord restarts.
- English and Spanish.

## Quick start

You need **Python 3.9 or newer** and the **Discord desktop app** running on the same computer and user account.

1. Install [pipx](https://pipx.pypa.io/) (or [uv](https://docs.astral.sh/uv/)) and then htb-presence:

   ```bash
   pipx install git+https://github.com/Pirrandi/htb-presence
   # or: uv tool install git+https://github.com/Pirrandi/htb-presence
   ```

2. Save your HTB App Token and language (see [Getting an App Token](#getting-an-app-token)):

   ```bash
   htb-presence setup
   ```

3. Start it automatically every time you log in:

   ```bash
   htb-presence install
   ```

Done. Spawn a machine on Hack The Box and check your Discord profile.

| System | What `install` does |
|---|---|
| Linux | Creates a systemd **user** service (`~/.config/systemd/user/htb-presence.service`). No root needed. |
| Windows | Adds a login entry under `HKCU\...\CurrentVersion\Run` that runs without a console window. |
| macOS | Creates a LaunchAgent (`~/Library/LaunchAgents/com.github.pirrandi.htb-presence.plist`). |

Prefer to run it by hand? Just run `htb-presence` in a terminal and stop it with `Ctrl+C`.

## Getting an App Token

1. Log in to Hack The Box.
2. Open **Profile Settings → App Tokens**.
3. Create a token and paste it when `htb-presence setup` asks for it.

The token is stored only on your computer, in a file readable by your user alone.

## Configuration

`htb-presence setup` writes a config file for you. Run `htb-presence status` to see where it is.

| System | Config file |
|---|---|
| Linux | `~/.config/htb-presence/config.env` (respects `$XDG_CONFIG_HOME`) |
| Windows | `%APPDATA%\htb-presence\config.env` |
| macOS | `~/Library/Application Support/htb-presence/config.env` |

| Key | Default | Description |
|---|---|---|
| `HTB_API_TOKEN` | *(required)* | Your HTB App Token. |
| `HTB_PRESENCE_LANG` | `en` | Presence language: `en` or `es`. |
| `HTB_PRESENCE_INTERVAL` | `30` | Seconds between HTB checks (minimum `15`). |
| `DISCORD_CLIENT_ID` | `1125543074861432864` | Discord application ID. Change only for a [custom app](#using-your-own-discord-application). |

Environment variables with the same names override the file. See [`config.env.example`](config.env.example) for a template.

## Commands

| Command | What it does |
|---|---|
| `htb-presence` / `htb-presence run` | Run in the foreground. |
| `htb-presence setup` | Save your token and language. |
| `htb-presence install` | Start automatically at login (and start now). |
| `htb-presence uninstall` | Remove the automatic start. |
| `htb-presence status` | Show config file, token state and autostart state. |
| `-v`, `--verbose` | Show debug logs (works with any command). |

## Troubleshooting

| Problem | Fix |
|---|---|
| Nothing shows in Discord | Discord must be the **desktop app**, running on the same computer and user. Check *Settings → Activity Privacy → Share your detected activities*. |
| Presence missing after reboot | Enable Discord's own **Open Discord on startup** (Settings → Windows/Linux Settings). htb-presence waits for Discord and connects when it appears. |
| "HTB rejected the API token" | The token is invalid or expired. Create a new one and run `htb-presence setup` again. |
| Checking logs | Linux: `journalctl --user -u htb-presence -f`. Windows: `%APPDATA%\htb-presence\htb-presence.log`. macOS: `~/Library/Logs/htb-presence.log`. Or run `htb-presence -v` in a terminal. |
| "Another instance is already running" | htb-presence is already running (probably the autostart). Use `htb-presence uninstall` if you want to run it by hand. |

## Using your own Discord application

You can use your own Discord application, for example to show your own images or name.

1. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Copy its **Application ID** (with Developer Mode enabled in *Settings → Advanced*, you can also right-click it to copy the ID).
3. Set it as `DISCORD_CLIENT_ID` in your config file and restart htb-presence.

The application ID is public; using your own app does not affect your privacy.

![Discord Developer Mode](https://i.imgur.com/79Insfc.png)

## Uninstall

```bash
htb-presence uninstall
pipx uninstall htb-presence   # or: uv tool uninstall htb-presence
```

Then delete the config folder listed in [Configuration](#configuration) if you want to remove your token too.

## Upgrading from the old script

Older versions were a single `htb-presence.py` with `setup.sh` / `setup.bat` and a `.env` file.

- Run `htb-presence setup` again; the `.env` file is no longer read.
- On Linux, remove the old root services: `sudo systemctl disable --now htb-presence discord` and delete `/etc/systemd/system/htb-presence.service`, `/etc/systemd/system/discord.service` and `/usr/local/bin/htb-presence/`.
- On Windows, delete `htb-presence-startup.bat` from your Startup folder.
- The [pypresence-htb](https://github.com/Pirrandi/pypresence-htb) fork is no longer needed: htb-presence now uses the official [pypresence](https://github.com/qwertyquerty/pypresence) library.

## Bugs and contributions

Found a bug or have an idea? Open an [issue](https://github.com/Pirrandi/htb-presence/issues). Constructive feedback and pull requests are welcome.

Development setup:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Credits

Built using the community **[HTB API documentation](https://github.com/Propolisa/htb-api-docs)**.

## Acknowledgments

<table>
    <tr>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/Pirrandi">
                <img src="https://avatars.githubusercontent.com/Pirrandi?v=3?s=100" width="100px;" alt="Pirrandi" />
                <br />
                <sub><b>Pirrandi</b>
            </a>
            <br />
            <sub>Main script creation and Spanish Docs
        </td>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/wh0crypt">
                <img src="https://avatars.githubusercontent.com/wh0crypt?v=3?s=100" width="100px;" alt="wh0crypt" />
                <br />
                <sub><b>wh0crypt</b>
            </a>
            <br />
            <sub>Setup script creation and English Docs
        </td>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/sealldeveloper">
                <img src="https://avatars.githubusercontent.com/sealldeveloper?v=3?s=100" width="100px;" alt="sealldeveloper" />
                <br />
                <sub><b>sealldeveloper</b>
            </a>
            <br />
            <sub>Additional code improvements
        </td>
    </tr>
</table>

## Disclaimer

This is a **non-official** project. It is not affiliated with, endorsed by or supported by Hack The Box or Discord.
