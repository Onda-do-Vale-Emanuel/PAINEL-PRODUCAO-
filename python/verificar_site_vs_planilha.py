import pandas as pd
import re
from datetime import datetime

CAMINHO = "excel/PEDIDOS ONDA.xlsx"

# ------------------- LIMPEZA NUMÉRICA -------------------
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    v = str(v).strip()

    # ❗ IGNORAR VALORES QUE PARECEM DATA-CONCATENADA
    # Exemplo errado: 2026-02-03151642
    if re.match(r"^\d{4}-\d{2}-\d{2}\d+$", v):
        return 0.0

    # remover letras e símbolos, exceto . , -
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ".", ",", ",-", ".-"]:
        return 0.0

    # formato 1.234.567,89
    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")
        try:
            return float(v)
        except:
            return 0.0

    # formato 123,45
    if "," in v:
        try:
            return float(v.replace(",", "."))
        except:
            return 0.0

    # formato 1234.56 ou erro
    try:
        return float(v)
    except:
        return 0.0

# ------------------- CARREGAR EXCEL -------------------
df = pd.read_excel(CAMINHO)
df.columns = df.columns.str.upper().str.strip()

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df = df[df["DATA"].notna()]

df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
df["KG"] = df["KG"].apply(limpar_numero)
df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

# ------------------- PERÍODO ATUAL -------------------
ultima_data = df["DATA"].max()
ano_atual = ultima_data.year
mes_atual = ultima_data.month

df_mes_atual = df[(df["DATA"].dt.year == ano_atual) & (df["DATA"].dt.month == mes_atual)]

primeira_data_atual = df_mes_atual["DATA"].min()
ultima_data_atual = df_mes_atual["DATA"].max()

df_periodo_atual = df[(df["DATA"] >= primeira_data_atual) & (df["DATA"] <= ultima_data_atual)]

# ------------------- PERÍODO ANO ANTERIOR -------------------
ano_ant = ano_atual - 1

primeira_ant = primeira_data_atual.replace(year=ano_ant)
ultima_ant = ultima_data_atual.replace(year=ano_ant)

# Caso a data do ano anterior não exista, usa a última data válida do mês
datas_ant_mes = df[(df["DATA"].dt.year == ano_ant) & (df["DATA"].dt.month == mes_atual)]["DATA"]

if datas_ant_mes.empty:
    # não existem pedidos no mês inteiro do ano anterior
    df_periodo_ant = df[df["DATA"].dt.year == ano_ant].iloc[0:0]
else:
    ultima_ant_real = datas_ant_mes.max()
    if ultima_ant > ultima_ant_real:
        ultima_ant = ultima_ant_real
    df_periodo_ant = df[(df["DATA"] >= primeira_ant) & (df["DATA"] <= ultima_ant)]

# ------------------- CÁLCULOS -------------------
def calcular(dfp):
    return {
        "pedidos": len(dfp),
        "fat": dfp["VALOR COM IPI"].sum(),
        "kg": dfp["KG"].sum(),
        "m2": dfp["TOTAL M2"].sum(),
        "ticket": (dfp["VALOR COM IPI"].sum() / len(dfp)) if len(dfp) else 0
    }

res_atual = calcular(df_periodo_atual)
res_ant = calcular(df_periodo_ant)

# ------------------- MOSTRAR RESULTADOS -------------------
print("\n==================== RESULTADOS ====================\n")

print(f"📅 ATUAL     : {primeira_data_atual.strftime('%d/%m/%Y')} → {ultima_data_atual.strftime('%d/%m/%Y')}")
print(res_atual)

print(f"\n📅 ANTERIOR  : {primeira_ant.strftime('%d/%m/%Y')} → {ultima_ant.strftime('%d/%m/%Y')}")
print(res_ant)

print("\n====================================================\n")
