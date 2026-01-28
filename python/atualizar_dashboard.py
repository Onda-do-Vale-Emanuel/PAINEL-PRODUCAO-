import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np

print("🔄 Atualizando KPI de faturamento (PEDIDOS ÚNICOS)...")

# ======================================================
# CAMINHOS
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[1]
ARQ_EXCEL = BASE_DIR / "excel" / "PEDIDOS ONDA.xlsx"
PASTA_DADOS = BASE_DIR / "site" / "dados"
PASTA_DADOS.mkdir(parents=True, exist_ok=True)

# ======================================================
# COLUNAS (BASE 0)
# ======================================================
COL_PEDIDO = 1   # Coluna B → Pedido
COL_TIPO   = 3   # Tipo (NORMAL)
COL_DATA   = 4   # Data
COL_VALOR  = 7   # Valor total do pedido

# ======================================================
# DATA DE REFERÊNCIA
# ======================================================
HOJE = datetime.today()
ANO_ATUAL = HOJE.year
ANO_ANTERIOR = HOJE.year - 1

# ======================================================
# LEITURA DA PLANILHA
# ======================================================
df = pd.read_excel(ARQ_EXCEL)
print(f"📄 Linhas lidas: {len(df)}")

# ======================================================
# FILTRAR PEDIDOS NORMAL
# ======================================================
df = df[df.iloc[:, COL_TIPO].astype(str).str.upper().str.strip() == "NORMAL"]
print(f"✅ NORMAL: {len(df)} linhas")

# ======================================================
# TRATAR DATA
# ======================================================
df["DATA_OK"] = pd.to_datetime(
    df.iloc[:, COL_DATA],
    errors="coerce",
    dayfirst=True
)
df = df.dropna(subset=["DATA_OK"])

# ======================================================
# CRIAR COLUNA ANO (EVITA FutureWarning)
# ======================================================
df["ANO"] = df["DATA_OK"].dt.year

# ======================================================
# TRATAR VALOR
# ======================================================
def converter_valor(v):
    if pd.isna(v):
        return 0.0
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    v = str(v).replace(".", "").replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

df["VALOR_OK"] = df.iloc[:, COL_VALOR].apply(converter_valor)

# ======================================================
# AGRUPAR POR PEDIDO + ANO (VALOR ÚNICO POR PEDIDO)
# ======================================================
df_pedidos = (
    df.groupby(
        [df.iloc[:, COL_PEDIDO], "ANO"],
        as_index=False
    )
    .agg({
        "VALOR_OK": "max",
        "DATA_OK": "min"
    })
)

# ======================================================
# FILTRAR PERÍODOS
# ======================================================
df_atual = df_pedidos[
    (df_pedidos["ANO"] == ANO_ATUAL) &
    (df_pedidos["DATA_OK"] <= HOJE)
]

df_ano_anterior = df_pedidos[
    (df_pedidos["ANO"] == ANO_ANTERIOR) &
    (df_pedidos["DATA_OK"] <= HOJE.replace(year=ANO_ANTERIOR))
]

# ======================================================
# CÁLCULOS
# ======================================================
valor_atual = round(df_atual["VALOR_OK"].sum(), 2)
valor_ano_anterior = round(df_ano_anterior["VALOR_OK"].sum(), 2)

if valor_ano_anterior > 0:
    variacao = round(
        ((valor_atual - valor_ano_anterior) / valor_ano_anterior) * 100, 1
    )
else:
    variacao = None

# ======================================================
# GERAR JSON
# ======================================================
dados = {
    "atual": valor_atual,
    "ano_anterior": valor_ano_anterior,
    "data_atual": HOJE.strftime("%d/%m/%Y"),
    "data_ano_anterior": HOJE.replace(year=ANO_ANTERIOR).strftime("%d/%m/%Y"),
    "variacao": variacao
}

with open(PASTA_DADOS / "kpi_faturamento.json", "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

# ======================================================
# LOG FINAL
# ======================================================
print("✅ KPI de faturamento gerado com sucesso")
print(f"💰 Faturamento até {dados['data_atual']}: {valor_atual:,.2f}")
print(f"💰 Faturamento até {dados['data_ano_anterior']}: {valor_ano_anterior:,.2f}")
print(f"📈 Variação: {variacao if variacao is not None else '--'}%")
