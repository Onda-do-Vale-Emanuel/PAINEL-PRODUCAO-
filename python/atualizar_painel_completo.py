import pandas as pd
import json
import re

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"


# ======================================================
# LIMPA NÚMEROS ESTILO BRASIL
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0
    v = re.sub(r"[^0-9,.-]", "", str(v))
    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)


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

    for c in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[c] = df[c].apply(limpar_numero)

    return df


# ======================================================
# CALCULA TODOS OS KPIs
# ======================================================
def calcular(df):
    # última data com pedido
    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month

    # linhas do mês atual
    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]

    # 1º dia COM PEDIDO no mês (para cálculo)
    primeira_com_pedido = df_mes["DATA"].min()

    # datas para EXIBIÇÃO (sempre dia 01)
    inicio_exib_atual = ultima.replace(day=1)
    inicio_exib_ant = inicio_exib_atual.replace(year=ano - 1)

    # PERÍODO REAL USADO PARA CÁLCULO (primeira data com pedido → última data)
    df_periodo = df[(df["DATA"] >= primeira_com_pedido) & (df["DATA"] <= ultima)]

    # valores atuais
    qtd = df_periodo["PEDIDO"].nunique()
    total = df_periodo["VALOR COM IPI"].sum()
    kg = df_periodo["KG"].sum()
    m2 = df_periodo["TOTAL M2"].sum()

    # ano anterior – mesmo intervalo real (dia da primeira_com_pedido até dia da última)
    inicio_real_ant = primeira_com_pedido.replace(year=ano - 1)
    fim_ant = ultima.replace(year=ano - 1)

    df_ant = df[(df["DATA"] >= inicio_real_ant) & (df["DATA"] <= fim_ant)]

    qtd_ant = df_ant["PEDIDO"].nunique()
    total_ant = df_ant["VALOR COM IPI"].sum()
    kg_ant = df_ant["KG"].sum()
    m2_ant = df_ant["TOTAL M2"].sum()

    # tickets
    ticket_atual = total / qtd if qtd else 0
    ticket_ant = total_ant / qtd_ant if qtd_ant else 0

    # monta estrutura final
    return {
        "faturamento": {
            "atual": round(total, 2),
            "ano_anterior": round(total_ant, 2),
            "variacao": ((total / total_ant) - 1) * 100 if total_ant else 0,
            # datas para EXIBIÇÃO
            "data_atual": ultima.strftime("%d/%m/%Y"),
            "inicio_mes": inicio_exib_atual.strftime("%d/%m/%Y"),
            "data_ano_anterior": fim_ant.strftime("%d/%m/%Y"),
            "inicio_mes_anterior": inicio_exib_ant.strftime("%d/%m/%Y"),
        },
        "qtd": {
            "atual": int(qtd),
            "ano_anterior": int(qtd_ant),
            "variacao": ((qtd / qtd_ant) - 1) * 100 if qtd_ant else 0,
        },
        "kg": {
            # arredonda pra zero casas → 7108 kg
            "atual": round(kg, 0),
            "ano_anterior": round(kg_ant, 0),
            "variacao": ((kg / kg_ant) - 1) * 100 if kg_ant else 0,
        },
        "ticket": {
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant) - 1) * 100 if ticket_ant else 0,
        },
        "preco": {
            "preco_medio_kg": round(total / kg, 2) if kg else 0,
            "preco_medio_m2": round(total / m2, 2) if m2 else 0,
            "total_kg": round(kg, 2),
            "total_m2": round(m2, 2),
            "data": ultima.strftime("%d/%m/%Y"),
        },
    }


# ======================================================
# SALVA JSON DUPLICADO (dados/ e site/dados/)
# ======================================================
def salvar(nome, dados):
    for caminho in (f"dados/{nome}", f"site/dados/{nome}"):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    df = carregar()
    res = calcular(df)

    salvar("kpi_faturamento.json", res["faturamento"])
    salvar("kpi_quantidade_pedidos.json", res["qtd"])
    salvar("kpi_kg_total.json", res["kg"])
    salvar("kpi_ticket_medio.json", res["ticket"])
    salvar("kpi_preco_medio.json", res["preco"])

    print("=====================================")
    print("Pedidos atuais:", res["qtd"]["atual"])
    print(
        "Período real usado:",
        "de",
        df["DATA"].min().strftime("%d/%m/%Y"),
        "até",
        df["DATA"].max().strftime("%d/%m/%Y"),
    )
    print("Data início exibida no site:", res["faturamento"]["inicio_mes"])
    print("Última data:", res["faturamento"]["data_atual"])
    print("=====================================")
