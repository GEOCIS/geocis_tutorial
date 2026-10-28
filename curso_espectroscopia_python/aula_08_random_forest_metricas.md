# Aula 8: Random Forest e métricas de avaliação

[← Aula 7](aula_07_plsr_validacao_cruzada.md) · [Plano do curso](README.md) · [Aula 9 →](aula_09_visualizacao_predicao.md)

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Resumo do plano

**Objetivos:** treinar um modelo não linear e avaliar os dois modelos com as métricas corretas.

**Conteúdo:**

- Random Forest: árvores, amostragem aleatória e média das predições; uso de escores do PCA como entrada e `Pipeline` para evitar vazamento.
- Hiperparâmetros principais e busca aleatória (`RandomizedSearchCV`).
- Métricas: R², RMSE, RPD, RPIQ e viés. Interpretação do RPD segundo a classificação de Chang et al. (2001).
- Comparação entre calibração, validação cruzada e validação para detectar sobreajuste.

**Prática:** notebook 04 (seções 4 a 6). Comparar PLSR e Random Forest, e explicar a diferença entre as métricas de calibração e de validação.

**Entregável:** tabela de métricas (como a do capítulo de resultados) e um parágrafo comparando os modelos.

**Perguntas de verificação:** quando o RPIQ é mais indicado que o RPD? Um R² alto na calibração garante um bom modelo?

## Material de aula: versão 1

**Capítulo:** Modelagem preditiva. **Notebook:** `04_modelagem.ipynb` (seções 4 a 6).

**Materiais:** notebook 04.

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 35 min: Random Forest, `Pipeline` e busca de hiperparâmetros.
- 35 a 70 min: métricas de avaliação (cálculo manual e interpretação).
- 70 a 100 min: execução das seções 4 a 6 e comparação dos modelos.
- 100 a 120 min: experimentos e entregável.

#### Conteúdo

**Random Forest.** Treina centenas de árvores de decisão, cada uma com uma amostra aleatória dos dados (com reposição) e, a cada divisão, um subconjunto aleatório das variáveis. A predição final é a média das árvores. Captura relações não lineares, é robusto a ruído e exige pouca preparação, mas não extrapola além da faixa dos dados de treino.

**Escores do PCA como entrada e `Pipeline`.** Em vez de dar centenas de bandas colineares à floresta, o notebook usa os escores de um PCA ajustado dentro de um `Pipeline` (PCA seguido do Random Forest). Assim, em qualquer validação cruzada ou predição, o PCA é ajustado apenas nos dados de treino, evitando vazamento de informação.

**Hiperparâmetros e busca.** Com `BUSCA_RF = True`, a busca aleatória (`RandomizedSearchCV`, `N_ITER_BUSCA` combinações, validação cruzada de 5 partições na calibração) testa o número de componentes do PCA, `max_features` e `min_samples_leaf`. Com `False`, usa `N_PCS_RF` componentes e parâmetros padrão.

**Métricas de avaliação** (função `utils.avalia`):

- **R²:** proporção da variância explicada. Depende da amplitude dos dados.
- **RMSE:** erro típico, na unidade do atributo. Quanto menor, melhor.
- **RPD:** desvio-padrão dos valores observados dividido pelo RMSE. Valores próximos de 1 indicam que o modelo é pouco melhor que predizer a média. Referência de Chang et al. (2001): abaixo de 1,4, pouco confiável; de 1,4 a 2,0, razoável; acima de 2,0, bom.
- **RPIQ:** distância interquartílica (Q3 - Q1) dividida pelo RMSE. Mais adequado para atributos assimétricos.
- **Viés:** erro médio (predito menos observado). Mostra tendência de superestimar ou subestimar.

**Calibração, validação cruzada e validação.** A diferença entre os erros de calibração e de validação indica sobreajuste. O Random Forest costuma ter erro muito baixo na calibração (cada árvore vê boa parte dos dados) e maior na validação, e por isso a calibração não deve ser usada para comparar modelos.

**Referência com os dados sintéticos** (valores arredondados; a numeração e os números podem variar um pouco):

| Modelo | Conjunto | R² | RMSE | RPD | RPIQ | Viés |
| --- | --- | --- | --- | --- | --- | --- |
| PLSR | Calibração | 0,976 | 2,96 | 6,48 | 9,42 | 0,00 |
| PLSR | Validação cruzada | 0,976 | 2,98 | 6,43 | 9,35 | 0,00 |
| PLSR | Validação | 0,980 | 2,91 | 7,06 | 7,65 | 0,26 |
| Random Forest | Calibração | 0,992 | 1,75 | 10,96 | 15,93 | 0,01 |
| Random Forest | Validação | 0,981 | 2,84 | 7,22 | 7,83 | -0,01 |

