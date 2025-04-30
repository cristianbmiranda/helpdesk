@echo off
echo Iniciando o sistema HelpDesk...
cd /d %~dp0
call venv\Scripts\activate
python app.py
pause
