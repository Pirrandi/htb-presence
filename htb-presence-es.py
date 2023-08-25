import requests
import time
from pypresence import Presence


import psutil
import os
import sys
import atexit

lock_file = '/tmp/test.py.lock'

def acquire_lock():
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read())
                if pid_exists(pid):
                    print("Another instance is already running. Exiting.")
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


# Configuración de las APIs de Discord Rich Presence y Hack The Box
client_id = '1125543074861432864'
htb_api_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiNTY5MzM0NDAyNTFjNGU1NDBkODYwNzZjNzU3M2YzZDI2NGM0MWVkMjJlNGU0ZmVkM2MzZWE3Yzc0YzY1NmFjNzhiOWNlOTVhZGZjNTg5ODIiLCJpYXQiOjE2OTI4NjAwNzYuOTMzNzA1LCJuYmYiOjE2OTI4NjAwNzYuOTMzNzA4LCJleHAiOjE3MDg0MTU2NzYuOTI2NzQ1LCJzdWIiOiIxNTMzOTkxIiwic2NvcGVzIjpbIjJmYSJdfQ.zhBoe0uaFGy-KsMV4C5sITLxEOOFtXaJTNmYlmvyxtlnXyJ8tOJvL1x2TqfMN0N9SjvTgeqhBXg9-jZm-q-uuO5V1EY4H6CqLfUPdyr-1OZdSG7M3dLds92nGes96_NHeDC9Wi7bavbPH6q5vofG1t0EySb-_L-e2oei0sUIllYa8dLwieCsTe9xZcATrXUORHv6DNS1C9V4Ywf1VaA1mS_UmS0gp5TSI4nkjpV9djciUlbzjbr4CS1A4RqpaifrGKzHkJoCTV3_jeh6shk9Du1F9YfY4JWu7NYvQ9Na6MBbLTCr5Q1FsRVYRsIMOAKnayFZSrAE1fiSvAauTRXSV-GN-u6KSMM_5Xr2c8xF-9UGxhOYavmdqHFbWGFfXt4rV-Gxo8TYR6iSE-ItusXVBLcFlzSGOqApqCcKiV1J5cJo8_DENC4lnpAc3uMZOE7KKTK30kSUkh4F5Ii-1EJ5TPbLwFGG8AWxlVL0wpYR4eXnDj-1e_3ZSQC5gwl6-ymTalX2JvHZW4VxiAtTLxKTAYeEDXiGxD5b0M4f5pHvULGRKE59R9WQHvdjf1JU9KCLRyRgG9GCDu3m_UAb4odQ8UBmRDHSWJOhGLSJgci0PtrL1rDf1ud2qIsqTqZZNurgCH52j-8M2gCGN0O5B0og6CcAb0-jSh4GB7UXLVs4fjs'
RPC = Presence(client_id)
RPC_status=0
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
        print("Discord está abierto.")
    else:
        print("Discord no está abierto.")

    while is_discord_open():


        # Configuración de la API de Hack The Box
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
                'label': 'Trabajando en este RP ⚒️',
                'url': 'https://github.com/Pirrandi'
            }
        ]

        def closeDiscord_clearRPC_status():
            global RPC_status
            if discord_status==0:
                RPC_status=0
                
        # Variable para almacenar el nombre de la máquina activa
        active_machine_name = None
        # Loop para verificar y actualizar el estado constantemente
        start_time=1
        while is_discord_open:
            try:
                is_discord_open()
                
                time.sleep(1)
                closeDiscord_clearRPC_status()
                # Obtener la información de la máquina activa desde HTB
                response_machine = requests.get(htb_machine_api, headers=headers)
                response_user = requests.get(htb_user_api, headers=headers)
                response_connection = requests.get(htb_connection_api, headers=headers)

                if RPC_status == 0:
                    print("Conectando RPC...")
                    RPC.connect()
                    RPC_status=1
                    print("Conectado a RPC...")
                
                
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
                        print("User Info obtenida")
                        if discord_status==1 and connection == "1" and RPC_status == 1 and active_machine_name == None:
                            print("Actualizando Rich Presence...")
                            RPC.update(
                                    details=f"Conectado a HTB",
                                    state="Estado: Esperando",
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
                        print("Machine Info obtenida")
                        
                        ###
                        htb_get_api = f"https://www.hackthebox.com/api/v4/profile/activity/{user['id']}"
                        response_activity = requests.get(htb_get_api, headers=headers)
                        data_activity = response_activity.json()
                        print("Conectado a las APIs")

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
                        print('Maquina encontrada')
                        RPC.update(
                                details=f"Máquina: {machine_name}",
                                large_image=machine_avatar,
                                large_text="Hack The Box",
                                small_image=user_avatar,
                                small_text=user_nickname,
                                state=f"User: {user_flag} | Root: {root_flag}",
                                start=start_time
                        )
                        
                        # Verificar si la máquina ha cambiado
                        if machine_name != active_machine_name:
                            active_machine_name = machine_name

                            start_time = int(time.time())
                            
                            # Actualizar el estado de la Rich Presence
                            
                            RPC.update(
                                details=f"Máquina: {machine_name}",
                                large_image=machine_avatar, 
                                large_text="Hack The Box",
                                small_image=user_avatar,
                                small_text=user_nickname,
                                state=f"User: {user_flag} | Root: {root_flag}",
                                start=start_time
                            )
                    else:
                        active_machine_name = None
                        print("Limpiando RPC... 2")
                        RPC.clear()
                else:
                    print(f"Error en la solicitud HTB: {response.status_code}")
                
            except Exception as e:
                print(f"Advertencia: Esperando una maquina activa.")
                active_machine_name = None
                def is_discord_open():
                    for process in psutil.process_iter(attrs=['pid', 'name']):
                        if 'discord' in process.info['name'].lower():
                            return 1
                    return 0
                discord_status= is_discord_open()   

                if discord_status==1 and connection=="0":
                    print("Limpiando RPC...")
                    
                    RPC.clear()
                    continue
                if discord_status==0:
                    print("Discord esta cerrado.")
                    continue               
release_lock()           
