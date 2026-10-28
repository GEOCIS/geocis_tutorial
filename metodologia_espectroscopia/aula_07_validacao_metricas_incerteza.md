# Aula 7: Validação, métricas e incerteza

[← Aula 6](aula_06_modelagem.md) · [Plano do curso](README.md) · [Aula 8 →](aula_08_dominio_reprodutibilidade_redacao.md)

**Questão central:** como estimar o desempenho real?

**Objetivos:** estimar o desempenho real do modelo e comunicar a incerteza.

**Tópicos:**

- Estratégias de validação: divisão aleatória, estratificada, Kennard-Stone e SPXY, validação cruzada repetida e aninhada, e validação externa.
- Autocorrelação espacial e amostras do mesmo local: quando divisões aleatórias levam a estimativas otimistas e como usar validação por grupos (por exemplo, deixar um local ou projeto de fora).
- Métricas: R², RMSE, RPD, RPIQ, viés e, opcionalmente, o coeficiente de concordância de Lin. O que cada uma informa e suas limitações.
- Interpretação do desempenho em função do uso pretendido (classificação de Chang et al., 2001, como orientação e não como regra).
- Comparação de modelos: repetição com várias sementes, média e desvio das métricas, e cautela com diferenças pequenas.
- Incerteza das predições: intervalos por *bootstrap*, regressão por quantis em florestas e análise de resíduos.

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).

## Conteúdo

### O que a validação mede

O desempenho que interessa é o desempenho em amostras que o modelo **não viu e que se parecem com o uso real**. Cada estratégia de validação responde a uma pergunta diferente.

| Estratégia | Como funciona | Quando é adequada | Cuidados |
| --- | --- | --- | --- |
| Divisão aleatória (*hold-out*) | Uma divisão em calibração e validação | Primeira avaliação, bancos grandes | Uma única divisão varia muito com a semente |
| Divisão estratificada | Mantém a distribuição dos grupos ou do atributo | Bancos heterogêneos | Exige definir o critério de estratificação |
| Kennard-Stone e SPXY | Selecionam para a calibração as amostras mais espalhadas no espaço espectral (SPXY inclui também o atributo) | Garantir que a calibração cubra a variabilidade | A validação fica "dentro" da calibração, o que pode ser otimista |
| Validação cruzada (k partições) | Cada parte é validação uma vez | Escolha de hiperparâmetros e bancos pequenos | Usar só na calibração quando há validação externa |
| Validação cruzada repetida | Repete a validação cruzada com sementes diferentes | Estimar a variabilidade da métrica | Custo computacional |
| Validação cruzada aninhada | Laço interno escolhe hiperparâmetros, laço externo avalia | Estimar o desempenho de um procedimento que inclui a escolha de parâmetros | Custo computacional |
| Validação por grupos | Deixa grupos inteiros (local, projeto, classe de solo) de fora | Quando haverá aplicação em locais ou projetos novos | Estimativa mais pessimista e mais realista |
| Validação externa independente | Dados de outro projeto, época ou região | O teste mais exigente de generalização | Exige dados adicionais |

### Autocorrelação espacial e pseudorrepetições

Amostras do mesmo local, do mesmo perfil ou do mesmo projeto são parecidas entre si. Em uma divisão aleatória, amostras vizinhas caem na calibração e na validação, e o modelo é testado em amostras "quase conhecidas", o que produz estimativas **otimistas** para o uso em locais novos. Se a aplicação prevista for em locais ou projetos novos, a validação deve deixar grupos inteiros de fora.

### Métricas

R², RMSE, RPD, RPIQ e viés (aula 8 do curso por capítulos) mais o **coeficiente de concordância de Lin (CCC)**, que combina correlação e proximidade da linha 1:1 (penaliza viés e inclinação diferente de 1). Cada métrica informa um aspecto, e relatar um conjunto, com o número de amostras, evita interpretações enganosas. As métricas devem ser calculadas na escala original do atributo. A interpretação depende do uso pretendido definido na aula 1; a classificação de Chang et al. (2001) é uma orientação, e não uma regra.

### Comparar modelos

