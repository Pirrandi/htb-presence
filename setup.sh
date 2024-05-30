#!/bin/bash

## Setup script for htb-presence.py
## Author: @wh0crypt

# Copy htb-presence.py to /usr/local/bin/
sudo mkdir /usr/local/bin/htb-presence/
sudo mkdir /usr/local/bin/htb-presence/translations/
sudo cp ./htb-presence.py /usr/local/bin/htb-presence/
sudo cp ./.env /usr/local/bin/htb-presence/
sudo cp ./translations/en.py /usr/local/bin/htb-presence/translations/
sudo cp ./translations/es.py /usr/local/bin/htb-presence/translations/

# Modify the service files with the users' username
sed -i "s/^User=/User=$USER/" "conf/discord.service"
sed -i "s/^User=/User=$USER/" "conf/htb-presence.service"

# Copy service files to /etc/systemd/system/
sudo cp ./conf/discord.service /etc/systemd/system/
sudo cp ./conf/htb-presence.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/htb-presence.service
sudo chmod 644 /etc/systemd/system/discord.service

# Reload daemons and start/enable services
sudo systemctl daemon-reload
sudo systemctl start discord
sudo systemctl enable discord
sudo systemctl start htb-presence
sudo systemctl enable htb-presence
