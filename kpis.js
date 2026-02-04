import pandas as pd
import json
import re

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ==============================
# LIMPAR NÚMEROS BR
# ==============================
def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0
    v = str(valor).strip()
    v = re.sub(r"[^0-9,.-]", "", v)
    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

# ==============================
# CARREGAR EXCEL
# ==============================
def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.strip().str.upper()

    obrig = ["DATA", "PEDIDO", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df

# ==============================
# PERÍODO
# ==============================
def obter_periodo(df):
    ultima = df["DATA"].max()
    df_mes = df[(df["DATA"].dt.year == ultima.year) & (df["DATA"].dt.month == ultima.month)]
    primeira = df_mes["DATA"].min()
    inicio_mes = primeira.replace(day=1)
    return primeira, ultima, inicio_mes

# ==============================
# EXECUÇÃO
# ==============================
def calcular(df):
    primeira, ultima, inicio_mes = obter_periodo(df)

    df_atual = df[(df["DATA"] >= primeira) & (df["DATA"] <= ultima)]
    ano_ant = primeira.year - 1
    df_ant = df[
        (df["DATA"] >= primeira.replace(year=ano_ant)) &
        (df["DATA"] <= ultima.replace(year=ano_ant))
    ]

    qtd_atual = df_atual["PEDIDO"].nunique()
    qtd_ant = df_ant["PEDIDO"].nunique()

    fat_atual = df_atual["VALOR COM IPI"].sum()
    fat_ant = df_ant["VALOR COM IPI"].sum()

    kg_atual = df_atual["KG"].sum()
    kg_ant = df_ant["KG"].sum()

    ticket_atual = fat_atual / qtd_atual if qtd_atual else 0
    ticket_ant = fat_ant / qtd_ant if qtd_ant else 0

    total_m2 = df_atual["TOTAL M2"].sum()

    return {
        "faturamento": {
            "atual": round(fat_atual, 2),
            "ano_anterior": round(fat_ant, 2),
            "variacao": ((fat_atual / fat_ant) - 1) * 100 if fat_ant else 0,
            "data_atual": ultima.strftime("%d/%m/%Y"),
            "data_ano_anterior": ultima.replace(year=ano_ant).strftime("%d/%m/%Y")
        },
        "quantidade": {
            "atual": qtd_atual,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd_atual / qtd_ant) - 1) * 100 if qtd_ant else 0
        },
        "kg": {
            "atual": round(kg_atual, 2),
            "ano_anterior": round(kg_ant, 2),
            "variacao": ((kg_atual / kg_ant) - 1) * 100 if kg_ant else 0
        },
        "ticket": {
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant) - 1) * 100 if ticket_ant else 0
        },
        "preco": {
            "preco_medio_kg": round(fat_atual / kg_atual, 2) if kg_atual else 0,
            "preco_medio_m2": round(fat_atual / total_m2, 2) if total_m2 else 0,
            "total_kg": round(kg_atual, 2),
            "total_m2": round(total_m2, 2),
            "data": ultima.strftime("%d/%m/%Y")
        }
    }

# ==============================
# SALVAR JSON
# ==============================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    df = carregar_excel()
    res = calcular(df)

    salvar("kpi_faturamento.json", res["faturamento"])
    salvar("kpi_quantidade_pedidos.json", res["quantidade"])
    salvar("kpi_kg_total.json", res["kg"])
    salvar("kpi_ticket_medio.json", res["ticket"])
    salvar("kpi_preco_medio.json", res["preco"])

    print("=====================================")
    print(f"Pedidos atuais: {res['quantidade']['atual']}")
    print(f"Período: 01/{res['faturamento']['data_atual'][3:]} → {res['faturamento']['data_atual']}")
    print("=====================================")
