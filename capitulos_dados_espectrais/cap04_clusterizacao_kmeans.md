# Clusterização espectral: método do cotovelo e k-means

[← Capítulo 3](cap03_pca.md) · [Índice](README.md) · [Capítulo 5 →](cap05_modelagem_plsr_rf.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

## 1. Introdução

Bibliotecas espectrais de solo reúnem amostras de regiões, materiais de origem e classes de solo muito diferentes. Essa heterogeneidade se reflete nos espectros e pode afetar o desempenho de modelos de predição calibrados com todas as amostras de uma só vez. A clusterização é uma técnica de aprendizado não supervisionado que agrupa amostras semelhantes sem usar informação do atributo-alvo, permitindo identificar subgrupos de solos com comportamento espectral parecido.

Neste capítulo, o algoritmo k-means é aplicado aos escores dos primeiros componentes principais, e o número de grupos (k) é escolhido pelo método do cotovelo, complementado por outros indicadores de qualidade do agrupamento.

## 2. Fundamentos do k-means

O k-means particiona as n amostras em k grupos, em um processo iterativo:

1. São escolhidos k centros iniciais (centroides).
2. Cada amostra é atribuída ao centroide mais próximo, em geral pela distância euclidiana.
3. Cada centroide é recalculado como a média das amostras do seu grupo.
4. Os passos 2 e 3 se repetem até que as atribuições deixem de mudar.

O algoritmo minimiza a **inércia**, também chamada de soma dos quadrados intra-grupo (WCSS): a soma das distâncias quadráticas entre cada amostra e o centroide do seu grupo. Quanto menor a inércia, mais compactos são os grupos.

O k-means tem limitações que devem ser consideradas: o número de grupos precisa ser definido antes; o resultado depende da inicialização dos centroides, podendo convergir para soluções locais; e o método tende a formar grupos esféricos e de tamanho semelhante, não sendo adequado para grupos alongados ou de formatos irregulares.

## 3. Dados de entrada

Agrupar diretamente centenas de bandas espectrais correlacionadas é pouco eficiente, pois a distância euclidiana passa a ser dominada por redundância e ruído. Por isso, a clusterização é feita sobre os escores dos primeiros componentes principais (neste projeto, os cinco primeiros), que resumem a maior parte da variação espectral em poucas dimensões:

```python
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

pca = PCA(n_components=10).fit(X_snv)
scores = pca.transform(X_snv)
Z = scores[:, :5]
```

Como os escores já estão em uma mesma escala (as bandas originais compartilham a mesma unidade), não é necessário padronizá-los. Se fossem misturadas variáveis de unidades diferentes (por exemplo, espectros e atributos de laboratório), a padronização seria indispensável.

## 4. Método do cotovelo

A inércia sempre diminui quando k aumenta, chegando a zero quando cada amostra forma o seu próprio grupo. Por isso, o objetivo não é minimizá-la, e sim encontrar o ponto a partir do qual o ganho deixa de compensar o acréscimo de grupos. No método do cotovelo, calcula-se a inércia para uma sequência de valores de k e observa-se o ponto em que a curva muda de inclinação, formando um "cotovelo":

```python
ks = range(1, 11)
inercia = [KMeans(n_clusters=k, n_init=10, random_state=0).fit(Z).inertia_ for k in ks]

plt.plot(ks, inercia, 'o-')
plt.xlabel('Número de grupos (k)')
plt.ylabel('Inércia (WCSS)')
plt.title('Método do cotovelo')
plt.show()
```

O parâmetro `n_init=10` executa o algoritmo dez vezes com inicializações diferentes e mantém a melhor solução, reduzindo o risco de mínimos locais; `random_state` garante a reprodutibilidade dos resultados.

Na prática, o cotovelo nem sempre é nítido, e a escolha de k envolve julgamento. Quando a curva é suave, vale combinar o método com outros critérios:

- **Coeficiente de silhueta**: mede, para cada amostra, quão próxima ela está do seu grupo em comparação com o grupo vizinho mais próximo. Varia de -1 a 1, e valores mais altos indicam grupos mais bem definidos.
- **Interpretabilidade**: o número de grupos deve fazer sentido agronômico e ser compatível com a variabilidade conhecida dos solos da amostra.
- **Tamanho dos grupos**: grupos com pouquíssimas amostras são pouco úteis para calibrar modelos próprios.

```python
from sklearn.metrics import silhouette_score

for k in range(2, 9):
    rotulos = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(Z)
    print(k, round(silhouette_score(Z, rotulos), 3))
```

Em bancos grandes, o cálculo da silhueta pode ser demorado, e é possível estimá-lo em uma subamostra por meio do argumento `sample_size`.

## 5. Aplicação do k-means e visualização dos grupos

Após escolher k com base no cotovelo e nos demais critérios, o modelo final é ajustado e os rótulos dos grupos são adicionados ao banco de dados. Os grupos são então visualizados no espaço dos dois primeiros componentes principais:

```python
K = 3   # definido após inspeção do cotovelo e da silhueta
km = KMeans(n_clusters=K, n_init=10, random_state=0).fit(Z)
df['cluster'] = km.labels_

plt.scatter(Z[:, 0], Z[:, 1], c=km.labels_, cmap='tab10', s=12)
plt.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
            c='black', marker='X', s=120, label='Centroides')
plt.xlabel('PC1'); plt.ylabel('PC2'); plt.legend(); plt.show()
```

Uma ressalva importante: o gráfico mostra apenas duas das cinco dimensões usadas no agrupamento. Grupos que parecem sobrepostos em PC1 e PC2 podem estar bem separados nos demais componentes.

## 6. Caracterização dos grupos

Os grupos só têm utilidade se forem interpretados. Três análises ajudam a descrever o que cada um representa.

**a) Estatística descritiva do atributo por grupo.** Mostra se os grupos diferem quanto ao atributo de interesse e quanto à sua variabilidade:

