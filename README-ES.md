<h1 align="center">htb-presence</h1>
<p align="center">Muestra en tu estado de Discord en qué estás trabajando en Hack The Box.<br/>Proyecto <b>no oficial</b>.</p>
<p align="center"><a href="README.md">Read in English</a></p>

| Esperando una máquina | Trabajando en una máquina | Flags capturadas |
|:---:|:---:|:---:|
| ![Esperando](https://i.imgur.com/lkAXh34.png) | ![Máquina](https://i.imgur.com/Wvn9x3m.png) | ![Flags](https://i.imgur.com/yJrS94P.png) |

## Funcionalidades

- **Estado de espera** cuando está conectado a la VPN de HTB sin una máquina activa.
- **Estado de máquina** con el nombre, su imagen y un temporizador desde que se inició.
- **Seguimiento de flags**: las flags User y Root se muestran como 🟢 (obtenida) o 🔴 (pendiente).
- **Se ejecuta en segundo plano** en Linux, Windows y macOS, y se recupera si Discord se reinicia.
- Inglés y español.

## Inicio rápido

Se necesita **Python 3.9 o superior** y la **aplicación de escritorio de Discord** abierta en el mismo equipo y con el mismo usuario.

1. Instale [pipx](https://pipx.pypa.io/) (o [uv](https://docs.astral.sh/uv/)) y después htb-presence:

   ```bash
   pipx install git+https://github.com/Pirrandi/htb-presence
   # o bien: uv tool install git+https://github.com/Pirrandi/htb-presence
   ```

2. Guarde su App Token de HTB y el idioma (consulte [Obtener un App Token](#obtener-un-app-token)):

   ```bash
   htb-presence setup
   ```

3. Configure el inicio automático al iniciar sesión:

   ```bash
   htb-presence install
   ```

Listo. Inicie una máquina en Hack The Box y revise su perfil de Discord.

| Sistema | Qué hace `install` |
|---|---|
| Linux | Crea un servicio systemd **de usuario** (`~/.config/systemd/user/htb-presence.service`). No requiere root. |
| Windows | Agrega una entrada de inicio en `HKCU\...\CurrentVersion\Run` que se ejecuta sin ventana de consola. |
| macOS | Crea un LaunchAgent (`~/Library/LaunchAgents/com.github.pirrandi.htb-presence.plist`). |

¿Prefiere ejecutarlo manualmente? Ejecute `htb-presence` en una terminal y deténgalo con `Ctrl+C`.

## Obtener un App Token

1. Inicie sesión en Hack The Box.
2. Abra **Profile Settings → App Tokens**.
3. Cree un token y péguelo cuando `htb-presence setup` lo solicite.

El token se guarda solo en su equipo, en un archivo que únicamente su usuario puede leer.

## Configuración

`htb-presence setup` crea el archivo de configuración. Ejecute `htb-presence status` para ver su ubicación.

| Sistema | Archivo de configuración |
|---|---|
| Linux | `~/.config/htb-presence/config.env` (respeta `$XDG_CONFIG_HOME`) |
| Windows | `%APPDATA%\htb-presence\config.env` |
| macOS | `~/Library/Application Support/htb-presence/config.env` |

| Clave | Valor por defecto | Descripción |
|---|---|---|
| `HTB_API_TOKEN` | *(obligatorio)* | Su App Token de HTB. |
| `HTB_PRESENCE_LANG` | `en` | Idioma del estado: `en` o `es`. |
| `HTB_PRESENCE_INTERVAL` | `30` | Segundos entre consultas a HTB (mínimo `15`). |
| `DISCORD_CLIENT_ID` | `1125543074861432864` | ID de la aplicación de Discord. Cámbielo solo si usa una [aplicación propia](#usar-una-aplicación-de-discord-propia). |

Las variables de entorno con el mismo nombre tienen prioridad sobre el archivo. Consulte [`config.env.example`](config.env.example) como plantilla.

## Comandos

| Comando | Qué hace |
|---|---|
| `htb-presence` / `htb-presence run` | Ejecuta en primer plano. |
| `htb-presence setup` | Guarda el token y el idioma. |
| `htb-presence install` | Activa el inicio automático (y lo inicia ahora). |
| `htb-presence uninstall` | Elimina el inicio automático. |
| `htb-presence status` | Muestra el archivo de configuración, el estado del token y del inicio automático. |
| `-v`, `--verbose` | Muestra logs de depuración (con cualquier comando). |

## Solución de problemas

| Problema | Solución |
|---|---|
| No aparece nada en Discord | Discord debe ser la **aplicación de escritorio**, abierta en el mismo equipo y usuario. Revise *Ajustes → Privacidad de actividad → Compartir tu actividad detectada*. |
| El estado no aparece tras reiniciar | Active la opción de Discord **Abrir Discord al iniciar el equipo**. htb-presence espera a Discord y se conecta cuando está disponible. |
| "HTB rejected the API token" | El token es inválido o expiró. Cree uno nuevo y ejecute `htb-presence setup` otra vez. |
| Revisar los logs | Linux: `journalctl --user -u htb-presence -f`. Windows: `%APPDATA%\htb-presence\htb-presence.log`. macOS: `~/Library/Logs/htb-presence.log`. O ejecute `htb-presence -v` en una terminal. |
| "Another instance is already running" | htb-presence ya se está ejecutando (probablemente por el inicio automático). Use `htb-presence uninstall` si prefiere ejecutarlo manualmente. |

## Usar una aplicación de Discord propia

Puede usar su propia aplicación de Discord, por ejemplo para mostrar otras imágenes o nombre.

1. Cree una aplicación en el [Discord Developer Portal](https://discord.com/developers/applications).
2. Copie su **Application ID** (con el Modo desarrollador activado en *Ajustes → Avanzado*, también puede copiarlo con clic derecho).
3. Defínalo como `DISCORD_CLIENT_ID` en el archivo de configuración y reinicie htb-presence.

El ID de la aplicación es público; usar una aplicación propia no afecta su privacidad.

![Modo desarrollador de Discord](https://i.imgur.com/79Insfc.png)

## Desinstalación

```bash
htb-presence uninstall
pipx uninstall htb-presence   # o bien: uv tool uninstall htb-presence
```

Después, elimine la carpeta de configuración indicada en [Configuración](#configuración) si también desea borrar su token.

## Actualizar desde el script anterior

Las versiones anteriores eran un único `htb-presence.py` con `setup.sh` / `setup.bat` y un archivo `.env`.

- Ejecute `htb-presence setup` de nuevo; el archivo `.env` ya no se utiliza.
- En Linux, elimine los servicios antiguos de root: `sudo systemctl disable --now htb-presence discord` y borre `/etc/systemd/system/htb-presence.service`, `/etc/systemd/system/discord.service` y `/usr/local/bin/htb-presence/`.
- En Windows, borre `htb-presence-startup.bat` de la carpeta de Inicio.
- El fork [pypresence-htb](https://github.com/Pirrandi/pypresence-htb) ya no es necesario: htb-presence ahora usa la librería oficial [pypresence](https://github.com/qwertyquerty/pypresence).

## Errores y contribuciones

¿Encontró un error o tiene una idea? Abra un [issue](https://github.com/Pirrandi/htb-presence/issues). Las críticas constructivas y los pull requests son bienvenidos.

Entorno de desarrollo:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Créditos

Desarrollado con la **[documentación comunitaria de la API de HTB](https://github.com/Propolisa/htb-api-docs)**.

## Agradecimientos

<table>
    <tr>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/Pirrandi">
                <img src="https://avatars.githubusercontent.com/Pirrandi?v=3?s=100" width="100px;" alt="Pirrandi" />
                <br />
                <sub><b>Pirrandi</b>
            </a>
            <br />
            <sub>Creación del script principal y documentación en español
        </td>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/wh0crypt">
                <img src="https://avatars.githubusercontent.com/wh0crypt?v=3?s=100" width="100px;" alt="wh0crypt" />
                <br />
                <sub><b>wh0crypt</b>
            </a>
            <br />
            <sub>Creación del script de instalación y documentación en inglés
        </td>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/sealldeveloper">
                <img src="https://avatars.githubusercontent.com/sealldeveloper?v=3?s=100" width="100px;" alt="sealldeveloper" />
                <br />
                <sub><b>sealldeveloper</b>
            </a>
            <br />
            <sub>Mejoras adicionales de código
        </td>
    </tr>
</table>

## Aviso

Este es un proyecto **no oficial**. No está afiliado, respaldado ni soportado por Hack The Box ni por Discord.
