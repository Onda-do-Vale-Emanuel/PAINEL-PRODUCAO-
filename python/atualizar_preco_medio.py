import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"
CAMINHO_JSON_PRECO = "dados/kpi_preco_medio.json"
CAMINHO_JSON_SITE = "site/dados/kpi_preco_medio.json"


def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0
    v = str(valor).strip()
    v = re.sub(r"[^0-9,.\-]", "", v)

    if v in ("", "-", ",", ".", ",-", ".-"):
        return 0.0

    if v.count("-") >= 2:
        return 0.0

    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        v = v.replace(",", ".")
    else:
        if "." in v:
            partes = v.split(".")
            if len(partes[-1]) == 3:
                v = v.replace(".", "")

    try:
        return float(v)
    except Exception:
        return 0.0


def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    colunas_necessarias = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in colunas_necessarias:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória não encontrada no Excel: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()].copy()

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
    df["KG"] = df["KG"].apply(limpar_numero)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

    if "TIPO DE PEDIDO" in df.columns:
        df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()
        df = df[df["TIPO DE PEDIDO"] == "NORMAL"].copy()

    return df


def obter_data_referencia(df):
    datas_validas = df["DATA"].dropna()
    if len(datas_validas) == 0:
        raise Exception("❌ Nenhuma data válida encontrada no Excel")
    return datas_validas.max()


def calcular_preco_medio(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]

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


def salvar_json(dados):
    with open(CAMINHO_JSON_PRECO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(CAMINHO_JSON_SITE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    df = carregar_excel()
    data_ref = obter_data_referencia(df)
    print("📅 Última data encontrada:", data_ref)

    preco = calcular_preco_medio(df, data_ref)

    print("Preço médio gerado:")
    print(json.dumps(preco, indent=2, ensure_ascii=False))

    salvar_json(preco)
    print("✓ JSON gerado com sucesso.")
