import time
import threading
import json
import tkinter.filedialog as fd
import customtkinter as ctk
from pynput import mouse, keyboard

class EventoMacro:
    def __init__(self, tipo_acao, atraso, detalhes):
        self.tipo_acao = tipo_acao
        self.atraso = atraso
        self.detalhes = detalhes

    def para_dicionario(self):
        detalhes = self.detalhes.copy()
        if 'button' in detalhes:
            detalhes['button'] = detalhes['button'].name
        if 'key' in detalhes:
            tecla = detalhes['key']
            if hasattr(tecla, 'char') and tecla.char is not None:
                detalhes['key'] = {'type': 'char', 'value': tecla.char}
            elif hasattr(tecla, 'name'):
                detalhes['key'] = {'type': 'special', 'value': tecla.name}
            elif hasattr(tecla, 'vk') and tecla.vk is not None:
                detalhes['key'] = {'type': 'vk', 'value': tecla.vk}
            else:
                detalhes['key'] = {'type': 'unknown', 'value': str(tecla)}
        if 'botoes_pressionados' in detalhes:
            detalhes['botoes_pressionados'] = [botao.name for botao in detalhes['botoes_pressionados']]
        return {'action_type': self.tipo_acao, 'delay': self.atraso, 'details': detalhes}

    @classmethod
    def de_dicionario(classe, dados):
        detalhes = dados['details']
        if 'button' in detalhes:
            detalhes['button'] = getattr(mouse.Button, detalhes['button'])
        if 'key' in detalhes:
            dados_tecla = detalhes['key']
            if dados_tecla['type'] == 'char':
                detalhes['key'] = keyboard.KeyCode.from_char(dados_tecla['value'])
            elif dados_tecla['type'] == 'special':
                detalhes['key'] = getattr(keyboard.Key, dados_tecla['value'])
            elif dados_tecla['type'] == 'vk':
                detalhes['key'] = keyboard.KeyCode.from_vk(dados_tecla['value'])
        if 'botoes_pressionados' in detalhes:
            detalhes['botoes_pressionados'] = [getattr(mouse.Button, nome) for nome in detalhes['botoes_pressionados']]
        return classe(dados['action_type'], dados['delay'], detalhes)


