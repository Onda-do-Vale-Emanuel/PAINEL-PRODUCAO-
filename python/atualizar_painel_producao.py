import pandas as pd
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
#  PAINEL INFORMATIVO PRODUÇÃO - BACKEND
#  - Lê planilhas de produção 2025/2026
#  - Filtra somente máquinas dos grupos definidos
#  - Calcula:
#       * Peso do dia (kg prod)
#       * Acumulado do mês (kg prod)
#  - Gera JSONs para o site em /dados e /site/dados
# ============================================================

# ---------- Descobrir diretório base (igual do painel comercial) ----------
def descobrir_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent

    for _ in range(6):
        # Se encontrar a pasta excel e (dados OU site), assume como raiz
        if (base / "excel").exists():
            return base
        base = base.parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = descobrir_base_dir()

# Planilhas de produção (sem acento no nome do arquivo)
EXCEL_2026 = BASE_DIR / "excel" / "Producao_2026.xlsx"
EXCEL_2025 = BASE_DIR / "excel" / "Producao_2025.xlsx"

# Pastas de saída dos JSONs
DADOS_DIR_1 = BASE_DIR / "dados"
DADOS_DIR_2 = BASE_DIR / "site" / "dados"

# Grupos de máquinas
GRUPO_IMPRESSORAS = [3, 2, 4]
GRUPO_ACABAMENTO = [11, 9, 8, 7, 20, 10, 15]


# ---------- Utilitários ----------
def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


def achar_coluna(df: pd.DataFrame, candidatos):
    cols = set(df.columns)
    for c in candidatos:
        if c in cols:
            return c
    return None


def limpar_numero(v) -> float:
    """Converte número em formato brasileiro ou bagunçado para float."""
    if pd.isna(v):
        return 0.0

    if isinstance(v, (int, float)):
        try:
            return float(v)
        except:
            return 0.0

    s = str(v).strip()
    s = re.sub(r"[^0-9,.\-]", "", s)

    if s in ("", "-", ",", ".", ",-", ".-"):
        return 0.0

    # Se tiver . e , assume que . é milhar e , é decimal
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except:
            return 0.0

    # Só vírgula -> decimal brasileiro
    if "," in s and "." not in s:
        try:
            return float(s.replace(",", "."))
        except:
            return 0.0

    # Só ponto
    if "." in s and "," not in s:
        try:
            return float(s)
        except:
            return 0.0

    try:
        return float(s)
    except:
        return 0.0


def salvar_json(nome: str, payload: dict):
    """Salva JSON em dados/ e, se existir, em site/dados/."""
    DADOS_DIR_1.mkdir(parents=True, exist_ok=True)
    with open(DADOS_DIR_1 / nome, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    if DADOS_DIR_2.parent.exists():  # se a pasta site existir
        DADOS_DIR_2.mkdir(parents=True, exist_ok=True)
        with open(DADOS_DIR_2 / nome, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)


# ---------- Leitura das planilhas ----------
def carregar_planilha_producao(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_excel(caminho, sheet_name=0)
    df = normalizar_colunas(df)

    # Colunas chave
    col_data = achar_coluna(df, ["DATA REFERÊNCIA", "DATA REFERENCIA", "DATA REF", "DATA"])
    if not col_data:
        raise KeyError(f"Não encontrei a coluna de DATA em {caminho.name}. Colunas: {list(df.columns)}")

    col_maq = achar_coluna(df, ["MAQ", "MÁQ", "MAQUINA", "MÁQUINA"])
    if not col_maq:
        raise KeyError(f"Não encontrei a coluna MAQ em {caminho.name}. Colunas: {list(df.columns)}")

    col_kg = achar_coluna(df, ["KG PROD", "KG PRODUZIDO", "KG_PROD", "KG"])
    if not col_kg:
        raise KeyError(f"Não encontrei a coluna KG PROD em {caminho.name}. Colunas: {list(df.columns)}")

    # Trata data
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce", dayfirst=True)
    df = df[df[col_data].notna()]

    # Converte máquina para número
    df[col_maq] = pd.to_numeric(df[col_maq], errors="coerce")

    # Converte kg
    df[col_kg] = df[col_kg].apply(limpar_numero)

    # Renomeia para nomes padrão
    df = df.rename(columns={
        col_data: "DATA",
        col_maq: "MAQ",
        col_kg: "KG_PROD",
    })

    # Filtra só as máquinas desejadas
    df = df[df["MAQ"].isin(GRUPO_IMPRESSORAS + GRUPO_ACABAMENTO)]

    return df


def ajustar_ano_seguro(data: datetime, delta_anos: int) -> datetime:
    """Tenta ajustar o ano mantendo mês/dia; se der erro (ex: 29/02), volta dia até funcionar."""
    alvo_ano = data.year + delta_anos
    dia = data.day
    while dia > 27:
        try:
            return datetime(alvo_ano, data.month, dia)
        except ValueError:
            dia -= 1
    # fallback simples
    return datetime(alvo_ano, data.month, 1)


# ---------- Cálculos de resumo ----------
def resumo_por_periodo(df: pd.DataFrame, inicio: datetime, fim: datetime):
    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)].copy()

    kg_imp = float(d.loc[d["MAQ"].isin(GRUPO_IMPRESSORAS), "KG_PROD"].sum())
    kg_acab = float(d.loc[d["MAQ"].isin(GRUPO_ACABAMENTO), "KG_PROD"].sum())
    kg_total = kg_imp + kg_acab

    return {
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y"),
        "impressoras": round(kg_imp, 2),
        "acabamento": round(kg_acab, 2),
        "total": round(kg_total, 2),
    }


