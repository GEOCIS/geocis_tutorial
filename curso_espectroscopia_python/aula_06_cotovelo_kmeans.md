# Aula 6: Método do cotovelo e k-means

[← Aula 5](aula_05_pca.md) · [Plano do curso](README.md) · [Aula 7 →](aula_07_plsr_validacao_cruzada.md)

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Resumo do plano

**Objetivos:** agrupar amostras por semelhança espectral e escolher o número de grupos com critério.

**Conteúdo:**

- Algoritmo k-means, inércia e sensibilidade à inicialização (`n_init`, `random_state`).
- Método do cotovelo e coeficiente de silhueta, e a subjetividade da escolha de k.
- Caracterização dos grupos: estatísticas do atributo, espectros médios e tamanho dos grupos.
- Usos na modelagem: divisão estratificada e modelos locais.

**Prática:** notebook 03 (seções 2 e 3). Testar diferentes valores de `K` e justificar a escolha com cotovelo, silhueta e interpretação agronômica.

**Entregável:** tabela descritiva por grupo e figura do espectro médio de cada grupo.

**Perguntas de verificação:** grupos espectrais equivalem a classes de solo? Quais são as limitações do k-means?

## Material de aula: versão 1

**Capítulo:** Método do cotovelo e k-means. **Notebook:** `03_pca_clusterizacao.ipynb` (seções 2 e 3).

**Materiais:** notebook 03, saídas das aulas anteriores.

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 35 min: algoritmo k-means, inércia e inicialização.
- 35 a 60 min: cotovelo e silhueta no notebook.
- 60 a 90 min: escolha de K e caracterização dos grupos.
- 90 a 110 min: exercício de comparação de valores de K.
- 110 a 120 min: resumo e entregável.

#### Conteúdo

A clusterização é um método **não supervisionado**: agrupa amostras semelhantes sem usar o atributo-alvo. No projeto, serve para entender a estrutura do banco, estratificar a divisão entre calibração e validação e analisar o erro por grupo.

**k-means em quatro passos:** escolher k centros iniciais; atribuir cada amostra ao centro mais próximo; recalcular cada centro como a média do grupo; repetir até estabilizar. Minimiza a **inércia** (soma dos quadrados das distâncias das amostras aos seus centros). Limitações: precisa de k definido antes, depende da inicialização (por isso `n_init=10` e `random_state`) e assume grupos aproximadamente esféricos.

**Por que usar os escores do PCA:** agrupar centenas de bandas colineares é dominado por redundância e ruído. O notebook agrupa os `N_PCS_CLUSTER` (5) primeiros componentes.

**Escolha de K:**

- **Cotovelo:** a inércia sempre diminui com mais grupos; procura-se o ponto em que a queda perde força. Nem sempre é nítido.
- **Coeficiente de silhueta:** de -1 a 1; valores mais altos indicam grupos mais bem separados. O notebook calcula em uma subamostra de até 5.000 pontos para ser rápido.
- **Interpretabilidade e tamanho dos grupos:** grupos minúsculos servem pouco, e os grupos devem fazer sentido agronômico.

**Caracterização dos grupos (seção 3):** contagem de amostras, estatísticas do atributo por grupo, espectro médio por grupo e gráfico dos grupos no espaço PC1 × PC2. Grupos espectrais **não** são classes taxonômicas de solo.

**Referência com os dados sintéticos:** com K = 3, os grupos têm cerca de 306, 122 e 415 amostras, com argila média próxima de 43, 71 e 20 (a numeração dos grupos pode mudar).

#### Prática guiada

1. Executar a seção 2 do notebook 03 e discutir a curva do cotovelo e da silhueta.
2. Definir `K` em `config.py` conforme a análise e executar a seção 3. Comentar a tabela por grupo e o gráfico de espectros médios.
3. **Comparação com outro método de agrupamento** (célula extra, em subamostra para economizar tempo):

```python
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score

rng = np.random.default_rng(0)
idx = rng.choice(len(Zc), min(500, len(Zc)), replace=False)

hier = AgglomerativeClustering(n_clusters=cfg.K, linkage="ward").fit_predict(Zc[idx])
km_sub = km.labels_[idx]
print("Concordância (ARI) entre k-means e hierárquico:", round(adjusted_rand_score(km_sub, hier), 3))
```

#### Exercícios

1. Executar a seção 3 com K = 2, 3, 4 e 5 e preencher uma tabela com o tamanho dos grupos e a silhueta de cada valor.
2. Escolher o K final e justificar com três critérios (cotovelo, silhueta e interpretação).
3. Mudar `N_PCS_CLUSTER` para 3 e para 10 e observar se os grupos mudam.
4. Discutir se os grupos obtidos podem ser chamados de classes de solo.

**Gabarito comentado:**

- (1) A silhueta tende a ser maior para K = 2 e cair depois; a inércia cai continuamente. O compromisso entre os dois critérios e a interpretação define o K.
- (3) Com poucos PCs, os grupos refletem a variação espectral dominante; com mais PCs, entram variações menores e possivelmente ruído, tornando os grupos menos estáveis.
- (4) Não. Os grupos são definidos só pela semelhança espectral, e seu significado agronômico deve ser verificado com informações de origem (região, classe de solo, material de origem).

#### Problemas comuns

- **Resultados diferentes a cada execução:** esquecer `random_state`.
- **Grupos desbalanceados com poucas amostras:** reduzir K ou reavaliar a necessidade de estratificar.
- **Silhueta lenta:** usar `sample_size`, como no notebook.