Uma diferença de desempenho em uma única divisão pode ser acaso. Boas práticas: repetir a avaliação com muitas divisões, relatar média e desvio e olhar a diferença **pareada** (os dois modelos nas mesmas divisões). Diferenças menores que a variabilidade entre divisões não justificam afirmar que um modelo é melhor.

### Incerteza das predições

Uma predição sem incerteza é incompleta. Métodos: intervalos baseados na distribuição dos resíduos de validação cruzada, *bootstrap* e, em florestas, regressão por quantis. A incerteza costuma aumentar nas extremidades da faixa e fora do domínio de aplicação.

## Atividade 1: a variabilidade de uma única divisão

Repetir a divisão calibração/validação com 10 sementes diferentes e resumir as métricas:

```python
resultados = []
for semente in range(10):
    tr, te = train_test_split(np.arange(len(y)), test_size=0.3, random_state=semente)
    m = PLSRegression(modelo['nlv']).fit(Xsg[tr], y[tr])
    resultados.append(utils.avalia(y[te], m.predict(Xsg[te]).ravel()))

tab = pd.DataFrame(resultados)[['R2', 'RMSE', 'RPD', 'RPIQ']]
print(tab.round(2))
print(tab.agg(['mean', 'std']).round(3))
```

**Gabarito e observações:** na execução de teste, a média do RMSE foi de cerca de 2,9, com desvio-padrão de cerca de 0,3, e o RPD variou entre cerca de 6 e 8 (média de 6,7 e desvio de 0,7). Relatar um único RPD (por exemplo, 7,6) é uma foto da variação, e a faixa é a informação honesta. Pedir aos alunos que relatem os resultados do seu atributo como média ± desvio.

## Atividade 2: validação aleatória versus validação por grupos

Usar os grupos do k-means (aula 5) como grupos de validação: cada grupo é deixado de fora uma vez.

```python
from sklearn.model_selection import LeaveOneGroupOut

cl = df_pp['cluster'].values
modelo_pls = PLSRegression(modelo['nlv'])

p_aleat = cross_val_predict(modelo_pls, Xsg, y, cv=KFold(5, shuffle=True, random_state=0)).ravel()
p_grupo = cross_val_predict(modelo_pls, Xsg, y, cv=LeaveOneGroupOut(), groups=cl).ravel()

print('Aleatória  :', {k: round(float(v), 2) for k, v in utils.avalia(y, p_aleat).items()})
print('Por grupos :', {k: round(float(v), 2) for k, v in utils.avalia(y, p_grupo).items()})
```

**Gabarito e observações:** na execução de teste, a validação aleatória deu RMSE de cerca de 3,0 e viés de cerca de 0,0, e a validação por grupos deu RMSE de cerca de 4,4 e viés de cerca de 1,6. A segunda é mais pessimista, pois cada grupo é previsto sem nenhuma amostra de si mesmo na calibração. Como os grupos do banco sintético são pedaços de um gradiente contínuo, o efeito é moderado. Com dados reais, em que grupos correspondem a locais ou projetos distintos, a diferença costuma ser maior. Perguntar: qual das duas estimativas responde à pergunta do protocolo da aula 1?

## Atividade 3: validação aninhada

Estimar o desempenho de um procedimento que escolhe o número de LVs por validação cruzada, sem usar os mesmos dados para escolher e avaliar:

```python
from sklearn.model_selection import cross_val_score

interno = GridSearchCV(PLSRegression(), {'n_components': list(range(1, 16))},
                       cv=5, scoring='neg_root_mean_squared_error')
externo = cross_val_score(interno, Xsg, y, cv=KFold(5, shuffle=True, random_state=1),
                         scoring='neg_root_mean_squared_error')
print('RMSE aninhado por partição:', (-externo).round(2), '| média:', (-externo).mean().round(3))

interno.fit(Xsg, y)
print('Melhor RMSE da busca (não aninhado):', (-interno.best_score_).round(3))
```

**Gabarito e observações:** na execução de teste, o RMSE aninhado foi de cerca de 2,94 (desvio entre partições de cerca de 0,36) e o da busca não aninhada, de cerca de 2,91. A diferença é pequena neste banco, mas o erro não aninhado tende a ser um pouco otimista, pois usa os mesmos dados para escolher o parâmetro e para avaliar. Em conjuntos pequenos e com muitos hiperparâmetros, o viés é maior.

