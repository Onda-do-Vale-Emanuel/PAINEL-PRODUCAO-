import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# LIMPA NÚMEROS ESTILO BRASIL (À PROVA DE ERRO)
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    v = str(v).strip()

    # Remove todos caracteres que NÃO sejam dígitos, vírgula ou ponto
    v = re.sub(r"[^0-9,.-]", "", v)

    # Ex: "2026-02-03151642" vira "20260203151642"
    # Se sobrar só números sem vírgula/ponto -> considerar erro -> 0
    if re.fullmatch(r"[0-9]+", v):
        # Se for absurdamente grande, também zeramos
        if len(v) > 7:  
            return 0.0
        return float(v)

    if v in ["", "-", ".", ","]:
        return 0.0

    # caso padrão BR 12.345,67
    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")

    try:
        return float(v)
    except:
        return 0.0


# ======================================================
# CARREGA E NORMALIZA PLANILHA
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["PEDIDO", "DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"Coluna ausente: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    # NORMALIZA NÚMEROS
    for c in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[c] = df[c].apply(limpar_numero)

    # Normalizar número do pedido → extrair só números
    df["PEDIDO"] = df["PEDIDO"].astype(str)
    df["PEDIDO"] = df["PEDIDO"].apply(lambda x: re.sub(r"[^0-9]", "", x))

    return df


# ======================================================
# CALCULA TODOS OS KPIS
# ======================================================
def calcular(df):
    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month

    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    primeira_com_pedido = df_mes["DATA"].min()

    if primeira_com_pedido is None:
        return None

    inicio_exib_atual = ultima.replace(day=1)
    inicio_exib_ant = inicio_exib_atual.replace(year=ano - 1)

    df_periodo = df[(df["DATA"] >= primeira_com_pedido) & (df["DATA"] <= ultima)]

    qtd = df_periodo["PEDIDO"].nunique()
    total = df_periodo["VALOR COM IPI"].sum()
    kg = df_periodo["KG"].sum()
    m2 = df_periodo["TOTAL M2"].sum()

    inicio_real_ant = primeira_com_pedido.replace(year=ano - 1)
    fim_ant = ultima.replace(year=ano - 1)

    df_ant = df[(df["DATA"] >= inicio_real_ant) & (df["DATA"] <= fim_ant)]

    qtd_ant = df_ant["PEDIDO"].nunique()
    total_ant = df_ant["VALOR COM IPI"].sum()
    kg_ant = df_ant["KG"].sum()
    m2_ant = df_ant["TOTAL M2"].sum()

    ticket_atual = total / qtd if qtd else 0
    ticket_ant = total_ant / qtd_ant if qtd_ant else 0

    return {
        "fat": {
            "atual": round(total, 2),
            "ano_anterior": round(total_ant, 2),
            "variacao": ((total / total_ant) - 1) * 100 if total_ant else 0,
            "data_atual": ultima.strftime("%d/%m/%Y"),
            "inicio_mes": inicio_exib_atual.strftime("%d/%m/%Y"),
            "data_ano_anterior": fim_ant.strftime("%d/%m/%Y"),
            "inicio_mes_anterior": inicio_exib_ant.strftime("%d/%m/%Y")
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
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant) - 1) * 100 if ticket_ant else 0
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
# SALVA JSON
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

    print("\n✓ JSON gerado com sucesso!")
    print("Pedidos atuais:", res["qtd"]["atual"])
    print("Período exibido:", res["fat"]["inicio_mes"], "→", res["fat"]["data_atual"])