Os dois modelos têm desempenho muito parecido na validação, e o Random Forest tem um RMSE de calibração bem menor, mostrando o otimismo da calibração. Os valores de RPD acima de 7 só ocorrem porque os dados sintéticos são simples.

#### Prática guiada

1. **Cálculo manual das métricas** (sem computador, depois conferindo no Python). Com valores observados `[10, 20, 30, 40]` e preditos `[12, 18, 33, 38]`, calcular erro, RMSE, R², RPD, RPIQ e viés.

```python
import numpy as np
import utils

obs = np.array([10, 20, 30, 40])
prd = np.array([12, 18, 33, 38])
print(utils.avalia(obs, prd))
```

2. Executar as seções 4 a 6 do notebook 04. Observar o resultado da busca de hiperparâmetros e a tabela de métricas.
3. Comparar PLSR e Random Forest na validação, usando RMSE, RPD e RPIQ, e comentar a diferença entre calibração e validação em cada modelo.

#### Exercícios

1. Conferir o cálculo manual do item 1 com `utils.avalia`.
2. Definir `BUSCA_RF = False` e `N_PCS_RF` igual a 5, 20 e 40, comparando o RMSE de validação.
3. Alterar `N_ARVORES` para 50, 200 e 500 e observar o efeito sobre o desempenho e o tempo.
4. Explicar por que o RMSE do Random Forest na calibração é muito menor que na validação.
5. Decidir, com base nas métricas, qual modelo seria recomendado para triagem de amostras e justificar (considere RPD, RPIQ, viés e simplicidade).

**Gabarito comentado:**

- (1) Erros: 2, -2, 3, -2; soma dos quadrados 21; RMSE = raiz(21/4) = 2,29. R² = 1 - 21/500 = 0,958 (a soma dos quadrados total é 500, com média 25). Desvio-padrão dos observados (sem correção) = 11,18, logo RPD = 11,18/2,29 = 4,88. Quartis 17,5 e 32,5, IQR = 15, logo RPIQ = 15/2,29 = 6,55. Viés = (2 - 2 + 3 - 2)/4 = 0,25.
- (2) Poucos componentes podem perder informação, e muitos acrescentam ruído e aumentam o tempo. O desempenho tende a se estabilizar a partir de certo número.
- (3) Mais árvores estabilizam a predição, com ganhos decrescentes e tempo crescente.
- (4) Cada árvore é treinada com amostras que incluem a própria amostra de calibração; na validação, o modelo vê amostras inéditas.
- (5) Com desempenhos semelhantes, a escolha pode favorecer o PLSR por ser mais simples e interpretável, ou o Random Forest se houver ganho claro em dados reais. O importante é argumentar com as métricas de validação.

#### Problemas comuns

- **Comparar modelos pelas métricas de calibração:** use sempre a validação (ou a validação cruzada).
- **Interpretar R² isolado:** olhar também RMSE, RPD e RPIQ.
- **Busca de hiperparâmetros muito lenta:** reduzir `N_ITER_BUSCA` e `N_ARVORES` durante os testes.

#### Entregável

Tabela de métricas dos dois modelos (calibração e validação), cálculo manual das métricas do exercício 1 e um parágrafo recomendando um modelo, com base nas métricas de validação.

## Material de aula: versão 2

**Capítulo:** Modelagem preditiva (Random Forest e métricas). **Notebook:** `04_modelagem.ipynb` (seções 4 a 6).

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: Random Forest e métricas (R², RMSE, RPD, RPIQ e viés).
- 40 a 80 min: execução comentada das seções 4 a 6 do notebook 04.
- 80 a 110 min: exercícios (cálculo manual das métricas e vazamento de informação).
- 110 a 120 min: resumo e entregável.

#### Conteúdo

**Random Forest.** Conjunto de árvores de decisão, cada uma treinada com uma amostra aleatória (com reposição) dos dados e, a cada divisão, com um subconjunto aleatório de variáveis. A previsão é a média das árvores. Captura relações não lineares, é robusto a ruído e dispensa suposições sobre a distribuição dos dados.

**Random Forest sobre escores de PCA.** No notebook, o PCA e o Random Forest formam um `Pipeline`. O PCA é ajustado só nos dados de treino em cada etapa (inclusive dentro da validação cruzada da busca de hiperparâmetros), o que evita vazamento. Com `BUSCA_RF = True`, uma busca aleatória testa combinações de número de componentes (10, 20 ou 30), `max_features` e `min_samples_leaf`, com validação cruzada na calibração.

**Métricas.** Para os valores observados `y` e preditos `ŷ`:

| Métrica | O que mede | Como interpretar |
| --- | --- | --- |
| R² | Fração da variância explicada | Próximo de 1 é melhor; depende da amplitude dos dados |
| RMSE | Erro típico, na unidade do atributo | Menor é melhor |
| RPD | Desvio-padrão de `y` dividido pelo RMSE | Maior é melhor; perto de 1 é pouco melhor que a média |
| RPIQ | Distância interquartílica de `y` dividida pelo RMSE | Mais adequado para distribuições assimétricas |
| Viés | Média de `ŷ - y` | Perto de 0 indica ausência de tendência |

