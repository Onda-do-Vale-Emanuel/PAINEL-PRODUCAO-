import os
import hashlib
import getpass
import sys
from datetime import datetime

# ==========================================
# CONFIGURAÇÕES
# ==========================================

LIMITE_EXECUCOES = 30
LIMITE_ERROS = 3

ARQUIVO_CONTADOR = "python/.contador_exec"
ARQUIVO_MES = "python/.mes_exec"
ARQUIVO_ERROS = "python/.erros_exec"

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def gerar_hash(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

def senha_valida_digitada():
    mes_atual = datetime.now().strftime("%m")
    senha_correta = f"Ondaviperx@{mes_atual}"
    hash_correto = gerar_hash(senha_correta)

    senha_digitada = getpass.getpass("Digite a senha para continuar: ")
    hash_digitado = gerar_hash(senha_digitada)

    return hash_digitado == hash_correto

def ler_arquivo(path, default=0):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return int(f.read().strip())

def salvar_arquivo(path, valor):
    with open(path, "w") as f:
        f.write(str(valor))

def bloquear():
    print("\nContate o Emanuel para liberação.")
    sys.exit(1)

# ==========================================
# VERIFICAÇÃO PRINCIPAL
# ==========================================

mes_atual = datetime.now().strftime("%m")
mes_salvo = None

if os.path.exists(ARQUIVO_MES):
    with open(ARQUIVO_MES, "r") as f:
        mes_salvo = f.read().strip()

# Se mudou o mês → exige senha
if mes_salvo != mes_atual:
    print("\nNovo mês detectado. Necessário autenticação.")
    erros = 0

    while erros < LIMITE_ERROS:
        if senha_valida_digitada():
            salvar_arquivo(ARQUIVO_MES, mes_atual)
            salvar_arquivo(ARQUIVO_CONTADOR, 0)
            salvar_arquivo(ARQUIVO_ERROS, 0)
            print("Autenticação mensal realizada com sucesso.\n")
            break
        else:
            erros += 1
            salvar_arquivo(ARQUIVO_ERROS, erros)
            print(f"Senha incorreta. Tentativa {erros}/{LIMITE_ERROS}")

    if erros >= LIMITE_ERROS:
        bloquear()

# Verificação de execuções
contador = ler_arquivo(ARQUIVO_CONTADOR, 0)
contador += 1

if contador > LIMITE_EXECUCOES:
    print("\nLimite de execuções atingido.")
    erros = 0

    while erros < LIMITE_ERROS:
        if senha_valida_digitada():
            contador = 1
            salvar_arquivo(ARQUIVO_ERROS, 0)
            print("Autorização concedida. Contador reiniciado.\n")
            break
        else:
            erros += 1
            salvar_arquivo(ARQUIVO_ERROS, erros)
            print(f"Senha incorreta. Tentativa {erros}/{LIMITE_ERROS}")

    if erros >= LIMITE_ERROS:
        bloquear()

salvar_arquivo(ARQUIVO_CONTADOR, contador)
