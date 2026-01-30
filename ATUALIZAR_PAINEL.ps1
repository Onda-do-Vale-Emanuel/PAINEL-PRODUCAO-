cd D:\USUARIOS\ADM05\Documents\dashboard_tv

Write-Host "🔄 Iniciando atualização dos KPIs..." -ForegroundColor Yellow

python python\atualizar_dashboard.py
python python\atualizar_kpi_quantidade_pedidos.py
# python python\atualizar_kpi_ticket_medio.py

git add site\dados\*.json
git commit -m "Atualização automática KPIs"
git push

Write-Host "✅ Painel atualizado com sucesso!" -ForegroundColor Green
pause
