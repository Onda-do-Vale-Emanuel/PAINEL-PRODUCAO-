import pandas as pd
import json
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# PAINEL PRODUÇÃO - META SEPARADA POR GRUPO
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

# ===== METAS MENSAIS (IGUAIS PARA AMBOS, MAS APLICADAS SEPARADO) =====

METAS_MENSAIS = {
    1: 100000,
    2: 100000,
    3: 120000,
    4: 130000,
    5: 130000,
    6: 130000,
    7: 150000,
    8: 150000,
    9: 150000,
    10: 150000,
    11: 150000,
    12: 98000
}


def normalizar_colunas(df):
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


def limpar_numero(v):
    if pd.isna(v):
        return 0.0
    try:
        return float(v)
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


def variacao(atual, anterior):
    if anterior == 0:
        return 0
    return round(((atual / anterior) - 1) * 100, 2)


def main():
    df26 = carregar_planilha(EXCEL_2026)
    df25 = carregar_planilha(EXCEL_2025)

    ultima_data = df26["DATA"].max()
    data_ant = ultima_data.replace(year=ultima_data.year - 1)

    mes_atual = ultima_data.month
    meta_mes = METAS_MENSAIS.get(mes_atual, 0)

    # ================= DIA =================
    dia26 = df26[df26["DATA"].dt.date == ultima_data.date()]
    dia25 = df25[df25["DATA"].dt.date == data_ant.date()]

    imp26 = dia26[dia26["MAQ"].isin(GRUPO_IMPRESSORAS)]["KG_PROD"].sum()
    imp25 = dia25[dia25["MAQ"].isin(GRUPO_IMPRESSORAS)]["KG_PROD"].sum()

    acab26 = dia26[dia26["MAQ"].isin(GRUPO_ACABAMENTO)]["KG_PROD"].sum()
    acab25 = dia25[dia25["MAQ"].isin(GRUPO_ACABAMENTO)]["KG_PROD"].sum()

    salvar_json("kpi_peso_dia.json", {
        "data_atual": ultima_data.strftime("%d/%m/%Y"),
        "data_anterior": data_ant.strftime("%d/%m/%Y"),
        "impressoras": {
            "atual": imp26,
            "ano_anterior": imp25,
            "variacao": variacao(imp26, imp25)
        },
        "acabamento": {
            "atual": acab26,
            "ano_anterior": acab25,
            "variacao": variacao(acab26, acab25)
        }
    })

    # ================= ACUMULADO =================
    inicio_mes = ultima_data.replace(day=1)

    mes26 = df26[(df26["DATA"] >= inicio_mes) & (df26["DATA"] <= ultima_data)]

    imp26m = mes26[mes26["MAQ"].isin(GRUPO_IMPRESSORAS)]["KG_PROD"].sum()
    acab26m = mes26[mes26["MAQ"].isin(GRUPO_ACABAMENTO)]["KG_PROD"].sum()

    salvar_json("kpi_acumulado_mes.json", {
        "periodo_atual": f"01/{ultima_data.strftime('%m/%Y')} até {ultima_data.strftime('%d/%m/%Y')}",
        "impressoras": {
            "atual": imp26m
        },
        "acabamento": {
            "atual": acab26m
        }
    })

    # ================= META SEPARADA =================
    meta_json = {
        "impressoras": {
            "meta": meta_mes,
            "producao": imp26m,
            "percentual": round((imp26m / meta_mes) * 100, 2) if meta_mes else 0,
            "falta": max(meta_mes - imp26m, 0)
        },
        "acabamento": {
            "meta": meta_mes,
            "producao": acab26m,
            "percentual": round((acab26m / meta_mes) * 100, 2) if meta_mes else 0,
            "falta": max(meta_mes - acab26m, 0)
        }
    }

    salvar_json("kpi_meta_mes.json", meta_json)

    print("\nPAINEL PRODUÇÃO ATUALIZADO - META SEPARADA\n")


if __name__ == "__main__":
    main()