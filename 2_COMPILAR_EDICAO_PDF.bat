@echo off
chcp 65001 >nul
title Compilar Edição PDF - Decifrando Dados
color 0A

cd /d "%~dp0"
python "Gerador de Newsletter\compilar_interativo.py"

