import pandas as pd
import json
import re
import math
from datetime import datetime, date
import calendar

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"


# ======================================================
# FUNÇÃO ROBUSTA PARA NÚMEROS BRASILEIROS + LIXO
# ======================================================
def limpar_numero(valor):
    """
    Converte textos variados em número float.
    Trata:
    - "1.234.567,89"
    - "1.234"
    - "1,234"
    - "1234"
    - "R$ 1.234,99"
    - E ignora lixos tipo "2026-02-03151642".
    """
    if pd.isna(valor):
        return 0.0

    v = str(valor).strip()

    # Mantém só dígitos, vírgula, ponto e hífen
    v = re.sub(r"[^0-9,.\-]", "", v)

    # Vazio ou símbolos soltos
    if v in ("", "-", ",", ".", ",-", ".-"):
        return 0.0

    # Se tiver vários hífens, é forte candidato a data/ID, não número
    if v.count("-") >= 2:
        return 0.0

    # Caso tenha "." e "," → formato “1.234.567,89”
    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")
    elif "," in v:
        # Só vírgula → decimal brasileiro
        v = v.replace(",", ".")
    else:
        # Só ponto: decidir se é milhar ou decimal
        if "." in v:
            partes = v.split(".")
            # Se a última parte tiver 3 dígitos, tratar como milhar
            if len(partes[-1]) == 3:
                v = v.replace(".", "")

    try:
        return float(v)
    except Exception:
        return 0.0


# ======================================================
# CARREGAR E PREPARAR EXCEL
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)

    # Normaliza nomes de colunas
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória não encontrada no Excel: {c}")

    # Converte DATA
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()].copy()

    # Limpa números principais
    for c in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[c] = df[c].apply(limpar_numero)

    # Filtra apenas TIPO DE PEDIDO = "NORMAL" se existir essa coluna
    if "TIPO DE PEDIDO" in df.columns:
        df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()
        df = df[df["TIPO DE PEDIDO"] == "NORMAL"].copy()

    return df


# ======================================================
# CÁLCULO DE PERÍODOS (MESMO DIA PARA AMBOS OS ANOS)
# ======================================================
def obter_regras_periodo(df: pd.DataFrame):
    """
    Regra:
    - Ano atual: 1º dia do mês até última data real com pedido.
    - Ano anterior: 1º dia do mesmo mês até MESMO dia do mês,
      limitado ao último dia do mês no ano anterior.
    """
    ultima_data = df["DATA"].max()
    ano_atual = int(ultima_data.year)
    mes_atual = int(ultima_data.month)
    dia_limite = int(ultima_data.day)

    # Início exibição ano atual = 01/mes/ano_atual
    inicio_atual = date(ano_atual, mes_atual, 1)

    # Fim real ano atual = última data com pedido
    fim_atual = ultima_data.date()

    # Ano anterior
    ano_anterior = ano_atual - 1
    # Último dia do mês no ano anterior (para não estourar em fev/29, etc.)
    ultimo_dia_mes_ant = calendar.monthrange(ano_anterior, mes_atual)[1]
    dia_limite_ant = min(dia_limite, ultimo_dia_mes_ant)

    inicio_anterior = date(ano_anterior, mes_atual, 1)
    fim_anterior = date(ano_anterior, mes_atual, dia_limite_ant)

    return {
        "ano_atual": ano_atual,
        "mes_atual": mes_atual,
        "dia_limite": dia_limite,
        "inicio_atual": inicio_atual,
        "fim_atual": fim_atual,
        "ano_anterior": ano_anterior,
        "inicio_anterior": inicio_anterior,
        "fim_anterior": fim_anterior,
    }


# ======================================================
# RESUMO DE UM PERÍODO
# ======================================================
def resumo_periodo(df: pd.DataFrame, ano: int, mes: int, dt_ini: date, dt_fim: date):
    mask = (
        (df["DATA"].dt.year == ano)
        & (df["DATA"].dt.month == mes)
        & (df["DATA"].dt.date >= dt_ini)
        & (df["DATA"].dt.date <= dt_fim)
    )

    d = df[mask].copy()

    fat = float(d["VALOR COM IPI"].sum())
    kg = float(d["KG"].sum())
    m2 = float(d["TOTAL M2"].sum())
    pedidos = int(len(d))

    ticket = fat / pedidos if pedidos > 0 else 0.0

    return {
        "pedidos": pedidos,
        "fat": fat,
        "kg": kg,
        "m2": m2,
        "ticket": ticket,
    }


