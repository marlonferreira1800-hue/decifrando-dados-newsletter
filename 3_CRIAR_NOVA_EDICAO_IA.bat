@echo off
chcp 65001 >nul
title Criar Nova Edição - Decifrando Dados (IA Autônoma)
color 0E

cd /d "%~dp0"
python "Gerador de Newsletter\criar_newsletter.py"

