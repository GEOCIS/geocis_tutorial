# Aula 5: Redução de dimensionalidade e agrupamento

[← Aula 4](aula_04_preprocessamento.md) · [Plano do curso](README.md) · [Aula 6 →](aula_06_modelagem.md)

**Questão central:** como resumir e organizar a variabilidade espectral?

**Objetivos:** usar PCA e clusterização como ferramentas de exploração e de apoio à modelagem, conhecendo suas premissas.

**Tópicos:**

- Maldição da dimensionalidade e colinearidade em espectros.
- PCA: premissas, escolha do número de componentes (variância acumulada, *scree*, validação cruzada) e interpretação de escores e loadings.
- Seleção de bandas como alternativa (VIP, regiões espectrais) e quando ela ajuda.
- Agrupamento: k-means, clusterização hierárquica e misturas gaussianas; pressupostos e limitações de cada um.
- Escolha de k: cotovelo, silhueta e interpretabilidade. Validade interna versus utilidade prática.
- Usos metodológicos dos grupos: estratificação da divisão dos dados, modelos locais e análise do erro por grupo.

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).

## Conteúdo

### O problema da dimensionalidade

Os espectros têm centenas de variáveis fortemente correlacionadas e, muitas vezes, mais variáveis do que amostras úteis. Isso causa instabilidade nos coeficientes, sobreajuste e dificuldade de interpretação. As saídas são reduzir a dimensionalidade (PCA e variáveis latentes do PLSR), selecionar bandas ou usar algoritmos que lidam bem com muitas variáveis.

### PCA: premissas e usos

O PCA é linear, descreve variância (e não relevância para o atributo) e é sensível a outliers e à escala. Em espectros, onde todas as bandas têm a mesma unidade, não é necessário padronizar por banda, e a centragem é feita automaticamente. Usos metodológicos: explorar a estrutura, detectar outliers, resumir os dados para clusterização e alimentar modelos como o Random Forest.

### Como escolher o número de componentes

Critérios, em ordem de preferência para modelagem:

1. **Desempenho preditivo em validação cruzada** (o critério que importa para predição).
2. Variância acumulada (por exemplo, 95% ou 99%), útil para exploração e resumo.
3. Inspeção do *scree plot* (cotovelo).

Para agrupamento ou exploração, os primeiros componentes bastam. Para predição, o número ótimo é definido pelo erro de validação cruzada, pois variância não é relevância: um atributo pode depender de componentes de baixa variância.

### PCR versus PLSR

A regressão por componentes principais (PCR) usa os componentes de maior variância como preditores, sem olhar o atributo. O PLSR constrói componentes que já maximizam a covariância com o atributo, e em geral precisa de menos componentes para o mesmo desempenho. A diferença é maior quando a informação do atributo está em direções de baixa variância.

### Seleção de bandas

Reduz a dimensão mantendo as regiões mais informativas (por exemplo, pelo VIP do PLSR, por correlação ou por algoritmos de otimização). Pode melhorar a interpretabilidade e, às vezes, o desempenho, mas **a seleção precisa ser feita dentro da validação cruzada**, senão causa vazamento (aula 4).

### Agrupamento: métodos e premissas

| Método | Ideia | Premissas e limitações |
| --- | --- | --- |
| k-means | Minimiza a distância ao centro do grupo | Grupos esféricos e de tamanho parecido; k fixo; sensível à inicialização |
| Hierárquico | Une as amostras mais próximas passo a passo | Não precisa de k de antemão, mas é custoso em bancos grandes |
| Misturas gaussianas (GMM) | Cada grupo é uma distribuição normal multivariada | Permite grupos elípticos e de tamanhos diferentes; k escolhido pelo BIC |

### Escolha de k e validade dos grupos

Cotovelo, silhueta e BIC (no GMM) são critérios **internos**, que medem a coesão dos grupos. Eles podem divergir, e não existe uma resposta única. O que justifica um número de grupos é a combinação de critérios internos, **estabilidade** (resultado parecido com sementes ou métodos diferentes) e **utilidade** (os grupos têm interpretação agronômica ou melhoram a modelagem).

### Usos dos grupos na modelagem

Estratificar a divisão entre calibração e validação, analisar o erro por grupo e calibrar modelos locais.

## Atividade 1: PCR versus PLSR

Comparar o erro de validação cruzada para o mesmo número de componentes:

```python
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

for n in (1, 2, 3, 5, 8, 12):
    p_pcr = cross_val_predict(make_pipeline(PCA(n), LinearRegression()), Xsg, y, cv=cv).ravel()
    p_pls = cross_val_predict(PLSRegression(n), Xsg, y, cv=cv).ravel()
    print(f'{n:>2} componentes: RMSE PCR = {rmse(y, p_pcr):.2f} | RMSE PLSR = {rmse(y, p_pls):.2f}')
```

