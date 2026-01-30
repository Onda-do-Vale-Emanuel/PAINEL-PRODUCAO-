import pandas as pd
import json

def atualizar_kpis(df_atual):
    kg_total = df_atual['Kg'].sum()
    total_m2 = df_atual['Total m2'].sum()
    valor_total = df_atual['Valor Com IPI'].sum()

    dados = {
        "atual": float(kg_total),
        "total_m2": float(total_m2),
        "valor_total": float(valor_total)
    }

    with open("dados/kpi_preco_medio.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
