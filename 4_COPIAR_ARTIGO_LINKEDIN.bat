@echo off
chcp 65001 >nul
title Copiar Artigo LinkedIn - Decifrando Dados
color 09

cd /d "%~dp0"
python "Gerador de Newsletter\copiar_linkedin.py"

