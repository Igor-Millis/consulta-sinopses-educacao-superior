@echo off
rem Consulta as Sinopses da Educacao Superior - Igor L. Millis - Projeto Independente com Dados Publicos (sem acento: o cmd le ASCII)
rem Inicia a interface local (abre o navegador em http://127.0.0.1:8765). Feche esta janela para encerrar.
rem Arquivo em ASCII com quebras CRLF de proposito: acentos ou quebras LF fazem o cmd do Windows ler errado.
cd /d "%~dp0"
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -I app\servidor.py
pause
