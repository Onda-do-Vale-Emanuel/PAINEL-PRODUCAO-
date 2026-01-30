from datetime import date
import calendar
import json
from pathlib import Path

import pandas as pd

# Caminhos base
BASE_DIR = Path(r"D:\USUARIOS\ADM05\Documents\dashboard_tv").resolve()
ARQ_EXCEL = BASE_DIR / "excel" / "PEDIDOS ONDA.xlsx"
PASTA_DADOS = BASE_DIR / "dados"
PASTA_SITE_DADOS = BASE_DIR / "site" / "dados"

print("📄 Iniciando atualização completa do painel...")

# Garante que as pastas existem
PASTA_DADOS.mkdir(exist_ok=True)
PASTA_SITE_DADOS.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------
# 1) LER EXCEL E FILTRAR SOMENTE TIPO DE PEDIDO = NORMAL
# -------------------------------------------------------------------
df = pd.read_excel(ARQ_EXCEL)

print(f"📄 Linhas lidas: {len(df)}")

df = df[df["Tipo de pedido"].astype(str).str.upper().str.strip() == "NORMAL"].copy()
print(f"✅ NORMAL: {len(df)} linhas")

# Converter data
df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["Data"])

# Quebrar data em ano/mês
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month

# Converter colunas numéricas importantes
for col in ["Valor Com IPI", "Kg"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Pedido como texto (só por segurança)
df["Pedido"] = df["Pedido"].astype(str).str.strip()

# -------------------------------------------------------------------
# 2) DEFINIR DATAS (MÊS ATUAL E MESMO MÊS DO ANO ANTERIOR)
# -------------------------------------------------------------------
hoje = date.today()
ANO_ATUAL = hoje.year
MES_ATUAL = hoje.month
ANO_ANTERIOR = ANO_ATUAL - 1

def encontrar_data_final(df_base: pd.DataFrame, ano: int, mes: int, data_alvo: date) -> date | None:
    """
    Começa da data_alvo (no ano/mes desejado) e volta dia a dia
    até achar uma data que tenha pelo menos 1 pedido NORMAL.
    """
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    dia = min(data_alvo.day, ultimo_dia_mes)

    while dia >= 1:
        d = date(ano, mes, dia)
        tem = ((df_base["Ano"] == ano) &
               (df_base["Mes"] == mes) &
               (df_base["Data"].dt.date == d)).any()
        if tem:
            return d
        dia -= 1

    return None

# Data final do ANO ATUAL (usa hoje e volta se não tiver pedido)
data_final_atual = encontrar_data_final(df, ANO_ATUAL, MES_ATUAL, hoje)

# Para o ANO ANTERIOR, usamos o mesmo dia do mês (se existir),
# senão voltamos dia a dia igual fizemos no ano atual
dia_alvo_anterior = min(
    hoje.day,
    calendar.monthrange(ANO_ANTERIOR, MES_ATUAL)[1]
)
data_alvo_anterior = date(ANO_ANTERIOR, MES_ATUAL, dia_alvo_anterior)
data_final_anterior = encontrar_data_final(df, ANO_ANTERIOR, MES_ATUAL, data_alvo_anterior)

if data_final_atual is None or data_final_anterior is None:
    raise SystemExit("❌ Não há dados suficientes para calcular os KPIs (mês atual ou ano anterior).")

print(f"📅 Data usada (atual): {data_final_atual.strftime('%d/%m/%Y')}")
print(f"📅 Data usada (ano anterior): {data_final_anterior.strftime('%d/%m/%Y')}")

# Intervalo: do 1º dia do mês até a data final encontrada
data_inicio_atual = date(ANO_ATUAL, MES_ATUAL, 1)
data_inicio_anterior = date(ANO_ANTERIOR, MES_ATUAL, 1)

mask_atual = (
    (df["Ano"] == ANO_ATUAL) &
    (df["Mes"] == MES_ATUAL) &
    (df["Data"].dt.date >= data_inicio_atual) &
    (df["Data"].dt.date <= data_final_atual)
)

mask_anterior = (
    (df["Ano"] == ANO_ANTERIOR) &
    (df["Mes"] == MES_ATUAL) &
    (df["Data"].dt.date >= data_inicio_anterior) &
    (df["Data"].dt.date <= data_final_anterior)
)

df_atual = df.loc[mask_atual].copy()
df_anterior = df.loc[mask_anterior].copy()

print(f"📊 Linhas ATUAL no mês: {len(df_atual)}")
print(f"📊 Linhas ANO ANTERIOR no mês: {len(df_anterior)}")

# -------------------------------------------------------------------
# 3) CALCULAR KPI DE FATURAMENTO, QTD, TICKET E KG
# -------------------------------------------------------------------
# FATURAMENTO = soma direta do "Valor Com IPI" do mês
valor_atual = float(df_atual["Valor Com IPI"].sum())
valor_anterior = float(df_anterior["Valor Com IPI"].sum())

# QUANTIDADE DE PEDIDOS = número de pedidos distintos na coluna "Pedido"
qtd_atual = int(df_atual["Pedido"].nunique())
qtd_anterior = int(df_anterior["Pedido"].nunique())

# KG TOTAL
kg_atual = float(df_atual["Kg"].sum())
kg_anterior = float(df_anterior["Kg"].sum())

def variacao_percentual(atual: float, anterior: float):
    if anterior == 0:
        return None
    return round((atual - anterior) / anterior * 100, 1)

var_fat = variacao_percentual(valor_atual, valor_anterior)
var_qtd = variacao_percentual(qtd_atual, qtd_anterior)
var_kg = variacao_percentual(kg_atual, kg_anterior)

# TICKET MÉDIO = faturamento / quantidade de pedidos
ticket_atual = float(valor_atual / qtd_atual) if qtd_atual > 0 else 0.0
ticket_anterior = float(valor_anterior / qtd_anterior) if qtd_anterior > 0 else 0.0
var_ticket = variacao_percentual(ticket_atual, ticket_anterior)

# -------------------------------------------------------------------
# 4) METAS DE KG POR MÊS (para o slide do KG)
# -------------------------------------------------------------------
META_KG = {
    1: 100_000,
    2: 100_000,
    3: 120_000,
    4: 130_000,
    5: 130_000,
    6: 130_000,
    7: 150_000,
    8: 150_000,
    9: 150_000,
    10: 150_000,
    11: 150_000,
    12: 98_000,
}

meta_kg = float(META_KG.get(MES_ATUAL, 0))
meta_kg_perc = round((kg_atual / meta_kg) * 100, 1) if meta_kg > 0 else None

# -------------------------------------------------------------------
# 5) GRAVAR JSONS EM dados\ E site\dados\
# -------------------------------------------------------------------
def escrever_json(nome: str, dados: dict):
    for pasta in (PASTA_DADOS, PASTA_SITE_DADOS):
        caminho = pasta / nome
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

kpi_faturamento = {
    "atual": round(valor_atual, 2),
    "ano_anterior": round(valor_anterior, 2),
    "variacao": var_fat,
    "data_atual": data_final_atual.strftime("%d/%m/%Y"),
    "data_ano_anterior": data_final_anterior.strftime("%d/%m/%Y"),
}

kpi_quantidade = {
    "atual": qtd_atual,
    "ano_anterior": qtd_anterior,
    "variacao": var_qtd,
}

kpi_ticket = {
    "atual": round(ticket_atual, 2),
    "ano_anterior": round(ticket_anterior, 2),
    "variacao": var_ticket,
}

kpi_kg = {
    "atual": round(kg_atual, 2),
    "ano_anterior": round(kg_anterior, 2),
    "variacao": var_kg,
    "meta": meta_kg,
    "meta_perc": meta_kg_perc,
}

escrever_json("kpi_faturamento.json", kpi_faturamento)
escrever_json("kpi_quantidade_pedidos.json", kpi_quantidade)
escrever_json("kpi_ticket_medio.json", kpi_ticket)
escrever_json("kpi_kg_total.json", kpi_kg)

# -------------------------------------------------------------------
# 6) LOG FINAL NO POWERSHELL
# -------------------------------------------------------------------
print("✅ KPIs gerados com sucesso")
print(f"💰 Valor pedidos (com IPI): {valor_atual:,.2f}")
print(f"📦 Pedidos únicos: {qtd_atual}")
print(f"🎯 Ticket médio: {ticket_atual:,.2f}")
print(f"⚖️ KG total: {kg_atual:,.2f}")
print("🌐 Dados sincronizados com site/dados")
