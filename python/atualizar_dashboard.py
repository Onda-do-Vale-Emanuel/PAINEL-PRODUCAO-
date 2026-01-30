from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_DADOS = BASE_DIR / "dados"

PASTA_DADOS.mkdir(exist_ok=True)

# EXEMPLO DE DADO (ajuste conforme sua lógica real)
kpi_faturamento = {
    "titulo": "Faturamento",
    "valor": 125000,
    "formato": "R$"
}

with open(PASTA_DADOS / "kpi_faturamento.json", "w", encoding="utf-8") as f:
    json.dump(kpi_faturamento, f, ensure_ascii=False, indent=2)

print("✅ KPI faturamento atualizado")
