# AFK47

AFK47 e um gravador e reprodutor de macros para Windows. Ele captura movimentos e cliques do mouse, rolagem e eventos do teclado, permitindo reproduzir a sequencia com controle de repeticoes e velocidade.

## Funcionalidades

- Gravacao de teclado e mouse.
- Reproducao de macros em segundo plano.
- Repeticao configuravel, incluindo repeticao infinita com `0`.
- Velocidade de reproducao de `1x` a `100x`.
- Salvamento e carregamento de macros em arquivos `.json`.
- Atalhos globais configuraveis.
- Interface grafica compacta sempre visivel.
- Geracao de executaveis e instalador para Windows.

## Atalhos padrao

Os atalhos sao carregados de `configuracoes.json`:

| Acao | Atalho atual |
| --- | --- |
| Gravar ou parar gravacao | `F8` |
| Iniciar ou pausar reproducao | `F9` |
| Parar reproducao | `F5` |

Os atalhos podem ser alterados pelo botao de configuracoes. Sao aceitos nomes de teclas, teclas de funcao (`F1` a `F12`) e letras individuais. Os tres atalhos devem ser preenchidos e diferentes.

## Requisitos

- Windows.
- Python 3.10 ou superior recomendado.
- `customtkinter`.
- `pynput`.
- `PyInstaller` para gerar os executaveis.
- `winshell` e `pywin32` para gerar o atalho do instalador.

## Execucao pelo codigo-fonte

Abra um terminal na pasta do projeto e crie ou ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
python -m pip install customtkinter pynput pyinstaller winshell pywin32
```

Execute a aplicacao:

```powershell
python Main.py
```

### Uso basico

1. Pressione `F8` ou clique em **Gravar**.
2. Execute as acoes que deseja registrar.
3. Pressione `F8` novamente para encerrar a gravacao.
4. Informe a quantidade de repeticoes e a velocidade.
5. Pressione `F9` ou clique em **Iniciar**.
6. Use `F5` ou o botao **Parar** para interromper a reproducao.

Use **Salvar** para exportar a macro para um arquivo JSON e **Abrir** para carregar uma macro existente.

## Gerar os executaveis

Com as dependencias instaladas e o ambiente virtual ativo, execute:

```powershell
python build.py
```

O script gera:

- `dist/AFK47.exe`: aplicacao principal.
- `dist/Instalador_AFK47.exe`: instalador da aplicacao.

O instalador copia o programa para `%LOCALAPPDATA%\AFK47` e cria um atalho no Menu Iniciar. O arquivo `configuracoes.json` e incluido no pacote para preservar os atalhos configurados no projeto.

## Estrutura do projeto

```text
AFK47/
├── Main.py              # Interface grafica e motor de gravacao/reproducao
├── Instalador.py        # Instalador e criacao do atalho no Menu Iniciar
├── build.py             # Geracao dos executaveis com PyInstaller
├── configuracoes.json   # Atalhos globais da aplicacao
├── README.md            # Documentacao do projeto
└── dist/                # Executaveis gerados pelo build
```

## Formato das macros

As macros sao salvas como uma lista JSON. Cada evento possui:

- `action_type`: tipo da acao, como `mouse_move`, `mouse_click`, `mouse_scroll`, `key_press` ou `key_release`.
- `delay`: intervalo, em segundos, desde o evento anterior.
- `details`: coordenadas, tecla, botao, estado do clique ou dados da rolagem.

## Observacoes de seguranca

O AFK47 usa listeners globais para capturar teclado e mouse e pode controlar o cursor e enviar teclas durante a reproducao. Evite gravar senhas, dados confidenciais ou qualquer sequencia que possa causar alteracoes indesejadas. Antes de iniciar uma macro, confirme a quantidade de repeticoes e mantenha o atalho de parada acessivel.

Além disso utilizei ferramentas de inteligência artificial para incrementar passos de meu conhecimento e alguns que não tenho estudos totalmente

## Licenca

O projeto é de código livre e pretendo melhora-lo no futuro