## Atividade 4: comparação pareada, incerteza e CCC

**(a) Comparar PLSR e Random Forest nas mesmas divisões:**

```python
from scipy.stats import ttest_rel
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor

r_pls, r_rf = [], []
for semente in range(10):
    tr, te = train_test_split(np.arange(len(y)), test_size=0.3, random_state=semente)
    pls = PLSRegression(modelo['nlv']).fit(Xsg[tr], y[tr])
    rf = Pipeline([('pca', PCA(20)),
                   ('rf', RandomForestRegressor(200, random_state=0, n_jobs=-1))]).fit(Xsg[tr], y[tr])
    r_pls.append(rmse(y[te], pls.predict(Xsg[te]).ravel()))
    r_rf.append(rmse(y[te], rf.predict(Xsg[te])))
r_pls, r_rf = np.array(r_pls), np.array(r_rf)

dif = r_rf - r_pls
print('RMSE médio  PLSR:', r_pls.mean().round(2), '| RF:', r_rf.mean().round(2))
print('Diferença média (RF - PLSR):', dif.mean().round(2), '± ', dif.std(ddof=1).round(2),
      '| RF melhor em', (dif < 0).sum(), 'de 10 divisões')
print('Teste t pareado: p =', ttest_rel(r_rf, r_pls).pvalue.round(3))
```

**(b) Intervalo de predição pelos resíduos da validação cruzada e CCC:**

```python
tr, te = train_test_split(np.arange(len(y)), test_size=0.3, random_state=0)
m = PLSRegression(modelo['nlv'])

p_cv = cross_val_predict(m, Xsg[tr], y[tr], cv=KFold(10, shuffle=True, random_state=0)).ravel()
li, ls = np.percentile(y[tr] - p_cv, [2.5, 97.5])         # resíduos observado - predito

m.fit(Xsg[tr], y[tr])
p_te = m.predict(Xsg[te]).ravel()
cobertura = np.mean((y[te] >= p_te + li) & (y[te] <= p_te + ls))
print(f'Intervalo de 95%: predito {li:+.2f} a {ls:+.2f} | cobertura na validação: {cobertura:.1%}')

def ccc(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return 2 * np.cov(a, b, ddof=0)[0, 1] / (a.var() + b.var() + (a.mean() - b.mean()) ** 2)
print('CCC de Lin:', round(ccc(y[te], p_te), 3))
```

**Gabarito e observações:** (a) na execução de teste, o RMSE médio foi de cerca de 2,95 para o PLSR e de cerca de 2,83 para o Random Forest, e este foi melhor em 6 das 10 divisões, com p de cerca de 0,34 no teste t pareado. A conclusão correta é que **não há evidência de diferença** entre os modelos neste banco. Observação metodológica: as divisões repetidas compartilham amostras, o que torna o teste t aproximado e um pouco otimista, e ele deve ser lido como um guia, e não como prova. (b) O intervalo foi de cerca de -6,7 a +5,0 em torno da predição, com cobertura de cerca de 96% na validação (próxima dos 95% nominais), e o CCC foi de cerca de 0,99.

## Perguntas de verificação

1. **Por que a validação aleatória pode ser otimista para uso em locais novos?** Porque amostras do mesmo local ou projeto aparecem na calibração e na validação, e o modelo é testado em amostras muito parecidas com as que treinou.
2. **O que a validação aninhada resolve?** Evita que os mesmos dados sirvam para escolher hiperparâmetros e para estimar o desempenho, que seria otimista.
3. **Uma diferença de RMSE de 0,1 entre dois modelos mostra qual é melhor?** Não, se a variabilidade entre divisões for maior que isso. É preciso repetir a avaliação e examinar a diferença pareada.

## Entregável

Quadro de validação com média e desvio das métricas em divisões repetidas, comparação entre validação aleatória e por grupos, análise dos resíduos, intervalo de predição com cobertura e interpretação de cada resultado para o uso pretendido do protocolo.
