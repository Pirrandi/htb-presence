#!/bin/bash

## Setup script for htb-presence.py
## Author: @wh0crypt

# Copy htb-presence.py to /usr/local/bin/
sudo cp ./htb-presence.py /usr/local/bin/

# Copy service files to /etc/systemd/system/
sudo cp ./conf/discord.service /etc/systemd/system/
sudo cp ./conf/htb-presence.service /etc/systemd/system/

# Reload daemons and start/enable services
sudo systemctl daemon-reload
sudo systemctl start discord
sudo systemctl enable discord
sudo systemctl start htb-presence
sudo systemctl enable htb-presence
