import pandas as pd
import json
import re

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ================= LIMPA NÚMEROS =================
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

# ================= CARREGA EXCEL =================
def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["DATA", "PEDIDO", "TIPO DE PEDIDO", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"Coluna obrigatória ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    # 🔥 FILTRO IGUAL AO EXCEL
    df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()
    df = df[df["TIPO DE PEDIDO"] == "NORMAL"]

    return df

# ================= CÁLCULO =================
def calcular(df):
    ultima = df["DATA"].max()

    df_mes = df[
        (df["DATA"].dt.year == ultima.year) &
        (df["DATA"].dt.month == ultima.month)
    ]

    inicio_mes = df_mes["DATA"].min()

    df_periodo = df[(df["DATA"] >= inicio_mes) & (df["DATA"] <= ultima)]

    # PEDIDOS ÚNICOS (igual Excel)
    pedidos_atual = df_periodo["PEDIDO"].nunique()

    total_valor = df_periodo["VALOR COM IPI"].sum()
    total_kg = df_periodo["KG"].sum()
    total_m2 = df_periodo["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    # ===== ANO ANTERIOR =====
    inicio_ant = inicio_mes.replace(year=inicio_mes.year - 1)
    fim_ant = ultima.replace(year=ultima.year - 1)

    df_ant = df[(df["DATA"] >= inicio_ant) & (df["DATA"] <= fim_ant)]

    pedidos_ant = df_ant["PEDIDO"].nunique()
    valor_ant = df_ant["VALOR COM IPI"].sum()
    kg_ant = df_ant["KG"].sum()
    m2_ant = df_ant["TOTAL M2"].sum()

    return {
        "fat": {
            "atual": round(total_valor, 2),
            "ano_anterior": round(valor_ant, 2),
            "variacao": ((total_valor / valor_ant - 1) * 100) if valor_ant else 0,
            "inicio_mes": inicio_mes.strftime("%d/%m/%Y"),
            "data": ultima.strftime("%d/%m/%Y"),
            "inicio_mes_anterior": inicio_ant.strftime("%d/%m/%Y"),
            "data_ano_anterior": fim_ant.strftime("%d/%m/%Y")
        },
        "qtd": {
            "atual": pedidos_atual,
            "ano_anterior": pedidos_ant,
            "variacao": ((pedidos_atual / pedidos_ant - 1) * 100) if pedidos_ant else 0
        },
        "kg": {
            "atual": round(total_kg, 2),
            "ano_anterior": round(kg_ant, 2),
            "variacao": ((total_kg / kg_ant - 1) * 100) if kg_ant else 0
        },
        "ticket": {
            "atual": round(total_valor / pedidos_atual, 2) if pedidos_atual else 0,
            "ano_anterior": round(valor_ant / pedidos_ant, 2) if pedidos_ant else 0,
            "variacao": (
                ((total_valor / pedidos_atual) /
                 (valor_ant / pedidos_ant) - 1) * 100
            ) if pedidos_ant else 0
        },
        "preco": {
            "preco_medio_kg": preco_kg,
            "preco_medio_m2": preco_m2,
            "total_kg": round(total_kg, 2),
            "total_m2": round(total_m2, 2),
            "data": ultima.strftime("%d/%m/%Y")
        }
    }

# ================= SALVAR =================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    df = carregar_excel()
    res = calcular(df)

    salvar("kpi_faturamento.json", res["fat"])
    salvar("kpi_quantidade_pedidos.json", res["qtd"])
    salvar("kpi_kg_total.json", res["kg"])
    salvar("kpi_ticket_medio.json", res["ticket"])
    salvar("kpi_preco_medio.json", res["preco"])

    print("✓ JSON gerados corretamente")
    print("Pedidos atuais:", res["qtd"]["atual"])
