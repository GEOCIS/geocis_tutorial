# Aula 1: Introdução e preparação do ambiente

[Plano do curso](README.md) · [Aula 2 →](aula_02_instalacao_python.md)

## Resumo do plano

**Objetivos:** entender o papel de cada ferramenta e preparar a organização do trabalho.

**Conteúdo:**

- Como as peças se encaixam: **Python** (linguagem), **VS Code** (editor), **Jupyter Notebook** (documento com código, texto e gráficos), **bibliotecas** (pacotes prontos, como pandas), **Git** (histórico de versões), **GitHub** (hospedagem e colaboração) e **Copilot** (assistente de código com IA).
- Noções básicas: pasta, caminho de arquivo, terminal (o que é e para que serve).
- Boas práticas de organização: uma pasta por projeto, nomes sem espaços e sem acentos.

**Prática:** criar a pasta `meus_projetos` e abrir o terminal do sistema (PowerShell no Windows, Terminal no macOS e Linux), navegando entre pastas com `cd` e listando arquivos (`dir` no Windows, `ls` no macOS e Linux).

## Material de aula

**Materiais:** computador com acesso à internet, projetor e a lista de verificação (*checklist*) impressa ou digital.

### Roteiro (120 min)

- 0 a 15 min: boas-vindas, apresentação do curso e levantamento de expectativas (quem já programou? qual sistema operacional cada um usa?).
- 15 a 45 min: as ferramentas e como elas se encaixam.
- 45 a 85 min: terminal na prática.
- 85 a 110 min: organização de pastas e nomes de arquivos.
- 110 a 120 min: *checklist* de instalação e tarefa para a próxima aula.

### Conteúdo

**As ferramentas, em uma analogia de laboratório:**

- **Python**: a linguagem em que damos instruções ao computador, como o idioma de um protocolo.
- **VS Code**: a bancada de trabalho, onde escrevemos, organizamos e executamos o código.
- **Jupyter Notebook**: o caderno de laboratório digital, que reúne código, resultados, gráficos e anotações no mesmo documento.
- **Bibliotecas** (pandas, numpy, matplotlib): a caixa de ferramentas pronta, para não reinventar cada função.
- **Git**: o histórico de versões do trabalho, que permite voltar a qualquer ponto anterior.
- **GitHub**: o armazenamento em nuvem dos projetos versionados, que também serve para colaborar e publicar.
- **GitHub Copilot**: um assistente que sugere código e explica erros, e cujas respostas sempre precisam ser conferidas.

**O fluxo de trabalho do curso:** instalar o Python, configurar o VS Code, criar um ambiente virtual e instalar as bibliotecas, analisar dados em um notebook, versionar com Git, publicar no GitHub e, por fim, usar o Copilot como apoio.

### Prática guiada: o terminal

O terminal é uma janela em que digitamos comandos de texto em vez de clicar. No Windows, abrir o **PowerShell** (menu Iniciar); no macOS, o **Terminal** (Spotlight); no Linux, o terminal da distribuição. Os comandos abaixo funcionam, com pequenas diferenças, nos três sistemas (o PowerShell aceita `ls`, `cd`, `mkdir` e `pwd`).

```bash
pwd                    # mostra a pasta atual
ls                     # lista arquivos (no Prompt de Comando do Windows: dir)
mkdir meus_projetos    # cria uma pasta
cd meus_projetos       # entra na pasta
mkdir aula01
cd aula01
cd ..                  # volta uma pasta
```

Pontos a explicar durante a demonstração:

- O terminal sempre "está" em alguma pasta, e os comandos agem nela.
- Caminho absoluto (completo, a partir da raiz) e caminho relativo (a partir da pasta atual).
- A tecla `Tab` completa nomes de arquivos e pastas, e a seta para cima repete comandos anteriores.
- Para interromper um comando travado: `Ctrl+C`.

### Organização de pastas e nomes

Boas práticas desde o início:

- Uma pasta por projeto, dentro de uma pasta geral (`meus_projetos`).
- Nomes sem espaços, sem acentos e sem caracteres especiais; usar `_` ou `-` (por exemplo, `analise_solos`, e não `Análise de Solos (final)`).
- Evitar pastas sincronizadas com serviços de nuvem para projetos com Git, pois podem causar conflitos.
- Estrutura sugerida para projetos de dados:

```text
meu_projeto/
  dados/
  notebooks/
  resultados/
  README.md
```

### Exercícios

1. No terminal, criar a estrutura `meus_projetos/aula01/` e, dentro dela, as pastas `dados`, `notebooks` e `resultados`.
2. Navegar entre as pastas usando caminho relativo e depois absoluto, mostrando a pasta atual com `pwd`.
3. Listar o conteúdo de `meus_projetos` e explicar o que apareceu.

### Observações para o professor

- Levantar logo o sistema operacional de cada aluno e se o computador é pessoal ou da instituição, pois computadores institucionais podem exigir permissão de administrador.
- Reservar tempo para ajudar os alunos com dificuldade no terminal, que costuma ser a maior barreira inicial.

### Entregável e preparação

Pasta `meus_projetos` com a estrutura criada. **Para a próxima aula:** conferir se há espaço livre em disco (alguns GB), conexão com a internet e permissão de instalação de programas.
