@echo off
cd /d %~dp0

python python\seguranca_execucao.py

IF %ERRORLEVEL% NEQ 0 (
    pause
    exit /b
)

echo =====================================
echo ATUALIZANDO PAINEL COMERCIAL
echo =====================================
echo.

python python\atualizar_painel_completo.py

echo.
echo =====================================
echo ENVIANDO PARA O GITHUB
echo =====================================
echo.

git add .
git commit -m "Atualização automática painel"
git push

echo.
echo =====================================
echo PAINEL ATUALIZADO COM SUCESSO
echo =====================================
pause
