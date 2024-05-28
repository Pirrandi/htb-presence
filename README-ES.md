<h1 align="center">htb-presence.py</h1>
<h3 align="center">RichPresence para HackTheBox, este proyecto NO es oficial.</h3>
<p align="center">Siéntete libre de hacer alguna crítica constructiva, y/o aportar al desarrollo.</p>

## Funciones

- Detecta automaticamente cuando estas conectado a la VPN de HackTheBox, y te pone en estado de "Espera" por RichPresence.
  
  ![](https://i.imgur.com/lkAXh34.png)
  
- Detecta automaticamente cuando estas conectado a una maquina de HackTheBox.
  
  ![](https://i.imgur.com/Wvn9x3m.png)
  
- Detecta automaticamente si has conseguido la User Flag o la Root Flag
  
  ![](https://i.imgur.com/yJrS94P.png)

## Requisitos
#### Es necesario ejecutarlo en la misma maquina que tiene instalado Discord.
Para poder funcionar, `htb-presence.py` necesita las siguientes librerías:
- `PyPresence`
- `psutil`
- `requests`

Las cuales pueden ser instaladas usando `pip3 install -r requirements.txt`.


## Configuración
Para poder funcionar, `htb-presence.py` necesita acceso a la cuenta de HackTheBox del usuario. Esto se consigue usando un *App Token*, que puede ser creado desde la sección de Public Information dentro de la pestaña de Profile Settings de HackTheBox. Una vez que se haya creado el Token, debe ser pegado dentro de la variable `htb_api_token`.

### Bot de Discord Auto-Hosteado
En el caso de que se quiera hostear un Bot de Discord propio, puede crearse desde el Portal de Desarrolladores de Discord e incluso incluir imágenes propias. Si se decide hacerlo, la variable `client_id` debe cambiarse al Token ID del nuevo bot, **no al del usuario**. Si no, no modificar.

**AVISO**: Tener un bot auto-hosteado NO afecta a la privacidad, ya que se usa el ID público del bot, como si fuera el ID público de un usuario. El ID se puede obtener haciendo click derecho sobre un usuario o bot con el Modo Desarrollador de Discord activado en Configuraciones > Avanzado > Modo Desarrollador.

![image](https://github.com/Pirrandi/htb-presence/assets/39172875/0ee75f6f-c7fb-416e-9766-4e0266453bea)

### Traducciones
En las dos primeras líneas del archivo `htb-presence.py` se importan las cadenas de texto en español e inglés, estando esta segunda opción por defecto. En caso de querer cadenas de texto en español, se debe comentar la línea `from translations.en import *` y descomentar la línea `from translations.es import *`.


## Creación de los Servicio y Ejecución en el Arranque
Para poder funcionar, `htb-presence.py` necesita ser ejecutado manualmente. Además, se necesita que Discord esté instalado y abierto en todo momento. Para solventar esta tediosa tarea y propensa a errores, se dispone del script de configuración `setup.sh`, que deberá ser ejecutado con `sudo bash setup.sh`.

Dicho script copiará el ejecutable `htb-presence.py` al directorio `/usr/local/bin/` y creará dos ficheros de configuración de servicio, `/etc/systemd/system/discord.service` y `/etc/systemd/system/htb-presence.service`. Luego, iniciará dichos servicios y los habilitará para que se ejecuten al arrancar la máquina y así no tener que repetir el proceso manualmente.

Si no se dispone de Discord instalado, por favor referirse a Google.


## Bugs y errores
Si encuentras algún bug o error, siéntete libre de abrir un **Issue** en el repositorio.


## Créditos
Este RichPresence se ha hecho con la **[HTB v4 API Documentation](https://github.com/Propolisa/htb-api-docs)**


## Reconocimientos
- [@Pirrandi](https://github.com/Pirrandi) - Creación del Script Principal y Doc. en Español
- [@wh0crypt](https://github.com/wh0crypt) - Creación del Script de Configuración y Doc. en Inglés
