@echo off

cd /d "%~dp0"

echo ==========================================
echo     ATUALIZANDO PAINEL PRODUCAO
echo ==========================================
echo.

REM Executa o EXE
if exist "PAINEL_PRODUCAO.exe" (
    PAINEL_PRODUCAO.exe
) else (
    echo ERRO: PAINEL_PRODUCAO.exe nao encontrado!
    pause
    exit
)

echo.
echo Enviando dados para o GitHub...

git add dados\*.json
git add site\dados\*.json

git commit -m "Atualizacao automatica painel producao"
git push

echo.
echo ==========================================
echo     PAINEL ATUALIZADO COM SUCESSO
echo ==========================================
echo.

pause