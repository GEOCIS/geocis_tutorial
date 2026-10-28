# Análise de Componentes Principais (PCA) aplicada aos espectros de solo

[← Capítulo 2](cap02_preprocessamento.md) · [Índice](README.md) · [Capítulo 4 →](cap04_clusterizacao_kmeans.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

## 1. Introdução

Um espectro Vis-NIR-SWIR de solo possui centenas de bandas (variáveis) fortemente correlacionadas entre si, pois bandas vizinhas medem praticamente a mesma informação. Essa alta dimensionalidade e colinearidade dificultam a visualização e a interpretação dos dados e prejudicam modelos que não lidam bem com muitas variáveis redundantes. A análise de componentes principais (PCA, *Principal Component Analysis*) resolve esse problema ao resumir a variação do conjunto em poucas variáveis novas, não correlacionadas entre si, chamadas componentes principais (PCs).

Neste projeto, o PCA tem três usos: (i) explorar a estrutura dos espectros e a separação entre grupos de solos, (ii) auxiliar na detecção de outliers e (iii) fornecer uma representação compacta dos espectros para a clusterização pelo método do cotovelo e para modelos como o Random Forest.

## 2. Fundamentos

O PCA encontra novos eixos, ortogonais entre si, ao longo dos quais a variância dos dados é máxima. O primeiro componente (PC1) é a direção de maior variância; o segundo (PC2) é a direção de maior variância restante e perpendicular ao primeiro, e assim por diante. Cada espectro passa a ser descrito por seus **escores** (coordenadas nos PCs) e cada PC é definido por seus **pesos** (*loadings*), que indicam a contribuição de cada banda espectral àquele componente.

Dois conceitos são centrais:

- **Variância explicada**: a fração da variância total dos dados capturada por cada PC. Os primeiros PCs costumam concentrar a maior parte da variância dos espectros de solo, já que a informação está distribuída de forma muito redundante entre as bandas.
- **Reconstrução**: com todos os PCs é possível recuperar exatamente os espectros originais; com apenas os primeiros, obtém-se uma versão simplificada, na qual boa parte do ruído foi descartada.

A biblioteca scikit-learn centraliza os dados (subtrai a média de cada banda) automaticamente antes de calcular os componentes. Como as bandas têm a mesma unidade e escala, não é necessário padronizá-las por banda, e a etapa anterior de SNV já reduziu os efeitos de espalhamento entre amostras.

## 3. Aplicação aos espectros pré-processados

O PCA é aplicado à matriz de espectros após o corte das bordas, a suavização e o SNV, de modo que os componentes reflitam a variação química e mineralógica e não ruído ou efeitos físicos:

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

pca = PCA(n_components=10).fit(X_snv)
scores = pca.transform(X_snv)

var_exp = pca.explained_variance_ratio_
print(var_exp.round(3))
print(var_exp.cumsum().round(3))
```

### 3.1 Variância explicada e número de componentes

O gráfico de variância explicada (*scree plot*), acompanhado da variância acumulada, ajuda a decidir quantos componentes reter:

```python
fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
ax[0].bar(range(1, 11), var_exp * 100)
ax[0].set_xlabel('Componente principal'); ax[0].set_ylabel('Variância explicada (%)')
ax[1].plot(range(1, 11), var_exp.cumsum() * 100, 'o-')
ax[1].set_xlabel('Nº de componentes'); ax[1].set_ylabel('Variância acumulada (%)')
plt.tight_layout(); plt.show()
```

Não há um critério único para o número de componentes. Os mais usados são: reter os PCs necessários para atingir um limiar de variância acumulada (por exemplo, 95% ou 99%); identificar o ponto em que a curva de variância deixa de cair de forma acentuada (critério do cotovelo no scree plot); ou escolher o número que maximiza o desempenho do modelo posterior em validação cruzada. Para espectros de solo, poucos componentes (da ordem de 3 a 10) costumam explicar mais de 95% da variância.

### 3.2 Gráfico de escores

A projeção das amostras nos dois primeiros componentes permite visualizar a estrutura do conjunto. Colorir os pontos pelo valor do atributo de interesse mostra se há relação entre a posição no espaço espectral e o atributo:

```python
plt.scatter(scores[:, 0], scores[:, 1], c=y, cmap='viridis', s=12)
plt.colorbar(label=COL_ALVO)
plt.xlabel(f'PC1 ({var_exp[0]*100:.1f}%)')
plt.ylabel(f'PC2 ({var_exp[1]*100:.1f}%)')
plt.show()
```

A interpretação do gráfico considera: (a) **gradientes de cor**, que indicam que o atributo está associado aos componentes e, portanto, tende a ser predizível a partir do espectro; (b) **agrupamentos separados**, que sugerem classes distintas de solo (por exemplo, texturas ou materiais de origem diferentes) e justificam a etapa de clusterização; e (c) **pontos isolados**, candidatos a outlier.

### 3.3 Pesos (loadings) e interpretação espectral

Os pesos mostram quais regiões do espectro mais contribuem para cada componente. Ao plotá-los contra o comprimento de onda, é possível relacionar os PCs a feições conhecidas:

```python
for i in range(3):
    plt.plot(wl, pca.components_[i], label=f'PC{i+1}')
plt.xlabel('Comprimento de onda (nm)'); plt.ylabel('Peso (loading)')
plt.legend(); plt.show()
```

Picos ou vales nas proximidades de 1400 e 1900 nm indicam influência da água e da hidroxila; na região de 2200 nm, de argilominerais como a caulinita; e no visível, da cor do solo, associada à matéria orgânica e aos óxidos de ferro (hematita e goethita). Essa leitura dá sentido físico aos componentes e aumenta a confiança de que os modelos exploram feições reais e não artefatos.

## 4. Detecção de outliers no espaço dos PCs

Além de explorar a estrutura dos dados, o PCA permite identificar espectros atípicos por dois indicadores complementares: a distância de Mahalanobis (ou T² de Hotelling), que mede o quão afastada do centro está a amostra dentro do espaço dos PCs retidos; e o resíduo de reconstrução (Q), que mede a parte do espectro que os PCs retidos não conseguem reproduzir.

```python
k = 5
pca_k = PCA(n_components=k).fit(X_snv)
sc = pca_k.transform(X_snv)

t2 = ((sc ** 2) / pca_k.explained_variance_).sum(axis=1)
X_rec = pca_k.inverse_transform(sc)
q = ((X_snv - X_rec) ** 2).sum(axis=1)

suspeitos = np.where((t2 > np.percentile(t2, 99)) | (q > np.percentile(q, 99)))[0]
print(len(suspeitos), 'amostras suspeitas')
```

Amostras com T² alto são extremas em relação ao padrão do conjunto; amostras com Q alto contêm feições que o modelo de componentes não explica, por exemplo contaminação ou erro de medição. Como já indicado no capítulo de pré-processamento, a remoção deve ser decidida pela análise dos espectros, nunca pelo valor do atributo-alvo, e deve ser registrada.

## 5. PCA como etapa para clusterização e modelagem

Os escores dos primeiros componentes funcionam como uma versão compacta e sem ruído dos espectros. Eles são usados em duas etapas seguintes do projeto:

- **Clusterização (k-means e método do cotovelo)**: agrupar as amostras nos primeiros PCs (por exemplo, os cinco primeiros) é mais estável do que agrupar centenas de bandas correlacionadas, e o resultado pode ser visualizado diretamente no gráfico de escores.
- **Random Forest**: o uso de um número moderado de componentes (por exemplo, 20) como variáveis preditoras reduz a dimensionalidade e o tempo de treinamento, mantendo a maior parte da informação espectral.

Para o PLSR, o PCA não é necessário, pois o método já constrói suas próprias variáveis latentes, otimizadas para predizer o atributo e não apenas para explicar a variância dos espectros.

## 6. Cuidados metodológicos

1. **Evitar vazamento de informação**: na etapa exploratória, o PCA pode ser ajustado ao conjunto todo. Porém, quando os escores forem usados como entrada de um modelo preditivo, o PCA deve ser ajustado apenas nos dados de calibração e depois aplicado (`transform`) aos dados de validação.
2. **Variância não é relevância**: os primeiros componentes capturam a maior variância dos espectros, que nem sempre é a mais relacionada ao atributo de interesse. Um atributo pode depender de componentes de menor variância, por isso o número de PCs deve ser definido também pelo desempenho do modelo.
3. **Sensibilidade a outliers**: poucos espectros extremos podem dominar os primeiros componentes. A identificação e o tratamento prévio de outliers tornam os PCs mais representativos do conjunto.
4. **Interpretação cautelosa**: os componentes são combinações lineares das bandas e não correspondem necessariamente a um constituinte químico específico do solo.

## 7. Síntese e encaminhamentos

O PCA permitiu resumir centenas de bandas espectrais correlacionadas em poucos componentes, avaliar a variância explicada, visualizar a estrutura do conjunto de amostras, interpretar as regiões espectrais mais influentes e apoiar a detecção de espectros atípicos. Os escores obtidos servem de base para a etapa seguinte, a clusterização pelo método do cotovelo, e para a modelagem de predição com PLSR e Random Forest.
