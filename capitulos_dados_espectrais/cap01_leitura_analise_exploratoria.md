# Leitura e análise exploratória/descritiva de dados espectrais de solo

[Índice](README.md) · [Capítulo 2 →](cap02_preprocessamento.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

## 1. Introdução

A análise exploratória é a primeira etapa de qualquer fluxo de modelagem e a que mais influencia a qualidade dos resultados finais. Antes de aplicar suavização, PCA, clusterização ou modelos de regressão, é preciso conhecer a estrutura do banco: quantas amostras existem, quais atributos de laboratório estão disponíveis, quantas bandas espectrais compõem cada espectro, onde há dados ausentes e se os espectros brutos apresentam ruídos, deslocamentos de linha de base ou amostras anômalas.

Neste trabalho, os dados espectrais são provenientes da Biblioteca Espectral de Solos do Brasil (BSSL, *Brazilian Soil Spectral Library*), que reúne espectros de reflectância na faixa do visível, infravermelho próximo e infravermelho de ondas curtas (Vis-NIR-SWIR, aproximadamente 350 a 2500 nm), associados a análises físicas e químicas convencionais de laboratório. O ambiente de trabalho foi o VS Code com Jupyter Notebook, usando Python e as bibliotecas pandas, numpy, matplotlib e scipy.

## 2. Ambiente e importação das bibliotecas

O VS Code, com a extensão Jupyter, permite executar o código em células, visualizar gráficos inline e manter o documento reprodutível, pois código, resultados e comentários ficam no mesmo arquivo `.ipynb`. As bibliotecas usadas nesta etapa são:

- **pandas**: leitura, organização e estatística descritiva de tabelas;
- **numpy**: operações matriciais sobre os espectros;
- **matplotlib**: gráficos de histogramas e de espectros.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ARQUIVO = 'bssl.csv'      # caminho do banco
COL_ALVO = 'argila'       # atributo a predizer
PREFIXO = ''              # prefixo das colunas espectrais, se houver
```

## 3. Leitura dos dados

O banco espectral costuma ter uma estrutura em formato largo (*wide*): cada linha é uma amostra de solo e cada coluna é ou um atributo de laboratório (argila, areia, matéria orgânica, CTC, pH etc.) ou uma banda espectral cujo nome é o comprimento de onda. Por isso, a primeira tarefa é separar as colunas espectrais das colunas de atributos.

```python
df = pd.read_csv(ARQUIVO)

cols_esp = [c for c in df.columns
            if str(c).replace(PREFIXO, '').replace('.', '', 1).isdigit()]
cols_ref = [c for c in df.columns if c not in cols_esp]

print(df.shape, len(cols_esp), 'bandas')
```

O critério usado identifica como espectrais as colunas cujo nome é numérico. Essa separação deve ser conferida visualmente, com `df.head()` e `df.dtypes`, para garantir que nenhuma variável de laboratório foi classificada como banda e vice-versa. Em seguida, os comprimentos de onda são extraídos dos nomes das colunas e os espectros são organizados em uma matriz numpy `X` (amostras × bandas), enquanto o atributo de interesse fica no vetor `y`.

```python
wl = np.array([float(str(c).replace(PREFIXO, '')) for c in cols_esp])
X = df[cols_esp].values.astype(float)
```

## 4. Estatística descritiva dos atributos

A estatística descritiva resume a distribuição de cada atributo de solo e permite avaliar se o banco é adequado para a calibração de modelos. Com pandas, uma única linha produz contagem, média, desvio-padrão, mínimo, quartis e máximo:

```python
display(df[cols_ref].describe().T)
```

Pontos de atenção na interpretação:

- **Amplitude e desvio-padrão**: atributos com variação muito pequena são difíceis de predizer, pois há pouco sinal a ser explicado pelos espectros.
- **Média versus mediana**: diferenças grandes indicam assimetria. Atributos como matéria orgânica, CTC e teores de nutrientes costumam ter distribuição assimétrica à direita.
- **Valores mínimos e máximos**: servem para identificar valores impossíveis (por exemplo, argila acima de 100% ou pH fora da escala), que indicam erros de digitação ou de unidade.
- **Número de observações por atributo**: bancos compilados de diferentes fontes raramente têm todas as análises para todas as amostras.

A distribuição do atributo-alvo deve ser inspecionada também graficamente, por meio de histogramas:

```python
df[COL_ALVO].hist(bins=30)
plt.title(COL_ALVO)
plt.show()
```

O histograma mostra a forma da distribuição (normal, assimétrica, bimodal) e a presença de caudas longas. Distribuições muito assimétricas podem se beneficiar de transformação (logarítmica, por exemplo) antes da modelagem, e distribuições bimodais podem indicar mistura de grupos de solos distintos, o que será investigado adiante com a clusterização.

## 5. Valores faltantes

Valores ausentes são comuns em bibliotecas espectrais, já que nem todas as amostras passaram por todas as análises. O diagnóstico é feito calculando a proporção de dados ausentes por coluna:

```python
display(df[cols_ref].isna().mean().sort_values(ascending=False).head(10))
```

O tratamento depende da natureza da variável:

- **Atributo-alvo ausente**: a amostra não pode ser usada para calibrar ou validar o modelo daquele atributo e é removida (`df.dropna(subset=[COL_ALVO])`). Cada atributo é, portanto, modelado com o seu próprio subconjunto de amostras.
- **Bandas espectrais ausentes**: devem ser verificadas separadamente (`df[cols_esp].isna().sum().sum()`). Se poucas amostras forem afetadas, elas podem ser descartadas; se houver falhas em bandas específicas, pode-se interpolar ao longo do eixo espectral.
- **Covariáveis auxiliares**: só devem ser imputadas se forem realmente necessárias, e a imputação precisa ser registrada, para não introduzir informação artificial.

```python
df = df.dropna(subset=[COL_ALVO]).reset_index(drop=True)
X = df[cols_esp].values.astype(float)
y = df[COL_ALVO].values
```

É importante comunicar, ao final dessa etapa, o número de amostras antes e depois da limpeza, pois ele define o tamanho real do conjunto de calibração e de validação.

## 6. Inspeção dos espectros brutos

A visualização dos espectros é a forma mais direta de avaliar a qualidade do dado espectral. Plotam-se alguns espectros (por exemplo, os 50 primeiros) contra o comprimento de onda:

```python
plt.plot(wl, X[:50].T, lw=0.5)
plt.xlabel('Comprimento de onda (nm)')
plt.ylabel('Reflectância')
plt.title('Espectros brutos')
plt.show()
```

Na leitura do gráfico, observam-se:

1. **Forma geral**: a reflectância do solo tende a aumentar do visível para o infravermelho próximo, com variações de intensidade entre amostras associadas à cor, ao teor de matéria orgânica, à mineralogia (óxidos de ferro, argilominerais) e à umidade.
2. **Feições de absorção**: bandas próximas de 1400 e 1900 nm estão ligadas à água e à hidroxila, e a banda próxima de 2200 nm está associada a argilominerais, como a caulinita. Essas feições são a base física para a predição de atributos como argila e CTC.
3. **Ruído nas extremidades**: o início (região do visível) e o final (acima de 2400 nm) do espectro costumam ser mais ruidosos, justificando o corte dessas bordas na etapa de pré-processamento.
4. **Deslocamento de linha de base e espalhamento**: espectros paralelos, com a mesma forma mas em alturas diferentes, indicam efeitos físicos de granulometria e de compactação da amostra, que serão tratados com SNV ou derivadas.
5. **Espectros anômalos**: curvas que fogem do padrão do conjunto, com saltos, valores negativos ou formato incomum, são candidatas a outliers e devem ser investigadas antes de serem removidas.

Além dos espectros individuais, o espectro médio e a faixa de variação (média ± desvio-padrão) por banda ajudam a resumir o conjunto e a identificar em quais regiões do espectro a variabilidade entre amostras é maior.

```python
media = X.mean(axis=0)
dp = X.std(axis=0)
plt.plot(wl, media)
plt.fill_between(wl, media - dp, media + dp, alpha=0.3)
plt.xlabel('Comprimento de onda (nm)')
plt.ylabel('Reflectância')
plt.show()
```

## 7. Relação preliminar entre espectros e atributo-alvo

Uma verificação útil antes da modelagem é colorir os espectros pelo valor do atributo (por exemplo, classes de argila) ou calcular a correlação de cada banda com o atributo. Se há um padrão visível, como solos mais argilosos com menor reflectância geral e feições de argilomineral mais marcadas, há indício de que o modelo poderá encontrar relação entre espectro e atributo.

```python
corr = [np.corrcoef(X[:, i], y)[0, 1] for i in range(X.shape[1])]
plt.plot(wl, corr)
plt.xlabel('Comprimento de onda (nm)')
plt.ylabel('Correlação com ' + COL_ALVO)
plt.show()
```

## 8. Síntese e encaminhamentos

A análise exploratória permitiu conhecer a estrutura do banco, resumir a distribuição dos atributos de solo, quantificar e tratar os dados ausentes e avaliar visualmente a qualidade dos espectros brutos. Os principais achados orientam as etapas seguintes: o corte das bordas ruidosas, a conversão para absorbância, a suavização por Savitzky-Golay, a correção de espalhamento por SNV, a detecção de outliers e, depois, a redução de dimensionalidade com PCA, a clusterização pelo método do cotovelo e a modelagem com PLSR e Random Forest.

Com isso, garante-se que os modelos de predição sejam calibrados sobre dados limpos, bem compreendidos e documentados, o que é condição para resultados confiáveis e reprodutíveis.
