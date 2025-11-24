@echo off
REM Script para fazer push no GitHub
REM Autor: Claude Code
REM Data: 2025-11-24

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo   PUSH PARA GITHUB - MONITORBUCHA
echo ================================================================================
echo.

REM Verifique se está no diretório correto
if not exist ".git" (
    echo ERRO: Este script deve ser executado no diretório raiz do projeto!
    echo.
    echo Navegue até: C:\Users\isl_7\OneDrive\Área de Trabalho\Trabalho\Genesis\Monitor de buchas\monitorbucha-main\monitorbucha-main\Software_Bucha
    echo.
    pause
    exit /b 1
)

echo STATUS DO GIT:
git status
echo.

REM Verifique se o remote já existe
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo AVISO: Remote origin não configurado!
    echo.
    echo Configurando remote...
    git remote add origin https://github.com/iloopes/monitorbucha.git
    echo Remote adicionado: https://github.com/iloopes/monitorbucha.git
    echo.
) else (
    echo Remote já existe:
    git remote -v
    echo.
)

REM Verifique a branch
for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD') do set branch=%%i
echo BRANCH ATUAL: %branch%
echo.

REM Se não for main, pergunte se quer renomear
if not "%branch%"=="main" (
    echo A branch atual não é 'main'. O GitHub prefere usar 'main' como padrão.
    echo.
    set /p rename="Deseja renomear para 'main'? (s/n) "
    if /i "%rename%"=="s" (
        git branch -M main
        echo Branch renomeada para 'main'
    )
    echo.
)

REM Faça o push
echo.
echo ================================================================================
echo FAZENDO PUSH PARA GITHUB...
echo ================================================================================
echo.

git push -u origin main

REM Verifique se foi bem-sucedido
if errorlevel 0 (
    echo.
    echo ================================================================================
    echo ✅ PUSH REALIZADO COM SUCESSO!
    echo ================================================================================
    echo.
    echo Repositório: https://github.com/iloopes/monitorbucha
    echo Branch: main
    echo Arquivos: 110
    echo Commit: %branch%
    echo.
    echo Verifique em: https://github.com/iloopes/monitorbucha
    echo.
) else (
    echo.
    echo ================================================================================
    echo ❌ ERRO AO FAZER PUSH
    echo ================================================================================
    echo.
    echo Verifique:
    echo 1. Você criou o repositório no GitHub?
    echo 2. Suas credenciais estão corretas?
    echo 3. Você tem acesso à internet?
    echo.
    echo Consulte: COMO_FAZER_PUSH.txt para instruções detalhadas
    echo.
)

pause
