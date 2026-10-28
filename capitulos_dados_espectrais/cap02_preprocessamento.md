# Pré-processamento dos espectros: corte de bordas, absorbância, Savitzky-Golay, derivada, SNV e outliers

[← Capítulo 1](cap01_leitura_analise_exploratoria.md) · [Índice](README.md) · [Capítulo 3 →](cap03_pca.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

## 1. Introdução

Os espectros brutos de solo carregam, além da informação química e mineralógica de interesse, ruído instrumental, efeitos físicos de espalhamento (granulometria, compactação, rugosidade da amostra) e, eventualmente, espectros defeituosos. O pré-processamento reduz essas fontes de variação indesejada e realça as feições espectrais relacionadas aos atributos do solo, melhorando a estabilidade e a capacidade de predição de modelos como PLSR e Random Forest.

Neste capítulo, as etapas são aplicadas na seguinte ordem: (i) corte das bordas ruidosas, (ii) conversão de reflectância em absorbância, (iii) suavização e derivada pelo filtro de Savitzky-Golay, (iv) correção de espalhamento por SNV e (v) detecção de outliers. Não existe uma sequência única ideal: a escolha deve ser testada e justificada pelo desempenho na validação.

## 2. Corte das bordas ruidosas

Os sensores Vis-NIR-SWIR têm baixa razão sinal/ruído nas extremidades da faixa de medição, em geral no início do visível (próximo de 350 a 450 nm) e no final do infravermelho de ondas curtas (acima de aproximadamente 2400 a 2450 nm). Manter essas regiões introduz variância sem informação útil e pode prejudicar a suavização e as derivadas, que são sensíveis a ruído. Por isso, elas são removidas:

```python
mask = (wl >= 450) & (wl <= 2450)
wl, X = wl[mask], X[:, mask]
print(X.shape)
```

Os limites (450 e 2450 nm) são valores usuais e devem ser ajustados conforme o espectrorradiômetro e a inspeção dos espectros brutos feita na etapa exploratória.

## 3. Conversão de reflectância em absorbância

A reflectância (R) varia de forma não linear com a concentração dos constituintes. A transformação para pseudo-absorbância, A = log10(1/R), lineariza parcialmente essa relação e torna as feições de absorção mais evidentes, sendo um procedimento tradicional em espectroscopia de solos:

```python
Xabs = np.log10(1 / np.clip(X, 1e-6, None))
```

O `np.clip` evita divisão por zero ou logaritmo de valores não positivos, que podem ocorrer em bandas com ruído. Se muitas amostras forem afetadas, isso indica um problema na medição, que deve ser investigado, e não apenas mascarado.

## 4. Suavização de Savitzky-Golay

O filtro de Savitzky-Golay ajusta, em uma janela móvel de pontos vizinhos, um polinômio por mínimos quadrados e substitui o valor central pelo valor ajustado. Diferentemente de uma média móvel simples, ele preserva a forma e a largura das feições de absorção, o que o torna adequado para espectros. Dois parâmetros controlam o resultado:

- **Tamanho da janela**: janelas pequenas removem pouco ruído; janelas grandes suavizam demais e podem distorcer feições estreitas. O tamanho deve ser ímpar.
- **Grau do polinômio**: graus baixos (2 ou 3) suavizam mais; graus altos acompanham mais o sinal original, inclusive o ruído.

```python
from scipy.signal import savgol_filter

X_suav = savgol_filter(Xabs, window_length=11, polyorder=2, deriv=0, axis=1)
```

A combinação mostrada (janela de 11 pontos, polinômio de grau 2) é um ponto de partida e deve ser comparada a outras configurações por validação cruzada.

## 5. Primeira derivada

A derivada espectral remove deslocamentos de linha de base (efeito aditivo) e realça feições sobrepostas, como as de óxidos de ferro e argilominerais. A primeira derivada elimina o deslocamento constante, e a segunda também elimina a inclinação linear da linha de base. O filtro de Savitzky-Golay calcula a derivada e suaviza ao mesmo tempo, o que é preferível à diferença simples entre bandas vizinhas, que amplifica o ruído:

```python
X_d1 = savgol_filter(Xabs, window_length=11, polyorder=2, deriv=1, axis=1)
```

Como a derivada aumenta a influência do ruído, a escolha da janela é mais crítica do que na suavização simples. Em contrapartida, o resultado costuma melhorar a predição de atributos como argila, CTC e matéria orgânica quando há forte variação de linha de base entre amostras.

## 6. Correção de espalhamento por SNV

O SNV (*Standard Normal Variate*) trata cada espectro individualmente: subtrai a sua média e divide pelo seu desvio-padrão. Com isso, reduz os efeitos multiplicativos e aditivos de espalhamento causados por diferenças de granulometria e de empacotamento da amostra:

```python
snv = lambda A: (A - A.mean(axis=1, keepdims=True)) / A.std(axis=1, keepdims=True)
X_snv = snv(X_suav)
```

Como o SNV usa apenas estatísticas do próprio espectro, ele não depende do conjunto de dados e pode ser aplicado sem risco de vazamento de informação entre calibração e validação. O mesmo vale para o filtro de Savitzky-Golay. Já técnicas que usam a média do conjunto, como o MSC, devem ter os parâmetros estimados apenas na calibração e depois aplicados à validação.

A comparação visual dos espectros em cada etapa ajuda a verificar o efeito do tratamento:

```python
fig, ax = plt.subplots(1, 4, figsize=(16, 3))
for a, M, t in zip(ax, [X, Xabs, X_suav, X_snv],
                   ['Reflectância', 'Absorbância', 'Suavizado (SG)', 'SNV']):
    a.plot(wl, M[:30].T, lw=0.5)
    a.set_title(t)
plt.tight_layout()
plt.show()
```

Após o SNV, os espectros devem apresentar menor dispersão vertical entre amostras, ficando mais parecidos em intensidade e diferindo principalmente pela forma das feições.

## 7. Detecção de outliers

Outliers espectrais podem decorrer de falhas de medição, contaminação, amostras de natureza muito distinta (por exemplo, solos orgânicos em um conjunto de solos minerais) ou erros de registro. Eles distorcem os modelos, especialmente os lineares. Dois critérios complementares são usados.

**a) Desvio do espectro médio (z-score).** Calcula-se a média de cada espectro e verifica-se quão distante ela está da média do conjunto, em unidades de desvio-padrão. Como o SNV centraliza cada espectro em média zero, esse critério deve ser aplicado antes do SNV, sobre a absorbância suavizada:

