@echo off
chcp 65001 >nul
title Central da Newsletter - Decifrando Dados
color 0F

:MENU
cls
echo ==============================================================================
echo   📰  DECIFRANDO DADOS  •  PAINEL DE CONTROLE CENTRAL
echo ==============================================================================
echo   Curadoria & Autoria: Marlon Ferreira  •  Formato: The BRIEF
echo ==============================================================================
echo.
echo   [1] 🏢 Abrir Redação Virtual 2D (Servidor 8080 + Canvas no Navegador)
echo   [2] 📄 Compilar Edição (Gera PDF Diagramado, HTML e Artigo LinkedIn)
echo   [3] 🤖 Criar Nova Edição com IA (Modo Autônomo com Link / Pauta / Tema)
echo   [4] 📋 Copiar Artigo do LinkedIn para Área de Transferência (Ctrl+V)
echo   [5] 📁 Abrir Pasta de Edições (.md)
echo   [6] 📁 Abrir Pasta de Publicações (PDFs e HTMLs)
echo   [7] 📖 Ver Receita de Bolo da Newsletter
echo   [0] ❌ Sair
echo.
echo ==============================================================================
set /p OPCAO="🎯 Escolha uma opção (0-7): "

if "%OPCAO%"=="1" goto OPCAO_1
if "%OPCAO%"=="2" goto OPCAO_2
if "%OPCAO%"=="3" goto OPCAO_3
if "%OPCAO%"=="4" goto OPCAO_4
if "%OPCAO%"=="5" goto OPCAO_5
if "%OPCAO%"=="6" goto OPCAO_6
if "%OPCAO%"=="7" goto OPCAO_7
if "%OPCAO%"=="0" goto SAIR

echo Opção inválida! Pressione qualquer tecla para tentar novamente...
pause >nul
goto MENU

:OPCAO_1
cls
call "%~dp01_INICIAR_REDACAO_VIRTUAL.bat"
goto MENU

:OPCAO_2
cls
call "%~dp02_COMPILAR_EDICAO_PDF.bat"
goto MENU

:OPCAO_3
cls
call "%~dp03_CRIAR_NOVA_EDICAO_IA.bat"
goto MENU

:OPCAO_4
cls
call "%~dp04_COPIAR_ARTIGO_LINKEDIN.bat"
goto MENU

:OPCAO_5
start "" explorer "C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes"
goto MENU

:OPCAO_6
start "" explorer "C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes"
goto MENU

:OPCAO_7
cls
echo ==============================================================================
echo   📖 RECEITA DE BOLO DA NEWSLETTER DECIFRANDO DADOS
echo ==============================================================================
type "%~dp0RECEITA_DE_BOLO_NEWSLETTER.md" | more
pause
goto MENU

:SAIR
cls
echo Até logo, Marlon!
timeout /t 1 >nul
exit