class MotorAFK47:
    def __init__(self, callback_atualizar_status):
        self.eventos = []
        self.botoes_pressionados = set()
        self.botoes_reproduzidos = set()
        self.esta_gravando = False
        self.esta_reproduzindo = False
        self.hora_ultimo_evento = 0
        self.atualizar_status = callback_atualizar_status
        self.controle_mouse = mouse.Controller()
        self.controle_teclado = keyboard.Controller()
        self.atalho_gravar = keyboard.Key.f8
        self.atalho_iniciar = keyboard.Key.f9
        self.atalho_parar = keyboard.Key.f10
        self.ouvinte_mouse = mouse.Listener(on_move=self._ao_mover_mouse, on_click=self._ao_clicar_mouse, on_scroll=self._ao_rolar_mouse)
        self.ouvinte_teclado = keyboard.Listener(on_press=self._ao_pressionar_tecla, on_release=self._ao_liberar_tecla)
        self.ouvinte_mouse.start()
        self.ouvinte_teclado.start()

    def _registrar_evento(self, tipo_acao, detalhes):
        if not self.esta_gravando: return
        hora_atual = time.time()
        atraso = hora_atual - self.hora_ultimo_evento
        self.hora_ultimo_evento = hora_atual
        self.eventos.append(EventoMacro(tipo_acao, atraso, detalhes))

    def _ao_mover_mouse(self, coordenada_x, coordenada_y):
        self._registrar_evento('mouse_move', {
            'x': coordenada_x,
            'y': coordenada_y,
            'botoes_pressionados': list(self.botoes_pressionados),
        })

    def _ao_clicar_mouse(self, coordenada_x, coordenada_y, botao, pressionado):
        self._registrar_evento('mouse_click', {'x': coordenada_x, 'y': coordenada_y, 'button': botao, 'pressed': pressionado})
        if pressionado:
            self.botoes_pressionados.add(botao)
        else:
            self.botoes_pressionados.discard(botao)
    def _ao_rolar_mouse(self, coordenada_x, coordenada_y, deslocamento_x, deslocamento_y): self._registrar_evento('mouse_scroll', {'x': coordenada_x, 'y': coordenada_y, 'dx': deslocamento_x, 'dy': deslocamento_y})

    def _ao_pressionar_tecla(self, tecla):
        if tecla == self.atalho_gravar:
            self.alternar_gravacao()
            return
        elif tecla == self.atalho_iniciar:
            if self.esta_reproduzindo: self.parar_reproducao()
            else: self.iniciar_reproducao(repeticoes=1)
            return
        elif tecla == self.atalho_parar:
            self.parar_reproducao()
            return
        self._registrar_evento('key_press', {'key': tecla})

    def _ao_liberar_tecla(self, tecla):
        if tecla in [self.atalho_gravar, self.atalho_iniciar, self.atalho_parar]: return
        self._registrar_evento('key_release', {'key': tecla})

    def configurar_atalhos(self, gravar, iniciar, parar):
        nomes = [gravar.strip().lower(), iniciar.strip().lower(), parar.strip().lower()]
        if not all(nomes) or len(set(nomes)) != 3:
            raise ValueError("Os atalhos devem ser preenchidos e diferentes.")

        teclas = [self._converter_tecla(nome) for nome in nomes]
        self.atalho_gravar, self.atalho_iniciar, self.atalho_parar = teclas

    def _converter_tecla(self, nome):
        aliases = {'espaco': 'space', 'espaço': 'space', 'enter': 'enter', 'tab': 'tab'}
        nome = aliases.get(nome, nome)
        tecla = getattr(keyboard.Key, nome, None)
        if tecla is not None:
            return tecla
        if len(nome) == 1:
            return keyboard.KeyCode.from_char(nome)
        raise ValueError(f"Tecla inválida: {nome}")

    def alternar_gravacao(self):
        if self.esta_reproduzindo: return
        self.esta_gravando = not self.esta_gravando
        if self.esta_gravando:
            self.eventos.clear()
            self.botoes_pressionados.clear()
            self.hora_ultimo_evento = time.time()
            self.atualizar_status("🔴 Gravando...")
        else:
            self.atualizar_status("⏹ Gravação salva")

    def iniciar_reproducao(self, repeticoes=1, velocidade=1):
        if self.esta_gravando or self.esta_reproduzindo or not self.eventos: return
        self.esta_reproduzindo = True
        threading.Thread(target=self._reproduzir_eventos, args=(repeticoes, velocidade), daemon=True).start()

    def parar_reproducao(self):
        self.esta_reproduzindo = False

    def _pausa_inteligente(self, atraso):
        inicio = time.time()
        while time.time() - inicio < atraso:
            if not self.esta_reproduzindo: return False
            time.sleep(0.005)
        return True

    def _reproduzir_eventos(self, repeticoes, velocidade):
        contagem_repeticoes = 0
        while (repeticoes == 0 or contagem_repeticoes < repeticoes) and self.esta_reproduzindo:
            contagem_repeticoes += 1
            self.atualizar_status(f"▶ Reproduzindo... (Loop {contagem_repeticoes}, {velocidade}x)")
            for evento in self.eventos:
                if not self.esta_reproduzindo: break
                if not self._pausa_inteligente(evento.atraso / velocidade): break
                try:
                    detalhes_evento = evento.detalhes
                    if evento.tipo_acao == 'mouse_move':
                        if 'botoes_pressionados' in detalhes_evento:
                            self._sincronizar_botoes(detalhes_evento['botoes_pressionados'])
                        self.controle_mouse.position = (detalhes_evento['x'], detalhes_evento['y'])
                    elif evento.tipo_acao == 'mouse_click':
                        self.controle_mouse.position = (detalhes_evento['x'], detalhes_evento['y'])
                        botao = detalhes_evento['button']
                        if detalhes_evento['pressed']:
                            self.controle_mouse.press(botao)
                            self.botoes_reproduzidos.add(botao)
                        else:
                            self.controle_mouse.release(botao)
                            self.botoes_reproduzidos.discard(botao)
                    elif evento.tipo_acao == 'mouse_scroll':
                        self.controle_mouse.position = (detalhes_evento['x'], detalhes_evento['y'])
                        self.controle_mouse.scroll(detalhes_evento['dx'], detalhes_evento['dy'])
                    elif evento.tipo_acao == 'key_press': self.controle_teclado.press(detalhes_evento['key'])
                    elif evento.tipo_acao == 'key_release': self.controle_teclado.release(detalhes_evento['key'])
                except Exception as erro:
                    print(f"Erro: {erro}")
        self.esta_reproduzindo = False
        self._sincronizar_botoes([])
        self.atualizar_status("✅ Concluído")

    def _sincronizar_botoes(self, botoes_desejados):
        botoes_desejados = set(botoes_desejados)
        for botao in self.botoes_reproduzidos - botoes_desejados:
            self.controle_mouse.release(botao)
        for botao in botoes_desejados - self.botoes_reproduzidos:
            self.controle_mouse.press(botao)
        self.botoes_reproduzidos = botoes_desejados

    def salvar_em_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'w') as arquivo:
            json.dump([evento.para_dicionario() for evento in self.eventos], arquivo, indent=4)
            self.atualizar_status("💾 Macro salvo!")

    def carregar_de_arquivo(self, caminho_arquivo):
        with open(caminho_arquivo, 'r') as arquivo:
            dados = json.load(arquivo)
            self.eventos = [EventoMacro.de_dicionario(dado) for dado in dados]
            self.atualizar_status("📂 Carregado")

