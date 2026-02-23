import tkinter as tk
from tkinter import messagebox
import subprocess
import json
import sys
from pathlib import Path

from seguranca_execucao_producao import (
    precisa_senha,
    validar_senha,
    registrar_execucao,
)
import atualizar_painel_producao

# Detectar pasta base (para rodar .py ou .exe)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DADOS_DIR = BASE_DIR / "dados"


def enviar_github():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", "Atualizacao automatica painel producao"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def carregar_resumo():
    try:
        with open(DADOS_DIR / "kpi_peso_dia.json", "r", encoding="utf-8") as f:
            dia = json.load(f)
        with open(DADOS_DIR / "kpi_acumulado_mes.json", "r", encoding="utf-8") as f:
            mes = json.load(f)
    except Exception as e:
        return f"Erro ao carregar dados de conferência: {e}"

    def fmt_kg(v):
        return f"{round(float(v)):,}".replace(",", ".") + " Kg"

    def fmt_pct(v):
        return f"{float(v):.2f}%".replace(".", ",")

    texto = []

    texto.append(f"📅 Dia {dia['data_atual']}")
    texto.append(
        f"  IMPRESSORAS: {fmt_kg(dia['impressoras']['atual'])} "
        f"(Ano anterior: {fmt_kg(dia['impressoras']['ano_anterior'])}, "
        f"Var: {fmt_pct(dia['impressoras']['variacao'])})"
    )
    texto.append(
        f"  ACABAMENTO: {fmt_kg(dia['acabamento']['atual'])} "
        f"(Ano anterior: {fmt_kg(dia['acabamento']['ano_anterior'])}, "
        f"Var: {fmt_pct(dia['acabamento']['variacao'])})"
    )
    texto.append("")

    texto.append(f"📊 Acumulado do mês")
    texto.append(f"  Período: {mes['periodo_atual']}")
    texto.append(
        f"  IMPRESSORAS: {fmt_kg(mes['impressoras']['atual'])} "
        f"(Ano anterior: {fmt_kg(mes['impressoras']['ano_anterior'])}, "
        f"Var: {fmt_pct(mes['impressoras']['variacao'])})"
    )
    texto.append(
        f"  ACABAMENTO: {fmt_kg(mes['acabamento']['atual'])} "
        f"(Ano anterior: {fmt_kg(mes['acabamento']['ano_anterior'])}, "
        f"Var: {fmt_pct(mes['acabamento']['variacao'])})"
    )

    return "\n".join(texto)


def iniciar_atualizacao():
    # Validação de senha, se necessário
    if precisa_senha():
        senha = entry_senha.get().strip()
        resultado = validar_senha(senha)

        if resultado is True:
            pass
        elif resultado == "bloqueado":
            messagebox.showerror(
                "Bloqueado", "Entrar em contato com o desenvolvedor Emanuel"
            )
            root.destroy()
            return
        else:
            messagebox.showerror("Erro", "Senha incorreta.")
            return

    # Ler data de referência (opcional)
    data_ref = entry_data.get().strip()
    if data_ref == "":
        data_ref = None
    else:
        # Validação básica de formato
        try:
            _ = datetime.strptime(data_ref, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror(
                "Data inválida",
                "Por favor, informe a data no formato DD/MM/AAAA ou deixe em branco para modo automático.",
            )
            return

    try:
        # Rodar atualização com ou sem data
        atualizar_painel_producao.main(data_ref)
        registrar_execucao()

        # Enviar para GitHub
        sucesso_git = enviar_github()

        # Carregar resumo para conferência
        resumo = carregar_resumo()

        if sucesso_git:
            messagebox.showinfo(
                "Sucesso",
                "Painel atualizado e enviado ao GitHub com sucesso!\n\n"
                "Resumo dos dados calculados:\n\n" + resumo,
            )
        else:
            messagebox.showwarning(
                "Atenção",
                "Painel atualizado localmente, mas houve erro ao enviar ao GitHub.\n\n"
                "Resumo dos dados calculados:\n\n" + resumo,
            )

        root.destroy()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")


# ================== INTERFACE TK ==================

from datetime import datetime as dt  # para usar no validar data acima

root = tk.Tk()
root.title("Atualização do Painel Produção")
root.geometry("520x320")

frame = tk.Frame(root)
frame.pack(pady=15)

# Campo de senha (aparece só quando precisa)
if precisa_senha():
    tk.Label(frame, text="Senha mensal:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_senha = tk.Entry(frame, show="*", width=25)
    entry_senha.grid(row=0, column=1, padx=5, pady=5)
else:
    entry_senha = tk.Entry(frame)
    entry_senha.insert(0, "")
    entry_senha.grid_forget()

# Campo de data de referência
tk.Label(frame, text="Data de referência (DD/MM/AAAA):", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_data = tk.Entry(frame, width=15)
entry_data.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="(Deixe em branco para usar a última data da planilha)", font=("Arial", 9), fg="#888").grid(
    row=2, column=0, columnspan=2, padx=5, pady=2
)

# Botão principal
tk.Button(
    root,
    text="Iniciar Atualização",
    bg="#f37021",
    fg="white",
    font=("Arial", 12, "bold"),
    width=22,
    command=iniciar_atualizacao,
).pack(pady=25)

root.mainloop()