**Gabarito e observações:** na execução de teste, com 1 componente os dois métodos tiveram erro alto (cerca de 19), e com 2 componentes ambos chegaram a cerca de 3,0. Depois disso, o PCR ficou estável (cerca de 3,0), enquanto o PLSR piorou levemente com mais variáveis latentes (cerca de 3,3 com 12), sinal de sobreajuste. Neste banco sintético, a informação do atributo está nos primeiros componentes, então a diferença entre os métodos é pequena. Perguntar aos alunos em que situação o PLSR teria vantagem clara (quando o atributo depende de componentes de baixa variância).

## Atividade 2: comparar métodos de agrupamento

Aplicar k-means e misturas gaussianas aos escores do PCA e examinar o BIC:

```python
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_rand_score

Z = PCA(5).fit_transform(Xsnv)

bics = [GaussianMixture(k, random_state=0, n_init=3).fit(Z).bic(Z) for k in range(1, 7)]
for k, b in zip(range(1, 7), bics):
    print(f'k = {k}: BIC = {b:.0f}')

rot_km = KMeans(3, n_init=10, random_state=0).fit_predict(Z)
k_gmm = int(np.argmin(bics)) + 1
rot_gmm = GaussianMixture(k_gmm, random_state=0, n_init=3).fit(Z).predict(Z)
print('k pelo BIC:', k_gmm, '| ARI k-means × GMM:', round(adjusted_rand_score(rot_km, rot_gmm), 3))
```

**Gabarito e observações:** na execução de teste, o BIC foi mínimo em k = 4, enquanto o cotovelo e a silhueta do pipeline levaram a k = 3. O índice ARI entre as duas soluções foi de cerca de 0,46, ou seja, concordância parcial. A discussão central: critérios diferentes sugerem números de grupos diferentes, e como o banco sintético varia de forma contínua, **não há uma resposta "verdadeira"**. O que se faz é escolher k com base em estabilidade e utilidade, e relatar a incerteza da escolha.

## Atividade 3: os grupos ajudam a modelar?

Comparar um modelo global com modelos locais (um por grupo), usando a mesma divisão estratificada. O número de LVs de cada modelo local é escolhido por validação cruzada no treino do próprio grupo:

```python
cl = df_pp['cluster'].values
tr, te = train_test_split(np.arange(len(y)), test_size=0.3, random_state=0, stratify=cl)
global_ = PLSRegression(modelo['nlv']).fit(Xsg[tr], y[tr])

linhas = []
for c in np.unique(cl):
    itr, ite = tr[cl[tr] == c], te[cl[te] == c]
    gs = GridSearchCV(PLSRegression(), {'n_components': list(range(1, 11))},
                      cv=5, scoring='neg_root_mean_squared_error').fit(Xsg[itr], y[itr])
    linhas.append({'grupo': c, 'n_treino': len(itr), 'n_teste': len(ite),
                   'LVs_local': gs.best_params_['n_components'],
                   'RMSE_global': rmse(y[ite], global_.predict(Xsg[ite]).ravel()),
                   'RMSE_local': rmse(y[ite], gs.best_estimator_.predict(Xsg[ite]).ravel())})
print(pd.DataFrame(linhas).round(2))
```

**Gabarito e observações:** na execução de teste, o erro local foi um pouco menor que o global nos três grupos (por exemplo, de cerca de 2,9 para 2,7 no grupo 0 e de cerca de 5,3 para 4,6 no grupo 1). A diferença é pequena e foi medida em uma única divisão, então não permite concluir que modelos locais sejam melhores. Discutir: modelos locais exigem amostras suficientes em cada grupo, aumentam a complexidade (um modelo por grupo e uma regra de atribuição de novas amostras) e precisam ser comparados com o modelo global em validação independente e repetida.

## Perguntas de verificação

1. **Por que o número de componentes do PCA para predição deve ser escolhido por validação cruzada e não pela variância acumulada?** Porque a variância explicada dos espectros não é a informação relevante para o atributo. O critério correto é o desempenho preditivo.
2. **Por que critérios internos de agrupamento podem discordar?** Medem propriedades diferentes (coesão, separação, ajuste estatístico), e dados contínuos não têm estrutura de grupos bem definida.
3. **Por que a seleção de bandas deve ser feita dentro da validação cruzada?** Porque usar o atributo para escolher bandas com todos os dados deixa a validação conhecer a resposta, o que gera vazamento e desempenho otimista.

## Entregável

Quadro de decisões (número de componentes e critério, método de agrupamento, k escolhido e critérios usados, estabilidade observada) e conclusão sobre a utilidade dos grupos, discutindo se eles têm significado agronômico.
