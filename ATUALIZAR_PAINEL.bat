@echo off
chcp 65001 >nul
title Atualizar Painel Comercial

cd /d D:\USUARIOS\ADM05\Documents\dashboard_tv

echo =====================================
echo Atualizando painel a partir do Excel
echo =====================================
echo.

python python\atualizar_painel_completo.py

if errorlevel 1 (
    echo.
    echo ❌ Erro na execução do Python
    pause
    exit /b
)

echo.
echo Publicando no GitHub...
echo.

git add dados\*.json site\dados\*.json
git commit -m "Atualização automática KPIs"
git push

echo.
echo =====================================
echo Painel atualizado com sucesso!
echo =====================================
echo.

pause
