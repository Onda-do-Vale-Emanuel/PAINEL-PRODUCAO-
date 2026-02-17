import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_2026 = "excel/PEDIDOS_2026.xlsx"
CAMINHO_2025 = "excel/PEDIDOS_2025.xlsx"

# ===============================
# LIMPAR NÚMERO
# ===============================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    if isinstance(v, (int, float)):
        return float(v)

    v = str(v).strip()
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

# ===============================
# CARREGAR PLANILHA
# ===============================
def carregar(caminho):
    df = pd.read_excel(caminho)
    df.columns = df.columns.str.upper().str.strip()

    for col in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        if col in df.columns:
            df[col] = df[col].apply(limpar_numero)

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]
    df = df[df["TIPO DE PEDIDO"] == "Normal"]

    return df

# ===============================
# RESUMO
# ===============================
def resumo(df, inicio, fim):
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
        "preco_m2": preco_m2
    }

# ===============================
# PERÍODO MANUAL OU AUTOMÁTICO
# ===============================
def definir_periodo(df_2026):

    escolha = input("Deseja filtrar por período específico? (S/N): ").strip().upper()

    if escolha == "S":
        inicio_str = input("Data inicial (dd/mm/aaaa): ")
        fim_str = input("Data final (dd/mm/aaaa): ")

        inicio_atual = datetime.strptime(inicio_str, "%d/%m/%Y")
        fim_atual = datetime.strptime(fim_str, "%d/%m/%Y")

    else:
        ultima_data = df_2026["DATA"].max()
        inicio_atual = ultima_data.replace(day=1)
        fim_atual = ultima_data

    inicio_ant = inicio_atual.replace(year=inicio_atual.year - 1)
    fim_ant = fim_atual.replace(year=fim_atual.year - 1)

    return inicio_atual, fim_atual, inicio_ant, fim_ant

# ===============================
# SALVAR JSON
# ===============================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":

    df_2026 = carregar(CAMINHO_2026)
    df_2025 = carregar(CAMINHO_2025)

    inicio_atual, fim_atual, inicio_ant, fim_ant = definir_periodo(df_2026)

    atual = resumo(df_2026, inicio_atual, fim_atual)
    anterior = resumo(df_2025, inicio_ant, fim_ant)

    salvar("kpi_faturamento.json", {
        "atual": atual["fat"],
        "ano_anterior": anterior["fat"],
        "variacao": ((atual["fat"]/anterior["fat"])-1)*100 if anterior["fat"] else 0,
        "inicio_mes": inicio_atual.strftime("%d/%m/%Y"),
        "data_atual": fim_atual.strftime("%d/%m/%Y"),
        "inicio_mes_anterior": inicio_ant.strftime("%d/%m/%Y"),
        "data_ano_anterior": fim_ant.strftime("%d/%m/%Y")
    })

    salvar("kpi_quantidade_pedidos.json", {
        "atual": atual["pedidos"],
        "ano_anterior": anterior["pedidos"],
        "variacao": ((atual["pedidos"]/anterior["pedidos"])-1)*100 if anterior["pedidos"] else 0
    })

    salvar("kpi_kg_total.json", {
        "atual": atual["kg"],
        "ano_anterior": anterior["kg"],
        "variacao": ((atual["kg"]/anterior["kg"])-1)*100 if anterior["kg"] else 0
    })

    salvar("kpi_ticket_medio.json", {
        "atual": atual["ticket"],
        "ano_anterior": anterior["ticket"],
        "variacao": ((atual["ticket"]/anterior["ticket"])-1)*100 if anterior["ticket"] else 0
    })

    print("ATUALIZAÇÃO CONCLUÍDA")
