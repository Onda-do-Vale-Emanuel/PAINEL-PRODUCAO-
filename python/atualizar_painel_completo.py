import pandas as pd
import json
import re
from datetime import datetime

# ======================================================
# CARREGA E TRATA O EXCEL
# ======================================================
def carregar_excel():
    df = pd.read_excel("excel/PEDIDOS ONDA.xlsx")

    # Normaliza nomes das colunas
    df.columns = df.columns.str.strip().str.upper()

    # Verifica colunas obrigatórias
    obrigatorias = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrigatorias:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente no Excel: {c}")

    # Converte DATA
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # Aplica limpeza brasileira correta
    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero_br)
    df["KG"] = df["KG"].apply(limpar_numero_br)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero_br)

    return df

# ======================================================
# FUNÇÃO CORRETA PARA FORMATOS BR (EVITA INFLAR NÚMEROS)
# ======================================================
def limpar_numero_br(valor):
    """
    Converte formatos brasileiros corretamente:
    - 1.234.567,89 → 1234567.89
    - 123,45 → 123.45
    - 1.234 → 1234
    - " 1.234,56 kg" → 1234.56
    """
    if pd.isna(valor):
        return 0

    s = str(valor).strip()

    # mantém apenas números, ponto e vírgula
    s = re.sub(r"[^0-9.,-]", "", s)

    # usa vírgula como decimal
    if "," in s:
        parte_inteira, parte_decimal = s.split(",", 1)
        parte_inteira = parte_inteira.replace(".", "")
        s = f"{parte_inteira}.{parte_decimal}"
    else:
        s = s.replace(".", "")

    try:
        return float(s)
    except:
        return 0

# ======================================================
# DATA DE REFERÊNCIA — SEMPRE A MAIOR DATA DO EXCEL
# ======================================================
def obter_data_ref(df):
    datas = df["DATA"].dropna()
    if datas.empty:
        raise Exception("❌ Sem datas válidas no Excel.")
    return datas.max()

# ======================================================
# CALCULA KPIs PADRÃO
# ======================================================
def calcular_kpis_padrao(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    atual = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    anterior = df[(df["DATA"].dt.year == ano - 1) & (df["DATA"].dt.month == mes)]

    fat_atual = atual["VALOR COM IPI"].sum()
    fat_ant = anterior["VALOR COM IPI"].sum()

    kg_atual = atual["KG"].sum()
    kg_ant = anterior["KG"].sum()

    qtd_atual = len(atual)
    qtd_ant = len(anterior)

    ticket_atual = fat_atual / qtd_atual if qtd_atual > 0 else 0
    ticket_ant = fat_ant / qtd_ant if qtd_ant > 0 else 0

    return {
        "faturamento": {
            "atual": round(fat_atual, 2),
            "ano_anterior": round(fat_ant, 2),
            "variacao": ((fat_atual / fat_ant - 1) * 100) if fat_ant > 0 else 0,
            "data_atual": data_ref.strftime("%d/%m/%Y"),
            "data_ano_anterior": data_ref.replace(year=ano - 1).strftime("%d/%m/%Y"),
        },
        "kg": {
            "atual": round(kg_atual, 2),
            "ano_anterior": round(kg_ant, 2),
            "variacao": ((kg_atual / kg_ant - 1) * 100) if kg_ant > 0 else 0,
        },
        "qtd": {
            "atual": qtd_atual,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd_atual / qtd_ant - 1) * 100) if qtd_ant > 0 else 0,
        },
        "ticket": {
            "atual": round(ticket_atual, 2),
            "ano_anterior": round(ticket_ant, 2),
            "variacao": ((ticket_atual / ticket_ant - 1) * 100) if ticket_ant > 0 else 0,
        },
    }

# ======================================================
# PREÇO MÉDIO (COM MESMA DATA DE REFERÊNCIA)
# ======================================================
def calcular_preco_medio(df, data_ref):
    mes = data_ref.month
    ano = data_ref.year

    df_mes = df[(df["DATA"].dt.month == mes) & (df["DATA"].dt.year == ano)]

    total_valor = df_mes["VALOR COM IPI"].sum()
    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg > 0 else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 > 0 else 0

    return {
        "preco_medio_kg": preco_kg,
        "preco_medio_m2": preco_m2,
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2),
        "data": data_ref.strftime("%d/%m/%Y"),
    }

# ======================================================
# SALVAR JSON
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ======================================================
# EXECUÇÃO PRINCIPAL
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

    print("\n✓ Atualização concluída com sucesso.")
