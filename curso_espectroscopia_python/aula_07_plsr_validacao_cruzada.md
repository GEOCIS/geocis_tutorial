# Aula 7: PLSR e validação cruzada

[← Aula 6](aula_06_cotovelo_kmeans.md) · [Plano do curso](README.md) · [Aula 8 →](aula_08_random_forest_metricas.md)

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Resumo do plano

**Objetivos:** calibrar um modelo PLSR e escolher o número de variáveis latentes sem vazamento.

**Conteúdo:**

- Por que a regressão linear múltipla falha com espectros (muitas bandas colineares) e como o PLSR contorna isso.
- Divisão em calibração e validação (70/30), com estratificação pelos grupos.
- Validação cruzada em 10 partições, curva de RMSECV e escolha do número de variáveis latentes. Subajuste e sobreajuste.
- Comparação de pré-tratamentos (`sg`, `d1` e `snv`) pelo RMSECV.

**Prática:** notebook 04 (seções 1 a 3). Observar qual tratamento é escolhido e testar `TRATAMENTO_FIXO` para forçar outro.

**Entregável:** curva de RMSECV com o número de variáveis latentes escolhido e justificativa.

**Perguntas de verificação:** por que o conjunto de validação não pode ser usado para escolher o número de variáveis latentes? O que acontece com poucas ou muitas variáveis latentes?

## Material de aula: versão 1

**Capítulo:** Modelagem preditiva. **Notebook:** `04_modelagem.ipynb` (seções 1 a 3).

**Materiais:** notebook 04, saídas dos notebooks 02 e 03. A execução completa do notebook 04 leva alguns minutos (a comparação dos pré-tratamentos e a busca do Random Forest são as partes mais demoradas).

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: por que PLSR, variáveis latentes e sobreajuste.
- 40 a 55 min: divisão em calibração e validação.
- 55 a 90 min: execução das seções 1 a 3 do notebook e análise das curvas.
- 90 a 110 min: experimento sobre sobreajuste.
- 110 a 120 min: resumo e entregável.

#### Conteúdo

**O problema dos espectros para a regressão.** Há centenas de variáveis colineares e frequentemente mais variáveis do que amostras. A regressão linear múltipla comum não funciona nessas condições. A **regressão por mínimos quadrados parciais (PLSR)** resolve isso projetando os espectros em poucas **variáveis latentes** (LVs), construídas para maximizar a covariância entre os espectros e o atributo. Diferentemente do PCA, o PLSR já considera o atributo ao construir as variáveis.

**O número de variáveis latentes** é o principal parâmetro: poucas LVs levam a **subajuste** (modelo simples demais); muitas levam a **sobreajuste** (o modelo memoriza o ruído da calibração e generaliza mal).

**Divisão dos dados (seção 1).** O conjunto é dividido em calibração (`1 - TEST_SIZE`) e validação (`TEST_SIZE`). A divisão é **estratificada pelos grupos do k-means**, para que todos os tipos de espectro estejam nos dois conjuntos. A validação não pode ser usada para tomar decisões; ela só serve para avaliar o resultado final.

**Validação cruzada (seção 2).** A calibração é dividida em `CV_FOLDS` (10) partes; o modelo é treinado em nove e testado na restante, repetindo para todas. O erro resultante (**RMSECV**) estima o desempenho em amostras novas, usando apenas a calibração. O notebook:

- calcula o RMSECV para 1 a `MAX_LV` variáveis latentes e para cada pré-tratamento (`sg`, `d1` e `snv`);
- escolhe o pré-tratamento com menor RMSECV (a menos que `TRATAMENTO_FIXO` esteja definido) e o número de LVs no mínimo da curva;
- ajusta o PLSR final e calcula predições na calibração, na validação cruzada e na validação.

**Referência com os dados sintéticos:** calibração de 590 amostras e validação de 253. RMSECV mínimo de cerca de 2,98 com 2 LVs para `sg`, 3,51 com 1 LV para `d1` e 3,29 com 2 LVs para `snv`; o `sg` é escolhido. Poucas LVs bastam porque os dados sintéticos têm pouca complexidade; com dados reais, valores de 8 a 15 LVs são comuns.

#### Prática guiada

1. Executar as seções 1 a 3 do notebook 04 e analisar a tabela de resumo e o gráfico do RMSECV por pré-tratamento.
2. **Visualizar o sobreajuste** (célula extra após a seção 3):

