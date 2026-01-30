from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_DADOS = BASE_DIR / "dados"

PASTA_DADOS.mkdir(exist_ok=True)

kpi_ticket = {
    "titulo": "Ticket Médio",
    "valor": 365.20,
    "formato": "R$"
}

with open(PASTA_DADOS / "kpi_ticket_medio.json", "w", encoding="utf-8") as f:
    json.dump(kpi_ticket, f, ensure_ascii=False, indent=2)

print("✅ KPI ticket médio atualizado")
