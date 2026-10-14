@echo off
chcp 65001 >nul
title Redação Virtual 2D - Decifrando Dados
color 0B
echo ==============================================================================
echo   🏢 DECIFRANDO DADOS  •  REDAÇÃO VIRTUAL 2D (ESCRITÓRIO VIRTUAL)
echo ==============================================================================
echo   Iniciando servidor local na porta 8080 e abrindo no navegador...
echo ==============================================================================
python "%~dp0redacao-virtual\Abrir_Escritorio_Virtual_2D.py"
