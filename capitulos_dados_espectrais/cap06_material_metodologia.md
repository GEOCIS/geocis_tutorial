# Material e metodologia

[← Capítulo 5](cap05_modelagem_plsr_rf.md) · [Índice](README.md) · [Capítulo 7 →](cap07_resultados.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

> Os trechos entre colchetes \[ \] devem ser preenchidos com as informações do banco de dados utilizado (número de amostras, regiões, atributos). A referência bibliográfica da BSSL também deve ser conferida antes da entrega.

## 1. Material: a Biblioteca Espectral de Solos do Brasil (BSSL)

### 1.1 Origem e características

Os dados utilizados provêm da Biblioteca Espectral de Solos do Brasil (BSSL, *Brazilian Soil Spectral Library*), uma base que reúne espectros de reflectância de amostras de solo de diferentes regiões do país, associados a análises convencionais de laboratório. A BSSL foi organizada por pesquisadores da ESALQ/USP e descrita por Demattê et al. (2019), sendo uma das principais fontes de dados para o desenvolvimento de modelos de predição de atributos do solo por espectroscopia no Brasil.

Os espectros cobrem as regiões do visível (Vis), infravermelho próximo (NIR) e infravermelho de ondas curtas (SWIR), em uma faixa de aproximadamente 350 a 2500 nm, medidos em laboratório sobre amostras secas e peneiradas. Neste trabalho foram utilizadas \[número\] amostras, provenientes de \[regiões/estados\], com \[número\] bandas espectrais por amostra.

### 1.2 Atributos do solo

Cada amostra possui espectro e valores de atributos determinados por métodos convencionais de laboratório. Os atributos considerados neste estudo foram:

- **Físicos**: \[por exemplo, teores de argila, silte e areia\];
- **Químicos**: \[por exemplo, matéria orgânica, CTC, pH, saturação por bases\].

Cada atributo foi modelado separadamente, usando as amostras que possuíam valor medido para ele, e o conjunto final de amostras variou conforme a disponibilidade de dados.

## 2. Ambiente computacional

Todo o processamento foi realizado em linguagem Python, no editor VS Code, com a extensão Jupyter, em arquivos de Jupyter Notebook (.ipynb) que combinam código, resultados e comentários. As principais bibliotecas foram:

- **pandas** e **numpy**: leitura, organização e operações sobre tabelas e matrizes espectrais;
- **scipy**: filtro de Savitzky-Golay;
- **scikit-learn**: PCA, k-means, PLSR, Random Forest, validação cruzada e métricas;
- **matplotlib**: gráficos.

## 3. Visão geral do fluxo metodológico

A metodologia seguiu as etapas abaixo, na ordem em que foram executadas:

1. **Leitura e análise exploratória**: estrutura do banco, estatística descritiva dos atributos, valores faltantes e espectros brutos.
2. **Pré-processamento espectral**: corte das bordas ruidosas, conversão em absorbância, suavização de Savitzky-Golay, primeira derivada, SNV e detecção de outliers.
3. **Redução de dimensionalidade**: PCA.
4. **Análise de agrupamentos**: método do cotovelo e k-means sobre os escores do PCA.
5. **Modelagem**: calibração de PLSR (variáveis latentes por validação cruzada) e Random Forest.
6. **Avaliação**: R², RMSE, RPD e RPIQ em amostras de validação independentes.
7. **Visualização e predição espectral**: gráficos dos resultados e aplicação dos modelos a novas amostras.

## 4. Leitura e análise exploratória

O banco foi importado com a biblioteca pandas, e as colunas foram separadas em espectrais (cujo nome corresponde ao comprimento de onda) e de atributos de laboratório. Foram calculadas estatísticas descritivas (contagem, média, desvio-padrão, mínimo, quartis e máximo) e a proporção de valores ausentes por variável, e a distribuição de cada atributo foi examinada por histogramas. Amostras sem valor medido do atributo modelado foram removidas. Os espectros brutos foram inspecionados visualmente para identificar feições de absorção, ruído nas extremidades, deslocamentos de linha de base e espectros anômalos.

## 5. Pré-processamento espectral

As bordas ruidosas do espectro (abaixo de 450 nm e acima de 2450 nm) foram removidas. A reflectância foi convertida em pseudo-absorbância, A = log10(1/R), e os espectros foram suavizados com o filtro de Savitzky-Golay (janela de 11 pontos, polinômio de grau 2). A primeira derivada, calculada pelo mesmo filtro, foi avaliada como alternativa para remover deslocamentos de linha de base, e o SNV foi aplicado para corrigir efeitos de espalhamento. Espectros atípicos foram identificados pelo desvio em relação ao espectro médio e pela distância de Mahalanobis no espaço dos componentes principais, e as amostras removidas foram registradas.

## 6. PCA e análise de agrupamentos

O PCA foi aplicado aos espectros pré-processados para avaliar a variância explicada, visualizar a estrutura das amostras (gráfico de escores) e interpretar os pesos dos componentes ao longo do espectro. Sobre os cinco primeiros componentes foi aplicado o k-means, com o número de grupos definido pelo método do cotovelo, complementado pelo coeficiente de silhueta. Os grupos foram caracterizados pelas estatísticas do atributo e pelos espectros médios.

## 7. Modelagem e avaliação

O conjunto de dados foi dividido em calibração (70%) e validação (30%). Dois modelos foram calibrados:

- **PLSR**: o número de variáveis latentes (de 1 a 20) foi escolhido pelo menor erro de validação cruzada com 10 partições (RMSECV), usando apenas os dados de calibração.
- **Random Forest**: treinado com 500 árvores sobre os 20 primeiros componentes principais, com o PCA ajustado apenas na calibração.

O desempenho nas amostras de validação foi avaliado por R², RMSE, RPD (desvio-padrão dividido pelo RMSE) e RPIQ (distância interquartílica dividida pelo RMSE), além do viés.

## 8. Visualização e predição espectral

### 8.1 Visualização dos resultados

Os resultados foram apresentados em gráficos que acompanham cada etapa: espectros brutos e pré-processados, variância explicada e escores do PCA, curva do cotovelo, gráficos de observado versus predito para cada modelo e coeficientes de regressão do PLSR em função do comprimento de onda. Essas visualizações permitem verificar a qualidade dos dados, a coerência das feições espectrais usadas pelos modelos e o comportamento dos erros ao longo da faixa de variação do atributo.

### 8.2 Predição para novas amostras

Para predizer o atributo em amostras novas, as mesmas etapas de pré-processamento aplicadas na calibração devem ser reproduzidas na mesma ordem e com os mesmos parâmetros. Por isso, o tratamento foi organizado em uma função e o modelo ajustado foi salvo em arquivo, para ser reutilizado sem recalibração:

```python
import joblib
from scipy.signal import savgol_filter

def preprocessa(X_raw, wl_raw, wl_min=450, wl_max=2450, janela=11, grau=2):
    mask = (wl_raw >= wl_min) & (wl_raw <= wl_max)
    X = X_raw[:, mask]
    absorb = np.log10(1 / np.clip(X, 1e-6, None))
    suav = savgol_filter(absorb, janela, grau, deriv=0, axis=1)
    return (suav - suav.mean(axis=1, keepdims=True)) / suav.std(axis=1, keepdims=True)

joblib.dump({'pls': pls, 'pca': pca_m, 'rf': rf, 'wl': wl_orig}, 'modelo_solo.joblib')
```

O objeto `wl_orig` corresponde ao vetor de comprimentos de onda original, antes do corte das bordas. Em seguida, as novas amostras são lidas, pré-processadas e submetidas ao modelo:

```python
modelo = joblib.load('modelo_solo.joblib')

novas = pd.read_csv('novas_amostras.csv')
X_novas = novas[cols_esp].values.astype(float)
X_novas_pp = preprocessa(X_novas, modelo['wl'])

pred_pls = modelo['pls'].predict(X_novas_pp).ravel()
pred_rf = modelo['rf'].predict(modelo['pca'].transform(X_novas_pp))

novas['pred_PLSR'] = pred_pls
novas['pred_RF'] = pred_rf
```

### 8.3 Verificação do domínio de aplicação

Um modelo só é confiável para amostras semelhantes às da calibração. Antes de aceitar uma predição, verifica-se se o espectro da nova amostra está dentro do domínio dos dados de treino, usando a distância de Mahalanobis (T²) no espaço dos componentes principais, com limite definido na calibração:

```python
pca_m = modelo['pca']
var = pca_m.explained_variance_

t2_cal = ((pca_m.transform(Xtr) ** 2) / var).sum(axis=1)
limite = np.percentile(t2_cal, 99)

t2_novas = ((pca_m.transform(X_novas_pp) ** 2) / var).sum(axis=1)
novas['dentro_dominio'] = t2_novas <= limite
print(novas['dentro_dominio'].value_counts())
```

Predições de amostras fora do domínio devem ser sinalizadas e interpretadas com cautela, ou excluídas, pois representam extrapolação do modelo. Também é recomendável comparar, em um gráfico de escores, a posição das novas amostras com a nuvem de calibração.

## 9. Considerações finais

A metodologia descrita combina etapas de preparação dos dados, exploração da estrutura espectral e modelagem supervisionada, e termina com a visualização dos resultados e a predição de novas amostras com verificação do domínio. Todos os parâmetros de pré-processamento e de modelagem foram definidos de forma explícita e reprodutível, e a avaliação final foi feita em amostras independentes, o que permite relatar o desempenho esperado dos modelos em condições reais de uso.

## Referência

DEMATTÊ, J. A. M. et al. The Brazilian Soil Spectral Library (BSSL): a general view, application and challenges. *Geoderma*, v. 354, 2019. \[conferir os dados completos da referência\]
