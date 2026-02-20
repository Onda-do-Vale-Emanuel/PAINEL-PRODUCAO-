import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
ARQ_CONTROLE = BASE_DIR / "controle_execucao.json"

SENHA_BASE = "Ondaviperx123@"
LIMITE_EXECUCOES = 30
LIMITE_ERROS = 3


def mes_atual():
    return datetime.now().strftime("%m")


def senha_mes():
    return SENHA_BASE + mes_atual()


def carregar_controle():
    if not ARQ_CONTROLE.exists():
        return {
            "mes": mes_atual(),
            "execucoes": 0,
            "erros": 0,
            "validado": False
        }

    with open(ARQ_CONTROLE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_controle(dados):
    with open(ARQ_CONTROLE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)


def precisa_senha():
    dados = carregar_controle()

    if dados["mes"] != mes_atual():
        dados["mes"] = mes_atual()
        dados["execucoes"] = 0
        dados["erros"] = 0
        dados["validado"] = False
        salvar_controle(dados)
        return True

    if dados["execucoes"] >= LIMITE_EXECUCOES:
        return True

    if not dados["validado"]:
        return True

    return False


def validar_senha(senha_digitada):
    dados = carregar_controle()

    if senha_digitada == senha_mes():
        dados["erros"] = 0
        dados["validado"] = True
        salvar_controle(dados)
        return True

    else:
        dados["erros"] += 1
        salvar_controle(dados)

        if dados["erros"] >= LIMITE_ERROS:
            return "bloqueado"

        return False


def registrar_execucao():
    dados = carregar_controle()
    dados["execucoes"] += 1
    salvar_controle(dados)