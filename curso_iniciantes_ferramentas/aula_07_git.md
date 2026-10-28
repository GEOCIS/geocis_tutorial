# Aula 7: Git, controle de versão

[← Aula 6](aula_06_primeira_analise_dados.md) · [Plano do curso](README.md) · [Aula 8 →](aula_08_github.md)

## Resumo do plano

**Objetivos:** registrar o histórico do projeto e desfazer erros com segurança.

**Conteúdo:**

- Por que versionar: histórico, reversão, trabalho em equipe e reprodutibilidade (fim dos arquivos `final_v2_agora_vai.ipynb`).
- Instalação do Git (git-scm.com) e configuração inicial:
  - `git config --global user.name "Seu Nome"`
  - `git config --global user.email "seu@email.com"`
- Conceitos: repositório, *working directory*, *staging area* e *commit*.
- Comandos essenciais: `git init`, `git status`, `git add`, `git commit -m "mensagem"`, `git log --oneline`, `git diff`.
- Arquivo `.gitignore`: o que não versionar (`.venv/`, dados grandes, arquivos de resultados e credenciais).
- Noções de ramos (*branches*): `git branch`, `git switch -c nova-ideia`, `git merge`.
- Git dentro do VS Code: painel *Source Control*, mensagens de commit e comparação de alterações.
- Cuidado com notebooks: o `.ipynb` é um arquivo JSON e gera diferenças grandes. Limpar as saídas antes do commit ajuda.

**Prática:** transformar a pasta do projeto em repositório, criar o `.gitignore` e fazer três commits com mensagens claras (por exemplo, "adiciona leitura dos dados").

## Material de aula

**Materiais:** Git instalado (git-scm.com), projeto `analise_solos` da aula 6, VS Code.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 30 min: por que versionar e como o Git funciona.
- 30 a 45 min: instalação e configuração inicial.
- 45 a 85 min: ciclo básico (`init`, `status`, `add`, `commit`, `log`, `diff`).
- 85 a 100 min: `.gitignore` e desfazer alterações.
- 100 a 115 min: ramos (*branches*) e o Git no VS Code.
- 115 a 120 min: resumo e entregável.

### Conteúdo

**O problema:** `analise_final.ipynb`, `analise_final_v2.ipynb`, `analise_final_agora_vai.ipynb`. Sem controle de versão, é difícil saber o que mudou, voltar a um estado anterior ou trabalhar em equipe sem sobrescrever o trabalho dos outros.

**O Git** é um sistema de controle de versão distribuído. Ele guarda o histórico do projeto como uma sequência de **commits**, que são fotografias do estado dos arquivos, cada uma com autor, data e mensagem. Conceitos a explicar com um desenho:

- **Diretório de trabalho** (*working directory*): os arquivos como estão agora.
- **Área de preparação** (*staging area*): o que será incluído no próximo commit.
- **Repositório**: a pasta oculta `.git` com todo o histórico.
- **Ramo** (*branch*): uma linha de desenvolvimento. O ramo principal costuma se chamar `main`.

Fluxo: editar arquivos, `git add` (escolher o que entra), `git commit` (registrar com uma mensagem).

### Instalação e configuração

- **Windows:** baixar o instalador em git-scm.com e aceitar as opções padrão (inclui o Git Credential Manager, útil na aula 8).
- **macOS:** executar `git --version` no Terminal, e o sistema oferece instalar as ferramentas de linha de comando; ou usar `brew install git`.
- **Linux (Debian e Ubuntu):** `sudo apt install git`.

Configuração feita uma única vez por computador:

```bash
git --version
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git config --global init.defaultBranch main
```

Explicar que o e-mail aparece nos commits e, se o projeto for publicado no GitHub, deve ser o mesmo da conta (ou o e-mail privado oferecido pelo GitHub).

### Prática guiada: o ciclo básico

No terminal integrado, na pasta do projeto `analise_solos`:

```bash
git init                      # cria o repositório
git status                    # mostra o estado: arquivos novos e alterados
```

Criar o arquivo `.gitignore` **antes** do primeiro commit, para não versionar arquivos desnecessários:

```text
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.env
```

Se houver dados grandes ou arquivos gerados (por exemplo, a pasta `resultados/`), incluir também seus nomes no `.gitignore`.

```bash
git add .gitignore analise_solos.ipynb requirements.txt
git status                    # os arquivos aparecem como "prontos para commit"
git commit -m "Primeira versão da análise de solos"
```

Fazer uma alteração (por exemplo, adicionar um gráfico ao notebook), e depois:

```bash
git status
git diff                      # mostra o que mudou, linha a linha
git add analise_solos.ipynb
git commit -m "Adiciona gráfico de correlação"
git log --oneline             # histórico resumido
```

**Boas mensagens de commit:** curtas, no presente ou no passado de forma consistente, e descrevendo *o que* mudou e *por que* (por exemplo, "Remove amostras sem pH"), e não "alterações" ou "teste".

### Desfazer alterações com segurança

```bash
git restore arquivo.py          # descarta alterações ainda não preparadas
git restore --staged arquivo.py # tira da área de preparação
git log --oneline               # localizar um commit anterior
git show <código_do_commit>     # ver o que aquele commit alterou
```

Avisar que `git restore` descarta alterações de forma permanente, e que comandos mais avançados (como `reset` e `revert`) ficam para outro momento.

### Ramos (visão introdutória)

```bash
git branch                    # lista os ramos
git switch -c nova-analise    # cria e muda para um ramo
# ... edições e commits ...
git switch main               # volta ao ramo principal
git merge nova-analise        # incorpora as mudanças
```

O ramo permite testar uma ideia sem afetar a versão estável.

### Git no VS Code

- O ícone de **Controle do Código-Fonte** na barra lateral lista as alterações.
- O sinal **+** ao lado de um arquivo equivale a `git add`; a caixa de mensagem e o botão **Commit** equivalem a `git commit`.
- Clicar em um arquivo alterado abre a comparação com a versão anterior.
- A barra de status mostra o ramo atual.

### Cuidado com notebooks

O arquivo `.ipynb` guarda também os resultados e as imagens, e pequenas alterações geram diferenças grandes. Antes do commit, use *Clear All Outputs* quando as saídas não forem essenciais, e adote commits pequenos.

### Exercícios

1. Transformar a pasta do projeto em um repositório e fazer o primeiro commit.
2. Fazer **três** alterações em momentos diferentes (por exemplo, nova célula, novo gráfico e correção de texto), cada uma com um commit e uma mensagem clara.
3. Alterar um arquivo, olhar o `git diff` e descartar a alteração com `git restore`.
4. Criar um ramo, fazer um commit nele e incorporá-lo ao `main`.
5. Mostrar o histórico com `git log --oneline` e explicar cada linha.

### Problemas comuns

- **"Please tell me who you are":** faltou configurar `user.name` e `user.email`.
- **Arquivos indesejados aparecem no `git status`:** incluí-los no `.gitignore`. Se já foram versionados, é preciso removê-los do controle com `git rm --cached` (explicar com cuidado).
- **Commit com arquivos errados:** conferir o `git status` antes de cada commit.

### Entregável

Repositório local com pelo menos três commits de mensagens claras, `.gitignore` e saída do `git log --oneline` colada em um arquivo de texto.
