# Aula 8: GitHub, repositório remoto e colaboração

[← Aula 7](aula_07_git.md) · [Plano do curso](README.md) · [Aula 9 →](aula_09_copilot_projeto_integrador.md)

## Resumo do plano

**Objetivos:** publicar o projeto e conhecer o fluxo básico de colaboração.

**Conteúdo:**

- Git e GitHub: Git é a ferramenta local; GitHub é a plataforma que hospeda repositórios.
- Criar conta, configurar o perfil e a autenticação (recomenda-se o *Git Credential Manager*, instalado com o Git para Windows, ou o GitHub CLI; chaves SSH como opção avançada). Não usar a senha da conta no terminal, e sim os métodos de login atuais.
- Criar um repositório (público ou privado) e conectar ao projeto local:
  - `git remote add origin URL`
  - `git branch -M main`
  - `git push -u origin main`
- Baixar e atualizar: `git clone` e `git pull`.
- Escrever um bom `README.md` (objetivo, como instalar, como executar) e escolher uma licença.
- Colaboração: *issues*, *forks* e *pull requests* (conceito e demonstração).
- Cuidados: nunca publicar senhas, chaves de API ou dados sensíveis, e verificar os termos de uso e a privacidade de bancos de dados antes de torná-los públicos.
- Publicação no GitHub Pages ou visualização de notebooks diretamente no repositório.

**Prática:** publicar o projeto da aula 6 no GitHub com README, clonar o repositório de um colega e abrir um *pull request* simples (por exemplo, corrigir um erro de digitação).

## Material de aula

**Materiais:** conta no GitHub (github.com), projeto versionado na aula 7, Git Credential Manager (incluído no Git para Windows) ou GitHub CLI.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 25 min: Git e GitHub, e criação da conta.
- 25 a 55 min: criar o repositório e publicar o projeto.
- 55 a 70 min: README e licença.
- 70 a 100 min: clonar, atualizar e colaborar (*fork* e *pull request*).
- 100 a 115 min: boas práticas e segurança.
- 115 a 120 min: resumo e entregável.

### Conteúdo

O **Git** é a ferramenta local. O **GitHub** é uma plataforma que hospeda repositórios Git na nuvem, com ferramentas de colaboração: *issues* (tarefas e discussões), *pull requests* (propostas de alteração para revisão), *forks* (cópias pessoais de um repositório), *Actions* (automações) e *Pages* (publicação de páginas). Existem alternativas, como GitLab e Bitbucket, com a mesma ideia.

Alunos podem se beneficiar de pacotes educacionais gratuitos do GitHub (GitHub Education), cujas condições devem ser conferidas no site.

### Autenticação

O GitHub não aceita mais a senha da conta para operações Git pela linha de comando. Opções:

- **HTTPS com Git Credential Manager:** no primeiro `git push`, abre-se uma janela do navegador para login, e a credencial fica salva de forma segura. É o caminho mais simples para iniciantes e já vem incluído no Git para Windows. No macOS e no Linux, usar o GitHub CLI ou instalar o Git Credential Manager.
- **GitHub CLI** (`gh auth login`): assistente de login pelo terminal.
- **Chave SSH:** mais avançada, indicada para uso frequente.

Nunca compartilhar tokens ou chaves, e nunca colocá-los em arquivos versionados.

### Prática guiada: publicar o projeto

1. **Criar a conta** e configurar o perfil (foto e nome), ativando a verificação em duas etapas.
2. **Criar um repositório:** botão *New*, nome sem espaços (por exemplo, `analise-solos`), visibilidade (público ou privado), **sem** marcar a criação de README, `.gitignore` ou licença (o projeto local já tem histórico).
3. **Conectar o projeto local ao remoto** (comandos exibidos pela própria página do repositório):

```bash
git remote add origin https://github.com/SEU_USUARIO/analise-solos.git
git branch -M main
git push -u origin main
```