class InterfaceAFK47(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AFK47")
        self.geometry("610x180")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.motor = MotorAFK47(self.atualizar_status_seguro)
        self.atalhos = {'gravar': 'F8', 'iniciar': 'F9', 'parar': 'F10'}
        self.arquivo_configuracoes = "configuracoes.json"
        self.janela_configuracoes = None
        self.carregar_configuracoes()
        self.criar_componentes()

    def criar_componentes(self):
        quadro_botoes = ctk.CTkFrame(self, fg_color="transparent")
        quadro_botoes.pack(pady=10)
        ctk.CTkButton(quadro_botoes, text="📂 Abrir", width=60, command=self.abrir_arquivo).grid(row=0, column=0, padx=2)
        ctk.CTkButton(quadro_botoes, text="💾 Salvar", width=60, command=self.salvar_arquivo).grid(row=0, column=1, padx=2)
        self.botao_gravar = ctk.CTkButton(quadro_botoes, text=f"🔴 Gravar ({self.atalhos['gravar']})", width=95, fg_color="#c0392b", hover_color="#e74c3c", command=self.motor.alternar_gravacao)
        self.botao_gravar.grid(row=0, column=2, padx=2)
        self.botao_iniciar = ctk.CTkButton(quadro_botoes, text=f"▶ Iniciar ({self.atalhos['iniciar']})", width=95, fg_color="#27ae60", hover_color="#2ecc71", command=self.acao_reproduzir)
        self.botao_iniciar.grid(row=0, column=3, padx=2)
        self.botao_configuracoes = ctk.CTkButton(quadro_botoes, text="⚙", width=35, command=self.abrir_configuracoes)
        self.botao_configuracoes.grid(row=0, column=4, padx=2)
        quadro_controles = ctk.CTkFrame(self, fg_color="transparent")
        quadro_controles.pack(fill="x", padx=15, pady=5)

        grupo_repeticoes = ctk.CTkFrame(quadro_controles, corner_radius=8, fg_color=("#e9eef2", "#202a33"))
        grupo_repeticoes.pack(side="left", padx=2)

        ctk.CTkLabel(grupo_repeticoes, text="🔁", width=28, text_color=("#2574a9", "#66c7f2")).pack(side="left", padx=(8, 2), pady=5)
        texto_repeticoes = ctk.CTkFrame(grupo_repeticoes, fg_color="transparent")
        texto_repeticoes.pack(side="left", pady=4)
        ctk.CTkLabel(texto_repeticoes, text="Repetições", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(texto_repeticoes, text="0 = infinito", font=ctk.CTkFont(size=10), text_color="gray", anchor="w").pack(anchor="w")

        self.campo_repeticoes = ctk.CTkEntry(grupo_repeticoes, width=54, height=30, justify="center", font=ctk.CTkFont(size=13, weight="bold"))
        self.campo_repeticoes.insert(0, "1")
        self.campo_repeticoes.pack(side="left", padx=(8, 8), pady=6)

        grupo_velocidade = ctk.CTkFrame(quadro_controles, corner_radius=8, fg_color=("#e9eef2", "#202a33"))
        grupo_velocidade.pack(side="left", padx=6)
        ctk.CTkLabel(grupo_velocidade, text="⚡", width=28, text_color=("#c77d18", "#f5c451")).pack(side="left", padx=(8, 2), pady=5)
        texto_velocidade = ctk.CTkFrame(grupo_velocidade, fg_color="transparent")
        texto_velocidade.pack(side="left", pady=4)
        ctk.CTkLabel(texto_velocidade, text="Velocidade", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(texto_velocidade, text="1 a 100x", font=ctk.CTkFont(size=10), text_color="gray", anchor="w").pack(anchor="w")

        self.campo_velocidade = ctk.CTkEntry(
            grupo_velocidade,
            width=58,
            height=30,
            justify="center",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.campo_velocidade.insert(0, "1")
        self.campo_velocidade.pack(side="left", padx=(8, 8), pady=6)

        self.botao_parar = ctk.CTkButton(quadro_controles, text=f"⏹ Parar ({self.atalhos['parar']})", width=95, fg_color="#7f8c8d", command=self.motor.parar_reproducao)
        self.botao_parar.pack(side="right")

        self.rotulo_status = ctk.CTkLabel(self, text="✅ Pronto. Pressione F8 para gravar.", text_color="gray")
        self.rotulo_status.pack(side="bottom", pady=5)

    def acao_reproduzir(self):
        try:
            repeticoes = int(self.campo_repeticoes.get())
            velocidade = int(self.campo_velocidade.get().rstrip("xX"))
            if velocidade < 1 or velocidade > 100:
                raise ValueError
            self.motor.iniciar_reproducao(repeticoes=repeticoes, velocidade=velocidade)
        except ValueError:
            self.atualizar_status_seguro("Erro: repetições e velocidade devem ser válidas!")

    def abrir_configuracoes(self):
        if self.janela_configuracoes is not None and self.janela_configuracoes.winfo_exists():
            self.janela_configuracoes.focus()
            return

        self.janela_configuracoes = ctk.CTkToplevel(self)
        self.janela_configuracoes.title("Configurações")
        self.janela_configuracoes.geometry("300x285")
        self.janela_configuracoes.resizable(False, False)
        self.janela_configuracoes.transient(self)

        campos = {}
        for indice, (nome, rotulo) in enumerate((
            ('gravar', 'Gravar'),
            ('iniciar', 'Iniciar'),
            ('parar', 'Parar'),
        )):
            ctk.CTkLabel(self.janela_configuracoes, text=f"Tecla para {rotulo}:").pack(pady=(10 if indice == 0 else 4, 2))
            campo = ctk.CTkEntry(self.janela_configuracoes, width=180)
            campo.insert(0, self.atalhos[nome])
            campo.pack()
            campos[nome] = campo

        mensagem = ctk.CTkLabel(self.janela_configuracoes, text="Use F1-F12, uma letra ou nome de tecla.", text_color="gray")
        mensagem.pack(pady=(8, 2))

        def aplicar():
            try:
                novos_atalhos = {nome: campo.get().strip().upper() for nome, campo in campos.items()}
                self.motor.configurar_atalhos(
                    novos_atalhos['gravar'], novos_atalhos['iniciar'], novos_atalhos['parar'])
                self.salvar_configuracoes(novos_atalhos)
                self.atalhos = novos_atalhos
                self.atualizar_textos_botoes()
                self.atualizar_status_seguro("⚙ Configurações salvas")
                self.janela_configuracoes.destroy()
                self.janela_configuracoes = None
            except (OSError, ValueError) as erro:
                mensagem.configure(text=str(erro), text_color="#e74c3c")

        ctk.CTkButton(self.janela_configuracoes, text="Salvar configurações", command=aplicar).pack(pady=8)

    def salvar_configuracoes(self, atalhos):
        with open(self.arquivo_configuracoes, 'w', encoding='utf-8') as arquivo:
            json.dump(atalhos, arquivo, indent=4, ensure_ascii=False)

    def carregar_configuracoes(self):
        try:
            with open(self.arquivo_configuracoes, 'r', encoding='utf-8') as arquivo:
                atalhos = json.load(arquivo)
            if not all(chave in atalhos for chave in self.atalhos):
                return
            novos_atalhos = {chave: str(atalhos[chave]).upper() for chave in self.atalhos}
            self.motor.configurar_atalhos(
                novos_atalhos['gravar'], novos_atalhos['iniciar'], novos_atalhos['parar'])
            self.atalhos = novos_atalhos
        except (FileNotFoundError, OSError, json.JSONDecodeError, ValueError, TypeError):
            pass

    def atualizar_textos_botoes(self):
        self.botao_gravar.configure(text=f"🔴 Gravar ({self.atalhos['gravar']})")
        self.botao_iniciar.configure(text=f"▶ Iniciar ({self.atalhos['iniciar']})")
        self.botao_parar.configure(text=f"⏹ Parar ({self.atalhos['parar']})")

    def salvar_arquivo(self):
        caminho_arquivo = fd.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if caminho_arquivo: self.motor.salvar_em_arquivo(caminho_arquivo)

    def abrir_arquivo(self):
        caminho_arquivo = fd.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if caminho_arquivo: self.motor.carregar_de_arquivo(caminho_arquivo)

    def atualizar_status_seguro(self, texto):
        self.after(0, lambda: self.rotulo_status.configure(text=texto))

if __name__ == "__main__":
    aplicativo = InterfaceAFK47()
    aplicativo.mainloop()