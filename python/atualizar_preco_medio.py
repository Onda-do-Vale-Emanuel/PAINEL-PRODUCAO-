import pandas as pd
import json
from datetime import datetime
from atualizar_painel_completo import carregar

ARQ1 = "dados/kpi_preco_medio.json"
ARQ2 = "site/dados/kpi_preco_medio.json"

def resumo_preco(df, ano, mes, dia):
    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes, dia)

    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]

    total_valor = float(d["VALOR COM IPI"].sum())
    total_kg = float(d["KG"].sum())
    total_m2 = float(d["TOTAL M2"].sum())

    return {
        "preco_medio_kg": round(total_valor/total_kg, 2) if total_kg else 0,
        "preco_medio_m2": round(total_valor/total_m2, 2) if total_m2 else 0,
        "total_kg": round(total_kg),
        "total_m2": round(total_m2),
        "data": f"{dia:02d}/{mes:02d}/{ano}"
    }

if __name__ == "__main__":
    df = carregar()

    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month
    dia = ultima.day

    dados = {
        "atual": resumo_preco(df, ano, mes, dia),
        "ano_anterior": resumo_preco(df, ano-1, mes, dia)
    }

    for arq in [ARQ1, ARQ2]:
        with open(arq, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    print("Preço médio atualizado corretamente.")