No primeiro `push`, fazer o login quando solicitado. Depois, atualizar a página do repositório no navegador para ver os arquivos e o histórico.

4. **Ciclo diário de trabalho:**

```bash
git pull                      # traz as alterações do remoto
# ... editar, git add, git commit ...
git push                      # envia os commits
```

### README e licença

O `README.md` é a porta de entrada do projeto. Modelo básico:

```markdown
# Análise de solos

Análise exploratória de dados fictícios de solos (argila, matéria orgânica e pH).

## Como executar
1. Criar o ambiente: `python -m venv .venv`
2. Ativar o ambiente e instalar: `pip install -r requirements.txt`
3. Abrir `analise_solos.ipynb` no VS Code e executar todas as células.

## Conteúdo
- `analise_solos.ipynb`: análise exploratória
- `requirements.txt`: bibliotecas necessárias

## Autoria
Seu Nome, 2026
```

Sobre **licença**: sem licença, ninguém tem permissão formal para reutilizar o código. Para trabalhos acadêmicos, discutir com o orientador a opção adequada (por exemplo, MIT para código, e licenças *Creative Commons* para textos), e verificar a política da instituição.

### Clonar e colaborar

**Clonar** um repositório existente (baixa o código e o histórico):

```bash
git clone https://github.com/USUARIO/REPOSITORIO.git
```

**Fluxo de colaboração por *fork* e *pull request*** (usado em projetos abertos):

1. No repositório de um colega, clicar em **Fork** para criar uma cópia na própria conta.
2. Clonar o *fork*, criar um ramo (`git switch -c corrige-readme`), fazer a alteração e o commit.
3. Enviar o ramo: `git push -u origin corrige-readme`.
4. No GitHub, abrir um **Pull Request** descrevendo a mudança.
5. O dono do repositório revisa, comenta e, se aprovar, faz o *merge*.

Para equipes pequenas, uma alternativa é adicionar colegas como colaboradores (*Settings > Collaborators*) e trabalhar com ramos e *pull requests* no mesmo repositório.

### Boas práticas e segurança

- Nunca publicar senhas, tokens, chaves de API ou arquivos `.env`. Se isso acontecer, trocar a credencial imediatamente (apagar o arquivo do histórico não basta).
- Antes de tornar público um repositório, conferir se há dados sensíveis, de terceiros ou sujeitos a restrições de uso.
- Não versionar arquivos de dados muito grandes (o GitHub limita o tamanho dos arquivos); usar `.gitignore` e documentar no README onde obter os dados.
- Fazer commits pequenos e mensagens claras, e `git pull` antes de começar a trabalhar.
- Os notebooks `.ipynb` são exibidos diretamente no GitHub, o que facilita compartilhar análises.

### Exercícios

1. Publicar o projeto da aula 6 no GitHub, com README, `requirements.txt` e `.gitignore`.
2. Clonar o repositório de um colega em outra pasta e executar o notebook seguindo apenas o README. Anotar o que faltou na documentação.
3. Em duplas, abrir um *pull request* no repositório do colega com uma pequena melhoria (por exemplo, corrigir o README ou acrescentar um gráfico) e revisar o *pull request* recebido.
4. Abrir uma *issue* sugerindo uma melhoria e fechá-la ao resolvê-la.

### Problemas comuns

- **`git push` rejeitado ("rejected"):** o remoto tem commits que o local não tem. Fazer `git pull` e tentar de novo.
- **Erro de autenticação:** refazer o login pelo Git Credential Manager ou pelo `gh auth login`.
- **Conflito de *merge*:** dois commits alteraram o mesmo trecho. O VS Code mostra as opções de resolução (manter uma das versões ou ambas); depois, fazer `git add` e o commit.
- **Arquivo grande demais:** removê-lo do repositório e incluí-lo no `.gitignore`.

### Entregável

Link do repositório público (ou privado, com o professor adicionado) com README, `requirements.txt` e histórico de commits, e o relato do *pull request* realizado.
