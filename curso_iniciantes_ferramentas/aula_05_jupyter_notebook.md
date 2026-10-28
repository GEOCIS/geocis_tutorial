# Aula 5: Jupyter Notebook no VS Code

[← Aula 4](aula_04_ambientes_virtuais_bibliotecas.md) · [Plano do curso](README.md) · [Aula 6 →](aula_06_primeira_analise_dados.md)

## Resumo do plano

**Objetivos:** criar e usar notebooks para análises documentadas.

**Conteúdo:**

- O que é um notebook (`.ipynb`): células de código e de texto (Markdown), execução incremental e saída abaixo da célula.
- Criar um notebook no VS Code e escolher o *kernel* (o ambiente virtual da aula 4).
- Executar células (`Shift+Enter`), adicionar e reordenar células, converter entre código e Markdown, reiniciar o kernel.
- Escrever texto com Markdown: títulos, listas, negrito e fórmulas simples.
- Boas práticas: executar de cima para baixo, nomes claros, uma ideia por célula e limpar saídas antes de versionar.
- Alternativas: JupyterLab e Jupyter Notebook clássico, instalados com `pip install jupyterlab`.

**Prática:** criar `primeiro_notebook.ipynb` com título, uma célula de cálculo e um gráfico simples (`plt.plot`) com texto explicativo.

## Material de aula

**Materiais:** ambiente `.venv` da aula 4 com `ipykernel`, VS Code com a extensão Jupyter.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 25 min: o que é um notebook e quando usar.
- 25 a 55 min: criar o notebook, escolher o kernel e executar células.
- 55 a 80 min: texto em Markdown e organização do documento.
- 80 a 100 min: armadilhas (ordem de execução e estado oculto) e boas práticas.
- 100 a 120 min: exercício e entregável.

### Conteúdo

Um **notebook** (`.ipynb`) é um documento dividido em **células**: células de código, que são executadas e mostram o resultado logo abaixo, e células de texto (Markdown), com explicações, títulos e fórmulas. É ideal para análise exploratória, ensino e relatórios, pois reúne o raciocínio, o código e os resultados. Para programas maiores e reutilizáveis, scripts `.py` continuam sendo melhores, e o ideal é combinar: funções em arquivos `.py` e a análise em notebooks (como no pipeline do projeto).

O **kernel** é o processo que executa o código do notebook. Ele guarda na memória as variáveis criadas, o que traz vantagens (não repetir cálculos) e riscos (resultados que dependem do que foi executado antes).

### Prática guiada

1. **Criar o notebook:** paleta de comandos (`Ctrl+Shift+P`), *Create: New Jupyter Notebook*, e salvar como `primeiro_notebook.ipynb` na pasta `aula05`.
2. **Escolher o kernel:** botão *Select Kernel* no canto superior direito, *Python Environments*, e o ambiente `.venv`. Se o VS Code oferecer a instalação do `ipykernel`, aceitar.
3. **Executar uma célula de código:**

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title("Função seno")
plt.xlabel("x")
plt.ylabel("sen(x)")
plt.show()
```

Executar com `Shift+Enter` (executa e vai para a próxima célula) ou `Ctrl+Enter` (executa e permanece na célula).

4. **Criar uma célula de texto:** botão *+ Markdown*, ou converter a célula pelo seletor de tipo. Exemplo de conteúdo Markdown:

```markdown
# Análise de teste

Este notebook demonstra o uso de **numpy** e **matplotlib**.

## Objetivos
- Gerar uma função seno
- Visualizar o gráfico

A média da função em um período completo é próxima de $0$.
```

Elementos de Markdown a mostrar: títulos (`#`, `##`), negrito (`**texto**`), itálico (`*texto*`), listas (`-`), links (`[texto](endereço)`) e fórmulas entre cifrões (`$x^2$`).

5. **Operações com células:** na barra de cada célula ou pelos atalhos em modo de comando (tecla `Esc` seleciona a célula): `A` insere uma célula acima, `B` abaixo, `M` converte em Markdown, `Y` em código, `D` duas vezes exclui. Também é possível arrastar células para reordená-las.

### A armadilha do estado oculto

Demonstrar com este experimento:

- Célula 1: `a = 10`
- Célula 2: `b = a * 2` (executar, resultado 20)
- Voltar à célula 1, alterar para `a = 100` e executar **sem** reexecutar a célula 2.
- Em uma célula nova, `print(b)` continua mostrando 20, embora `a` seja 100.

Isso mostra que os números na margem das células indicam a ordem real de execução, e que o notebook pode ficar inconsistente. A solução é **reiniciar o kernel e executar tudo, de cima para baixo** (botões *Restart* e *Run All*), sempre antes de concluir uma análise.

### Boas práticas

- Executar de cima para baixo e garantir que o notebook funcione com *Restart + Run All*.
- Começar com um título, o objetivo e a data.
- Colocar as importações na primeira célula.
- Uma ideia por célula, com nomes de variáveis claros.
- Explicar em Markdown o que será feito e o que foi observado.
- Limpar as saídas antes de versionar com Git, se elas forem grandes (*Clear All Outputs*).
- Exportar o resultado para compartilhar: no menu *...* do notebook, *Export*, escolhendo HTML ou PDF (o PDF pode exigir ferramentas adicionais).

**Alternativas:** o JupyterLab e o Jupyter Notebook clássico funcionam em navegador e são instalados com `pip install jupyterlab`, e iniciados com `jupyter lab`. O formato do arquivo é o mesmo.

### Exercício: "Meu primeiro relatório"

Criar um notebook com:

1. Um título e um parágrafo de objetivo em Markdown.
2. Uma célula que cria uma lista de cinco valores de teor de argila e calcula média, mínimo e máximo.
3. Uma célula com um gráfico de barras desses valores, com título e rótulos dos eixos.
4. Uma célula de Markdown com duas conclusões escritas pelo aluno.
5. Verificação final com *Restart* e *Run All*.

**Exemplo de solução (células de código):**

```python
import numpy as np
import matplotlib.pyplot as plt

argila = np.array([22.0, 35.5, 41.0, 18.2, 30.7])
print("Média:", argila.mean(), "| Mín:", argila.min(), "| Máx:", argila.max())

plt.bar(["A", "B", "C", "D", "E"], argila)
plt.title("Teor de argila por amostra")
plt.xlabel("Amostra")
plt.ylabel("Argila (%)")
plt.show()
```

### Problemas comuns

- **Kernel não aparece na lista:** instalar `ipykernel` no ambiente (`pip install ipykernel`) e reiniciar o VS Code.
- **`ModuleNotFoundError` no notebook:** o kernel selecionado não é o ambiente onde a biblioteca foi instalada.
- **Gráfico não aparece:** conferir se `plt.show()` foi executado e se não houve erro na célula anterior.

### Entregável

Arquivo `primeiro_notebook.ipynb` e o notebook do exercício, que devem ser executados com sucesso por *Restart + Run All*.
