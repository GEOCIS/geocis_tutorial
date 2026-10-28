# Aula 6: Primeira análise de dados

[← Aula 5](aula_05_jupyter_notebook.md) · [Plano do curso](README.md) · [Aula 7 →](aula_07_git.md)

## Resumo do plano

**Objetivos:** aplicar pandas, numpy e matplotlib em um conjunto de dados real e pequeno.

**Conteúdo:**

- Ler dados: `pd.read_csv()`, e inspecionar com `head()`, `info()`, `describe()` e `shape`.
- Selecionar colunas e filtrar linhas, valores ausentes (`isna()`, `dropna()`), estatísticas por grupo (`groupby`).
- Gráficos: histograma, dispersão e boxplot com matplotlib.
- Salvar resultados: `to_csv()` e `savefig()`.
- Conexão com o projeto da disciplina: mostrar como a mesma lógica aparece na análise exploratória de espectros de solo.

**Prática:** analisar uma tabela fornecida pelo professor (por exemplo, dados de produtividade ou de solo), respondendo a três perguntas simples com tabelas e gráficos.

## Material de aula

**Materiais:** ambiente `.venv` com pandas, numpy e matplotlib. Os dados do exercício são gerados por um código fornecido (conjunto fictício), o que evita a necessidade de baixar arquivos.

### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 25 min: geração e leitura dos dados.
- 25 a 50 min: inspeção da tabela.
- 50 a 75 min: seleção, filtros e valores faltantes.
- 75 a 95 min: estatísticas por grupo.
- 95 a 115 min: gráficos e salvamento dos resultados.
- 115 a 120 min: resumo e entregável.

### Conteúdo

O **pandas** trabalha com o **DataFrame**, uma tabela com linhas (amostras) e colunas (variáveis, cada uma com um tipo de dado). A análise exploratória segue um roteiro: conhecer a tabela, verificar a qualidade (faltantes e valores estranhos), resumir com estatísticas e visualizar com gráficos.

### Gerar o conjunto de dados fictício

Em um novo notebook `analise_solos.ipynb`, a primeira célula cria e salva a tabela `solos.csv` (dados fictícios, apenas para treino):

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(1)
n = 80

argila = np.clip(rng.normal(35, 12, n), 5, 80)
mo = np.clip(4 - 0.03 * argila + rng.normal(0, 0.8, n) + 2, 0.5, 8)
ph = np.clip(rng.normal(5.6, 0.5, n), 4, 7.5)

df = pd.DataFrame({
    "amostra": [f"S{i:03d}" for i in range(n)],
    "cultura": rng.choice(["soja", "milho", "pastagem"], n),
    "argila": argila.round(1),
    "materia_organica": mo.round(2),
    "ph": ph.round(2),
})
df.loc[rng.choice(n, 6, replace=False), "ph"] = np.nan   # valores faltantes

df.to_csv("solos.csv", index=False)
print("Arquivo criado:", df.shape)
```

### Roteiro de análise (cada item em uma célula)

**1. Leitura e primeira inspeção**

```python
df = pd.read_csv("solos.csv")
df.head()          # primeiras linhas
df.shape           # (linhas, colunas)
df.info()          # tipos e quantidade de valores não nulos
```

**2. Estatísticas descritivas e valores faltantes**

```python
df.describe()                # média, desvio, mínimo, quartis, máximo
df.isna().sum()              # faltantes por coluna
df["cultura"].value_counts() # contagem por categoria
```

**3. Seleção e filtros**

```python
df["argila"]                              # uma coluna
df[["amostra", "argila", "ph"]]           # várias colunas
df[df["argila"] > 40]                     # linhas que atendem a uma condição
df[(df["cultura"] == "soja") & (df["ph"] < 5.5)]
```

**4. Tratamento de faltantes**

```python
df_limpo = df.dropna(subset=["ph"])       # remove linhas sem pH
print(len(df), "->", len(df_limpo))
```

Discutir: remover é uma decisão que reduz amostras, e substituir por uma média (imputação) pode esconder informação. A escolha depende do objetivo e deve ser registrada.

**5. Estatísticas por grupo**

```python
df_limpo.groupby("cultura")[["argila", "materia_organica", "ph"]].mean().round(2)
df_limpo[["argila", "materia_organica", "ph"]].corr().round(2)   # correlações
```

**6. Gráficos**

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 3, figsize=(14, 4))

ax[0].hist(df_limpo["argila"], bins=15, edgecolor="white")
ax[0].set(title="Distribuição de argila", xlabel="Argila (%)", ylabel="Frequência")

ax[1].scatter(df_limpo["argila"], df_limpo["materia_organica"])
ax[1].set(title="Argila × matéria orgânica", xlabel="Argila (%)", ylabel="MO (%)")

df_limpo.boxplot(column="ph", by="cultura", ax=ax[2])
ax[2].set(title="pH por cultura", xlabel="Cultura", ylabel="pH")
plt.suptitle("")

plt.tight_layout()
plt.savefig("graficos_solos.png", dpi=150)
plt.show()
```

**7. Salvar resultados**

```python
resumo = df_limpo.groupby("cultura")[["argila", "materia_organica", "ph"]].mean().round(2)
resumo.to_csv("resumo_por_cultura.csv")
```

### Exercícios (para entregar)

Responder, com tabela ou gráfico e uma frase de interpretação, a três perguntas:

1. Qual cultura tem, em média, o maior teor de argila?
2. Existe relação entre argila e matéria orgânica? Qual a correlação e o que ela significa?
3. Quantas amostras têm pH abaixo de 5,5, e como se distribuem entre as culturas?

**Dicas de resposta:** para (3), `df_limpo[df_limpo["ph"] < 5.5]["cultura"].value_counts()`. Lembrar que correlação não implica causalidade, e que os dados são fictícios.

### Problemas comuns

- **`FileNotFoundError`:** o notebook está em outra pasta; o caminho do arquivo é relativo à pasta do notebook. Conferir com `import os; os.getcwd()`.
- **Colunas com nomes diferentes (acentos, espaços):** conferir com `df.columns`.
- **Tipos errados:** números lidos como texto, por causa de vírgula decimal. Usar `pd.read_csv(..., decimal=",", sep=";")` em arquivos no formato brasileiro.

### Conexão com o projeto da disciplina

Mostrar como esse mesmo roteiro (ler, inspecionar, descrever, verificar faltantes e visualizar) é o que o notebook de análise exploratória faz com os espectros de solo no projeto de predição.

### Entregável

Notebook `analise_solos.ipynb` executado de cima para baixo, com as respostas às três perguntas e o arquivo `graficos_solos.png`.
