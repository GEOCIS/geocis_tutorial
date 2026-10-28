# Apêndices

[← Aula 9](aula_09_copilot_projeto_integrador.md) · [Plano do curso](README.md)

## Apêndice A: folha de referência rápida

### Terminal e Python

| Tarefa | Comando |
| --- | --- |
| Ver a pasta atual | `pwd` |
| Listar arquivos | `ls` (no Prompt de Comando do Windows: `dir`) |
| Criar pasta | `mkdir nome` |
| Entrar e voltar | `cd nome` e `cd ..` |
| Versão do Python | `python --version` (macOS e Linux: `python3 --version`) |
| Executar um script | `python arquivo.py` |
| Criar ambiente virtual | `python -m venv .venv` |
| Ativar (Windows PowerShell) | `.venv\Scripts\Activate.ps1` |
| Ativar (macOS e Linux) | `source .venv/bin/activate` |
| Instalar biblioteca | `pip install nome` |
| Registrar dependências | `pip freeze > requirements.txt` |
| Reinstalar dependências | `pip install -r requirements.txt` |

### Git e GitHub

| Tarefa | Comando |
| --- | --- |
| Configurar identidade | `git config --global user.name "Nome"` e `git config --global user.email "email"` |
| Criar repositório | `git init` |
| Ver o estado | `git status` |
| Preparar arquivos | `git add arquivo` (ou `git add .`) |
| Registrar versão | `git commit -m "mensagem"` |
| Ver histórico | `git log --oneline` |
| Ver diferenças | `git diff` |
| Descartar alterações | `git restore arquivo` |
| Criar ramo | `git switch -c nome` |
| Conectar ao GitHub | `git remote add origin URL` |
| Enviar | `git push -u origin main` (depois, apenas `git push`) |
| Baixar atualizações | `git pull` |
| Clonar | `git clone URL` |

### Atalhos do VS Code (no macOS, trocar Ctrl por Cmd)

| Ação | Atalho |
| --- | --- |
| Paleta de comandos | `Ctrl+Shift+P` |
| Abrir arquivo | `Ctrl+P` |
| Extensões | `Ctrl+Shift+X` |
| Terminal integrado | `Ctrl+` e a tecla de acento grave |
| Comentar linha | `Ctrl+/` |
| Executar célula | `Shift+Enter` |

## Apêndice B: glossário

- **Biblioteca:** conjunto de código pronto para tarefas específicas.
- **Branch (ramo):** linha de desenvolvimento independente no Git.
- **Commit:** registro de uma versão do projeto, com mensagem.
- **DataFrame:** tabela do pandas.
- **Fork:** cópia pessoal de um repositório no GitHub.
- **Kernel:** processo que executa o código de um notebook.
- **Pull request:** proposta de alteração enviada para revisão no GitHub.
- **Repositório:** pasta de projeto com o histórico controlado pelo Git.
- **Ambiente virtual:** cópia isolada do Python e das bibliotecas de um projeto.
