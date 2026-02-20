import pandas as pd
import json
import sys
from pathlib import Path

# ===============================
# DETECTAR PASTA CORRETA
# ===============================

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

EXCEL_2026 = BASE_DIR / "excel" / "Producao_2026.xlsx"
EXCEL_2025 = BASE_DIR / "excel" / "Producao_2025.xlsx"
DADOS_DIR = BASE_DIR / "dados"

GRUPO_IMPRESSORAS = [3,2,4]
GRUPO_ACABAMENTO = [11,9,8,7,20,10,15]

METAS_MENSAIS = {
    1:100000,2:100000,3:120000,4:130000,
    5:130000,6:130000,7:150000,8:150000,
    9:150000,10:150000,11:150000,12:98000
}

def salvar_json(nome, payload):
    DADOS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DADOS_DIR / nome, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def variacao(atual, anterior):
    if anterior == 0:
        return 0.0
    return round(((atual / anterior) - 1) * 100, 2)

def main():

    if not EXCEL_2026.exists():
        print("ERRO: Arquivo Producao_2026.xlsx não encontrado.")
        return

    if not EXCEL_2025.exists():
        print("ERRO: Arquivo Producao_2025.xlsx não encontrado.")
        return

    df26 = pd.read_excel(EXCEL_2026)
    df25 = pd.read_excel(EXCEL_2025)

    df26.columns = df26.columns.str.strip().str.lower()
    df25.columns = df25.columns.str.strip().str.lower()

    df26["data referência"] = pd.to_datetime(df26["data referência"], dayfirst=True)
    df25["data referência"] = pd.to_datetime(df25["data referência"], dayfirst=True)

    df26["kg prod"] = pd.to_numeric(df26["kg prod"], errors="coerce").fillna(0)
    df25["kg prod"] = pd.to_numeric(df25["kg prod"], errors="coerce").fillna(0)

    df26 = df26[df26["maq"].isin(GRUPO_IMPRESSORAS + GRUPO_ACABAMENTO)]
    df25 = df25[df25["maq"].isin(GRUPO_IMPRESSORAS + GRUPO_ACABAMENTO)]

    ultima_data = df26["data referência"].max()
    data_ant = ultima_data.replace(year=ultima_data.year - 1)

    inicio_mes_26 = ultima_data.replace(day=1)
    inicio_mes_25 = data_ant.replace(day=1)

    def soma(df, grupo):
        return float(df[df["maq"].isin(grupo)]["kg prod"].sum())

    # ===== DIA =====
    dia26 = df26[df26["data referência"] == ultima_data]
    dia25 = df25[df25["data referência"] == data_ant]

    salvar_json("kpi_peso_dia.json", {
        "data_atual": ultima_data.strftime("%d/%m/%Y"),
        "data_anterior": data_ant.strftime("%d/%m/%Y"),
        "impressoras": {
            "atual": soma(dia26, GRUPO_IMPRESSORAS),
            "ano_anterior": soma(dia25, GRUPO_IMPRESSORAS),
            "variacao": variacao(soma(dia26, GRUPO_IMPRESSORAS),
                                 soma(dia25, GRUPO_IMPRESSORAS))
        },
        "acabamento": {
            "atual": soma(dia26, GRUPO_ACABAMENTO),
            "ano_anterior": soma(dia25, GRUPO_ACABAMENTO),
            "variacao": variacao(soma(dia26, GRUPO_ACABAMENTO),
                                 soma(dia25, GRUPO_ACABAMENTO))
        }
    })

    # ===== ACUMULADO =====
    mes26 = df26[(df26["data referência"] >= inicio_mes_26) & (df26["data referência"] <= ultima_data)]
    mes25 = df25[(df25["data referência"] >= inicio_mes_25) & (df25["data referência"] <= data_ant)]

    imp26 = soma(mes26, GRUPO_IMPRESSORAS)
    imp25 = soma(mes25, GRUPO_IMPRESSORAS)
    ac26 = soma(mes26, GRUPO_ACABAMENTO)
    ac25 = soma(mes25, GRUPO_ACABAMENTO)

    salvar_json("kpi_acumulado_mes.json", {
        "periodo_atual": f"{inicio_mes_26.strftime('%d/%m/%Y')} até {ultima_data.strftime('%d/%m/%Y')}",
        "impressoras": {
            "atual": imp26,
            "ano_anterior": imp25,
            "variacao": variacao(imp26, imp25)
        },
        "acabamento": {
            "atual": ac26,
            "ano_anterior": ac25,
            "variacao": variacao(ac26, ac25)
        }
    })

    print("Atualização concluída com sucesso.")

if __name__ == "__main__":
    main()