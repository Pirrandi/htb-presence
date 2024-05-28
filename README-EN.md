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
- `PyPresence`
- `psutil`
- `requests`

Which can be installed using `pip3 install -r requirements.txt`.


## Configuration
In order to work, `htb-presence.py` needs access to the user's HackTheBox account. That is achieved by using an *App Token*, which can be created from the HackTheBox's Public Information section inside the Profile Settings tab. Once the Token is created, it must be pasted into the variable `htb_api_token`.

### Self-hosted Discord Bot
In case you want to host your own Discord Bot, you can create it from the Discord Developer Portal and even include your own images. If you decide to do so, the `client_id` variable must be set to the new bot's ID Token, **not user's**. Otherwise, leave it as it is.

**WARNING**: Having a self-hosted bot does NOT affect privacy, since the Bot's Public ID is being used, as if it were an User's Public ID. The ID can be retrieved right-clicking an user or bot with the Discord Developer Mode enabled in Settings > Advanced > Developer Mode.

![image](https://github.com/Pirrandi/htb-presence/assets/39172875/0ee75f6f-c7fb-416e-9766-4e0266453bea)

### Translations
In the first two lines of the file `htb-presence.py` Spanish and English strings are imported, being this second option the default one. In case of wanting to change them to the Spanish ones, the line `from translations.en import *` must be commented and the line `from translations.es import *` must be uncommented.


## Service Creation and Startup Execution
In order to work, `htb-presence.py` needs to be executed manually. Furthermore, Discord needs to be installed and running at all times. To solve this tedious task and error-prone, a setup script `setup.sh` is available, which needs to be executed with `sudo bash setup.sh`.

The script will copy the executable `htb-presence.py` to the directory `/usr/local/bin/` and will create two service configuration files, `/etc/systemd/system/discord.service` and `/etc/systemd/system/htb-presence.service`. Then, it will start those services and enable them so they will be executed when the machine is started and won't be necessary to repeat the process manually.

If you don't have Discord installed, please refer to Google.


## Bugs and errors
If you encounter any type of bug or error, feel free to open an **Issue** in the repository.


## Credits
This RichPresence was built using the **[HTB v4 API Documentation](https://github.com/Propolisa/htb-api-docs)**


## Acknowledgments
- [@Pirrandi](https://github.com/Pirrandi) - Main script creation and Spanish Docs
- [@wh0crypt](https://github.com/wh0crypt) - Setup script creation and English Docs