#### Entregável

Tabela de K (2 a 5) com tamanho dos grupos e silhueta, o K escolhido com justificativa e o gráfico de espectros médios por grupo.

## Material de aula: versão 2

**Capítulo:** Método do cotovelo e k-means. **Notebook:** `03_pca_clusterizacao.ipynb` (seções 2 e 3).

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: k-means, inércia, cotovelo e silhueta.
- 40 a 75 min: execução comentada das seções 2 e 3 do notebook 03.
- 75 a 105 min: exercícios (variar k e comparar métodos).
- 105 a 120 min: resumo e entregável.

#### Conteúdo

**k-means.** O algoritmo escolhe k centros, atribui cada amostra ao centro mais próximo, recalcula os centros como a média de cada grupo e repete até estabilizar. Minimiza a **inércia** (soma das distâncias quadráticas entre as amostras e o centro do grupo). Limitações: k precisa ser definido antes, depende da inicialização (`n_init` e `random_state`) e assume grupos aproximadamente esféricos e de tamanhos semelhantes.

**Por que agrupar nos escores do PCA?** Centenas de bandas correlacionadas tornam a distância euclidiana pouco informativa. Os cinco primeiros componentes (`N_PCS_CLUSTER = 5`) resumem a variação e reduzem o ruído.

**Escolha de k:**

- **Cotovelo:** a inércia sempre cai quando k aumenta. Procura-se o ponto em que a queda deixa de compensar.
- **Silhueta:** mede, para cada amostra, a proximidade ao próprio grupo em relação ao grupo vizinho (de -1 a 1). Valores próximos de 0,5 ou mais indicam grupos bem definidos, e valores baixos indicam sobreposição.
- **Interpretabilidade e tamanho dos grupos:** os grupos devem fazer sentido agronômico e ter amostras suficientes.

**Atenção didática importante:** no banco sintético, os espectros variam de forma contínua com a argila e a matéria orgânica, **sem grupos naturais**. Mesmo assim, o k-means sempre divide os dados, e a silhueta pode ficar moderada: em uma execução de teste, foi de cerca de 0,6 para k = 2 e caiu gradualmente até cerca de 0,4 para k = 8, sem um cotovelo nítido. Aproveitar para discutir que uma silhueta moderada não prova a existência de grupos reais, pois pode refletir apenas a partição de um contínuo. Em dados reais da BSSL, com solos de origens distintas, a estrutura de grupos tende a ser mais evidente.

#### Prática guiada: notebook 03, seções 2 e 3

1. Executar a célula do cotovelo e da silhueta (`K_MAX = 10`) e interpretar os dois gráficos.
2. Definir `K` em `config.py` (por exemplo, 3) e executar a célula do k-means final.
3. Ler a contagem de amostras por grupo e a estatística do atributo por grupo (`groupby`). Os grupos diferem no atributo?
4. Interpretar o gráfico de escores com os centroides e os espectros médios por grupo.
5. Conferir que `df_pp.pkl` foi atualizado com a coluna `cluster` e que `cluster_model.joblib` foi salvo.

#### Exercícios

1. Testar `K = 2`, `3` e `5`. Para cada um, registrar a silhueta, o tamanho dos grupos e o que muda no gráfico de escores. Escolher um valor e justificar.
2. **Comparar com outro método de agrupamento** (hierárquico) e medir a concordância:

```python
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score

rot_h = AgglomerativeClustering(n_clusters=cfg.K).fit_predict(Zc)
print('Concordância k-means × hierárquico (ARI):', round(adjusted_rand_score(km.labels_, rot_h), 3))
```

3. **Estabilidade:** repetir o k-means com cinco sementes diferentes e medir a concordância entre elas:

```python
rots = [KMeans(cfg.K, n_init=10, random_state=s).fit_predict(Zc) for s in range(5)]
for s in range(1, 5):
    print(f'semente 0 × {s}: ARI = {adjusted_rand_score(rots[0], rots[s]):.3f}')
```

4. Descrever, em um parágrafo, os grupos: tamanho, média do atributo e diferença no espectro médio.

**Gabarito e observações:** (1) em dados sem grupos naturais, a silhueta tende a cair gradualmente quando k aumenta e não mostra um pico claro. Valores moderados (próximos de 0,5) não devem ser lidos como prova de grupos reais. (2) O índice ARI varia de 0 (concordância ao acaso) a 1 (idêntico). Valores moderados entre k-means e hierárquico indicam que os grupos não são bem definidos. (3) Com `n_init=10`, as sementes diferentes tendem a produzir soluções parecidas, e valores de ARI próximos de 1 indicam solução estável. (4) Os grupos do banco sintético se organizam ao longo do gradiente de argila e de matéria orgânica, o que aparece como diferenças de média do atributo entre grupos.

#### Perguntas de verificação

1. **Grupos espectrais equivalem a classes de solo?** Não necessariamente. Refletem semelhança espectral, que pode estar ligada à mineralogia, à matéria orgânica ou à umidade, e precisam ser interpretados.
2. **Quais são as limitações do k-means?** Número de grupos definido de antemão, dependência da inicialização, formato esférico e sensibilidade a outliers.
3. **Como os grupos serão usados na modelagem?** Na aula 7, para estratificar a divisão entre calibração e validação, garantindo que todos os tipos de amostra estejam nos dois conjuntos.

#### Entregável

Tabela descritiva por grupo (n, média e desvio do atributo), figura do espectro médio de cada grupo e justificativa escrita da escolha de k.
