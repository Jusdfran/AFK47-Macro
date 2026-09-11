import os
import sys
import shutil
import winshell
from win32com.client import Dispatch
import customtkinter as ctk

class InstaladorAFK47(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instalador - AFK47")
        self.geometry("400x200")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.pasta_instalacao = os.path.join(os.environ["LOCALAPPDATA"], "AFK47")
        self.criar_componentes()

    def criar_componentes(self):
        self.label_titulo = ctk.CTkLabel(self, text="Instalação do AFK47", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=20)
        
        self.label_status = ctk.CTkLabel(self, text="Clique em Instalar para continuar.", text_color="gray")
        self.label_status.pack(pady=10)
        
        self.botao_instalar = ctk.CTkButton(self, text="Instalar", command=self.instalar)
        self.botao_instalar.pack(pady=10)

    def instalar(self):
        self.botao_instalar.configure(state="disabled")
        self.label_status.configure(text="Instalando...")
        self.update()
        
        try:
            # Criar pasta
            if not os.path.exists(self.pasta_instalacao):
                os.makedirs(self.pasta_instalacao)
            
            # Copiar executável
            caminho_exe_destino = os.path.join(self.pasta_instalacao, "AFK47.exe")
            
            # Se estamos rodando como exe compilado (Instalador), o AFK47.exe estará na pasta temp do PyInstaller
            if hasattr(sys, '_MEIPASS'):
                caminho_exe_origem = os.path.join(sys._MEIPASS, "AFK47.exe")
                caminho_config_origem = os.path.join(sys._MEIPASS, "configuracoes.json")
            else:
                caminho_exe_origem = "dist/AFK47.exe"
                caminho_config_origem = "configuracoes.json"
            
            if os.path.exists(caminho_exe_origem):
                shutil.copy2(caminho_exe_origem, caminho_exe_destino)
            else:
                self.label_status.configure(text=f"Erro: AFK47.exe não encontrado.", text_color="red")
                self.botao_instalar.configure(state="normal")
                return
                
            if os.path.exists(caminho_config_origem):
                shutil.copy2(caminho_config_origem, os.path.join(self.pasta_instalacao, "configuracoes.json"))

            # Criar atalho no Menu Iniciar
            pasta_menu_iniciar = winshell.programs()
            caminho_atalho = os.path.join(pasta_menu_iniciar, "AFK47.lnk")
            
            shell = Dispatch('WScript.Shell')
            atalho = shell.CreateShortCut(caminho_atalho)
            atalho.Targetpath = caminho_exe_destino
            atalho.WorkingDirectory = self.pasta_instalacao
            atalho.IconLocation = caminho_exe_destino
            atalho.save()
            
            self.label_status.configure(text="Instalação concluída com sucesso!", text_color="green")
            self.botao_instalar.configure(text="Concluir", command=self.destroy, state="normal")
            
        except Exception as e:
            self.label_status.configure(text=f"Erro: {str(e)}", text_color="red")
            self.botao_instalar.configure(state="normal")

if __name__ == "__main__":
    app = InstaladorAFK47()
    app.mainloop()
