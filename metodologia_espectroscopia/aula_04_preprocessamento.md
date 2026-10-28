# Aula 4: Metodologia de pré-processamento

[← Aula 3](aula_03_amostragem_qualidade_exploratoria.md) · [Plano do curso](README.md) · [Aula 5 →](aula_05_dimensionalidade_agrupamento.md)

**Questão central:** qual tratamento usar e como decidir?

**Objetivos:** escolher tratamentos espectrais com critério, sem vazamento de informação e com um ponto de comparação (o dado sem tratamento).

**Tópicos:**

- Tipos de variação indesejada e o tratamento adequado a cada um: ruído (corte das bordas e suavização Savitzky-Golay); deslocamento de linha de base (derivadas); espalhamento multiplicativo e aditivo (SNV e MSC); não linearidade (absorbância).
- Parâmetros (janela, grau, ordem da derivada) como hiperparâmetros a serem definidos por validação cruzada na calibração.
- Vazamento de informação: transformações que usam estatísticas do conjunto (MSC, centragem, PCA) devem ser ajustadas só na calibração e aplicadas depois à validação. SNV e Savitzky-Golay são por espectro e não têm esse problema.
- Uso de `Pipeline` para encadear transformações e modelo de modo seguro.
- Mais tratamento não é sempre melhor: comparar com o dado bruto como linha de base.

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).


## Conteúdo

### Problema, tratamento e custo

Cada tratamento resolve um problema e tem um custo, pois remove também parte do sinal:

| Variação indesejada | Tratamento | Observação, custo ou risco |
| --- | --- | --- |
| Ruído nas extremidades | Corte das bordas | Limites dependem do sensor; perda de bandas que poderiam ter informação |
| Ruído aleatório | Suavização (Savitzky-Golay, média móvel, *binning*) | Janela e grau são hiperparâmetros; janela grande alarga feições estreitas |
| Não linearidade com a concentração | Absorbância; Kubelka-Munk | Aplicada antes dos demais tratamentos; amplifica ruído em baixa reflectância |
| Deslocamento de linha de base | 1ª e 2ª derivadas | Amplificam o ruído |
| Espalhamento multiplicativo e aditivo | SNV, MSC | Removem também a intensidade geral (albedo), que pode estar ligada à matéria orgânica |

### SNV versus MSC

O SNV padroniza cada espectro com a própria média e desvio-padrão. O MSC (*Multiplicative Scatter Correction*) ajusta cada espectro, por regressão, a um espectro de referência (em geral a média da calibração), removendo o deslocamento e a inclinação. O MSC **depende do conjunto**, pois a referência é a média das amostras, e por isso deve ser ajustado só na calibração e depois aplicado à validação.

### Tratamento é hiperparâmetro

A combinação de tratamentos e seus parâmetros (janela, grau do polinômio, ordem da derivada) é uma escolha do analista, que deve ser comparada com validação cruzada **dentro da calibração**, e não decidida por convenção ou olhando a validação final.

### Parcimônia: mais tratamento não é sempre melhor

Toda comparação precisa de uma **linha de base**: o dado apenas convertido em absorbância. Tratamentos que não superam a linha de base não se justificam. Cada transformação remove uma fonte de variação, mas pode remover também informação útil. O SNV, por exemplo, elimina diferenças de intensidade geral entre espectros. Se o atributo se relaciona justamente com a intensidade geral (como a matéria orgânica, que escurece o solo), o SNV pode apagar o sinal. Por isso o efeito de cada tratamento deve ser medido para o atributo em questão.

### Vazamento de informação (*data leakage*)

Ocorre quando informação das amostras de validação (ou de amostras que não estariam disponíveis na predição) influencia o ajuste do modelo ou de alguma etapa de transformação. Fontes comuns:

1. transformações que usam estatísticas do conjunto (MSC, centragem, padronização por banda, PCA) ajustadas com todas as amostras antes da divisão;
2. seleção de bandas ou de variáveis usando o atributo-alvo em todo o conjunto antes da validação cruzada;
3. escolha de parâmetros olhando a validação.

O efeito é desempenho **otimista**, que desaparece quando o modelo vai a dados realmente novos. A defesa é encadear as transformações e o modelo em um `Pipeline`, que as reajusta apenas nos dados de treino de cada partição de validação cruzada.

SNV e Savitzky-Golay atuam por espectro e **não** vazam informação. MSC, que usa o espectro médio, precisa ser ajustado só na calibração.

## Atividade 1: comparar tratamentos com linha de base

Cada candidato é um `Pipeline` (tratamento + PLSR), com o número de variáveis latentes escolhido por validação cruzada dentro da calibração. O MSC é implementado como um transformador, o que permite usá-lo dentro do `Pipeline`:

