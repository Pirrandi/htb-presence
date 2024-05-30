<h1 align="center">htb-presence.py</h1>
<h3 align="center">RichPresence for HackTheBox, a NON-official project.</h3>
<p align="center">Feel free to make any constructive criticism and/or contribute to the development.</p>

## Functionality

- Automatically detects when the user is connected to the HackTheBox VPN and shows a "Waiting" status using RichPressence.
  
  ![](https://i.imgur.com/lkAXh34.png)
  
- Automatically detects when the user is connected to a HackTheBox Machine.
  
  ![](https://i.imgur.com/Wvn9x3m.png)
 
- Automatically detects if the user has captured the User or Root Flag.
  
  ![](https://i.imgur.com/yJrS94P.png)


## Requirements
#### It's necessary to execute it on the machine where Discord is running.
In order to work, `htb-presence.py` needs the following libraries:

- `PyPresence-htb` Fork for this project https://github.com/Pirrandi/pypresence-htb
- `psutil`
- `requests`
- `python-dotenv`

Which can be installed using `pip3 install -r requirements.txt`.


## Configuration
In order to work, `.env.example` needs to be renamed to `.env` and needs access to the user's HackTheBox account. That is achieved by using an __App Token__, which can be created from the HackTheBox's Public Information section inside the Profile Settings tab. Once the Token is created, it must be pasted into the variable `HTB_API_TOKEN` in the `.env`.

### Self-hosted Discord Bot
In case you want to host your own Discord Bot, you can create it from the Discord Developer Portal and even include your own images. If you decide to do so, the `client_id` variable must be set to the new bot's ID Token, **not user's**. Otherwise, leave it as it is.

**WARNING**: Having a self-hosted bot does NOT affect privacy, since the Bot's Public ID is being used, as if it were an User's Public ID. The ID can be retrieved right-clicking an user or bot with the Discord Developer Mode enabled in Settings > Advanced > Developer Mode.

![image](https://i.imgur.com/79Insfc.png)

### Translations
Translations exist for both English (`EN`) and Spanish (`ES`), the default language is English but can be changed in the `.env` by changing the `LANG` key to either `ES` or `EN`.


## Service Creation and Startup Execution
In order to work, `htb-presence.py` needs to be executed manually. Furthermore, Discord needs to be installed and running at all times. To solve this tedious task and error-prone, a setup script `setup.sh` is available, which needs to be executed with `sudo bash setup.sh`.

The script will copy the executable `htb-presence.py` to the directory `/usr/local/bin/` and will create two service configuration files, `/etc/systemd/system/discord.service` and `/etc/systemd/system/htb-presence.service`. Then, it will start those services and enable them so they will be executed when the machine is started and won't be necessary to repeat the process manually.

If you don't have Discord installed, please refer to Google.


## Bugs and errors
If you encounter any type of bug or error, feel free to open an **Issue** in the repository.


## Credits
This RichPresence was built using the **[HTB v4 API Documentation](https://github.com/Propolisa/htb-api-docs)**


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
