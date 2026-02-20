import pandas as pd
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
#  PAINEL INFORMATIVO PRODUÇÃO - VERSÃO CORRIGIDA DATA
# ============================================================

def descobrir_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent

    for _ in range(6):
        if (base / "excel").exists():
            return base
        base = base.parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = descobrir_base_dir()

EXCEL_2026 = BASE_DIR / "excel" / "Producao_2026.xlsx"
EXCEL_2025 = BASE_DIR / "excel" / "Producao_2025.xlsx"

DADOS_DIR_1 = BASE_DIR / "dados"
DADOS_DIR_2 = BASE_DIR / "site" / "dados"

GRUPO_IMPRESSORAS = [3, 2, 4]
GRUPO_ACABAMENTO = [11, 9, 8, 7, 20, 10, 15]


def normalizar_colunas(df):
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


def limpar_numero(v):
    if pd.isna(v):
        return 0.0
    try:
        return float(str(v).replace(".", "").replace(",", "."))
    except:
        return 0.0


def carregar_planilha(caminho):
    df = pd.read_excel(caminho)
    df = normalizar_colunas(df)

    df["DATA REFERÊNCIA"] = pd.to_datetime(
        df["DATA REFERÊNCIA"], errors="coerce", dayfirst=True
    )

    df["MAQ"] = pd.to_numeric(df["MAQ"], errors="coerce")
    df["KG PROD"] = df["KG PROD"].apply(limpar_numero)

    df = df[df["MAQ"].isin(GRUPO_IMPRESSORAS + GRUPO_ACABAMENTO)]

    df = df.rename(
        columns={
            "DATA REFERÊNCIA": "DATA",
            "KG PROD": "KG_PROD",
        }
    )

    return df


def salvar_json(nome, payload):
    DADOS_DIR_1.mkdir(parents=True, exist_ok=True)
    with open(DADOS_DIR_1 / nome, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    DADOS_DIR_2.mkdir(parents=True, exist_ok=True)
    with open(DADOS_DIR_2 / nome, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def resumo_por_dia(df, data):
    d = df[df["DATA"].dt.date == data.date()]

    imp = d[d["MAQ"].isin(GRUPO_IMPRESSORAS)]["KG_PROD"].sum()
    acab = d[d["MAQ"].isin(GRUPO_ACABAMENTO)]["KG_PROD"].sum()

    return round(imp, 2), round(acab, 2)


def resumo_acumulado_mes(df, data):
    inicio = data.replace(day=1)

    d = df[
        (df["DATA"].dt.date >= inicio.date())
        & (df["DATA"].dt.date <= data.date())
    ]

    imp = d[d["MAQ"].isin(GRUPO_IMPRESSORAS)]["KG_PROD"].sum()
    acab = d[d["MAQ"].isin(GRUPO_ACABAMENTO)]["KG_PROD"].sum()

    return round(imp, 2), round(acab, 2)


def variacao(atual, anterior):
    if anterior == 0:
        return 0
    return round(((atual / anterior) - 1) * 100, 2)


def main():
    df26 = carregar_planilha(EXCEL_2026)
    df25 = carregar_planilha(EXCEL_2025)

    ultima_data = df26["DATA"].max()
    data_ant = ultima_data.replace(year=ultima_data.year - 1)

    # PESO DO DIA
    imp26, acab26 = resumo_por_dia(df26, ultima_data)
    imp25, acab25 = resumo_por_dia(df25, data_ant)

    salvar_json(
        "kpi_peso_dia.json",
        {
            "data_atual": ultima_data.strftime("%d/%m/%Y"),
            "data_anterior": data_ant.strftime("%d/%m/%Y"),
            "impressoras": {
                "atual": imp26,
                "ano_anterior": imp25,
                "variacao": variacao(imp26, imp25),
            },
            "acabamento": {
                "atual": acab26,
                "ano_anterior": acab25,
                "variacao": variacao(acab26, acab25),
            },
        },
    )

    # ACUMULADO
    imp26m, acab26m = resumo_acumulado_mes(df26, ultima_data)
    imp25m, acab25m = resumo_acumulado_mes(df25, data_ant)

    salvar_json(
        "kpi_acumulado_mes.json",
        {
            "periodo_atual": f"01/{ultima_data.strftime('%m/%Y')} até {ultima_data.strftime('%d/%m/%Y')}",
            "periodo_anterior": f"01/{data_ant.strftime('%m/%Y')} até {data_ant.strftime('%d/%m/%Y')}",
            "impressoras": {
                "atual": imp26m,
                "ano_anterior": imp25m,
                "variacao": variacao(imp26m, imp25m),
            },
            "acabamento": {
                "atual": acab26m,
                "ano_anterior": acab25m,
                "variacao": variacao(acab26m, acab25m),
            },
        },
    )

    print("\n=====================================")
    print("PAINEL PRODUÇÃO ATUALIZADO COM SUCESSO")
    print("=====================================")
    print("Data dia:", ultima_data.strftime("%d/%m/%Y"))
    print("=====================================\n")


if __name__ == "__main__":
    main()