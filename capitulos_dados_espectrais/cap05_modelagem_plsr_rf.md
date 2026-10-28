# Modelagem preditiva: PLSR e Random Forest

[← Capítulo 4](cap04_clusterizacao_kmeans.md) · [Índice](README.md) · [Capítulo 6 →](cap06_material_metodologia.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

## 1. Introdução

O objetivo final do projeto é predizer atributos físicos e químicos do solo (como argila, areia, matéria orgânica, CTC e pH) a partir dos espectros, substituindo ou complementando análises de laboratório caras e demoradas. Para isso, são calibrados e comparados dois modelos: a regressão por mínimos quadrados parciais (PLSR), método clássico e de referência em quimiometria, e o Random Forest, algoritmo de aprendizado de máquina não linear baseado em conjuntos de árvores de decisão. O desempenho é avaliado em amostras independentes por R², RMSE, RPD e RPIQ.

## 2. Divisão dos dados em calibração e validação

O conjunto é dividido em calibração (treino), usado para ajustar o modelo e escolher seus parâmetros, e validação (teste), reservado para a avaliação final em amostras que o modelo nunca viu. Neste projeto foi adotada a proporção de 70% para calibração e 30% para validação:

```python
import numpy as np
from sklearn.model_selection import train_test_split

Xtr, Xte, ytr, yte = train_test_split(X_snv, y, test_size=0.3, random_state=42)
print(Xtr.shape, Xte.shape)
```

A divisão aleatória é simples e adequada como ponto de partida. Para garantir que todos os tipos de solo estejam representados nos dois conjuntos, é possível estratificar a divisão pelos grupos obtidos na clusterização ou usar algoritmos de seleção, como Kennard-Stone. Em qualquer caso, a validação não pode ser usada para ajustar parâmetros: isso inflaria o desempenho aparente e comprometeria a avaliação.

## 3. Regressão por mínimos quadrados parciais (PLSR)

### 3.1 Fundamentos

Os espectros têm muito mais variáveis (bandas) do que amostras em muitos casos, e as bandas são altamente colineares, o que inviabiliza a regressão linear múltipla comum. O PLSR contorna esse problema projetando os espectros em um número reduzido de **variáveis latentes** (LVs), construídas de modo a maximizar a covariância entre os espectros e o atributo a predizer. Diferentemente do PCA, que busca apenas explicar a variância dos espectros, o PLSR já orienta a redução de dimensionalidade para a predição do atributo.

O principal parâmetro do modelo é o número de variáveis latentes. Poucas LVs levam a um modelo simples demais (subajuste); muitas incorporam ruído e levam a um modelo que se ajusta bem à calibração mas generaliza mal (sobreajuste).

### 3.2 Escolha do número de variáveis latentes por validação cruzada

O número de LVs é definido por validação cruzada (k-fold, com k = 10) apenas nos dados de calibração. Para cada número de LVs de 1 a 20, calcula-se o erro de validação cruzada (RMSECV), e escolhe-se o valor que o minimiza:

```python
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import mean_squared_error

max_lv = 20
rmsecv = []
for n in range(1, max_lv + 1):
    pred = cross_val_predict(PLSRegression(n_components=n), Xtr, ytr, cv=10).ravel()
    rmsecv.append(np.sqrt(mean_squared_error(ytr, pred)))

nlv = int(np.argmin(rmsecv)) + 1

plt.plot(range(1, max_lv + 1), rmsecv, 'o-')
plt.axvline(nlv, color='red', linestyle='--')
plt.xlabel('Variáveis latentes'); plt.ylabel('RMSECV')
plt.show()
```

Quando a curva do RMSECV é muito plana próximo ao mínimo, vale preferir o modelo mais simples cujo erro esteja dentro de um erro-padrão do mínimo (regra de um erro-padrão), pois ele tende a generalizar melhor e é mais fácil de interpretar. Com o número de LVs definido, o modelo final é ajustado em toda a calibração:

```python
pls = PLSRegression(n_components=nlv).fit(Xtr, ytr)
y_pls = pls.predict(Xte).ravel()
```

## 4. Random Forest

### 4.1 Fundamentos

O Random Forest constrói centenas de árvores de decisão, cada uma treinada com uma amostra aleatória (com reposição) dos dados e, a cada divisão, considerando apenas um subconjunto aleatório das variáveis. A predição final é a média das predições das árvores. Essa combinação reduz a variância e o risco de sobreajuste de uma árvore isolada, captura relações não lineares e interações entre variáveis e dispensa suposições sobre a distribuição dos dados.

Como o espectro tem centenas de bandas colineares, é comum alimentar o Random Forest com os escores dos primeiros componentes principais, o que reduz a dimensionalidade e o tempo de treinamento. Para evitar vazamento de informação, o PCA é ajustado apenas nos dados de calibração e depois aplicado à validação:

```python
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor

pca_m = PCA(n_components=20).fit(Xtr)
Ztr, Zte = pca_m.transform(Xtr), pca_m.transform(Xte)

rf = RandomForestRegressor(n_estimators=500, random_state=0, n_jobs=-1).fit(Ztr, ytr)
y_rf = rf.predict(Zte)
```

### 4.2 Hiperparâmetros

Os hiperparâmetros mais influentes são o número de árvores (`n_estimators`), o número de variáveis consideradas em cada divisão (`max_features`) e o tamanho mínimo das folhas (`min_samples_leaf`). Embora os valores padrão costumem ter bom desempenho, o ajuste por busca em grade ou aleatória, com validação cruzada na calibração, pode melhorar o resultado. O número de componentes principais de entrada também pode ser tratado como hiperparâmetro.

## 5. Métricas de avaliação

O desempenho é avaliado comparando os valores observados (laboratório) com os preditos nas amostras de validação. Quatro métricas são usadas, pois cada uma informa um aspecto diferente.

- **R² (coeficiente de determinação)**: proporção da variância do atributo explicada pelo modelo. Quanto mais próximo de 1, melhor. Depende da amplitude dos dados e, isoladamente, pode ser enganoso.
- **RMSE (raiz do erro quadrático médio)**: erro típico da predição, na mesma unidade do atributo (por exemplo, g/kg ou %). Quanto menor, melhor, e a interpretação depende da escala do atributo.
- **RPD (*Ratio of Performance to Deviation*)**: razão entre o desvio-padrão dos valores observados e o RMSE. Indica quantas vezes o erro do modelo é menor que a variabilidade natural do atributo. Valores próximos de 1 significam que o modelo é pouco melhor que predizer a média.
- **RPIQ (*Ratio of Performance to Interquartile Distance*)**: razão entre a distância interquartílica (Q3 - Q1) e o RMSE. É mais adequado que o RPD para atributos com distribuição assimétrica, comuns em solos, pois o desvio-padrão é muito influenciado por valores extremos.

```python
from sklearn.metrics import r2_score

def avalia(y_obs, y_pred):
    rmse = np.sqrt(mean_squared_error(y_obs, y_pred))
    iqr = np.subtract(*np.percentile(y_obs, [75, 25]))
    return {
        'R2': r2_score(y_obs, y_pred),
        'RMSE': rmse,
        'RPD': y_obs.std() / rmse,
        'RPIQ': iqr / rmse,
        'Viés': np.mean(y_pred - y_obs),
    }

import pandas as pd
resultados = pd.DataFrame({
    'PLSR': avalia(yte, y_pls),
    'Random Forest': avalia(yte, y_rf),
}).T
print(resultados.round(3))
```

A função inclui também o viés (erro médio), que indica se o modelo tende a superestimar ou subestimar o atributo. Como referência para interpretar o RPD, é comum a classificação de Chang et al. (2001): valores abaixo de 1,4 indicam modelos pouco confiáveis; entre 1,4 e 2,0, modelos razoáveis, adequados para triagem e estimativas aproximadas; e acima de 2,0, modelos bons a excelentes. Essas faixas são orientações e não regras rígidas, pois a exigência depende do atributo e da aplicação. Convém também apresentar as métricas de calibração e de validação cruzada (R²cv e RMSECV), para que a diferença entre elas e o resultado na validação evidencie eventual sobreajuste.

## 6. Comparação gráfica dos modelos

Além das métricas numéricas, o gráfico de valores observados contra preditos mostra onde o modelo erra. Os pontos devem se distribuir próximos à linha 1:1:

```python
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for a, pred, nome in zip(ax, [y_pls, y_rf], ['PLSR', 'Random Forest']):
    lim = [min(yte.min(), pred.min()), max(yte.max(), pred.max())]
    a.scatter(yte, pred, s=10)
    a.plot(lim, lim, 'r--')
    a.set_xlabel('Observado'); a.set_ylabel('Predito'); a.set_title(nome)
plt.tight_layout(); plt.show()
```

Na análise do gráfico, observam-se: (a) pontos afastados da linha 1:1 em regiões específicas, que indicam perda de desempenho em certas faixas do atributo; (b) tendência dos modelos a "comprimir" os valores, subestimando os extremos altos e superestimando os baixos, comportamento comum do Random Forest; e (c) dispersão crescente com o valor do atributo, que sugere a necessidade de transformação (por exemplo, logarítmica) da variável resposta.

## 7. Interpretação dos modelos

Para o PLSR, os coeficientes de regressão em função do comprimento de onda indicam as regiões espectrais que mais contribuem para a predição, e é possível verificar se coincidem com feições conhecidas (água e hidroxila em 1400 e 1900 nm; argilominerais em 2200 nm):

```python
coef = pls.coef_.ravel()
plt.plot(wl, coef)
plt.xlabel('Comprimento de onda (nm)'); plt.ylabel('Coeficiente de regressão')
plt.show()
```

Para o Random Forest, a importância dos componentes (`rf.feature_importances_`) mostra quais PCs são mais usados nas divisões das árvores. Como cada PC é uma combinação das bandas, a interpretação espectral pode ser feita associando a importância dos PCs aos seus pesos, conforme visto no capítulo de PCA.

## 8. Cuidados metodológicos

1. **Nenhuma decisão com base na validação**: a escolha do número de LVs, dos hiperparâmetros e do pré-processamento deve usar apenas validação cruzada na calibração. A validação é usada uma única vez, para relatar o desempenho final.
2. **Vazamento de informação**: o PCA, e qualquer outra transformação que dependa do conjunto de dados, deve ser ajustado somente na calibração.
3. **Representatividade**: o modelo só é confiável para amostras semelhantes às da calibração. Novas amostras devem ter espectros dentro do domínio dos dados de treino, o que pode ser verificado pelos indicadores T² e Q do PCA.
4. **Variabilidade da divisão**: o resultado de uma única divisão aleatória pode variar. Repetir o procedimento com diferentes sementes, ou usar validação cruzada aninhada, fornece uma estimativa mais robusta, com média e desvio das métricas.
5. **Sem modelo universalmente melhor**: o PLSR costuma ser competitivo e mais interpretável, sobretudo para atributos com forte relação linear com as feições espectrais (como argila e matéria orgânica). O Random Forest tende a se destacar quando há relações não lineares ou grande heterogeneidade entre amostras. A comparação deve ser feita para cada atributo.

## 9. Síntese e conclusões

Foram calibrados e avaliados dois modelos de predição dos atributos do solo a partir de espectros Vis-NIR-SWIR. O PLSR teve o número de variáveis latentes escolhido por validação cruzada, e o Random Forest foi treinado sobre os escores do PCA. O desempenho em amostras independentes foi medido por R², RMSE, RPD e RPIQ, complementado por gráficos de observado versus predito e pela interpretação espectral dos modelos. A comparação dessas métricas, atributo por atributo, indica qual abordagem é mais adequada em cada caso e se a precisão alcançada atende ao uso pretendido, seja triagem de amostras, mapeamento ou apoio à análise de rotina em laboratório.
