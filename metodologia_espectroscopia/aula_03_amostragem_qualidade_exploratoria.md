# Aula 3: Amostragem, qualidade dos dados e análise exploratória

[← Aula 2](aula_02_espectroscopia_e_referencia.md) · [Plano do curso](README.md) · [Aula 4 →](aula_04_preprocessamento.md)

**Questão central:** os dados são adequados para modelar?

**Objetivos:** avaliar se o banco é adequado para modelar, diagnosticar problemas de qualidade e decidir como tratá-los, com critério e registro.

**Tópicos:**

- Representatividade: cobertura geográfica, de classes de solo e da faixa de variação do atributo.
- Valores faltantes: mecanismos e decisão de remover, imputar ou modelar cada atributo com o seu subconjunto.
- Análise exploratória como etapa metodológica: estatística descritiva, distribuição, assimetria, correlação espectro-atributo.
- Outliers: critérios espectrais (z-score, T², Q) e critérios de decisão. Remover com base no espectro, nunca no valor do atributo-alvo, e documentar cada exclusão.
- Transformação da variável resposta para distribuições assimétricas (por exemplo, logaritmo) e seus efeitos sobre as métricas.

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).


## Conteúdo

### Representatividade

Um modelo aprende a relação entre espectro e atributo **nas amostras que viu**. Sua validade se limita à variabilidade coberta pela calibração. Verificar:

- **População:** os solos, regiões, profundidades e épocas representam os solos aos quais o modelo será aplicado?
- **Cobertura da faixa do atributo:** a faixa de variação na calibração cobre a faixa esperada no uso? Se há poucas amostras nos extremos, o modelo extrapola mal nessas regiões.
- **Cobertura espectral e de classes de solo:** pode ser avaliada com o gráfico de escores do PCA (aula 5), observando regiões vazias.
- **Equilíbrio:** bancos com muitas amostras de uma região e poucas de outras produzem modelos que funcionam bem para a região dominante e mal para as demais.
- **Independência:** há amostras do mesmo local ou do mesmo perfil (pseudorrepetições)? Isso afeta a validação (aula 7).
- **Semelhança entre calibração e validação:** as distribuições do atributo devem ser parecidas, para que a validação represente o uso.

### Valores faltantes: o mecanismo importa

Antes de decidir o que fazer, entender por que os dados faltam:

| Mecanismo | Significado | Consequência |
| --- | --- | --- |
| MCAR (faltam ao acaso) | A falta não depende de nenhuma variável | Remover amostras causa perda de informação, mas não vício |
| MAR (faltam condicionadas a outra variável observada) | Depende, por exemplo, do laboratório que não mede certo atributo ou da época | Pode ser tratado levando em conta a variável; remover costuma ser seguro |
| MNAR (faltam por causa do próprio valor) | Por exemplo, valores acima do limite de detecção que não foram registrados | Remover ou imputar produz viés e merece discussão |

Na modelagem espectral, é comum remover amostras sem o atributo, mas é preciso verificar se o conjunto restante continua representativo e registrar quantas amostras foram removidas e por quê. Imputar o **atributo-alvo** raramente é recomendável, pois cria dado de referência que não foi medido e que o modelo tentaria aprender.

### Três tipos de problema, três tratamentos

| Problema | Como se detecta | Como se trata |
| --- | --- | --- |
| Espectro anômalo | Gráficos, z-score, T² e Q | Inspecionar e remover com registro |
| Valor de referência impossível | Limites físicos (argila fora de 0 a 100%) e coerência entre atributos | Verificar a origem; corrigir ou excluir |
| Duplicatas | Espectros ou identificadores repetidos | Remover duplicatas, para que não apareçam na calibração e na validação ao mesmo tempo |

### Outliers como decisão metodológica

A detecção (z-score, T² e Q) apenas sinaliza. A decisão de remover precisa de critério explícito: erro de medição comprovado ou espectro fisicamente implausível justificam a remoção. Amostras extremas, mas legítimas, aumentam a faixa de variação e a robustez do modelo, e devem ser mantidas. Registrar o número de amostras antes e depois de cada exclusão e o motivo.

**Regra de ouro dos outliers:** excluir pelo espectro ou por impossibilidade física do valor, nunca porque o modelo errou muito a amostra. Excluir os maiores erros do modelo melhora artificialmente as métricas. Quando uma amostra tem erro muito grande, investiga-se a causa (erro de laboratório, de medição, amostra de outra natureza) e registra-se a decisão.

### Transformação da variável resposta

Atributos de cauda longa à direita (matéria orgânica, alguns nutrientes) são às vezes transformados (logaritmo, raiz quadrada) para estabilizar a variância dos resíduos. Cuidados:

