import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# 🔥 FUNÇÃO PARA LIMPAR NÚMEROS + DATAS CORROMPIDAS
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    v_str = str(v).strip()

    # Detectar datas acidentais no formato ISO (1900 etc)
    if re.match(r"^\d{4}-\d{2}-\d{2}", v_str):
        try:
            dt = pd.to_datetime(v_str, errors="coerce")
            if not pd.isna(dt):
                # Converter data para número aproximado (ex.: 29/10/1900 → 2910)
                return float(f"{dt.day}{dt.month}")
        except:
            pass

    # Limpar caracteres estranhos
    v_clean = re.sub(r"[^0-9,.-]", "", v_str)

    if v_clean in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    # Número 9.999,99 → BR
    if "." in v_clean and "," in v_clean:
        return float(v_clean.replace(".", "").replace(",", "."))

    # Número 999,99
    if "," in v_clean:
        return float(v_clean.replace(",", "."))

    return float(v_clean)


# ======================================================
# 🔥 CARREGAMENTO DO EXCEL
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    # limpar colunas numéricas
    COLUNAS = ["VALOR TOTAL", "VALOR PRODUTO", "VALOR EMBALAGEM",
               "VALOR COM IPI", "KG", "TOTAL M2"]

    for col in COLUNAS:
        if col in df.columns:
            df[col] = df[col].apply(limpar_numero)

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    df["PEDIDO_NUM"] = df["PEDIDO"].apply(limpar_numero)
    df = df[(df["PEDIDO_NUM"] >= 30000) & (df["PEDIDO_NUM"] <= 50000)]

    return df


# ======================================================
# 🔥 REGRAS DE PERÍODO ATUAL E ANTERIOR
# ======================================================
def obter_periodos(df):
    ultima = df["DATA"].max()
    mes = ultima.month

    inicio_atual = ultima.replace(day=1)
    fim_atual = ultima

    ano_ant = ultima.year - 1
    inicio_ant = inicio_atual.replace(year=ano_ant)
    fim_alvo_ant = ultima.replace(year=ano_ant)

    df_ant = df[(df["DATA"].dt.year == ano_ant) & (df["DATA"].dt.month == mes)]

    if df_ant.empty:
        fim_ant = fim_alvo_ant
    else:
        df_ant_filtrado = df_ant[df_ant["DATA"] <= fim_alvo_ant]
        fim_ant = df_ant_filtrado["DATA"].max() if not df_ant_filtrado.empty else df_ant["DATA"].max()

    return (inicio_atual, fim_atual), (inicio_ant, fim_ant)


# ======================================================
# 🔥 RESUMO GENERICO DO PERÍODO
# ======================================================
def resumo(df, inicio, fim):
    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]

    total_fat = d["VALOR COM IPI"].sum()
    total_kg = d["KG"].sum()
    total_m2 = d["TOTAL M2"].sum()
    pedidos = len(d)

    ticket = total_fat / pedidos if pedidos else 0
    preco_kg = total_fat / total_kg if total_kg else 0
    preco_m2 = total_fat / total_m2 if total_m2 else 0

    return {
        "pedidos": pedidos,
        "fat": total_fat,
        "kg": total_kg,
        "m2": total_m2,
        "ticket": ticket,
        "preco_kg": preco_kg,
        "preco_m2": preco_m2,
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y")
    }


# ======================================================
# 🔥 SALVAR EM DUAS PASTAS
# ======================================================
def salvar(nome, dados):
    for caminho in [f"dados/{nome}", f"site/dados/{nome}"]:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# 🔥 EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    df = carregar()
    (ini_at, fim_at), (ini_ant, fim_ant) = obter_periodos(df)

    atual = resumo(df, ini_at, fim_at)
    anterior = resumo(df, ini_ant, fim_ant)

    # FATURAMENTO
    salvar("kpi_faturamento.json", {
        "atual": atual["fat"],
        "ano_anterior": anterior["fat"],
        "variacao": ((atual["fat"]/anterior["fat"]) - 1) * 100 if anterior["fat"] else 0,
        "inicio_mes": atual["inicio"],
        "data_atual": atual["fim"],
        "inicio_mes_anterior": anterior["inicio"],
        "data_ano_anterior": anterior["fim"]
    })

    # QUANTIDADE
    salvar("kpi_quantidade_pedidos.json", {
        "atual": atual["pedidos"],
        "ano_anterior": anterior["pedidos"],
        "variacao": ((atual["pedidos"]/anterior["pedidos"]) - 1) * 100 if anterior["pedidos"] else 0
    })

    # KG TOTAL (SEM CASAS)
    salvar("kpi_kg_total.json", {
        "atual": round(atual["kg"], 0),
        "ano_anterior": round(anterior["kg"], 0),
        "variacao": ((atual["kg"]/anterior["kg"]) - 1) * 100 if anterior["kg"] else 0
    })

    # TICKET
    salvar("kpi_ticket_medio.json", {
        "atual": atual["ticket"],
        "ano_anterior": anterior["ticket"],
        "variacao": ((atual["ticket"]/anterior["ticket"]) - 1) * 100 if anterior["ticket"] else 0
    })

    # PREÇO MÉDIO + ANTERIOR
    salvar("kpi_preco_medio.json", {
        "atual": {
            "preco_medio_kg": round(atual["preco_kg"], 2),
            "preco_medio_m2": round(atual["preco_m2"], 2),
            "data": atual["fim"]
        },
        "ano_anterior": {
            "preco_medio_kg": round(anterior["preco_kg"], 2),
            "preco_medio_m2": round(anterior["preco_m2"], 2),
            "data": anterior["fim"]
        }
    })

    print("\n=====================================")
    print(" ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=====================================\n")
