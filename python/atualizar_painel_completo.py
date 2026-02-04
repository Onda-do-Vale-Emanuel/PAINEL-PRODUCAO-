import pandas as pd
import json
import re
from datetime import datetime


CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"


# ======================================================
# 🔹 Função para limpar números brasileiros
# ======================================================
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


# ======================================================
# 🔹 CARREGA e NORMALIZA A PLANILHA
# ======================================================
def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.strip().str.upper()

    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória não encontrada no Excel: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    return df


# ======================================================
# 🔹 DEFINE PERÍODO REAL DO MÊS
# ======================================================
def obter_periodo(df):
    ultima_data = df["DATA"].max()
    mes = ultima_data.month
    ano = ultima_data.year

    primeira_real = df[df["DATA"].dt.month == mes]["DATA"].min()

    # EXIBIÇÃO NO SITE SEMPRE COMEÇA EM 01/MM/AAAA
    primeira_exibicao = datetime(ano, mes, 1)

    return primeira_real, ultima_data, primeira_exibicao


# ======================================================
# 🔹 CALCULA TODOS OS KPIs
# ======================================================
def calcular_kpis(df):
    primeira_real, ultima, primeira_exibicao = obter_periodo(df)

    # 📌 1 — Filtrar período real do mês
    df_periodo = df[(df["DATA"] >= primeira_real) & (df["DATA"] <= ultima)]

    # 📌 2 — Totais do período real
    total_valor = df_periodo["VALOR COM IPI"].sum()
    total_kg = df_periodo["KG"].sum()
    total_m2 = df_periodo["TOTAL M2"].sum()
    qtd = len(df_periodo)

    # 📌 3 — Ano anterior (mesmo range)
    ano_ant = ultima.year - 1
    primeira_ant = primeira_real.replace(year=ano_ant)
    ultima_ant = ultima.replace(year=ano_ant)

    df_ant = df[(df["DATA"] >= primeira_ant) & (df["DATA"] <= ultima_ant)]

    total_valor_ant = df_ant["VALOR COM IPI"].sum()
    qtd_ant = len(df_ant)
    total_kg_ant = df_ant["KG"].sum()
    total_m2_ant = df_ant["TOTAL M2"].sum()

    # 📌 4 — Ticket médio
    ticket_atual = total_valor / qtd if qtd else 0
    ticket_ant = total_valor_ant / qtd_ant if qtd_ant else 0

    # 📌 5 — Preço médio
    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    return {
        "periodo": {
            "primeira_real": primeira_real,
            "ultima": ultima,
            "primeira_exibicao": primeira_exibicao
        },
        "fat": {
            "atual": round(total_valor, 2),
            "ano_anterior": round(total_valor_ant, 2),
            "variacao": ((total_valor / total_valor_ant - 1) * 100) if total_valor_ant else 0,
            "data_atual": ultima.strftime("%d/%m/%Y"),
            "data_ano_anterior": ultima_ant.strftime("%d/%m/%Y"),
            "inicio_exibicao": primeira_exibicao.strftime("%d/%m/%Y")
        },
        "qtd": {
            "atual": qtd,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd / qtd_ant - 1) * 100) if qtd_ant else 0
        },
        "kg": {
            "atual": round(total_kg, 2),
            "ano_anterior": round(total_kg_ant, 2),
            "variacao": ((total_kg / total_kg_ant - 1) * 100) if total_kg_ant else 0
        },
        "ticket": {
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant - 1) * 100) if ticket_ant else 0
        },
        "preco": {
            "preco_medio_kg": preco_kg,
            "preco_medio_m2": preco_m2,
            "total_kg": round(total_kg, 2),
            "total_m2": round(total_m2, 2),
            "data": ultima.strftime("%d/%m/%Y")
        }
    }


# ======================================================
# 🔹 SALVAR JSON
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# 🔹 EXECUTAR SCRIPT
# ======================================================
if __name__ == "__main__":
    df = carregar_excel()
    resultado = calcular_kpis(df)

    salvar("kpi_faturamento.json", resultado["fat"])
    salvar("kpi_quantidade_pedidos.json", resultado["qtd"])
    salvar("kpi_kg_total.json", resultado["kg"])
    salvar("kpi_ticket_medio.json", resultado["ticket"])
    salvar("kpi_preco_medio.json", resultado["preco"])

    print("\n✓ JSON gerados corretamente.")
    print("📅 Mostrando no site: 01/" + resultado["fat"]["data_atual"][3:])
    print("📌 Período real usado:", resultado["periodo"]["primeira_real"], "→", resultado["periodo"]["ultima"])
