import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# 1) Função robusta para ler números no formato BR
#    e ignorar valores "bugados" tipo 1900-10-29011200
# ======================================================
def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0

    v = str(valor).strip()

    # Se vier algo tipo 2026-02-03151642 ou 1900-10-29011200, zera
    if re.match(r"\d{4}-\d{2}-\d{2}", v):
        return 0.0

    # Mantém apenas números, vírgula, ponto e sinal
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ("", "-", ",", ".", ",-", ".-"):
        return 0.0

    # Caso milhar com ponto e decimal com vírgula: 1.234,56
    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")
        try:
            return float(v)
        except:
            return 0.0

    # Só vírgula => decimal BR
    if "," in v:
        v = v.replace(",", ".")
        try:
            return float(v)
        except:
            return 0.0

    # Só ponto ou só dígitos
    try:
        return float(v)
    except:
        return 0.0


# ======================================================
# 2) Carregar planilha e filtrar somente pedidos válidos
#    - Tipo de pedido = NORMAL
#    - Tipo = Caixas
#    - Número do pedido entre 30000 e 50000
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2",
             "PEDIDO", "TIPO", "TIPO DE PEDIDO"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória não encontrada: {c}")

    # Datas válidas
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    # Filtros de tipo
    df["TIPO"] = df["TIPO"].astype(str).str.upper().str.strip()
    df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()

    df = df[
        (df["TIPO"] == "CAIXAS") &
        (df["TIPO DE PEDIDO"] == "NORMAL")
    ]

    # Limpar colunas numéricas principais
    for col in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[col] = df[col].apply(limpar_numero)

    # Filtrar pedidos "reais" pela faixa numérica
    df["PEDIDO_NUM"] = df["PEDIDO"].apply(limpar_numero)
    df = df[(df["PEDIDO_NUM"] >= 30000) & (df["PEDIDO_NUM"] <= 50000)]

    return df


# ======================================================
# 3) Definir períodos ATUAL e ANO ANTERIOR
#    - Ambos do 1º dia do mês até:
#      -> ano atual: última data real com pedido
#      -> ano anterior: última data real do mês, limitada
#         pelo mesmo dia do ano atual (se não existir,
#         pega a última data anterior)
# ======================================================
def obter_periodos(df: pd.DataFrame):
    ultima = df["DATA"].max()
    ano_atual = ultima.year
    mes_atual = ultima.month
    dia_limite = ultima.day

    # ---- Ano atual ----
    df_atual_mes = df[
        (df["DATA"].dt.year == ano_atual) &
        (df["DATA"].dt.month == mes_atual)
    ]
    fim_atual = df_atual_mes["DATA"].max()
    inicio_atual = datetime(ano_atual, mes_atual, 1)

    # ---- Ano anterior ----
    ano_ant = ano_atual - 1
    df_ant_mes = df[
        (df["DATA"].dt.year == ano_ant) &
        (df["DATA"].dt.month == mes_atual)
    ]

    if not df_ant_mes.empty:
        # limita pelo mesmo dia do ano atual
        df_ant_lim = df_ant_mes[df_ant_mes["DATA"].dt.day <= dia_limite]
        if df_ant_lim.empty:
            fim_ant = df_ant_mes["DATA"].max()
        else:
            fim_ant = df_ant_lim["DATA"].max()
    else:
        # se não tiver nada naquele mês no ano anterior, usa o mesmo dia
        fim_ant = datetime(ano_ant, mes_atual, dia_limite)

    inicio_ant = datetime(ano_ant, mes_atual, 1)

    return (inicio_atual, fim_atual), (inicio_ant, fim_ant)


# ======================================================
# 4) Resumo de um período
# ======================================================
def resumo(df: pd.DataFrame, inicio: datetime, fim: datetime):
    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]

    total_valor = d["VALOR COM IPI"].sum()
    total_kg = d["KG"].sum()
    total_m2 = d["TOTAL M2"].sum()
    pedidos = len(d)

    ticket = total_valor / pedidos if pedidos else 0
    preco_kg = total_valor / total_kg if total_kg else 0
    preco_m2 = total_valor / total_m2 if total_m2 else 0

    return {
        "pedidos": pedidos,
        "fat": total_valor,
        "kg": total_kg,
        "m2": total_m2,
        "ticket": ticket,
        "preco_kg": preco_kg,
        "preco_m2": preco_m2,
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y"),
    }


# ======================================================
# 5) Salvar JSON em /dados e /site/dados
# ======================================================
def salvar(nome, dados):
    for base in ["dados", "site/dados"]:
        caminho = f"{base}/{nome}"
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)


# ======================================================
# 6) Execução principal
# ======================================================
if __name__ == "__main__":
    df = carregar()
    (inicio_atual, fim_atual), (inicio_ant, fim_ant) = obter_periodos(df)

    atual = resumo(df, inicio_atual, fim_atual)
    anterior = resumo(df, inicio_ant, fim_ant)

    print("=====================================")
    print("Período ATUAL    :", atual["inicio"], "→", atual["fim"])
    print("Período ANTERIOR :", anterior["inicio"], "→", anterior["fim"])
    print("Pedidos ATUAL    :", atual["pedidos"])
    print("Pedidos ANTERIOR :", anterior["pedidos"])
    print("=====================================")

    # ---------- Faturamento ----------
    salvar("kpi_faturamento.json", {
        "atual": atual["fat"],
        "ano_anterior": anterior["fat"],
        "variacao": ((atual["fat"] / anterior["fat"]) - 1) * 100 if anterior["fat"] else 0,
        "inicio_mes": atual["inicio"],
        "data_atual": atual["fim"],
        "inicio_mes_anterior": anterior["inicio"],
        "data_ano_anterior": anterior["fim"],
    })

    # ---------- Quantidade de pedidos ----------
    salvar("kpi_quantidade_pedidos.json", {
        "atual": atual["pedidos"],
        "ano_anterior": anterior["pedidos"],
        "variacao": ((atual["pedidos"] / anterior["pedidos"]) - 1) * 100 if anterior["pedidos"] else 0,
    })

    # ---------- KG total ----------
    salvar("kpi_kg_total.json", {
        "atual": atual["kg"],
        "ano_anterior": anterior["kg"],
        "variacao": ((atual["kg"] / anterior["kg"]) - 1) * 100 if anterior["kg"] else 0,
    })

    # ---------- Ticket médio ----------
    salvar("kpi_ticket_medio.json", {
        "atual": atual["ticket"],
        "ano_anterior": anterior["ticket"],
        "variacao": ((atual["ticket"] / anterior["ticket"]) - 1) * 100 if anterior["ticket"] else 0,
    })

    # ---------- Preço médio (ATUAL x ANO ANTERIOR) ----------
    preco_atual = {
        "preco_medio_kg": round(atual["preco_kg"], 2),
        "preco_medio_m2": round(atual["preco_m2"], 2),
        "total_kg": round(atual["kg"], 2),
        "total_m2": round(atual["m2"], 2),
        "data": atual["fim"],
    }

    preco_ant = {
        "preco_medio_kg": round(anterior["preco_kg"], 2),
        "preco_medio_m2": round(anterior["preco_m2"], 2),
        "total_kg": round(anterior["kg"], 2),
        "total_m2": round(anterior["m2"], 2),
        "data": anterior["fim"],
    }

    salvar("kpi_preco_medio.json", {
        "atual": preco_atual,
        "ano_anterior": preco_ant,
    })

    print("✓ JSON gerados corretamente!")
