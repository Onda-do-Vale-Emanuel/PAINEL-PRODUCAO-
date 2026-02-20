import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from seguranca_execucao_producao import *
import atualizar_painel_producao


def iniciar_atualizacao():
    if precisa_senha():
        senha = entry_senha.get()

        resultado = validar_senha(senha)

        if resultado == True:
            messagebox.showinfo("Autenticação", "Senha validada com sucesso.")
        elif resultado == "bloqueado":
            messagebox.showerror("Bloqueado", "Entrar em contato com o desenvolvedor Emanuel")
            root.destroy()
            return
        else:
            messagebox.showerror("Erro", "Senha incorreta.")
            return

    atualizar_painel_producao.main()
    registrar_execucao()

    messagebox.showinfo("Sucesso", "Painel atualizado com sucesso!")
    root.destroy()


root = tk.Tk()
root.title("Atualização do Painel Produção")
root.geometry("500x300")

frame = tk.Frame(root)
frame.pack(pady=20)

if precisa_senha():
    tk.Label(frame, text="Digite a senha mensal:", font=("Arial", 12)).pack()
    entry_senha = tk.Entry(frame, show="*", width=30)
    entry_senha.pack(pady=10)
else:
    entry_senha = tk.Entry(frame)
    entry_senha.insert(0, "")
    entry_senha.pack_forget()

tk.Button(root, text="Iniciar Atualização", bg="#f37021", fg="white",
          font=("Arial", 12), command=iniciar_atualizacao).pack(pady=20)

root.mainloop()