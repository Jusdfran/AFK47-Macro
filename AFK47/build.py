import os
import subprocess

def main():
    print("Construindo AFK47...")
    # Constrói o executável principal
    subprocess.run(["pyinstaller", "--noconfirm", "--onefile", "--windowed", "--name", "AFK47", "Main.py"], check=True)
    
    print("Construindo Instalador...")
    # Constrói o instalador anexando o AFK47.exe como recurso
    subprocess.run([
        "pyinstaller", 
        "--noconfirm", 
        "--onefile", 
        "--windowed", 
        "--name", "Instalador_AFK47", 
        "--add-data", "dist/AFK47.exe;.", 
        "--add-data", "configuracoes.json;.",
        "Instalador.py"
    ], check=True)
    
    print("Construção concluída! O instalador está em dist/Instalador_AFK47.exe")

if __name__ == "__main__":
    main()