def calcular_variacao(atual: float, anterior: float) -> float:
    if anterior == 0:
        return 0.0
    return round(((atual / anterior) - 1) * 100, 2)


# ---------- Função principal ----------
def main():
    # Carrega planilhas
    df_2026 = carregar_planilha_producao(EXCEL_2026)
    df_2025 = carregar_planilha_producao(EXCEL_2025)

    # Última data válida em 2026
    ultima_data_2026 = df_2026["DATA"].max()

    # -------- Peso do dia --------
    inicio_dia_atual = ultima_data_2026.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_dia_atual = inicio_dia_atual

    dia_anterior = ajustar_ano_seguro(ultima_data_2026, -1)
    inicio_dia_ant = dia_anterior.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_dia_ant = inicio_dia_ant

    resumo_dia_atual = resumo_por_periodo(df_2026, inicio_dia_atual, fim_dia_atual)
    resumo_dia_ant = resumo_por_periodo(df_2025, inicio_dia_ant, fim_dia_ant)

    # Variações peso do dia
    var_imp_dia = calcular_variacao(resumo_dia_atual["impressoras"], resumo_dia_ant["impressoras"])
    var_acab_dia = calcular_variacao(resumo_dia_atual["acabamento"], resumo_dia_ant["acabamento"])
    var_total_dia = calcular_variacao(resumo_dia_atual["total"], resumo_dia_ant["total"])

    payload_peso_dia = {
        "data_atual": resumo_dia_atual["inicio"],
        "data_ano_anterior": resumo_dia_ant["inicio"],
        "impressoras": {
            "atual": resumo_dia_atual["impressoras"],
            "ano_anterior": resumo_dia_ant["impressoras"],
            "variacao": var_imp_dia,
        },
        "acabamento": {
            "atual": resumo_dia_atual["acabamento"],
            "ano_anterior": resumo_dia_ant["acabamento"],
            "variacao": var_acab_dia,
        },
        "total": {
            "atual": resumo_dia_atual["total"],
            "ano_anterior": resumo_dia_ant["total"],
            "variacao": var_total_dia,
        },
    }

    salvar_json("kpi_peso_dia.json", payload_peso_dia)

    # -------- Acumulado do mês --------
    inicio_mes_atual = ultima_data_2026.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim_mes_atual = ultima_data_2026.replace(hour=0, minute=0, second=0, microsecond=0)

    inicio_mes_ant = ajustar_ano_seguro(inicio_mes_atual, -1)
    fim_mes_ant = ajustar_ano_seguro(fim_mes_atual, -1)

    resumo_mes_atual = resumo_por_periodo(df_2026, inicio_mes_atual, fim_mes_atual)
    resumo_mes_ant = resumo_por_periodo(df_2025, inicio_mes_ant, fim_mes_ant)

    var_imp_mes = calcular_variacao(resumo_mes_atual["impressoras"], resumo_mes_ant["impressoras"])
    var_acab_mes = calcular_variacao(resumo_mes_atual["acabamento"], resumo_mes_ant["acabamento"])
    var_total_mes = calcular_variacao(resumo_mes_atual["total"], resumo_mes_ant["total"])

    payload_acumulado_mes = {
        "periodo_atual": {
            "inicio": resumo_mes_atual["inicio"],
            "fim": resumo_mes_atual["fim"],
        },
        "periodo_ano_anterior": {
            "inicio": resumo_mes_ant["inicio"],
            "fim": resumo_mes_ant["fim"],
        },
        "impressoras": {
            "atual": resumo_mes_atual["impressoras"],
            "ano_anterior": resumo_mes_ant["impressoras"],
            "variacao": var_imp_mes,
        },
        "acabamento": {
            "atual": resumo_mes_atual["acabamento"],
            "ano_anterior": resumo_mes_ant["acabamento"],
            "variacao": var_acab_mes,
        },
        "total": {
            "atual": resumo_mes_atual["total"],
            "ano_anterior": resumo_mes_ant["total"],
            "variacao": var_total_mes,
        },
    }

    salvar_json("kpi_acumulado_mes.json", payload_acumulado_mes)

    # Resumo para exibir na interface
    resumo_print = {
        "data_peso_dia_2026": resumo_dia_atual["inicio"],
        "data_peso_dia_2025": resumo_dia_ant["inicio"],
        "peso_dia_total_2026": resumo_dia_atual["total"],
        "peso_dia_total_2025": resumo_dia_ant["total"],
        "periodo_mes_2026": f"{resumo_mes_atual['inicio']} até {resumo_mes_atual['fim']}",
        "periodo_mes_2025": f"{resumo_mes_ant['inicio']} até {resumo_mes_ant['fim']}",
        "peso_mes_total_2026": resumo_mes_atual["total"],
        "peso_mes_total_2025": resumo_mes_ant["total"],
    }

    print("\n=====================================")
    print("ATUALIZAÇÃO PAINEL PRODUÇÃO CONCLUÍDA")
    print("=====================================")
    print(f"Peso do dia (Total) 2026 [{resumo_dia_atual['inicio']}]: {resumo_dia_atual['total']:.2f} kg")
    print(f"Peso do dia (Total) 2025 [{resumo_dia_ant['inicio']}]: {resumo_dia_ant['total']:.2f} kg")
    print("-------------------------------------")
    print(f"Acumulado mês 2026: {resumo_mes_atual['total']:.2f} kg")
    print(f"Acumulado mês 2025: {resumo_mes_ant['total']:.2f} kg")
    print("=====================================\n")

    return resumo_print


if __name__ == "__main__":
    main()