1. as métricas devem ser calculadas na **escala original**, depois da retransformação, que é a escala de uso;
2. ao voltar da escala logarítmica, a predição fica com viés (a média do logaritmo não é o logaritmo da média), e a retransformação pode amplificar erros.

A transformação é uma hipótese a testar, e não uma regra: só se justifica se melhorar o desempenho ou o comportamento dos resíduos na escala original.

## Atividade 1: relatório de qualidade

```python
cols_esp, cols_ref = utils.identificar_colunas(df, cfg.PREFIXO)

relatorio = {
    'amostras': len(df),
    'espectros duplicados': int(df.duplicated(subset=cols_esp).sum()),
    'identificadores duplicados': int(df['id'].duplicated().sum()),
    'reflectância mínima': round(float(Xraw.min()), 3),
    'reflectância máxima': round(float(Xraw.max()), 3),
    'valores de reflectância fora de (0, 1)': int(((Xraw <= 0) | (Xraw >= 1)).sum()),
    'argila fora de [0, 100]': int(((df['argila'] < 0) | (df['argila'] > 100)).sum()),
}
print(pd.Series(relatorio))
print(df[cols_ref].describe().T.round(2))
```

**Resultado de referência (dados sintéticos):** não há duplicatas, e a reflectância fica entre cerca de 0,06 e 0,48.

## Atividade 2: a divisão dos dados e a representatividade

**2a. Calibração e validação são parecidas?**

```python
print(pd.DataFrame({'calibração': pd.Series(ytr).describe(),
                    'validação': pd.Series(yte).describe()}).round(2))
```

**2b. Divisão aleatória versus divisão enviesada** (treino com os valores baixos e teste com os valores altos):

```python
from scipy.stats import ks_2samp

# divisão aleatória
tr, te = train_test_split(np.arange(len(y)), test_size=0.3, random_state=0)
m = PLSRegression(modelo['nlv']).fit(Xsg[tr], y[tr])
print('Aleatória: p do teste KS =', ks_2samp(y[tr], y[te]).pvalue.round(3))
print({k: round(float(v), 2) for k, v in utils.avalia(y[te], m.predict(Xsg[te]).ravel()).items()})

# divisão enviesada: treino com os 70% menores valores, teste com os 30% maiores
lim = np.percentile(y, 70)
tr2, te2 = np.where(y <= lim)[0], np.where(y > lim)[0]
m2 = PLSRegression(modelo['nlv']).fit(Xsg[tr2], y[tr2])
print('Enviesada: p do teste KS =', ks_2samp(y[tr2], y[te2]).pvalue)
print({k: round(float(v), 2) for k, v in utils.avalia(y[te2], m2.predict(Xsg[te2]).ravel()).items()})
```

**Gabarito e observações:** na execução de teste, a divisão aleatória teve p do teste KS de cerca de 0,4 (distribuições compatíveis) e R² de cerca de 0,98. Na divisão enviesada, o p do teste KS foi praticamente zero (distribuições muito diferentes), o RMSE passou de cerca de 2,6 para cerca de 5,1 e o R² caiu para cerca de 0,85. Isso mostra que um modelo avaliado fora da faixa de variação da calibração tem desempenho pior, e que a representatividade importa tanto quanto o algoritmo.

## Atividade 3: faltantes que dependem do próprio valor (MNAR)

Simular a perda das amostras de valores altos e ver o efeito sobre a média:

```python
rng = np.random.default_rng(0)
p_falta = (y > np.percentile(y, 70)) * 0.5       # 50% de chance de faltar nos 30% mais altos
falta = rng.random(len(y)) < p_falta
print('Média completa:', y.mean().round(2), '| média após remoção:', y[~falta].mean().round(2),
      '| n:', (~falta).sum())
```

**Gabarito:** a média cai (na execução de teste, de cerca de 35,9 para cerca de 32,2), e o conjunto passa a subestimar os valores altos. Um modelo calibrado com esse subconjunto teria pior desempenho justamente na faixa que falta. Discutir como detectar essa situação (comparar com outras fontes, olhar a distribuição truncada) e como relatar a limitação.

## Atividade 4: transformação do alvo

Comparar o PLSR na escala original e com o logaritmo do alvo, sempre com as métricas na escala original.

**4a. Matéria orgânica (distribuição assimétrica)**, com o número de LVs escolhido por validação cruzada:

