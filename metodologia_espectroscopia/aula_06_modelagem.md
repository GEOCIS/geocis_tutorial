# Aula 6: Modelagem preditiva

[← Aula 5](aula_05_dimensionalidade_agrupamento.md) · [Plano do curso](README.md) · [Aula 7 →](aula_07_validacao_metricas_incerteza.md)

**Questão central:** como escolher e ajustar um modelo sem sobreajuste?

**Objetivos:** escolher e ajustar modelos controlando o compromisso entre viés e variância.

**Tópicos:**

- Regressão linear múltipla, regressão por componentes principais (PCR) e PLSR: o que cada uma faz e por que o PLSR é a referência em quimiometria.
- Escolha do número de variáveis latentes: subajuste, sobreajuste e a regra do erro-padrão.
- Modelos de aprendizado de máquina: Random Forest (conjuntos de árvores), SVR, Cubist e redes neurais, e quando cada um tende a ser vantajoso.
- Hiperparâmetros e busca (grade e aleatória), sempre com validação cruzada dentro da calibração.
- Modelos globais versus locais, e o efeito do tamanho da amostra de calibração (curva de aprendizado).
- Parcimônia: preferir o modelo mais simples que atende ao critério de sucesso.

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).

## Conteúdo

### Viés e variância

O erro de um modelo se decompõe em viés (simplificação excessiva, o modelo não captura a relação) e variância (sensibilidade excessiva aos dados de treino, o modelo segue o ruído). Modelos simples têm viés alto e variância baixa, e modelos flexíveis, o contrário. O objetivo é a complexidade em que o erro em dados novos é mínimo. O sinal prático é a diferença entre o erro de treino e o de validação: uma diferença grande indica variância alta (sobreajuste).

### A família de modelos para espectros

| Modelo | Característica | Quando tende a ser vantajoso |
| --- | --- | --- |
| PLSR | Linear, interpretável, poucos parâmetros | Relações aproximadamente lineares e poucas amostras |
| PCR | Linear, usa componentes de maior variância | Quando a informação está nos primeiros componentes |
| Random Forest | Conjunto de árvores, captura não linearidades | Muitas amostras, relações não lineares e interações |
| SVR | Kernel, flexível, sensível a escala e a parâmetros | Relações não lineares com ajuste cuidadoso |
| Cubist | Árvores com regressões lineares nas folhas | Muito usado em ciência do solo; não faz parte do scikit-learn |
| Redes neurais (incluindo convolucionais) | Muito flexíveis | Bancos grandes, como a BSSL completa, e com cuidado contra sobreajuste |

Não há modelo universalmente melhor. A escolha é empírica, por atributo, e é sempre justificada em validação.

### Hiperparâmetros

Parâmetros que não são aprendidos diretamente dos dados (número de LVs, número de árvores, `max_features`, `C` do SVR etc.). Devem ser ajustados por validação cruzada na calibração, com busca em grade ou aleatória. A validação final não participa.

### Parcimônia

Entre modelos de desempenho equivalente, preferir o mais simples (menos LVs, menos parâmetros). Isso favorece a robustez e a interpretação, e é formalizado na regra do erro-padrão.

### Efeito do tamanho da calibração

A curva de aprendizado mostra o erro de validação em função do número de amostras de treino. Se a curva ainda cai, mais amostras ajudariam. Se estabilizou, o limite é o modelo ou o ruído. Modelos flexíveis costumam se beneficiar mais de bancos grandes.

### Modelos globais e locais

Um modelo global usa todas as amostras. Modelos locais usam subconjuntos (por grupo, região ou semelhança espectral) e podem capturar relações específicas, mas exigem amostras suficientes em cada subconjunto (ver a atividade 3 da aula 5).

## Atividade 1: curvas de aprendizado de três modelos

