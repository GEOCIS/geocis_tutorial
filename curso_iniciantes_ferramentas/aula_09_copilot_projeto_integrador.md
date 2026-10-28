# Aula 9: GitHub Copilot e projeto integrador

[← Aula 8](aula_08_github.md) · [Plano do curso](README.md) · [Apêndices →](apendices.md)

## Resumo do plano

**Objetivos:** usar o Copilot como assistente, com revisão crítica, e consolidar o aprendizado em um projeto.

**Conteúdo:**

- O que é o GitHub Copilot: assistente de IA que sugere código e responde perguntas dentro do editor. Verificar no site do GitHub os planos disponíveis, os limites de uso e a gratuidade para estudantes e docentes (*GitHub Education*), pois as condições mudam com o tempo.
- Instalação da extensão no VS Code e login com a conta GitHub.
- Recursos principais:
  - **Sugestões em linha**: escrever um comentário ou o nome de uma função e aceitar a sugestão com `Tab` (ou recusar com `Esc`).
  - **Chat do Copilot**: perguntar sobre o código, pedir explicações, correções de erros, testes e documentação.
  - **Contexto**: o Copilot usa os arquivos abertos, então mantenha o projeto organizado e dê instruções claras.
- Como escrever bons *prompts*: objetivo, dados de entrada, formato esperado e restrições. Exemplo: "Escreva uma função que leia um CSV, remova linhas sem o valor da coluna `argila` e retorne um DataFrame".
- Uso responsável:
  - **Revisar e testar** tudo o que for sugerido: o Copilot pode errar ou gerar código desatualizado.
  - **Entender antes de aceitar**: usar a IA para aprender, e não apenas para copiar.
  - **Privacidade**: não colar dados sensíveis ou credenciais em prompts.
  - **Integridade acadêmica**: seguir as regras da disciplina sobre o uso de IA e declarar o uso quando exigido.
  - Atenção a questões de licenciamento do código sugerido.

**Projeto integrador:** em duplas, criar um repositório com um notebook que leia um conjunto de dados, faça limpeza e análise exploratória, produza ao menos três gráficos e conclusões escritas em Markdown. O projeto deve ter `README.md`, `requirements.txt`, `.gitignore` e histórico de commits com pelo menos cinco mensagens claras. O Copilot pode ser usado, e cada dupla deve registrar no README ao menos um trecho em que a sugestão precisou ser corrigida.

## Material de aula

**Materiais:** VS Code, conta no GitHub com acesso ao Copilot (verificar o plano gratuito e os benefícios para estudantes e docentes no site do GitHub, pois as condições mudam), projeto `analise_solos` versionado.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 25 min: o que é o Copilot, instalação e login.
- 25 a 60 min: sugestões em linha e chat, com demonstrações.
- 60 a 85 min: revisão crítica de código sugerido (exercício) e uso responsável.
- 85 a 115 min: apresentação e início do projeto integrador.
- 115 a 120 min: encerramento do curso e combinados de entrega.

### Conteúdo

O **GitHub Copilot** é um assistente de programação baseado em IA, integrado ao editor. Ele sugere código enquanto se digita, responde perguntas em um chat e pode explicar, corrigir, documentar e testar código. Ele **não entende o problema como uma pessoa**: gera respostas prováveis a partir do contexto, e por isso pode errar com aparência de certeza, inventar funções que não existem ou sugerir código desatualizado. O papel do programador é descrever bem o problema, revisar, testar e decidir.

### Instalação e login

1. Na visão de extensões (`Ctrl+Shift+X`), pesquisar **GitHub Copilot** (publicador: GitHub) e instalar. Nas versões atuais, a extensão inclui o chat; se a interface do VS Code solicitar, instalar também a extensão **GitHub Copilot Chat**.
2. Fazer o login com a conta do GitHub quando o VS Code solicitar, e autorizar.
3. Conferir o ícone do Copilot na barra de status e a disponibilidade do plano da conta.

### Recursos principais

**1. Sugestões em linha.** Ao digitar um comentário ou o início de uma função, o Copilot mostra uma sugestão em cinza.

- `Tab`: aceitar. `Esc`: recusar.
- Quando houver alternativas, o editor oferece atalhos para navegar entre elas (mostrados na própria caixa da sugestão).
- Quanto melhor o comentário ou o nome da função, melhor a sugestão.

**2. Chat do Copilot.** Painel de conversa (ícone do Copilot na barra superior, ou paleta de comandos) para perguntar sobre o código aberto. Exemplos de uso:

- "Explique o que este código faz, passo a passo."
- "Por que este erro aparece e como corrigi-lo?" (colando a mensagem de erro)
- "Escreva testes para esta função."
- "Adicione comentários (docstrings) a esta função."

Comandos de barra usados em versões atuais, como `/explain`, `/fix`, `/tests` e `/doc`, podem variar entre versões do editor. Conferir a lista ao digitar `/` no chat.

**3. Chat em linha.** Selecionar um trecho e abrir o chat em linha (atalho `Ctrl+I`, ou pelo menu de contexto) para pedir uma alteração diretamente no arquivo, aceitando ou descartando a mudança.

**4. Contexto.** O Copilot considera principalmente o arquivo aberto e outros arquivos abertos no editor. Manter o projeto organizado e abrir os arquivos relacionados melhora as respostas.

### Como escrever bons *prompts*

Um bom pedido informa: **o objetivo**, **os dados de entrada** (nomes das colunas, tipos), **o formato esperado da saída** e **restrições** (bibliotecas, versão, estilo).

