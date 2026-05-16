#!/usr/bin/env python3

## htb-presence.py - RichPresence for HackTheBox on Discord
## Author: @Pirrandi (https://github.com/Pirrandi)
## Translator: @wh0crypt (https://github.com/wh0crypt)
## Additional Contributions: @sealldev (https://github.com/sealldeveloper)

from pypresence import Presence
import psutil
import requests
import time
import os
import sys
import atexit
import traceback
from dotenv import load_dotenv
from tempfile import gettempdir
from pathlib import Path
from platform import system

# Load environment variables
load_dotenv()

# Load appropriate language
lang = os.getenv('LANGUAGE') if os.getenv('LANGUAGE') else 'EN' # default is english
if lang == 'EN':
    from translations.en import *
elif lang == 'ES':
    from translations.es import *


lock_file = os.path.join(Path("/tmp" if system() == "Darwin" else gettempdir()),'test.py.lock')

def acquire_lock():
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read())
                if pid_exists(pid):
                    print(another_instance_running_str)
                    sys.exit(1)
                else:
                    os.remove(lock_file)
        except Exception:
            pass
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

def release_lock():
    if os.path.exists(lock_file):
        os.remove(lock_file)

def pid_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

if __name__ == "__main__":
    atexit.register(release_lock)
    acquire_lock()



# HackTheBox and Discord APIs configuration
client_id = os.getenv('CLIENT_ID') if os.getenv('CLIENT_ID') else '1125543074861432864' # default is '1125543074861432864'
htb_base_url = 'https://labs.hackthebox.com'
htb_api_base_url = f'{htb_base_url}/api/v4'
htb_api_token = os.getenv('HTB_API_TOKEN') if os.getenv('HTB_API_TOKEN') else None
if not htb_api_token or htb_api_token == 'HTB_TOKEN_HERE':
    print(htb_api_token_not_set)
    sys.exit()
RPC_status=0
RPC = Presence(client_id)
connection=0

def htb_url(value):
    if not value:
        return value
    if value.startswith('http://') or value.startswith('https://'):
        return value
    return f'{htb_base_url}{value}'

test=1
while test==1:
    def is_discord_open():
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if 'discord' in process.info['name'].lower():
                return 1
        return 0
    discord_status= is_discord_open()
    if not discord_status:
        time.sleep(30)
        continue

    while is_discord_open():
        # HackTheBox API configuration
        htb_machine_api = f'{htb_api_base_url}/machine/active'
        htb_user_api = f'{htb_api_base_url}/user/info'
        htb_connection_api = f'{htb_api_base_url}/user/connection/status'

        headers = {
            'User-Agent': 'HTB Discord Rich Presence',
            'Authorization': f'Bearer {htb_api_token}'
        }

        # Media
        htb_logo = 'https://yt3.googleusercontent.com/ytc/AOPolaR5R7bueWAUHc7ctRNCy5r63xddkeL17RDHOwxAlw=s900-c-k-c0x00ffffff-no-rj'
        buttons = [
            {
                'label': label1_str,
                'url': url1_str
            },
            {
                'label': label2_str,
                'url': url2_str
            }
        ]
        def closeDiscord_clearRPC_status():
            global RPC_status
            if discord_status==0:
                RPC_status=0
                
        # Variable that stores the Active Machine's name
        active_machine_name = None
        # Loop for continuous state update and verification
        start_time=1
        while is_discord_open:
            try:
                is_discord_open()
                
                time.sleep(30)
                closeDiscord_clearRPC_status()
                # Retrieve the Active Machine's information from HackTheBox
                response_machine = requests.get(htb_machine_api, headers=headers)
                response_user = requests.get(htb_user_api, headers=headers)
                response_connection = requests.get(htb_connection_api, headers=headers)
                if RPC_status == 0:
                    RPC.connect()
                    RPC_status=1
                
                if response_machine.status_code == 200:
                    data_machine = response_machine.json()
                    data_user = response_user.json()
                    data_connection = response_connection.json()
                    
                    connection = data_connection['status']
                    if data_machine:
                        user = data_user['info']
                        user_nickname = user['name']
                        user_avatar = htb_url(user['avatar'])
                        if discord_status==1 and connection == True and RPC_status == 1 and active_machine_name == None:
                            RPC.update(
                                    details=connected_htb_str,
                                    state=waiting_state_str,
                                    large_image=htb_logo,
                                    large_text="Hack The Box",
                                    small_text=user_nickname,
                                    buttons=buttons
                                )                        
                        
                        machine = data_machine['info']
                        machine_name = machine['name']
                        machine_avatar = htb_url(machine['avatar'])
                        ###
                        htb_get_api = f"{htb_base_url}/api/v5/user/profile/activity/{user['id']}?per_page=5"
                        response_activity = requests.get(htb_get_api, headers=headers)
                        data_activity = response_activity.json()

                        pwned = "🟢"
                        no_pwned = "🔴"
                        has_root = False
                        has_user = False
                        activity_records = data_activity.get("data", [])

                        for record in activity_records:
                            if record["name"] == machine_name:
                                if record.get("avatar"):
                                    machine_avatar = htb_url(record["avatar"])
                                if record["type"] == "root":
                                    has_root = True
                                elif record["type"] == "user":
                                    has_user = True
                    
                        if has_root == True:
                            root_flag = pwned
                        else:
                            root_flag = no_pwned
                        if has_user == True:
                            user_flag = pwned

                        else:
                            user_flag = no_pwned
                        RPC.update(
                                details=machine_str+machine_name,
                                large_image=machine_avatar,
                                large_text="Hack The Box",
                                small_text=user_nickname,
                                state=f"User: {user_flag} | Root: {root_flag}"
                        )
                        
                        # Check if the machine has changed
                        if machine_name != active_machine_name:
                            active_machine_name = machine_name

                            start_time = int(time.time())
                            
                            # Update RichPresence's state
                            RPC.update(
                                details=machine_str+machine_name,
                                large_image=machine_avatar, 
                                large_text="Hack The Box",
                                small_text=user_nickname,
                                state=f"User: {user_flag} | Root: {root_flag}"
                            )
                    else:
                        active_machine_name = None
                        RPC.clear()

            except Exception as e:
                active_machine_name = None
                def is_discord_open():
                    for process in psutil.process_iter(attrs=['pid', 'name']):
                        if 'discord' in process.info['name'].lower():
                            return 1
                    return 0
                discord_status= is_discord_open()   
                
                if discord_status==1 and connection==False:
                    RPC.clear()
                    continue
                if discord_status==0:
                    time.sleep(30)
                    continue
release_lock()           