```python
from sklearn.model_selection import learning_curve
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

modelos = {
    'PLSR': PLSRegression(modelo['nlv']),
    'Random Forest': Pipeline([('pca', PCA(20)),
                               ('rf', RandomForestRegressor(200, random_state=0, n_jobs=-1))]),
    'SVR': Pipeline([('pca', PCA(20)), ('sc', StandardScaler()), ('svr', SVR(C=10))]),
}

plt.figure(figsize=(8, 4))
for nome, mod in modelos.items():
    n_amostras, treino, validacao = learning_curve(
        mod, Xsg, y, train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0], cv=5,
        scoring='neg_root_mean_squared_error', shuffle=True, random_state=0)
    linha, = plt.plot(n_amostras, -validacao.mean(axis=1), 'o-', label=f'{nome} (validação)')
    plt.plot(n_amostras, -treino.mean(axis=1), '--', c=linha.get_color(), label=f'{nome} (treino)')
plt.xlabel('Amostras de treino'); plt.ylabel('RMSE'); plt.legend(fontsize=8); plt.tight_layout(); plt.show()
```

**Gabarito e observações:** na execução de teste, o PLSR ficou praticamente plano em torno de 2,9 de RMSE, com erro de treino e de validação muito próximos (modelo simples, que já aprendeu o que podia com poucas amostras). O Random Forest teve erro de validação decrescente (de cerca de 4,3 para cerca de 2,7) e erro de treino muito menor (cerca de 1,0), uma diferença grande que indica variância alta. O SVR ficou com erro maior (cerca de 5,3 no maior tamanho), pois não foi ajustado. Discutir: a forma das curvas mostra se mais amostras ajudariam, e a distância entre treino e validação mostra o sobreajuste. O SVR sem ajuste de hiperparâmetros não é uma comparação justa, e comparar modelos exige ajustar cada um.

## Atividade 2: ajuste justo do SVR

Ajustar `C` e `gamma` do SVR por busca com validação cruzada e comparar com o PLSR em uma divisão separada:

```python
tr, te = train_test_split(np.arange(len(y)), test_size=0.3, random_state=0)
pipe_svr = Pipeline([('pca', PCA(20)), ('sc', StandardScaler()), ('svr', SVR())])
espaco = {'svr__C': [1, 10, 100, 1000], 'svr__gamma': ['scale', 0.01, 0.001], 'svr__epsilon': [0.1, 1.0]}
busca = GridSearchCV(pipe_svr, espaco, cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1).fit(Xsg[tr], y[tr])
print('Melhores parâmetros:', busca.best_params_)

pls = PLSRegression(modelo['nlv']).fit(Xsg[tr], y[tr])
print('SVR ajustado :', {k: round(float(v), 2) for k, v in utils.avalia(y[te], busca.predict(Xsg[te])).items()})
print('PLSR         :', {k: round(float(v), 2) for k, v in utils.avalia(y[te], pls.predict(Xsg[te]).ravel()).items()})
```

**Gabarito:** na execução de teste, o SVR ajustado (com C de 1000, gamma de 0,001 e epsilon de 1,0) obteve RMSE de cerca de 2,35, contra cerca de 2,57 do PLSR na mesma divisão. Isso é uma melhora grande em relação ao SVR sem ajuste (cerca de 5,3 na atividade anterior) e uma diferença pequena em relação ao PLSR, medida em uma única divisão, o que não basta para concluir que um modelo é melhor (ver aula 7). O objetivo é mostrar que a comparação entre algoritmos só é válida se cada um tiver recebido o mesmo esforço de ajuste.

## Atividade 3: decisão de modelagem

Cada aluno escolhe o modelo final para o seu atributo (comparando ao menos PLSR e Random Forest) com base em: desempenho em validação cruzada, estabilidade, simplicidade, interpretabilidade e custo computacional, e escreve a justificativa em um parágrafo, discutindo quando a complexidade adicional se justifica e indicando o que o faria mudar de ideia.

## Perguntas de verificação

1. **Como a curva de aprendizado ajuda a decidir se mais amostras valem a pena?** Se o erro de validação ainda cai quando o treino aumenta, mais amostras ajudariam. Se estabilizou, o ganho viria de outro modelo ou de dados melhores.
2. **Por que comparar algoritmos sem ajustar hiperparâmetros é injusto?** Porque o desempenho de modelos flexíveis depende fortemente dos hiperparâmetros, e o ranking pode refletir apenas o esforço de ajuste.
3. **O que indica uma grande distância entre o erro de treino e o de validação?** Variância alta, ou seja, sobreajuste.

## Entregável

Curvas de aprendizado comparadas, tabela de desempenho dos modelos ajustados e justificativa da escolha do modelo final.
