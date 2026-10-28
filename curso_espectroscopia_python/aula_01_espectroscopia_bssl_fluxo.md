# Aula 1: Espectroscopia de solos, BSSL e visão do fluxo

[Plano do curso](README.md) · [Aula 2 →](aula_02_leitura_exploratoria.md)

**Capítulo:** Material e metodologia. **Notebook:** nenhum (preparação do ambiente e estrutura do pipeline).

**Materiais:** pasta `pipeline_bssl`, ambiente virtual configurado, projetor.

**Objetivos:** compreender o princípio da espectroscopia Vis-NIR-SWIR aplicada ao solo e o fluxo de trabalho do projeto.

**Tópicos:**

- Por que espectros predizem atributos do solo: feições de absorção da água e hidroxila (1400 e 1900 nm), dos argilominerais (2200 nm) e da cor e matéria orgânica (visível).
- A BSSL: origem, faixa espectral, atributos de laboratório e limitações de uma biblioteca compilada de várias fontes.
- Visão das etapas: exploração, pré-processamento, PCA, clusterização, modelagem, avaliação e predição.
- Estrutura do pipeline: `config.py` (parâmetros), `utils.py` (funções) e cinco notebooks numerados, e a pasta `resultados/` com as saídas.

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Roteiro (120 min)

- 0 a 15 min: apresentação do curso, objetivos, dinâmica e combinados de avaliação.
- 15 a 50 min: princípio da espectroscopia Vis-NIR-SWIR aplicada ao solo.
- 50 a 70 min: a BSSL, a estrutura dos dados e o dado de referência.
- 70 a 95 min: visão geral do fluxo e estrutura do pipeline.
- 95 a 115 min: prática (gerar os dados, explorar a pasta e primeiro contato com os dados).
- 115 a 120 min: resumo e entregável.

## Conteúdo

### O que o espectro mede

Em um espectrorradiômetro, a luz atinge a amostra seca e peneirada, e o equipamento registra a fração refletida em cada comprimento de onda, a **reflectância**. A luz que atinge uma amostra de solo é refletida de forma difusa, e a fração refletida em cada comprimento de onda depende da composição. Na faixa **Vis-NIR-SWIR (cerca de 350 a 2500 nm)**:

- **Visível (cerca de 350 a 700 nm):** a cor do solo domina e está ligada aos óxidos de ferro (goethita e hematita) e à matéria orgânica, que escurece o solo e reduz a reflectância.
- **Infravermelho próximo (NIR, até cerca de 1100 nm) e de ondas curtas (SWIR, de cerca de 1100 a 2500 nm):** aparecem bandas de absorção causadas por sobretons e combinações de vibrações moleculares. Destacam-se as bandas da água e da hidroxila em torno de 1400 e 1900 nm e a banda dos argilominerais (como a caulinita) em torno de 2200 nm. Carbonatos aparecem perto de 2340 nm.

Por isso a argila, a matéria orgânica e os óxidos têm resposta espectral direta e tendem a ser bem preditos, enquanto atributos sem resposta espectral direta, como alguns nutrientes e o pH, costumam ser preditos por correlação indireta com esses constituintes e são mais difíceis.

### O que limita a predição

O espectro é muito rico, mas contém também ruído, efeitos de espalhamento (granulometria e compactação da amostra) e diferenças entre instrumentos. Além disso, o valor de referência vem de um método de laboratório que tem erro próprio, e esse erro limita o melhor desempenho possível.

### A ideia da calibração

Medem-se espectros e valores de laboratório de um conjunto de amostras e constrói-se um modelo estatístico que relaciona os dois. Depois, novas amostras só precisam do espectro. A vantagem é a rapidez e o baixo custo, e o limite é a qualidade do dado de referência e a representatividade das amostras de calibração.

### A BSSL (*Brazilian Soil Spectral Library*)

A Biblioteca Espectral de Solos do Brasil reúne espectros de solos de várias regiões do país, medidos em laboratório e associados a análises convencionais. Foi organizada por pesquisadores da ESALQ/USP e descrita por Demattê et al. (2019). A grande variabilidade de solos é uma vantagem, mas a origem diversa (laboratórios, métodos e épocas) gera heterogeneidade que precisa ser considerada nas conclusões. Detalhes como número de amostras e atributos disponíveis devem ser conferidos no banco usado pela turma.

### Estrutura de um banco espectral

Formato largo: cada linha é uma amostra e cada coluna é um atributo de laboratório ou uma banda espectral, cujo nome é o comprimento de onda.

### O fluxo do projeto

1. Leitura e análise exploratória (notebook 01).
2. Pré-processamento (notebook 02).
3. PCA e clusterização (notebook 03).
4. Modelagem e avaliação (notebook 04).
5. Visualização e predição de novas amostras (notebook 05).
6. Relatório (resultados e conclusão).

Os notebooks se comunicam por arquivos na pasta `resultados/`.

### Estrutura do pipeline

