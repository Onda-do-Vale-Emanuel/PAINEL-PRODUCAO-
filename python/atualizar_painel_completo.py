import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# CONVERTE DATA/HORA EXCEL PARA NÚMERO
# ======================================================
def excel_datetime_para_numero(dt):
    base = datetime(1899, 12, 30)
    return (dt - base).total_seconds() / 86400.0

# ======================================================
# LIMPAR NÚMEROS
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    if isinstance(v, (int, float)):
        return float(v)

    if isinstance(v, (datetime, pd.Timestamp)):
        return float(excel_datetime_para_numero(v.to_pydatetime()))

    s = str(v).strip()

    try:
        dt = pd.to_datetime(s, errors="raise", dayfirst=True)
        if any(ch in s for ch in ["/", "-", ":"]):
            return float(excel_datetime_para_numero(dt.to_pydatetime()))
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

    df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()
    df = df[df["TIPO DE PEDIDO"] == "NORMAL"]

    df = df[(df["PEDIDO_NUM"] >= 30000) & (df["PEDIDO_NUM"] <= 50000)]
    df = df.drop_duplicates(subset=["PEDIDO_NUM"])

    return df

# ======================================================
# RESUMO
# ======================================================
def resumo(df, ano, mes, dia_limite):
    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes, dia_limite)

    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]

    pedidos = len(d)
    fat = float(d["VALOR COM IPI"].sum())
    kg = float(d["KG"].sum())
    m2 = float(d["TOTAL M2"].sum())

    ticket = fat / pedidos if pedidos else 0
    preco_kg = fat / kg if kg else 0
    preco_m2 = fat / m2 if m2 else 0

    return pedidos, fat, kg, m2, ticket, preco_kg, preco_m2

# ======================================================
# SALVAR JSON
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    df = carregar()

    ultima_data = df["DATA"].max()
    ano = ultima_data.year
    mes = ultima_data.month
    dia = ultima_data.day

    # ATUAL
    ped_a, fat_a, kg_a, m2_a, ticket_a, preco_kg_a, preco_m2_a = resumo(df, ano, mes, dia)

    # ANO ANTERIOR
    ped_b, fat_b, kg_b, m2_b, ticket_b, preco_kg_b, preco_m2_b = resumo(df, ano - 1, mes, dia)

    salvar("kpi_preco_medio.json", {
        "atual": {
            "preco_medio_kg": round(preco_kg_a, 2),
            "preco_medio_m2": round(preco_m2_a, 2),
            "total_kg": round(kg_a, 2),
            "total_m2": round(m2_a, 2),
            "data": ultima_data.strftime("%d/%m/%Y")
        },
        "ano_anterior": {
            "preco_medio_kg": round(preco_kg_b, 2),
            "preco_medio_m2": round(preco_m2_b, 2),
            "total_kg": round(kg_b, 2),
            "total_m2": round(m2_b, 2),
            "data": f"{dia:02d}/{mes:02d}/{ano-1}"
        }
    })

    print("=====================================")
    print(" ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=====================================")
