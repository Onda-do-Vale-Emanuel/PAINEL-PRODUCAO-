import pandas as pd
import json
from datetime import datetime

# ======================================================
# CARREGA EXCEL E PADRONIZA COLUNAS
# ======================================================
def carregar_excel():
    df = pd.read_excel("excel/PEDIDOS ONDA.xlsx")

    # padroniza nomes
    df.columns = df.columns.str.upper()

    # validações
    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente no Excel: {c}")

    # converte datas
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # limpa números
    for col in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

# ======================================================
# OBTÉM ÚLTIMA DATA DO EXCEL
# ======================================================
def obter_data_ref(df):
    datas = df["DATA"].dropna()
    if datas.empty:
        raise Exception("❌ Sem datas válidas no Excel.")
    return datas.max()

# ======================================================
# CALCULA KPIs PADRÃO (FATURAMENTO, KG, TICKET)
# ======================================================
def calcular_kpis_padrao(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    atual = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    anterior = df[(df["DATA"].dt.year == ano - 1) & (df["DATA"].dt.month == mes)]

    def soma_fat(x): return x["VALOR COM IPI"].sum()
    def soma_kg(x): return x["KG"].sum()

    fat_atual = soma_fat(atual)
    fat_ant = soma_fat(anterior)

    kg_atual = soma_kg(atual)
    kg_ant = soma_kg(anterior)

    # ticket
    qtd_atual = len(atual)
    qtd_ant = len(anterior)

    ticket_atual = fat_atual / qtd_atual if qtd_atual > 0 else 0
    ticket_ant = fat_ant / qtd_ant if qtd_ant > 0 else 0

    return {
        "faturamento": {
            "atual": fat_atual,
            "ano_anterior": fat_ant,
            "variacao": ((fat_atual / fat_ant - 1) * 100) if fat_ant > 0 else 0,
            "data_atual": data_ref.strftime("%d/%m/%Y"),
            "data_ano_anterior": data_ref.replace(year=data_ref.year - 1).strftime("%d/%m/%Y")
        },
        "kg": {
            "atual": kg_atual,
            "ano_anterior": kg_ant,
            "variacao": ((kg_atual / kg_ant - 1) * 100) if kg_ant > 0 else 0
        },
        "qtd": {
            "atual": qtd_atual,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd_atual / qtd_ant - 1) * 100) if qtd_ant > 0 else 0
        },
        "ticket": {
            "atual": ticket_atual,
            "ano_anterior": ticket_ant,
            "variacao": ((ticket_atual / ticket_ant - 1) * 100) if ticket_ant > 0 else 0
        }
    }

# ======================================================
# CALCULA PREÇO MÉDIO OFICIAL (MESMO DO SCRIPT SEPARADO)
# ======================================================
def calcular_preco_medio(df, data_ref):
    df_mes = df[df["DATA"].dt.month == data_ref.month]

    total_valor = df_mes["VALOR COM IPI"].sum()
    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["TOTAL M2"].sum()

    return {
        "preco_medio_kg": round(total_valor / total_kg, 2) if total_kg > 0 else 0,
        "preco_medio_m2": round(total_valor / total_m2, 2) if total_m2 > 0 else 0,
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2),
        "data": data_ref.strftime("%d/%m/%Y")
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
# EXECUTA TUDO
# ======================================================
if __name__ == "__main__":
    df = carregar_excel()
    data_ref = obter_data_ref(df)

    print("📅 Última data encontrada:", data_ref)

    kpis = calcular_kpis_padrao(df, data_ref)
    preco = calcular_preco_medio(df, data_ref)

    salvar("kpi_faturamento.json", kpis["faturamento"])
    salvar("kpi_kg_total.json", kpis["kg"])
    salvar("kpi_quantidade_pedidos.json", kpis["qtd"])
    salvar("kpi_ticket_medio.json", kpis["ticket"])
    salvar("kpi_preco_medio.json", preco)

    print("✓ Arquivos JSON atualizados com sucesso.")
