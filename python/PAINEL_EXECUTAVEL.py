import os
import sys
import getpass
import subprocess
from datetime import datetime
import json
import pandas as pd
import re

BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
os.chdir(os.path.dirname(BASE_DIR))

# ==============================
# CONFIGURAÇÕES
# ==============================
SENHA_BASE = "Ondaviperx@"
MAX_TENTATIVAS = 3
ARQUIVO_CONTROLE = "controle_execucao.json"

# ==============================
# GERAR SENHA DO MÊS
# ==============================
def senha_mes():
    mes = datetime.now().strftime("%m")
    return SENHA_BASE + mes

# ==============================
# CONTROLE DE EXECUÇÕES
# ==============================
def carregar_controle():
    if not os.path.exists(ARQUIVO_CONTROLE):
        return {"mes": "", "execucoes": 0}
    with open(ARQUIVO_CONTROLE, "r") as f:
        return json.load(f)

def salvar_controle(dados):
    with open(ARQUIVO_CONTROLE, "w") as f:
        json.dump(dados, f)

def verificar_execucao():
    controle = carregar_controle()
    mes_atual = datetime.now().strftime("%Y-%m")

    if controle["mes"] != mes_atual:
        controle = {"mes": mes_atual, "execucoes": 0}

    if controle["execucoes"] >= 30:
        print("🔒 Limite mensal atingido.")
        validar_senha()

    controle["execucoes"] += 1
    salvar_controle(controle)

# ==============================
# VALIDAÇÃO DE SENHA
# ==============================
def validar_senha():
    senha_correta = senha_mes()

    for _ in range(MAX_TENTATIVAS):
        senha = getpass.getpass("Digite a senha: ")
        if senha == senha_correta:
            return
        print("Senha incorreta.")

    print("Contate o Emanuel para liberação.")
    sys.exit()

# ==============================
# FUNÇÃO LIMPAR NÚMERO
# ==============================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    if isinstance(v, (int, float)):
        return float(v)

    if isinstance(v, datetime):
        return float(v.timestamp())

    v = str(v).strip()
    v = re.sub(r"[^0-9,.-]", "", v)

    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

# ==============================
# ATUALIZAÇÃO DO PAINEL
# ==============================
def atualizar():
    print("Atualizando painel...")

    subprocess.run(["python", "python/atualizar_painel_completo.py"])
    subprocess.run(["python", "python/atualizar_preco_medio.py"])

    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Atualização automática painel"])
    subprocess.run(["git", "push"])

    print("Painel atualizado com sucesso.")

# ==============================
# EXECUÇÃO PRINCIPAL
# ==============================
if __name__ == "__main__":
    verificar_execucao()
    atualizar()