- Fraco: "faz uma análise do arquivo".
- Melhor: "Usando pandas, leia `solos.csv` (colunas: amostra, cultura, argila, materia\_organica, ph), remova linhas sem pH e calcule a média de argila por cultura. Retorne um DataFrame ordenado do maior para o menor valor."

Dicas: pedir em etapas pequenas, informar o erro completo, pedir explicações do que foi gerado e pedir alternativas mais simples quando a resposta for complexa demais.

### Prática guiada

No projeto `analise_solos`, criar um arquivo `copilot_pratica.py` e experimentar:

1. **Sugestão a partir de comentário.** Digitar apenas o comentário abaixo e observar a sugestão:

```python
# função que recebe um DataFrame e retorna a média de argila por cultura, ordenada do maior para o menor
```

2. **Explicação.** Selecionar uma função do notebook e pedir ao chat: "Explique este código para um iniciante".
3. **Correção de erro.** Provocar um erro de propósito (por exemplo, chamar uma coluna inexistente, `df["argilla"]`) e pedir ao chat para explicá-lo e corrigi-lo.
4. **Testes.** Pedir ao chat testes para a função de média de argila, e executá-los.

### Exercício de revisão crítica

O código abaixo, típico de uma sugestão que parece correta, tem problemas. Pedir aos alunos que o executem, descubram o que falha e corrijam, sem usar o Copilot em um primeiro momento:

```python
import pandas as pd

df = pd.read_csv("solos.csv")

resultados = pd.DataFrame()
for cultura in df["cultura"].unique():
    sub = df[df["cultura"] == cultura]
    resultados = resultados.append({"cultura": cultura, "argila_media": sub["argila"].mean()}, ignore_index=True)

print(resultados)
```

**Gabarito:** o método `DataFrame.append` foi removido nas versões atuais do pandas, e o código gera um erro. A forma recomendada é `groupby`:

```python
resultados = (df.groupby("cultura")["argila"].mean()
                .reset_index(name="argila_media")
                .sort_values("argila_media", ascending=False))
print(resultados)
```

Lição: sugestões podem usar recursos obsoletos. Sempre executar, testar e ler a documentação da versão instalada.

### Checklist de revisão de código sugerido

1. Entendi cada linha? Se não, pedir explicação ou simplificar.
2. Executei e testei com um exemplo cujo resultado conheço?
3. As funções e os parâmetros existem na versão das bibliotecas instaladas?
4. O código trata casos especiais (valores faltantes, divisão por zero, lista vazia)?
5. O resultado faz sentido físico e agronômico?
6. O código é compatível com as regras de uso de IA da disciplina?

### Uso responsável

- **Aprender, não apenas copiar:** tentar primeiro, e usar o Copilot para tirar dúvidas e comparar soluções.
- **Privacidade:** não incluir senhas, chaves, dados pessoais ou dados sigilosos em *prompts* ou em arquivos abertos quando o Copilot estiver ativo. Verificar as configurações de privacidade da conta e as políticas da instituição.
- **Integridade acadêmica:** seguir as regras da disciplina sobre o uso de IA e declarar o uso quando exigido.
- **Licenças:** o código sugerido pode se assemelhar a código existente. Conferir as opções de filtro de sugestões públicas nas configurações do Copilot e a licença quando o código for publicado.
- **Responsabilidade:** quem aceita o código responde por ele.

### Projeto integrador

**Objetivo:** consolidar as ferramentas do curso em um projeto reprodutível.

**Formato:** em duplas, com apresentação de 5 a 8 minutos na semana seguinte.

**Tarefa:** criar um repositório com um notebook que:

1. leia um conjunto de dados (os dados fictícios do curso, ou outro conjunto aprovado pelo professor);
2. faça limpeza e análise exploratória (estatísticas, faltantes e filtros);
3. produza pelo menos **três gráficos** com títulos, eixos rotulados e interpretação;
4. termine com **conclusões** escritas em Markdown.

**Requisitos do repositório:** `README.md` (objetivo, como instalar e executar), `requirements.txt`, `.gitignore` e, no mínimo, **cinco commits** com mensagens claras, de ambos os integrantes. O Copilot pode ser usado, e a dupla deve registrar no README **pelo menos um trecho em que a sugestão precisou ser corrigida** e o que foi feito.

**Cronograma sugerido:** definir o conjunto de dados e criar o repositório (aula 9); desenvolvimento durante a semana, com commits frequentes; apresentação e discussão na semana seguinte.

### Critérios de avaliação do projeto

| Critério | Peso | O que se observa |
| --- | --- | --- |
| Reprodutibilidade | 25% | Outra pessoa consegue executar seguindo o README, com `requirements.txt` |
| Análise e gráficos | 30% | Perguntas claras, gráficos corretos e interpretação coerente |
| Uso do Git e do GitHub | 20% | Histórico de commits, mensagens claras, contribuição dos dois integrantes |
| Documentação | 15% | README completo, notebook organizado, texto em Markdown |
| Uso crítico do Copilot | 10% | Registro de uma correção e reflexão sobre o que foi aprendido |

### Encerramento do curso

Retomar o fluxo completo (Python, VS Code, ambiente virtual, bibliotecas, notebook, Git, GitHub e Copilot), pedir que cada aluno liste o que aprendeu e o que ainda tem dúvidas, e indicar os próximos passos: o curso por capítulos sobre o pipeline de espectroscopia de solos e o curso de metodologia.

### Entregável

Repositório do projeto integrador no GitHub, com o link enviado ao professor antes da apresentação.
