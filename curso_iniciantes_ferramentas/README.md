# Curso para iniciantes: VS Code, Python, Jupyter Notebook, Git, GitHub e GitHub Copilot

*Plano de aulas sobre instalação e uso de um ambiente de ciência de dados, do zero ao primeiro projeto versionado*

## 1. Visão geral

**Público:** pessoas sem experiência prévia em programação, como estudantes de áreas aplicadas (agronomia, biologia, engenharias) que querem analisar dados.

**Objetivo geral:** ao final do curso, o aluno será capaz de configurar um ambiente de trabalho completo, escrever e executar análises em Jupyter Notebook, gerenciar bibliotecas, versionar o projeto com Git, publicá-lo no GitHub e usar o GitHub Copilot como apoio, com senso crítico.

**Pré-requisitos:** computador com Windows, macOS ou Linux, acesso à internet e permissão para instalar programas.

**Formato sugerido:** 9 aulas de 2 horas (18 horas), com cerca de 30% de explicação e 70% de prática guiada. Cada aula termina com um entregável simples, e o curso termina com um projeto integrador.

## 2. Cronograma

| Aula | Tema | Entregável |
| --- | --- | --- |
| 1 | Introdução e preparação do ambiente | Pasta de trabalho organizada e checklist de ferramentas |
| 2 | Instalação do Python | `python --version` funcionando e primeiro script |
| 3 | VS Code: instalação e uso | VS Code configurado com extensões e script executado |
| 4 | Ambientes virtuais e bibliotecas | Ambiente `.venv` e arquivo `requirements.txt` |
| 5 | Jupyter Notebook no VS Code | Notebook com texto, código e gráfico |
| 6 | Primeira análise de dados | Notebook de análise exploratória de uma tabela |
| 7 | Git: controle de versão | Repositório local com pelo menos 3 commits |
| 8 | GitHub: repositório remoto e colaboração | Projeto publicado no GitHub com README |
| 9 | GitHub Copilot e projeto integrador | Mini-projeto completo, versionado e publicado |

## Arquivos do curso

| Arquivo | Conteúdo |
| --- | --- |
| [aula_01_introducao_ambiente.md](aula_01_introducao_ambiente.md) | Aula 1: Introdução e preparação do ambiente |
| [aula_02_instalacao_python.md](aula_02_instalacao_python.md) | Aula 2: Instalação do Python |
| [aula_03_vscode.md](aula_03_vscode.md) | Aula 3: VS Code, instalação e uso |
| [aula_04_ambientes_virtuais_bibliotecas.md](aula_04_ambientes_virtuais_bibliotecas.md) | Aula 4: Ambientes virtuais e bibliotecas |
| [aula_05_jupyter_notebook.md](aula_05_jupyter_notebook.md) | Aula 5: Jupyter Notebook no VS Code |
| [aula_06_primeira_analise_dados.md](aula_06_primeira_analise_dados.md) | Aula 6: Primeira análise de dados |
| [aula_07_git.md](aula_07_git.md) | Aula 7: Git, controle de versão |
| [aula_08_github.md](aula_08_github.md) | Aula 8: GitHub, repositório remoto e colaboração |
| [aula_09_copilot_projeto_integrador.md](aula_09_copilot_projeto_integrador.md) | Aula 9: GitHub Copilot e projeto integrador |
| [apendices.md](apendices.md) | Apêndice A: folha de referência rápida; Apêndice B: glossário |

Cada aula tem 2 horas e segue o cronograma acima. O material traz o roteiro com tempos, o conteúdo a expor, a prática guiada passo a passo, os exercícios com gabarito e o entregável. Os tempos são sugestões e podem ser ajustados conforme a turma.

**Antes do curso (para o professor):** testar todos os passos em um computador limpo de cada sistema operacional usado pela turma, e conferir se as versões atuais das ferramentas mantêm os menus e os nomes citados aqui.

## 3. Avaliação sugerida

- **Entregáveis semanais (40%)**: checklist de cada aula.
- **Projeto integrador (50%)**: organização, reprodutibilidade, qualidade da análise e histórico de commits.
- **Participação e uso crítico do Copilot (10%)**.

## 4. Problemas comuns e soluções

- **`python` não é reconhecido**: reinstalar marcando *Add to PATH* ou usar `py` (Windows) e `python3` (macOS e Linux).
- **Kernel não aparece no notebook**: instalar `ipykernel` no ambiente e selecionar o interpretador correto no VS Code.
- **Biblioteca instalada, mas `import` falha**: o ambiente virtual ativo não é o mesmo selecionado no editor.
- **Erro de política de execução ao ativar o `.venv` no PowerShell**: ajustar a política de execução para o usuário atual ou usar o Prompt de Comando.
- **`git push` rejeitado**: o repositório remoto tem commits que o local não tem, então fazer `git pull` antes.
- **Arquivo grande demais para o GitHub**: não versionar dados volumosos, e usar `.gitignore` ou serviços de armazenamento de dados.

## 5. Materiais e referências

- Documentação oficial: Python (docs.python.org), VS Code (code.visualstudio.com/docs), Jupyter (jupyter.org), pandas (pandas.pydata.org), Git (git-scm.com/doc) e GitHub Docs (docs.github.com).
- Para o Copilot, consultar a documentação do GitHub, que é atualizada com frequência.
- Conjuntos de dados abertos para prática, como os do próprio curso ou de repositórios públicos de dados agronômicos.

## 6. Orientações para quem ministra

1. Reservar os primeiros minutos de cada aula para resolver problemas de instalação, que consomem muito tempo.
2. Combinar um único sistema de trabalho (por exemplo, Python do python.org com `venv`) para evitar suporte a várias configurações.
3. Incentivar o trabalho em duplas e a prática de erro e correção, com leitura das mensagens de erro.
4. Gravar os comandos principais em uma folha de referência rápida (*cheat sheet*) distribuída ao final de cada aula.
5. Revisar as instruções de instalação e os planos do Copilot antes de cada turma, pois interfaces e condições mudam.
