import tkinter as tk
from tkinter import messagebox
import subprocess
from seguranca_execucao_producao import *
import atualizar_painel_producao


def enviar_github():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Atualizacao automatica painel producao"], check=True)
        subprocess.run(["git", "push"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def iniciar_atualizacao():
    if precisa_senha():
        senha = entry_senha.get()
        resultado = validar_senha(senha)

        if resultado == True:
            pass
        elif resultado == "bloqueado":
            messagebox.showerror("Bloqueado", "Entrar em contato com o desenvolvedor Emanuel")
            root.destroy()
            return
        else:
            messagebox.showerror("Erro", "Senha incorreta.")
            return

    try:
        atualizar_painel_producao.main()
        registrar_execucao()

        sucesso_git = enviar_github()

        if sucesso_git:
            messagebox.showinfo("Sucesso", "Painel atualizado e enviado ao GitHub com sucesso!")
        else:
            messagebox.showwarning("Atenção", "Atualizou os dados, mas houve erro ao enviar ao GitHub.")

        root.destroy()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")


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
    entry_senha.pack_forget()

tk.Button(root, text="Iniciar Atualização",
          bg="#f37021",
          fg="white",
          font=("Arial", 12),
          command=iniciar_atualizacao).pack(pady=20)

root.mainloop()