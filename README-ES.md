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

- `PyPresence-htb` Fork para este proyecto https://github.com/Pirrandi/pypresence-htb
- `psutil`
- `requests`
- `python-dotenv`

Las cuales pueden ser instaladas usando `pip3 install -r requirements.txt`.


## Configuración
Para que funcione, `.env.example` debe ser renombrado a `.env` y necesita acceso a la cuenta de HackTheBox del usuario. Esto se logra utilizando un Token de Aplicación, que puede ser creado desde la sección de Información Pública de HackTheBox dentro de la pestaña de Configuración del Perfil. Una vez creado el Token, debe ser pegado en la variable `HTB_API_TOKEN` en el archivo `.env`.

### Bot de Discord Auto-Hosteado
En el caso de que se quiera hostear un Bot de Discord propio, puede crearse desde el Portal de Desarrolladores de Discord e incluso incluir imágenes propias. Si se decide hacerlo, la variable `client_id` debe cambiarse al Token ID del nuevo bot, **no al del usuario**. Si no, no modificar.

**AVISO**: Tener un bot auto-hosteado NO afecta a la privacidad, ya que se usa el ID público del bot, como si fuera el ID público de un usuario. El ID se puede obtener haciendo click derecho sobre un usuario o bot con el Modo Desarrollador de Discord activado en Configuraciones > Avanzado > Modo Desarrollador.

![image](https://i.imgur.com/79Insfc.png)

### Traducciones
Existen traducciones tanto para inglés (`EN`) como para español (`ES`), el idioma predeterminado es inglés pero se puede cambiar en el archivo .env modificando la clave `LANGUAGE` a `ES` o `EN`.


## Creación de los Servicio y Ejecución en el Arranque
Para poder funcionar, `htb-presence.py` necesita ser ejecutado manualmente. Además, se necesita que Discord esté instalado y abierto en todo momento. Para solventar esta tediosa tarea y propensa a errores, se dispone del script de configuración `setup.sh`, que deberá ser ejecutado con `sudo bash setup.sh`.

Dicho script copiará el ejecutable `htb-presence.py` al directorio `/usr/local/bin/` y creará dos ficheros de configuración de servicio, `/etc/systemd/system/discord.service` y `/etc/systemd/system/htb-presence.service`. Luego, iniciará dichos servicios y los habilitará para que se ejecuten al arrancar la máquina y así no tener que repetir el proceso manualmente.

Si no se dispone de Discord instalado, por favor referirse a Google.


## Bugs y errores
Si encuentras algún bug o error, siéntete libre de abrir un **Issue** en el repositorio.


## Créditos
Este RichPresence se ha hecho con la **[HTB v4 API Documentation](https://github.com/Propolisa/htb-api-docs)**


## Reconocimientos
<table>
    <tr>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/Pirrandi">
                <img src="https://avatars.githubusercontent.com/Pirrandi?v=3?s=100" width="100px;" alt="Pirrandi" />
                <br />
                <sub><b>Pirrandi</b>
            </a>
            <br />
            <sub>Creación del Script Principal y Doc. en Español
        </td>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/wh0crypt">
                <img src="https://avatars.githubusercontent.com/wh0crypt?v=3?s=100" width="100px;" alt="wh0crypt" />
                <br />
                <sub><b>wh0crypt</b>
            </a>
            <br />
            <sub>Creación del Script de Configuración y Doc. en Inglés
        </td>
        <td align="center" valign="top" width="14.28%">
            <a href="https://github.com/sealldeveloper">
                <img src="https://avatars.githubusercontent.com/sealldeveloper?v=3?s=100" width="100px;" alt="sealldeveloper" />
                <br />
                <sub><b>sealldeveloper</b>
            </a>
            <br />
            <sub>Mejoras de código adicionales
        </td>
    </tr>
</table>
