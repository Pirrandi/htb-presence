#!/bin/bash

## Setup script for htb-presence.py
## Author: @wh0crypt

# Copy htb-presence.py to /usr/local/bin/
sudo cp ./htb-presence.py /usr/local/bin/

# Modify the service files with the users' username
sed -i "s/^User=/User=$USER/" "conf/discord.service"
sed -i "s/^User=/User=$USER/" "conf/htb-presence.service"

# Copy service files to /etc/systemd/system/
sudo cp ./conf/discord.service /etc/systemd/system/
sudo cp ./conf/htb-presence.service /etc/systemd/system/

# Reload daemons and start/enable services
sudo systemctl daemon-reload
sudo systemctl start discord
sudo systemctl enable discord
sudo systemctl start htb-presence
sudo systemctl enable htb-presence