```python
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from scipy.signal import savgol_filter

class MSC(BaseEstimator, TransformerMixin):
    """Correção multiplicativa de espalhamento: o espectro de referência vem só da calibração."""
    def fit(self, X, y=None):
        self.ref_ = X.mean(axis=0)
        return self
    def transform(self, X):
        out = np.empty_like(X, dtype=float)
        for i, x in enumerate(X):
            b, a = np.polyfit(self.ref_, x, 1)       # x ≈ a + b * referência
            out[i] = (x - a) / b
        return out

sg  = FunctionTransformer(lambda A: savgol_filter(A, cfg.SG_JANELA, cfg.SG_GRAU, axis=1))
d1  = FunctionTransformer(lambda A: savgol_filter(A, cfg.SG_JANELA, cfg.SG_GRAU, deriv=1, axis=1))
snv = FunctionTransformer(utils.snv)

candidatos = {'absorbância (linha de base)': [], 'SG': [sg], 'SG + SNV': [sg, snv],
              'SG + MSC': [sg, MSC()], 'SG + 1ª derivada': [d1]}

Xa_tr, Xa_te, ya_tr, ya_te = train_test_split(X_abs, y, test_size=cfg.TEST_SIZE, random_state=cfg.SEED)
linhas = []
for nome, passos in candidatos.items():
    pipe = make_pipeline(*passos, PLSRegression())
    busca = GridSearchCV(pipe, {'plsregression__n_components': range(1, 13)}, cv=cv,
                         scoring='neg_root_mean_squared_error', n_jobs=-1).fit(Xa_tr, ya_tr)
    linhas.append({'tratamento': nome, 'RMSECV': -busca.best_score_,
                   'LVs': busca.best_params_['plsregression__n_components']})
print(pd.DataFrame(linhas).round(3))
```

**Resultado de referência (argila, dados sintéticos):** a linha de base e o SG empatam (RMSECV de cerca de 2,8, com 2 LVs), e SNV (cerca de 3,1), MSC (cerca de 3,3) e a 1ª derivada (cerca de 3,3) ficam **piores**. Em uma execução com todas as amostras (sem separar a validação), a ordem foi a mesma: absorbância e SG com cerca de 2,96, SG + SNV com cerca de 3,23, SG + MSC com cerca de 3,44 e 1ª derivada com cerca de 3,46.

Neste banco sintético o escurecimento geral do espectro carrega informação sobre o atributo, e por isso os tratamentos que removem a intensidade geral (SNV e MSC) não ajudam e podem piorar. A conclusão didática é que **o melhor tratamento depende dos dados** e que o dado apenas convertido em absorbância é uma linha de base obrigatória. Em dados reais, com mais espalhamento e linha de base variável, a ordem costuma mudar, e é por isso que o teste é necessário.

## Atividade 2: o SNV pode remover informação

```python
mo = df['mo'].values
for nome, M in [('SG (sem SNV)', X_sg), ('SG + SNV', X_snv)]:
    for alvo, v in [('argila', y), ('mo', mo)]:
        busca = GridSearchCV(PLSRegression(), {'n_components': range(1, 13)}, cv=cv,
                             scoring='neg_root_mean_squared_error', n_jobs=-1).fit(M, v)
        k = busca.best_params_['n_components']
        p = cross_val_predict(PLSRegression(k), M, v, cv=cv).ravel()
        r2 = 1 - ((v - p) ** 2).sum() / ((v - v.mean()) ** 2).sum()
        print(f'{nome:>14} | {alvo:>6}: RMSECV = {-busca.best_score_:5.2f} | R2cv = {r2:5.2f} | LVs = {k}')
```

**Resultado de referência:** para a argila, a diferença entre as duas versões é pequena. Para a matéria orgânica, o R² de validação cruzada cai de cerca de 0,43 (sem SNV) para cerca de 0,06 (com SNV), porque, no banco sintético, o efeito da matéria orgânica é uma mudança da intensidade geral do espectro, exatamente o que o SNV remove.

## Atividade 3: demonstração de vazamento de informação

Usar um alvo que é puro ruído, sem relação alguma com as variáveis. Um procedimento honesto deve obter R² menor ou igual a zero.

**3a. Dados de puro ruído (demonstração rápida):**

```python
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

rng = np.random.default_rng(0)
Xr = rng.normal(size=(60, 500))      # 60 amostras, 500 variáveis de ruído
yr = rng.normal(size=60)             # alvo sem relação com as variáveis
cv5 = KFold(5, shuffle=True, random_state=0)

# ERRADO: seleciona as 20 melhores variáveis usando TODAS as amostras e só depois valida
X_sel = SelectKBest(f_regression, k=20).fit_transform(Xr, yr)
r2_errado = cross_val_score(Ridge(1.0), X_sel, yr, cv=cv5, scoring='r2').mean()

# CERTO: a seleção faz parte do Pipeline e é refeita em cada partição de treino
pipe = make_pipeline(SelectKBest(f_regression, k=20), Ridge(1.0))
r2_certo = cross_val_score(pipe, Xr, yr, cv=cv5, scoring='r2').mean()

print('R² com vazamento:', round(r2_errado, 2), '| R² sem vazamento:', round(r2_certo, 2))
```