Orientação de Chang et al. (2001) para o RPD: abaixo de 1,4, modelo pouco confiável; de 1,4 a 2,0, razoável; acima de 2,0, bom a excelente. São referências, e não regras rígidas: a exigência depende do atributo e do uso pretendido.

**Calibração × validação.** Um desempenho muito melhor na calibração do que na validação indica sobreajuste. Em florestas aleatórias, o erro de calibração é quase sempre otimista, pois cada amostra participa do treino de muitas árvores. Por isso, a avaliação decisiva é a da validação.

#### Prática guiada: notebook 04, seções 4 a 6

1. **Random Forest.** Executar a busca de hiperparâmetros (pode levar alguns minutos) e ler os melhores parâmetros e o RMSECV impressos.
2. **Tabela de métricas.** Interpretar as linhas de PLSR (calibração, validação cruzada e validação) e de Random Forest (calibração e validação). Comparar o PLSR e o Random Forest na validação.
3. **Domínio de aplicação e salvamento.** Entender o PCA do domínio (`N_PCS_DOMINIO`) e os limites de T² e Q guardados. Conferir os arquivos `modelo_solo.joblib`, `metricas.csv` e `predicoes_validacao.csv`.

#### Exercícios

1. **Cálculo manual das métricas.** Com os valores abaixo, calcular RMSE, RPD, RPIQ, R² e viés à mão e depois conferir com `utils.avalia`:

```python
y_obs  = np.array([10, 20, 30, 40])
y_pred = np.array([12, 18, 33, 37])
print(utils.avalia(y_obs, y_pred))
```

2. **Vazamento de informação.** Comparar a escolha do número de LVs pela validação cruzada na calibração com a escolha pelo menor erro na própria validação:

```python
erros_val = []
for n in range(1, cfg.MAX_LV + 1):
    m = PLSRegression(n_components=n).fit(Xtr, ytr)
    erros_val.append(np.sqrt(mean_squared_error(yte, m.predict(Xte).ravel())))
nlv_trapaca = int(np.argmin(erros_val)) + 1
print('LVs por validação cruzada (correto):', nlv)
print('LVs escolhidas olhando a validação (incorreto):', nlv_trapaca)
print('RMSE na validação com a escolha incorreta:', round(min(erros_val), 3))
```

3. **Importância dos hiperparâmetros.** Comparar o Random Forest do notebook com um sem busca (`BUSCA_RF = False`, 20 componentes) e registrar a diferença de RMSE na validação.
4. Escrever um parágrafo comparando PLSR e Random Forest com os números da tabela, incluindo se há sinal de sobreajuste.

**Gabarito do exercício 1:** o erro é 2, -2, 3 e -3, então o RMSE é a raiz de 6,5, cerca de 2,55. O desvio-padrão populacional de `y_obs` é cerca de 11,18, e o RPD é cerca de 4,39. O Q1 é 17,5 e o Q3 é 32,5, então a distância interquartílica é 15 e o RPIQ é cerca de 5,88. A soma de quadrados dos resíduos é 26 e a soma total é 500, então o R² é 0,948. O viés é 0.

**Observações dos demais exercícios:** (2) a escolha olhando a validação produz um RMSE igual ou menor do que o resultado honesto, mas esse valor é otimista, pois a validação deixou de ser independente. Em um estudo real, esse procedimento invalida a estimativa de desempenho. (3) Em dados sintéticos, a diferença tende a ser pequena. Em dados reais, a busca costuma melhorar o resultado e reduzir o sobreajuste. (4) No banco sintético, a relação entre espectro e atributo é aproximadamente linear, e por isso os dois modelos devem ter desempenho próximo (em um teste, o RMSE de validação cruzada ficou em torno de 3,1 a 3,3 para ambos). A diferença é pequena e, com dados reais, a comparação pode mudar.

#### Perguntas de verificação

1. **Quando o RPIQ é mais indicado que o RPD?** Quando a distribuição do atributo é assimétrica ou tem valores extremos, que inflam o desvio-padrão sem refletir a variabilidade típica.
2. **Um R² alto na calibração garante um bom modelo?** Não. O que importa é o desempenho em amostras independentes. O R² da calibração pode ser alto por sobreajuste.
3. **Por que o PCA entra no `Pipeline` do Random Forest?** Para ser ajustado apenas nos dados de treino de cada partição de validação cruzada, evitando que informação das amostras de teste influencie os componentes.

#### Entregável

Tabela de métricas (calibração, validação cruzada e validação) para PLSR e Random Forest, e um parágrafo comparando os modelos, com interpretação do RPD e do RPIQ.
