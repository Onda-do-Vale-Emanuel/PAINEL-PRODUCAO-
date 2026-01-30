from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_DADOS = BASE_DIR / "dados"

PASTA_DADOS.mkdir(exist_ok=True)

kpi_quantidade = {
    "titulo": "Pedidos",
    "valor": 342
}

with open(PASTA_DADOS / "kpi_quantidade_pedidos.json", "w", encoding="utf-8") as f:
    json.dump(kpi_quantidade, f, ensure_ascii=False, indent=2)

print("✅ KPI quantidade de pedidos atualizado")
