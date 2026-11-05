@echo off
cd /d "%~dp0"
echo Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Falha ao instalar dependencias. Verifique se o Python 3.10+ esta instalado e no PATH.
  pause
  exit /b 1
)
echo Iniciando o site da newsletter em http://127.0.0.1:5000 ...
start "Decifrando Dados - Newsletter" python app.py
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:5000
