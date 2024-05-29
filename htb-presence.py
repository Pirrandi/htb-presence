#!/usr/bin/env python3

## htb-presence.py - RichPresence for HackTheBox on Discord
## Author: @Pirrandi (https://github.com/Pirrandi)
## Translator: @wh0crypt (https://github.com/wh0crypt)

from translations.en import *  # English translations
#from translations.es import * # Traducciones en Español
from pypresence import Presence
import psutil
import requests
import time
import os
import sys
import atexit
import traceback


lock_file = '/tmp/test.py.lock'

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
client_id = '1125543074861432864' # Default Client ID, do NOT change unless you want to configure your own Discord App/Bot
htb_api_token = 'HTB Token Here'
connection=0

test=1
while test==1:
    def is_discord_open():
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if 'discord' in process.info['name'].lower():
                return 1
        return 0
    discord_status= is_discord_open()
    print(discord_status)

    if is_discord_open():
        print(discord_running_str)
    else:
        print(discord_not_running_str)

    while is_discord_open():
        # HackTheBox API configuration
        htb_machine_api = 'https://www.hackthebox.com/api/v4/machine/active'
        htb_user_api = 'https://www.hackthebox.com/api/v4/user/info'
        htb_connection_api = 'https://www.hackthebox.com/api/v4/user/connection/status'

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
                
                time.sleep(1)
                closeDiscord_clearRPC_status()
                # Retrieve the Active Machine's information from HackTheBox
                response_machine = requests.get(htb_machine_api, headers=headers)
                response_user = requests.get(htb_user_api, headers=headers)
                response_connection = requests.get(htb_connection_api, headers=headers)

                if RPC_status == 0:
                    print(connecting_rpc_str)

                    RPC.connect()
                    RPC_status=1
                    print(connected_rpc_str)
                
                if response_machine.status_code == 200:
                    data_machine = response_machine.json()
                    data_user = response_user.json()
                    data_connection = response_connection.json()
                    
                    connection = data_connection['status']
                    if data_machine:
                        user = data_user['info']
                        user_nickname = user['name']
                        user_avatar = user['avatar']
                        user_avatar = f"https://www.hackthebox.com{user['avatar']}"
                        print(user_info_retrieved_str)
                        print(discord_status)
                        print(RPC_status)
                        if discord_status==1 and connection == True and RPC_status == 1 and active_machine_name == None:
                            print(updating_rp_str)
                            RPC.update(
                                    details=connected_htb_str,
                                    state=waiting_state_str,
                                    large_image=htb_logo,
                                    large_text="Hack The Box",
                                    small_image=user_avatar,
                                    small_text=user_nickname,
                                    buttons=buttons
                                )                        
                        
                        machine = data_machine['info']
                        machine_name = machine['name']
                        machine_avatar = machine['avatar']
                        machine_avatar = f"https://www.hackthebox.com{machine['avatar']}"
                        print(machine_info_retrieved_str)
                        
                        ###
                        htb_get_api = f"https://www.hackthebox.com/api/v4/profile/activity/{user['id']}"
                        response_activity = requests.get(htb_get_api, headers=headers)
                        data_activity = response_activity.json()
                        print(apis_connected_str)

                        pwned = "🟢"
                        no_pwned = "🔴"
                        has_root = False
                        has_user = False

                        for record in data_activity["profile"]["activity"]:
                            if record["name"] == machine_name:
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
                        print(machine_found_str)
                        RPC.update(
                                details=machine_str+machine_name,
                                large_image=machine_avatar,
                                large_text="Hack The Box",
                                small_image=user_avatar,
                                small_text=user_nickname,
                                state=f"User: {user_flag} | Root: {root_flag}",
                                start=start_time
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
                                small_image=user_avatar,
                                small_text=user_nickname,
                                state=f"User: {user_flag} | Root: {root_flag}",
                                start=start_time
                            )
                    else:
                        active_machine_name = None
                        print(cleaning_rpc_str)
                        RPC.clear()
                else:
                    print(request_error_str+response.status_code)
                
            except Exception as e:
                print(active_machine_warning_str)
                active_machine_name = None
                def is_discord_open():
                    for process in psutil.process_iter(attrs=['pid', 'name']):
                        if 'discord' in process.info['name'].lower():
                            return 1
                    return 0
                discord_status= is_discord_open()   
                
                if discord_status==1 and connection==False:
                    print(cleaning_rpc_str)              
                    RPC.clear()
                    continue
                if discord_status==0:
                    print(discord_not_running_str)
                    continue               
release_lock()           
