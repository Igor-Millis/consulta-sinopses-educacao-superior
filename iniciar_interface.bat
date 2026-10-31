@echo off
rem Consulta as Sinopses da Educacao Superior - criacao e desenvolvimento: Igor L. Millis (projeto independente).
rem Inicia a interface local (abre o navegador em http://127.0.0.1:8765). Feche esta janela para encerrar.
rem Arquivo em ASCII com quebras CRLF de proposito: acentos ou quebras LF fazem o cmd do Windows ler errado.
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -I app\servidor.py
pause