# ======================================================
# CALCULA TODOS OS KPIs
# ======================================================
def calcular_kpis(df: pd.DataFrame):
    regras = obter_regras_periodo(df)

    ano_atual = regras["ano_atual"]
    mes_atual = regras["mes_atual"]
    inicio_atual = regras["inicio_atual"]
    fim_atual = regras["fim_atual"]
    ano_anterior = regras["ano_anterior"]
    inicio_anterior = regras["inicio_anterior"]
    fim_anterior = regras["fim_anterior"]

    # Resumos
    atual = resumo_periodo(df, ano_atual, mes_atual, inicio_atual, fim_atual)
    anterior = resumo_periodo(df, ano_anterior, mes_atual, inicio_anterior, fim_anterior)

    # Variações (evita divisão por zero)
    def variacao(p_atual, p_ant):
        if p_ant == 0:
            return 0.0
        return (p_atual / p_ant - 1.0) * 100.0

    fat_var = variacao(atual["fat"], anterior["fat"])
    kg_var = variacao(atual["kg"], anterior["kg"])
    qtd_var = variacao(atual["pedidos"], anterior["pedidos"])
    ticket_var = variacao(atual["ticket"], anterior["ticket"])

    # Datas para exibição no site
    data_atual_str = fim_atual.strftime("%d/%m/%Y")
    data_ano_anterior_str = fim_anterior.strftime("%d/%m/%Y")
    inicio_mes_atual_str = inicio_atual.strftime("%d/%m/%Y")
    inicio_mes_anterior_str = inicio_anterior.strftime("%d/%m/%Y")

    # Monta estruturas finais
    kpi_fat = {
        "atual": round(atual["fat"], 2),
        "ano_anterior": round(anterior["fat"], 2),
        "variacao": fat_var,
        "inicio_mes": inicio_mes_atual_str,
        "data_atual": data_atual_str,
        "inicio_mes_anterior": inicio_mes_anterior_str,
        "data_ano_anterior": data_ano_anterior_str,
    }

    kpi_qtd = {
        "atual": atual["pedidos"],
        "ano_anterior": anterior["pedidos"],
        "variacao": qtd_var,
    }

    kpi_kg = {
        "atual": round(atual["kg"], 2),
        "ano_anterior": round(anterior["kg"], 2),
        "variacao": kg_var,
    }

    kpi_ticket = {
        "atual": round(atual["ticket"], 2),
        "ano_anterior": round(anterior["ticket"], 2),
        "variacao": ticket_var,
    }

    return {
        "fat": kpi_fat,
        "qtd": kpi_qtd,
        "kg": kpi_kg,
        "ticket": kpi_ticket,
        "regras": regras,
    }


# ======================================================
# SALVAR JSON EM /dados E /site/dados
# ======================================================
def salvar(nome, dados):
    # pasta raiz
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    # pasta usada pelo site
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    print("=====================================")
    print("Atualizando painel a partir do Excel")
    print("=====================================")

    df = carregar()
    kpis = calcular_kpis(df)
    regras = kpis["regras"]

    # Debug no console (PowerShell)
    print("=====================================")
    print(
        f"Período ATUAL     : {regras['inicio_atual'].strftime('%d/%m/%Y')} → "
        f"{regras['fim_atual'].strftime('%d/%m/%Y')}"
    )
    print(
        f"Período ANTERIOR  : {regras['inicio_anterior'].strftime('%d/%m/%Y')} → "
        f"{regras['fim_anterior'].strftime('%d/%m/%Y')}"
    )
    print(f"Pedidos atuais    : {kpis['qtd']['atual']}")
    print(f"Pedidos ano ant.  : {kpis['qtd']['ano_anterior']}")
    print("=====================================")

    # Salva JSONs para o site
    salvar("kpi_faturamento.json", kpis["fat"])
    salvar("kpi_quantidade_pedidos.json", kpis["qtd"])
    salvar("kpi_kg_total.json", kpis["kg"])
    salvar("kpi_ticket_medio.json", kpis["ticket"])

    print("✓ JSON gerados corretamente!")
