import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# CONVERTER DATA EXCEL PARA NÚMERO
# ======================================================
def excel_datetime_para_numero(dt):
    base = datetime(1899, 12, 30)
    return (dt - base).total_seconds() / 86400.0

# ======================================================
# FUNÇÃO DEFINITIVA PARA LIMPAR NÚMEROS
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    # Se já for número
    if isinstance(v, (int, float)):
        return float(v)

    # Se for datetime (tanto pandas quanto python)
    if isinstance(v, (pd.Timestamp, datetime)):
        return float(excel_datetime_para_numero(v))

    s = str(v).strip()

    # Tenta converter string de data
    try:
        dt = pd.to_datetime(s, errors="raise", dayfirst=True)
        if any(x in s for x in ["/", "-", ":"]):
            return float(excel_datetime_para_numero(dt))
    except:
        pass

    s = re.sub(r"[^0-9,.\-]", "", s)

    if s in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
        return float(s)

    if "," in s:
        return float(s.replace(",", "."))

    if "." in s:
        partes = s.split(".")
        if len(partes[-1]) == 3:
            s = s.replace(".", "")
        return float(s)

    return float(s)

# ======================================================
# CARREGAR PLANILHA
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    for col in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[col] = df[col].apply(limpar_numero)

    df["PEDIDO_NUM"] = df["PEDIDO"].apply(limpar_numero)

    if "TIPO DE PEDIDO" in df.columns:
        df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()
        df = df[df["TIPO DE PEDIDO"] == "NORMAL"]

    df = df[(df["PEDIDO_NUM"] >= 30000) & (df["PEDIDO_NUM"] <= 50000)]
    df = df.drop_duplicates(subset=["PEDIDO_NUM"])

    return df

# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    df = carregar()

    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month
    dia = ultima.day

    inicio_atual = datetime(ano, mes, 1)
    inicio_ant = datetime(ano - 1, mes, 1)
    fim_ant = datetime(ano - 1, mes, dia)

    atual = df[(df["DATA"] >= inicio_atual) & (df["DATA"] <= ultima)]
    anterior = df[(df["DATA"] >= inicio_ant) & (df["DATA"] <= fim_ant)]

    fat_atual = float(atual["VALOR COM IPI"].sum())
    fat_ant = float(anterior["VALOR COM IPI"].sum())

    kg_atual = float(atual["KG"].sum())
    kg_ant = float(anterior["KG"].sum())

    pedidos_atual = len(atual)
    pedidos_ant = len(anterior)

    ticket_atual = fat_atual / pedidos_atual if pedidos_atual else 0
    ticket_ant = fat_ant / pedidos_ant if pedidos_ant else 0

    def salvar(nome, dados):
        with open(f"dados/{nome}", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    salvar("kpi_faturamento.json", {
        "atual": fat_atual,
        "ano_anterior": fat_ant,
        "variacao": ((fat_atual/fat_ant)-1)*100 if fat_ant else 0,
        "inicio_mes": inicio_atual.strftime("%d/%m/%Y"),
        "data_atual": ultima.strftime("%d/%m/%Y"),
        "inicio_mes_anterior": inicio_ant.strftime("%d/%m/%Y"),
        "data_ano_anterior": fim_ant.strftime("%d/%m/%Y")
    })

    salvar("kpi_quantidade_pedidos.json", {
        "atual": pedidos_atual,
        "ano_anterior": pedidos_ant,
        "variacao": ((pedidos_atual/pedidos_ant)-1)*100 if pedidos_ant else 0
    })

    salvar("kpi_kg_total.json", {
        "atual": round(kg_atual),
        "ano_anterior": round(kg_ant),
        "variacao": ((kg_atual/kg_ant)-1)*100 if kg_ant else 0
    })

    salvar("kpi_ticket_medio.json", {
        "atual": round(ticket_atual, 2),
        "ano_anterior": round(ticket_ant, 2),
        "variacao": ((ticket_atual/ticket_ant)-1)*100 if ticket_ant else 0
    })

    print("\n=====================================")
    print(" ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=====================================")
