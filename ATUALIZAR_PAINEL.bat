@echo off
chcp 65001 >nul

cd /d D:\USUARIOS\ADM05\Documents\dashboard_tv

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; ^
python python\atualizar_dashboard.py; ^
python python\atualizar_kpi_quantidade_pedidos.py; ^
git add site/dados/*.json; ^
git commit -m 'Atualização automática KPIs' || exit 0; ^
git push"

echo.
echo Painel atualizado com sucesso!
pause
