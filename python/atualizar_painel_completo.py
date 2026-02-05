import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# LIMPA NÚMEROS BRASILEIROS (NÃO USADO PARA PEDIDO!)
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    v = str(v).strip()

    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ".", ","]:
        return 0.0

    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")

    elif "," in v:
        v = v.replace(",", ".")

    try:
        return float(v)
    except:
        return 0.0


# ======================================================
# CARREGAR PLANILHA
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["PEDIDO", "DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"Faltando coluna: {c}")

    # datas
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    # TRATAR PEDIDO COMO STRING SEMPRE
    df["PEDIDO"] = df["PEDIDO"].astype(str).str.strip()

    # limpar numéricos (somente onde necessário!)
    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df


# ======================================================
# KPIS
# ======================================================
def calcular(df):
    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month

    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    if df_mes.empty:
        return None

    primeira_real = df_mes["DATA"].min()

    # Para exibição no site → sempre 01/MM
    inicio_exib = datetime(ano, mes, 1)
    inicio_exib_ant = datetime(ano - 1, mes, 1)

    # Filtragem real
    df_periodo = df[(df["DATA"] >= primeira_real) & (df["DATA"] <= ultima)]

    qtd = df_periodo["PEDIDO"].nunique()
    total = df_periodo["VALOR COM IPI"].sum()
    kg = df_periodo["KG"].sum()
    m2 = df_periodo["TOTAL M2"].sum()

    # Ano anterior
    primeira_ant = primeira_real.replace(year=ano - 1)
    ultima_ant = ultima.replace(year=ano - 1)

    df_ant = df[(df["DATA"] >= primeira_ant) & (df["DATA"] <= ultima_ant)]

    qtd_ant = df_ant["PEDIDO"].nunique()
    total_ant = df_ant["VALOR COM IPI"].sum()
    kg_ant = df_ant["KG"].sum()
    m2_ant = df_ant["TOTAL M2"].sum()

    return {
        "fat": {
            "atual": round(total, 2),
            "ano_anterior": round(total_ant, 2),
            "variacao": ((total / total_ant) - 1) * 100 if total_ant else 0,
            "inicio_mes": inicio_exib.strftime("%d/%m/%Y"),
            "data_atual": ultima.strftime("%d/%m/%Y"),
            "inicio_mes_anterior": inicio_exib_ant.strftime("%d/%m/%Y"),
            "data_ano_anterior": ultima_ant.strftime("%d/%m/%Y")
        },
        "qtd": {
            "atual": int(qtd),
            "ano_anterior": int(qtd_ant),
            "variacao": ((qtd / qtd_ant) - 1) * 100 if qtd_ant else 0
        },
        "kg": {
            "atual": round(kg, 0),
            "ano_anterior": round(kg_ant, 0),
            "variacao": ((kg / kg_ant) - 1) * 100 if kg_ant else 0
        },
        "ticket": {
            "atual": round(total / qtd, 2) if qtd else 0,
            "ano_anterior": round(total_ant / qtd_ant, 2) if qtd_ant else 0,
            "variacao": (((total / qtd) / (total_ant / qtd_ant)) - 1) * 100 if qtd_ant else 0
        },
        "preco": {
            "preco_medio_kg": round(total / kg, 2) if kg else 0,
            "preco_medio_m2": round(total / m2, 2) if m2 else 0,
            "total_kg": round(kg, 2),
            "total_m2": round(m2, 2),
            "data": ultima.strftime("%d/%m/%Y")
        }
    }


# ======================================================
# SALVAR JSONS
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    df = carregar()
    res = calcular(df)

    salvar("kpi_faturamento.json", res["fat"])
    salvar("kpi_quantidade_pedidos.json", res["qtd"])
    salvar("kpi_kg_total.json", res["kg"])
    salvar("kpi_ticket_medio.json", res["ticket"])
    salvar("kpi_preco_medio.json", res["preco"])

    print("✓ JSON atualizado corretamente!")
    print("Pedidos atuais:", res["qtd"]["atual"])
    print("Período mostrado no site:", res["fat"]["inicio_mes"], "→", res["fat"]["data_atual"])