```python
rmse_cal, rmse_cv = [], []
for n in range(1, cfg.MAX_LV + 1):
    m = PLSRegression(n_components=n).fit(Xtr, ytr)
    rmse_cal.append(np.sqrt(mean_squared_error(ytr, m.predict(Xtr).ravel())))
    p = cross_val_predict(PLSRegression(n_components=n), Xtr, ytr, cv=cv, n_jobs=-1).ravel()
    rmse_cv.append(np.sqrt(mean_squared_error(ytr, p)))

plt.figure(figsize=(7, 3.5))
plt.plot(range(1, cfg.MAX_LV + 1), rmse_cal, "o-", label="Calibração")
plt.plot(range(1, cfg.MAX_LV + 1), rmse_cv, "o-", label="Validação cruzada")
plt.xlabel("Variáveis latentes"); plt.ylabel("RMSE"); plt.legend(); plt.show()
```

A curva de calibração sempre cai com mais LVs, enquanto a de validação cruzada para de cair ou sobe. A distância entre as duas indica sobreajuste.

3. **Variabilidade da divisão.** Alterar `SEED` em `config.py` (por exemplo, 1, 2 e 3), reexecutar o notebook e anotar o RMSECV e o número de LVs. Discutir a estabilidade.

#### Exercícios

1. Fixar `TRATAMENTO_FIXO = "d1"` e comparar as métricas de validação com as do tratamento escolhido automaticamente.
2. Alterar `CV_FOLDS` para 5 e para 20 e observar o efeito sobre o RMSECV e o tempo de execução.
3. Aplicar a regra do erro-padrão de forma aproximada: escolher o menor número de LVs cujo RMSECV esteja dentro de um erro-padrão do mínimo:

```python
curva = curvas[TRAT_FINAL]
p = cross_val_predict(PLSRegression(n_components=nlv), Xtr, ytr, cv=cv, n_jobs=-1).ravel()
se_mse = np.std((ytr - p) ** 2) / np.sqrt(len(ytr))      # aproximação didática
limite = curva.min() ** 2 + se_mse
nlv_1se = int(np.argmax(curva ** 2 <= limite)) + 1
print("LVs no mínimo:", nlv, "| regra do erro-padrão:", nlv_1se)
```

4. Explicar por que o PCA da aula 5 e o PLSR produzem variáveis diferentes, embora ambos resumam o espectro.

**Gabarito comentado:**

- (2) Com menos partições, o erro é estimado com modelos treinados em menos dados (mais pessimista) e o cálculo é mais rápido; com mais partições, o oposto. Dez é um compromisso comum.
- (3) Em geral, `nlv_1se` é menor ou igual a `nlv`. Um modelo mais simples dentro da incerteza do mínimo tende a generalizar melhor e a ser mais interpretável.
- (4) O PCA busca direções de máxima variância nos espectros, sem usar o atributo; o PLSR busca direções que também sejam relevantes para o atributo.

#### Problemas comuns

- **Usar a validação para escolher parâmetros:** é o erro metodológico mais comum, e infla o desempenho.
- **LVs demais para poucas amostras:** limitar `MAX_LV` ao tamanho do conjunto.
- **Execução lenta:** reduzir `MAX_LV`, `CV_FOLDS` ou a quantidade de tratamentos comparados.

#### Entregável

Gráfico do RMSECV por número de LVs, tabela de comparação dos pré-tratamentos, justificativa do pré-tratamento e do número de LVs escolhidos.

## Material de aula: versão 2

**Capítulo:** Modelagem preditiva (PLSR). **Notebook:** `04_modelagem.ipynb` (seções 1 a 3).

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: por que o PLSR, divisão dos dados e validação cruzada.
- 40 a 85 min: execução comentada das seções 1 a 3 do notebook 04.
- 85 a 110 min: exercícios (regra do erro-padrão e efeito do pré-tratamento).
- 110 a 120 min: resumo e entregável.

#### Conteúdo

**O problema.** Com centenas de bandas colineares, a regressão linear múltipla é instável ou impossível. O **PLSR** projeta os espectros em poucas **variáveis latentes** (LVs), construídas para maximizar a covariância com o atributo. Assim, diferentemente do PCA, a redução de dimensionalidade já é orientada à predição.

**Compromisso entre subajuste e sobreajuste.** Poucas LVs levam a um modelo simples demais, que erra tanto na calibração quanto na validação. Muitas LVs ajustam o ruído: o erro na calibração cai, mas o da validação sobe. O número ótimo fica no meio, e deve ser escolhido com dados que **não** sejam os da validação final.

**Divisão dos dados.** O notebook separa 70% para calibração e 30% para validação (`TEST_SIZE = 0.3`), estratificando pelos grupos da aula 6, para que todos os tipos de amostra estejam nos dois conjuntos. A validação é reservada para a avaliação final.