**Resultado de referência:** com vazamento, o R² sai positivo (cerca de 0,09), sugerindo alguma capacidade preditiva. Sem vazamento, fica negativo (cerca de -0,7), que é o correto para dados sem relação nenhuma (o modelo é pior do que prever a média).

**3b. Espectros reais com alvo de ruído, repetido 100 vezes com 40 amostras:**

```python
from sklearn.linear_model import LinearRegression

cv5 = KFold(5, shuffle=True, random_state=0)
r_errado, r_correto = [], []
for semente in range(100):
    rng = np.random.default_rng(semente)
    sub = rng.choice(len(Xsnv), 40, replace=False)
    Xp, y_ruido = Xsnv[sub], rng.normal(0, 1, 40)        # alvo sem relação com os espectros

    # errado: escolher as 5 bandas mais correlacionadas usando TODAS as amostras
    corr = np.abs(np.corrcoef(Xp.T, y_ruido)[-1, :-1])
    idx = np.argsort(-corr)[:5]
    p1 = cross_val_predict(LinearRegression(), Xp[:, idx], y_ruido, cv=cv5)
    r_errado.append(r2_score(y_ruido, p1))

    # correto: seleção de bandas dentro de cada partição, pelo Pipeline
    pipe = make_pipeline(SelectKBest(f_regression, k=5), LinearRegression())
    p2 = cross_val_predict(pipe, Xp, y_ruido, cv=cv5)
    r_correto.append(r2_score(y_ruido, p2))

print('R² médio, seleção com todos os dados (errado):', np.mean(r_errado).round(3))
print('R² médio, seleção dentro do pipeline (correto):', np.mean(r_correto).round(3))
```

**Gabarito e observações:** na execução de teste, o R² médio foi de cerca de -0,06 no procedimento errado e de cerca de -0,40 no correto. Para um alvo que é puro ruído, o resultado honesto é claramente negativo. O procedimento errado parece muito melhor, sem ter nenhuma informação real: o vazamento torna o desempenho **artificialmente otimista**. Em conjuntos com poucas amostras e muitas bandas, o efeito é grande, o que é o caso típico da espectroscopia.

## Atividade 4: decisão e justificativa

Com os resultados da atividade 1, cada aluno escreve um parágrafo de justificativa do tratamento escolhido para o seu atributo, incluindo a comparação com a linha de base e a observação de que a decisão foi tomada só com a calibração.

## Exercícios

1. Repetir a atividade 1 para a matéria orgânica, incluindo uma versão `sg` sem SNV, e comparar com o resultado da argila. Concluir sobre a escolha do tratamento para cada atributo.
2. Na atividade 3a, repetir com `k=5` e com `k=100` variáveis selecionadas e registrar o efeito sobre o R² com vazamento.
3. Explicar por que o SNV não vaza informação, mas o MSC pode.
4. Escrever dois parágrafos de metodologia sobre o pré-processamento do atributo escolhido, descrevendo as alternativas comparadas e o critério de escolha.

<details>
<summary>Gabarito</summary>

1. Para a matéria orgânica, a versão sem SNV tende a ser melhor, e para a argila, a diferença é pequena. O tratamento ideal depende do atributo.
2. O efeito do vazamento tende a ser maior quando o número de variáveis candidatas é muito maior que o de amostras.
3. O SNV usa só a média e o desvio-padrão do próprio espectro. O MSC usa o espectro médio do conjunto, que, se calculado com todas as amostras, carrega informação da validação.

</details>

## Perguntas de verificação

1. **Por que incluir o dado sem tratamento (apenas absorbância) na comparação?** Para saber se os tratamentos realmente ajudam. Sem linha de base, não se pode afirmar que o pré-processamento melhorou o modelo.
2. **O que é um vazamento de informação e como se evita?** Quando informação da validação influencia o ajuste do modelo ou das transformações. Evita-se ajustando tudo apenas nos dados de treino, com `Pipeline`.
3. **Como o `Pipeline` evita o vazamento?** Ele reajusta todas as transformações apenas com os dados de treino de cada partição, e as aplica à parte de validação sem recalculá-las.
4. **Por que o MSC exige cuidado com a divisão dos dados e o SNV não?** O MSC usa o espectro médio da calibração como referência, e portanto depende do conjunto. O SNV usa apenas estatísticas do próprio espectro.
5. **Por que o mesmo tratamento pode ajudar um atributo e prejudicar outro?** Porque o tratamento remove um tipo de variação, e o atributo pode depender justamente dela.

## Entregável

Tabela de comparação de tratamentos (RMSECV e número de LVs, com linha de base), resultado da demonstração de vazamento e texto de justificativa de um parágrafo do tratamento escolhido para o atributo.