```python
mo = df['mo'].values
print('Assimetria:', round(pd.Series(mo).skew(), 2), '| após log1p:', round(pd.Series(np.log1p(mo)).skew(), 2))

Xa, Xb, ma, mb = train_test_split(X_sg, mo, test_size=0.3, random_state=1)
busca = GridSearchCV(PLSRegression(), {'n_components': range(1, 13)}, cv=cv,
                     scoring='neg_root_mean_squared_error', n_jobs=-1)

p_direto = busca.fit(Xa, ma).predict(Xb).ravel()
p_log = np.expm1(busca.fit(Xa, np.log1p(ma)).predict(Xb).ravel())     # volta à escala original

print(pd.DataFrame({'direto': utils.avalia(mb, p_direto),
                    'log (escala original)': utils.avalia(mb, p_log)}).T.round(3))
```

**Resultado de referência (dados sintéticos):** a assimetria da matéria orgânica cai de cerca de 1,1 para cerca de -0,2 com o logaritmo. Na escala original, o ganho do modelo com logaritmo é pequeno (RMSE de cerca de 8,3 contra 8,4, e R² de cerca de 0,40 contra 0,39), e a transformação **introduz viés** (cerca de -2,2 contra -0,5 do modelo direto).

**4b. Argila (relação aproximadamente linear)**, com 8 LVs fixos:

```python
X1, X2, y1, y2 = train_test_split(Xsg, y, test_size=0.3, random_state=0)

m1 = PLSRegression(8).fit(X1, y1)
p1 = m1.predict(X2).ravel()

m2 = PLSRegression(8).fit(X1, np.log(y1))
p2 = np.exp(m2.predict(X2).ravel())            # volta à escala original

print('Escala original :', {k: round(float(v), 2) for k, v in utils.avalia(y2, p1).items()})
print('Log + retorno   :', {k: round(float(v), 2) for k, v in utils.avalia(y2, p2).items()})
```

**Gabarito e observações:** no banco sintético, a relação espectro-argila é aproximadamente linear, e por isso a transformação **piora** o resultado (na execução de teste, o RMSE passou de cerca de 2,9 para cerca de 8,5). A retransformação com `exp` amplifica os erros nos valores altos. Em dados reais assimétricos o efeito pode ser o contrário, e por isso a decisão deve ser tomada comparando as métricas na escala original, e não por hábito.

## Exercícios

1. Executar o relatório de qualidade para o atributo escolhido na aula 1 e listar os problemas encontrados e o tratamento proposto para cada um.
2. Para cada situação, indicar se a exclusão é adequada: (a) um espectro com reflectância negativa em várias bandas; (b) uma amostra com argila de 105%; (c) a amostra com o maior erro de predição na validação; (d) amostras duplicadas, uma na calibração e outra na validação.
3. Executar a atividade 4a para o atributo `argila` e comparar com os resultados da matéria orgânica. A transformação se justifica?

<details>
<summary>Gabarito</summary>

2. (a) adequada, é um problema espectral (investigar e registrar); (b) adequada, valor fisicamente impossível (verificar a origem antes de excluir); (c) **não** adequada, seria excluir pelo erro do modelo (investigar a causa, mas manter se não houver erro comprovado); (d) a duplicata deve ser removida, pois a mesma amostra na calibração e na validação infla o desempenho.
3. A argila tem assimetria menor e, em geral, a transformação não traz ganho que compense o viés e a complexidade adicionais.

</details>

## Perguntas de verificação

1. **Por que a representatividade pode importar mais que o algoritmo?** Porque nenhum algoritmo prediz bem fora da variabilidade que viu. Um modelo simples bem calibrado em amostras representativas supera um modelo sofisticado calibrado em amostras que não representam o uso.
2. **Por que não imputar o atributo-alvo?** Os valores imputados são artificiais e o modelo aprenderia a reproduzi-los, o que distorce a relação espectro-atributo e a avaliação.
3. **Por que não excluir amostras com grande erro de predição?** Porque melhora artificialmente as métricas. Deve-se investigar a causa e só excluir com justificativa independente do erro do modelo.
4. **Quando uma amostra sinalizada como outlier deve ser mantida?** Quando é legítima, ou seja, é um solo real e extremo, sem erro de medição, e representa uma variabilidade que o modelo deve conhecer.
5. **Por que calcular as métricas na escala original após uma transformação?** Porque é a escala de uso do modelo, e métricas na escala transformada não são comparáveis entre estudos nem representam o erro prático.
6. **O que é o viés da retrotransformação?** Ao voltar da escala logarítmica, a exponencial da média dos logaritmos tende a subestimar a média na escala original, o que gera erro sistemático.

## Entregável

Relatório de qualidade dos dados com: número de amostras antes e depois de cada exclusão e a justificativa de cada decisão, mecanismo provável dos faltantes, análise de representatividade (distribuição do atributo e cobertura no espaço dos componentes) e decisão justificada sobre a transformação do alvo.
