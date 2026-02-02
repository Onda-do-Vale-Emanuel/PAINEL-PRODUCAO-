import pandas as pd
import json
from datetime import datetime

# ==========================================================
# Carregar Excel corrigindo tipos numéricos
# ==========================================================
def carregar_excel():
    caminho = "excel/PEDIDOS ONDA.xlsx"
    df = pd.read_excel(caminho)

    # Padroniza nomes das colunas em MAIÚSCULAS
    df.columns = df.columns.str.upper()

    # Colunas necessárias
    colunas_obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]

    for col in colunas_obrig:
        if col not in df.columns:
            raise Exception(f"❌ A coluna '{col}' não foi encontrada no Excel.")

    # Converte DATA
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # ==========================================================
    # Forçar conversão numérica (corrige texto, vírgula, vazio etc.)
    # ==========================================================
    for coluna_num in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[coluna_num] = (
            df[coluna_num]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
        )

        df[coluna_num] = pd.to_numeric(df[coluna_num], errors="coerce").fillna(0)

    return df


# ==========================================================
# Selecionar a data mais recente do Excel
# ==========================================================
def obter_data_referencia(df):
    datas_validas = df["DATA"].dropna()
    if datas_validas.empty:
        raise Exception("❌ Nenhuma data válida encontrada no Excel.")
    return datas_validas.max()


# ==========================================================
# Calcular Preço Médio
# ==========================================================
def calcular_preco_medio(df, data_ref):
    # Filtra pelo mês da data referência
    df_mes = df[df["DATA"].dt.month == data_ref.month]

    total_valor = df_mes["VALOR COM IPI"].sum()
    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["TOTAL M2"].sum()

    preco_kg = total_valor / total_kg if total_kg > 0 else 0
    preco_m2 = total_valor / total_m2 if total_m2 > 0 else 0

    return {
        "preco_medio_kg": round(preco_kg, 2),
        "preco_medio_m2": round(preco_m2, 2),
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2),
        "data": data_ref.strftime("%d/%m/%Y"),
    }


# ==========================================================
# Salvar arquivos JSON
# ==========================================================
def salvar_json(dados):
    with open("dados/kpi_preco_medio.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open("site/dados/kpi_preco_medio.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================
if __name__ == "__main__":
    df = carregar_excel()

    data_ref = obter_data_referencia(df)
    print("📅 Última data encontrada:", data_ref)

    preco = calcular_preco_medio(df, data_ref)

    print("Preço médio gerado:")
    print(json.dumps(preco, indent=2, ensure_ascii=False))

    salvar_json(preco)
