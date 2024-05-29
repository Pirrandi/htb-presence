@echo off
rem Add Python script to startup
echo python "%~dp0htb-presence.py" >> "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\htb-presence-startup.bat"