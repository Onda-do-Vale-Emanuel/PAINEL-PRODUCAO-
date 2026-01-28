import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import numpy as np

print("Iniciando atualização do painel...")

# ======================================================
# CAMINHOS
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[1]
ARQ_EXCEL = BASE_DIR / "excel" / "PEDIDOS ONDA.xlsx"
PASTA_DADOS = BASE_DIR / "site" / "dados"
PASTA_DADOS.mkdir(parents=True, exist_ok=True)

# ======================================================
# CONFIGURAÇÕES DE COLUNAS (base 0)
# ======================================================
COL_TIPO = 3
COL_DATA = 4
COL_VALOR = 7   # CONFIRME SE ESTA É A COLUNA DO VALOR FINAL

# ======================================================
# DATA ÚNICA
# ======================================================
HOJE = datetime.now()
ANO_ATUAL = HOJE.year
ANO_ANTERIOR = HOJE.year - 1

# ======================================================
# LEITURA
# ======================================================
df = pd.read_excel(ARQ_EXCEL)
print(f"Linhas lidas: {len(df)}")

# ======================================================
# FILTRO NORMAL
# ======================================================
df = df[
    df.iloc[:, COL_TIPO]
    .astype(str)
    .str.upper()
    .str.strip()
    == "NORMAL"
]

print(f"Pedidos NORMAL: {len(df)}")

# ======================================================
# DATA
# ======================================================
df["DATA_OK"] = pd.to_datetime(
    df.iloc[:, COL_DATA],
    errors="coerce",
    dayfirst=True
)
df = df.dropna(subset=["DATA_OK"])

# ======================================================
# VALOR
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
# FILTRO PERÍODO
# ======================================================
df_atual = df[
    (df["DATA_OK"].dt.year == ANO_ATUAL) &
    (df["DATA_OK"].dt.date <= HOJE.date())
]

df_ano_anterior = df[
    (df["DATA_OK"].dt.year == ANO_ANTERIOR) &
    (df["DATA_OK"].dt.date <= HOJE.replace(year=ANO_ANTERIOR).date())
]

print(f"Pedidos ano atual: {len(df_atual)}")
print(f"Pedidos ano anterior: {len(df_ano_anterior)}")

# ======================================================
# KPIs
# ======================================================
faturamento_atual = round(float(df_atual["VALOR_OK"].sum()), 2)
faturamento_anterior = round(float(df_ano_anterior["VALOR_OK"].sum()), 2)

qtd_atual = int(len(df_atual))
qtd_anterior = int(len(df_ano_anterior))

ticket_medio = round(
    faturamento_atual / qtd_atual, 2
) if qtd_atual > 0 else 0.0

variacao_faturamento = round(
    ((faturamento_atual - faturamento_anterior) / faturamento_anterior) * 100, 1
) if faturamento_anterior > 0 else None

variacao_qtd = round(
    ((qtd_atual - qtd_anterior) / qtd_anterior) * 100, 1
) if qtd_anterior > 0 else None

# ======================================================
# JSONs
# ======================================================
json.dump(
    {
        "atual": faturamento_atual,
        "ano_anterior": faturamento_anterior,
        "variacao": variacao_faturamento,
        "data": HOJE.strftime("%d/%m/%Y")
    },
    open(PASTA_DADOS / "kpi_faturamento.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2
)

json.dump(
    {
        "atual": qtd_atual,
        "ano_anterior": qtd_anterior,
        "variacao": variacao_qtd,
        "data": HOJE.strftime("%d/%m/%Y")
    },
    open(PASTA_DADOS / "kpi_quantidade_pedidos.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2
)

json.dump(
    {
        "valor": ticket_medio,
        "data": HOJE.strftime("%d/%m/%Y")
    },
    open(PASTA_DADOS / "kpi_ticket_medio.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2
)

# ======================================================
# LOG FINAL
# ======================================================
print("Atualização concluída com sucesso")
print(f"Faturamento: {faturamento_atual:,.2f}")
print(f"Pedidos: {qtd_atual}")
print(f"Ticket médio: {ticket_medio:,.2f}")