```python
m = X_suav.mean(axis=1)
z = np.abs((m - m.mean()) / m.std())
print('Possíveis outliers (z > 3):', (z > 3).sum())
```

**b) Distância de Mahalanobis no espaço dos componentes principais.** Projeta-se o conjunto em poucos componentes principais e mede-se a distância de cada amostra ao centro da nuvem, considerando a variância de cada componente. Amostras com distância muito acima do restante são candidatas a outlier:

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=5).fit(X_snv)
scores = pca.transform(X_snv)
d2 = ((scores ** 2) / pca.explained_variance_).sum(axis=1)   # Mahalanobis ao quadrado
limite = np.percentile(d2, 99)
outliers = np.where(d2 > limite)[0]
print(len(outliers), 'amostras acima do percentil 99')
```

O limite (percentil 99, ou um ponto de corte da distribuição qui-quadrado) é uma escolha do analista. Duas recomendações importantes: a remoção deve ser baseada nos espectros e não no valor do atributo-alvo, para não enviesar a avaliação do modelo; e cada amostra removida deve ser inspecionada e registrada, relatando-se o número de amostras antes e depois da limpeza.

```python
mantem = np.setdiff1d(np.arange(X_snv.shape[0]), outliers)
X_final, y_final = X_snv[mantem], y[mantem]
```

## 8. Síntese e encaminhamentos

O pré-processamento transformou os espectros brutos em dados mais adequados à modelagem: bordas ruidosas foram removidas, a reflectância foi convertida em absorbância, o ruído foi atenuado pelo filtro de Savitzky-Golay, os efeitos de espalhamento foram corrigidos pelo SNV e as amostras atípicas foram identificadas. A primeira derivada fica como alternativa ao SNV para remover a linha de base, e a melhor combinação de tratamentos deve ser escolhida comparando o desempenho dos modelos em validação cruzada.

Com os espectros tratados, o próximo passo é explorar a estrutura dos dados com a análise de componentes principais (PCA) e a clusterização pelo método do cotovelo, antes de calibrar os modelos PLSR e Random Forest.
