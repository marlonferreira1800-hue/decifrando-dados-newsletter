@echo off
chcp 65001 >nul
title Escritorio Virtual 2D - Decifrando Dados
echo ==============================================================================
echo   DECIFRANDO DADOS - ESCRITORIO VIRTUAL 2D (PORTA 8080)
echo ==============================================================================
echo.
echo Iniciando servidor da Redacao Virtual e abrindo http://localhost:8080 ...
echo.
start "" http://localhost:8080
python "%~dp0server.py" 8080
pause