| Arquivo | Função |
| --- | --- |
| `config.py` | Todos os parâmetros (atributo-alvo, janela do filtro, k, proporção de validação etc.) |
| `utils.py` | Funções reutilizadas (pré-processamento, métricas, T² e Q, VIP) |
| `01_leitura_exploratoria.ipynb` | Leitura, estatísticas, faltantes e espectros brutos |
| `02_preprocessamento.ipynb` | Tratamentos espectrais e outliers |
| `03_pca_clusterizacao.ipynb` | PCA, cotovelo e k-means |
| `04_modelagem.ipynb` | PLSR, Random Forest e métricas |
| `05_visualizacao_predicao.ipynb` | Gráficos, interpretação e predição |

O ponto metodológico a destacar: **parâmetros em um único arquivo e funções reutilizáveis** tornam a análise reprodutível e fácil de repetir para outros atributos.

## Prática guiada

1. Abrir a pasta `pipeline_bssl` no VS Code e selecionar o interpretador do ambiente virtual.
2. **Gerar os dados de treino** pelo terminal (na pasta `pipeline_bssl`, com o ambiente ativo):

```bash
python gerar_dados_sinteticos.py
```

Isso cria `dados/bssl.csv` (900 amostras, colunas `id`, `argila`, `mo` e as bandas de 350 a 2500 nm) e `dados/novas_amostras.csv`.

3. **Conhecer o `config.py`.** Abrir o arquivo e localizar: o caminho do banco (`ARQUIVO`), o atributo-alvo (`COL_ALVO`), o corte espectral (`WL_MIN` e `WL_MAX`), o filtro de Savitzky-Golay (`SG_JANELA` e `SG_GRAU`), o número de grupos (`K`), a proporção de validação (`TEST_SIZE`) e os parâmetros dos modelos.
4. Abrir `dados/bssl.csv` e identificar as colunas de atributos e as colunas espectrais (nomes numéricos).
5. Abrir `utils.py` e listar as funções e o que cada uma faz, sem ler o código em detalhe.
6. **Primeiro contato com os dados** (em um notebook novo, fora do pipeline):

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("dados/bssl.csv")
print(df.shape)
print(df.iloc[:3, :6])

wl = np.array([float(c) for c in df.columns[3:]])   # nomes das colunas = comprimentos de onda
X = df.iloc[:, 3:].values

plt.figure(figsize=(8, 3.5))
plt.plot(wl, X[10])
for x, rotulo in [(1400, "água/OH"), (1900, "água"), (2200, "argilominerais")]:
    plt.axvline(x, ls="--", c="gray")
    plt.text(x, X[10].max(), rotulo, rotation=90, va="top", ha="right")
plt.xlabel("Comprimento de onda (nm)")
plt.ylabel("Reflectância")
plt.show()
```

## Exercícios

1. Desenhar, em uma folha, o fluxo do pipeline, indicando para cada notebook os arquivos de entrada e de saída em `resultados/`.
2. Explicar com suas palavras por que é esperado que a argila seja melhor predita do que o pH.
3. Identificar no gráfico dos dados sintéticos as feições em 1400, 1900 e 2200 nm.
4. Escolher o atributo que cada aluno vai modelar durante o curso (por exemplo, `argila` ou `mo`) e justificar, com base nas feições espectrais, se é esperado que ele seja bem predito.

<details>
<summary>Gabarito</summary>

**Exercício 1:** 01 lê `dados/bssl.csv` e salva `dados_brutos.npz` e `df_limpo.pkl`; 02 lê esses arquivos e salva `espectros_pp.npz` e `df_pp.pkl`; 03 lê os dois e atualiza `df_pp.pkl` com a coluna `cluster`, além de salvar `cluster_model.joblib`; 04 lê `espectros_pp.npz` e `df_pp.pkl` e salva `modelo_solo.joblib`, `metricas.csv` e `predicoes_validacao.csv`; 05 lê o modelo e as predições e salva `predicoes_novas_amostras.csv`. As figuras de todos os notebooks vão para `resultados/figuras/`.

</details>

## Perguntas de verificação

1. **Por que o espectro de um solo contém informação sobre a argila?** Porque os argilominerais têm feições de absorção características (por exemplo, perto de 2200 nm), e o teor de argila também altera a água retida e o espalhamento, que aparecem em outras regiões do espectro.
2. **Por que separar parâmetros (`config.py`) e funções (`utils.py`) em arquivos próprios?** Para repetir a análise com outro atributo ou banco alterando só o arquivo de parâmetros, evitar duplicação de código entre os notebooks e garantir reprodutibilidade.
3. **Por que o erro do método de laboratório limita o desempenho do modelo?** Porque o modelo aprende a reproduzir um valor de referência que já tem incerteza; nenhum modelo consegue ser mais preciso que o dado que o calibra.
4. **O que limita a melhor precisão possível de um modelo espectral?** O erro do método de laboratório que gerou os valores de referência, a variabilidade espectral não relacionada ao atributo e a representatividade da calibração.

## Entregável

Fluxograma do pipeline com as entradas e saídas de cada notebook, gráfico de espectro com as feições marcadas e texto de cinco linhas sobre o atributo que o aluno pretende modelar ao longo do curso, com a escolha justificada.