**Validação cruzada (10 partições).** A calibração é dividida em 10 partes. Treina-se com 9 e prevê-se a 10ª, repetindo para cada parte. O erro obtido, o **RMSECV**, estima o desempenho em amostras novas sem tocar na validação. É calculado para cada número de LVs, de 1 a 20 (`MAX_LV`).

**Escolha do pré-tratamento.** O notebook compara `sg`, `d1` e `snv` pelo menor RMSECV e escolhe o melhor, a menos que `TRATAMENTO_FIXO` esteja definido. Assim, o pré-tratamento também é tratado como um hiperparâmetro, decidido apenas com os dados de calibração.

#### Prática guiada: notebook 04, seções 1 a 3

1. **Divisão.** Conferir os tamanhos de calibração e validação impressos (cerca de 70% e 30%).
2. **Comparação de tratamentos.** Ler a tabela de resumo com o número ótimo de LVs e o RMSECV de cada tratamento, e o gráfico das curvas. Identificar o pré-tratamento escolhido.
3. **Curva de RMSECV.** Observar a queda inicial, o mínimo e, se houver, o aumento posterior. A linha vermelha marca o número de LVs escolhido.
4. **PLSR final.** Ajustado com o número de LVs escolhido, gera previsões na calibração, na validação cruzada e na validação.

#### Exercícios

1. Em `config.py`, definir `TRATAMENTO_FIXO = 'snv'` e depois `'d1'`, executar o notebook e comparar o número de LVs e o RMSECV. Voltar a `None` ao final.
2. **Regra do erro-padrão (1-SE).** Escolher o menor número de LVs cujo erro esteja dentro de um erro-padrão do mínimo, o que favorece modelos mais simples:

```python
Xtr_t = TRATS[TRAT_FINAL][idx_tr]

def rmse_folds(X, y, n):
    out = []
    for tr, va in cv.split(X):
        m = PLSRegression(n_components=n).fit(X[tr], y[tr])
        out.append(np.sqrt(mean_squared_error(y[va], m.predict(X[va]).ravel())))
    return np.array(out)

medias, ses = [], []
for n in range(1, cfg.MAX_LV + 1):
    f = rmse_folds(Xtr_t, ytr, n)
    medias.append(f.mean())
    ses.append(f.std(ddof=1) / np.sqrt(len(f)))
medias, ses = np.array(medias), np.array(ses)

i_min = medias.argmin()
nlv_1se = int(np.where(medias <= medias[i_min] + ses[i_min])[0][0]) + 1
print('LVs pelo mínimo:', i_min + 1, '| LVs pela regra 1-SE:', nlv_1se)
```

3. **Subajuste e sobreajuste na prática.** Comparar o erro de calibração com o de validação cruzada para 1, 5, `nlv` e 20 LVs:

```python
for n in (1, 5, nlv, 20):
    m = PLSRegression(n_components=n).fit(Xtr, ytr)
    cal = np.sqrt(mean_squared_error(ytr, m.predict(Xtr).ravel()))
    cvp = cross_val_predict(PLSRegression(n_components=n), Xtr, ytr, cv=cv, n_jobs=-1).ravel()
    cvr = np.sqrt(mean_squared_error(ytr, cvp))
    print(f'{n:>2} LVs: RMSE calibração = {cal:.3f} | RMSE validação cruzada = {cvr:.3f}')
```

**Gabarito e observações:** (1) a diferença entre tratamentos é pequena em dados sintéticos bem comportados, e em dados reais pode ser maior, especialmente pela presença de espalhamento e de deslocamentos de linha de base. (2) A regra 1-SE costuma escolher um número igual ou menor de LVs que o mínimo. (3) O RMSE de calibração cai continuamente com mais LVs, enquanto o de validação cruzada tem um mínimo e depois estabiliza ou sobe. A distância entre os dois erros sinaliza sobreajuste.

#### Perguntas de verificação

1. **Por que o conjunto de validação não pode ser usado para escolher o número de LVs?** Porque a escolha usaria a informação da validação, e o desempenho final ficaria otimista. A validação precisa ser usada uma única vez, depois de todas as decisões.
2. **O que acontece com poucas ou muitas variáveis latentes?** Poucas levam a subajuste (erro alto em ambos os conjuntos). Muitas levam a sobreajuste (erro baixo na calibração e maior na validação).
3. **Por que estratificar a divisão pelos grupos?** Para que as classes de amostras estejam representadas nos dois conjuntos e a validação reflita a diversidade do banco.

#### Entregável

Curva de RMSECV com o número de LVs escolhido, tabela de comparação dos pré-tratamentos e justificativa escrita da escolha final.
