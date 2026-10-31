@echo off
rem Inicia a interface local do IJSN (abre o navegador em http://127.0.0.1:8765). Feche esta janela para encerrar.
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -I app\servidor.py
pause