```python
print(df.groupby('cluster')[COL_ALVO].describe())
```

**b) Espectro médio por grupo.** Revela as feições espectrais que distinguem os grupos, como diferenças de albedo (associadas à matéria orgânica e à cor) e de intensidade das bandas de argilominerais e óxidos de ferro:

```python
for c in range(K):
    plt.plot(wl, X_suav[df['cluster'] == c].mean(axis=0), label=f'Grupo {c}')
plt.xlabel('Comprimento de onda (nm)'); plt.ylabel('Absorbância')
plt.legend(); plt.show()
```

**c) Tamanho dos grupos e outros atributos.** Contar as amostras por grupo (`df['cluster'].value_counts()`) e comparar outros atributos de laboratório, ou informações de origem (região, tipo de solo, profundidade), ajuda a dar significado agronômico aos agrupamentos.

É importante lembrar que os grupos refletem semelhança espectral e não correspondem necessariamente a classes taxonômicas de solo. Seu significado deve ser verificado, e não presumido.

## 7. Uso dos grupos na modelagem

Os resultados da clusterização podem apoiar a modelagem de duas formas:

- **Divisão estratificada dos dados**: ao separar calibração e validação, a seleção das amostras de cada grupo garante que todos os tipos de solo estejam representados nos dois conjuntos, o que torna a avaliação mais confiável.
- **Modelos locais**: calibrar um modelo separado para cada grupo pode melhorar a predição quando os grupos são muito distintos, desde que cada um tenha amostras suficientes. Por outro lado, modelos globais, treinados com todas as amostras, tendem a ser mais robustos quando a variabilidade interna dos grupos é alta ou os grupos são pequenos. A decisão deve ser tomada comparando o desempenho dos dois tipos de modelo em validação independente.

Vale lembrar que, quando a clusterização for usada para dividir os dados, os rótulos dos grupos de uma nova amostra devem ser obtidos com `km.predict`, aplicado aos escores calculados com o mesmo PCA e o mesmo pré-processamento usados na calibração.

## 8. Cuidados metodológicos

1. **Reprodutibilidade**: definir `random_state` e registrar os parâmetros de PCA e k-means, pois a inicialização aleatória pode alterar os grupos.
2. **Escolha de k é subjetiva**: justificar a decisão com mais de um critério (cotovelo, silhueta e interpretação dos grupos).
3. **Pressupostos do algoritmo**: o k-means assume grupos aproximadamente esféricos e de tamanhos semelhantes. Caso a estrutura dos dados seja mais complexa, métodos alternativos, como misturas gaussianas ou clusterização hierárquica, podem ser testados.
4. **Outliers**: espectros atípicos podem deslocar centroides ou formar grupos próprios de uma só amostra. O tratamento de outliers deve ser feito antes da clusterização.
5. **Ausência de verdade de referência**: como a clusterização não é supervisionada, não há acerto ou erro absoluto, e a qualidade do agrupamento é julgada por critérios internos e pela interpretabilidade.

## 9. Síntese e encaminhamentos

O método do cotovelo, apoiado pelo coeficiente de silhueta, orientou a escolha do número de grupos, e o k-means aplicado aos escores do PCA permitiu agrupar as amostras de acordo com a semelhança espectral. A caracterização dos grupos por estatísticas do atributo e por espectros médios ajuda a interpretar sua origem e a decidir sobre o uso de divisão estratificada ou de modelos locais. Com a estrutura do banco compreendida, a etapa seguinte é a calibração e a validação dos modelos de predição com PLSR e Random Forest.
