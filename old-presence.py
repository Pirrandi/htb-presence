import requests
import time
from pypresence import Presence

# Configuración de las APIs de Discord Rich Presence y Hack The Box
client_id = '1125543074861432864'
htb_api_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiNTY5MzM0NDAyNTFjNGU1NDBkODYwNzZjNzU3M2YzZDI2NGM0MWVkMjJlNGU0ZmVkM2MzZWE3Yzc0YzY1NmFjNzhiOWNlOTVhZGZjNTg5ODIiLCJpYXQiOjE2OTI4NjAwNzYuOTMzNzA1LCJuYmYiOjE2OTI4NjAwNzYuOTMzNzA4LCJleHAiOjE3MDg0MTU2NzYuOTI2NzQ1LCJzdWIiOiIxNTMzOTkxIiwic2NvcGVzIjpbIjJmYSJdfQ.zhBoe0uaFGy-KsMV4C5sITLxEOOFtXaJTNmYlmvyxtlnXyJ8tOJvL1x2TqfMN0N9SjvTgeqhBXg9-jZm-q-uuO5V1EY4H6CqLfUPdyr-1OZdSG7M3dLds92nGes96_NHeDC9Wi7bavbPH6q5vofG1t0EySb-_L-e2oei0sUIllYa8dLwieCsTe9xZcATrXUORHv6DNS1C9V4Ywf1VaA1mS_UmS0gp5TSI4nkjpV9djciUlbzjbr4CS1A4RqpaifrGKzHkJoCTV3_jeh6shk9Du1F9YfY4JWu7NYvQ9Na6MBbLTCr5Q1FsRVYRsIMOAKnayFZSrAE1fiSvAauTRXSV-GN-u6KSMM_5Xr2c8xF-9UGxhOYavmdqHFbWGFfXt4rV-Gxo8TYR6iSE-ItusXVBLcFlzSGOqApqCcKiV1J5cJo8_DENC4lnpAc3uMZOE7KKTK30kSUkh4F5Ii-1EJ5TPbLwFGG8AWxlVL0wpYR4eXnDj-1e_3ZSQC5gwl6-ymTalX2JvHZW4VxiAtTLxKTAYeEDXiGxD5b0M4f5pHvULGRKE59R9WQHvdjf1JU9KCLRyRgG9GCDu3m_UAb4odQ8UBmRDHSWJOhGLSJgci0PtrL1rDf1ud2qIsqTqZZNurgCH52j-8M2gCGN0O5B0og6CcAb0-jSh4GB7UXLVs4fjs'

import psutil

def is_discord_open():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'discord' in process.info['name'].lower():
            return True
    return False

if is_discord_open():
    print("Discord está abierto.")
else:
    print("Discord no está abierto.")

while is_discord_open():
    
RPC = Presence(client_id)
RPC.connect()

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
        'label': 'Trabajando en este RP ⚒️ ',
        'url': 'https://github.com/Pirrandi'
    }
]


# Variable para almacenar el nombre de la máquina activa
active_machine_name = None

# Loop para verificar y actualizar el estado constantemente
start_time=1
while True:
    try:
        time.sleep(2)
        # Obtener la información de la máquina activa desde HTB
        response_machine = requests.get(htb_machine_api, headers=headers)
        response_user = requests.get(htb_user_api, headers=headers)
        response_connection = requests.get(htb_connection_api, headers=headers)
        

        
        
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

                
                
                machine = data_machine['info']
                machine_name = machine['name']
                machine_avatar = machine['avatar']
                machine_avatar = f"https://www.hackthebox.com{machine['avatar']}"
                
                
                ###
                htb_get_api = f"https://www.hackthebox.com/api/v4/profile/activity/{user['id']}"
                response_activity = requests.get(htb_get_api, headers=headers)
                data_activity = response_activity.json()
                
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
                RPC.clear()
        else:
            print(f"Error en la solicitud HTB: {response.status_code}")
        
    except Exception as e:
        print(f"Advertencia: Esperando una maquina activa.")
        active_machine_name = None

        if connection == "1":
            RPC.update(
                            details=f"Conectado a HTB",
                            state="Estado: Esperando",
                            large_image=htb_logo,
                            large_text="Hack The Box",
                            small_image=user_avatar,
                            small_text=user_nickname,
                            buttons=buttons
                            
                        )
        else:
            RPC.clear()
            continue