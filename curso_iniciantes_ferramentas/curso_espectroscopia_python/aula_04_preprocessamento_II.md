# Aula 4: Pré-processamento II (SNV e outliers)

[← Aula 3](aula_03_preprocessamento_I.md) · [Plano do curso](README.md) · [Aula 5 →](aula_05_pca.md)

**Capítulo:** Pré-processamento. **Notebook:** `02_preprocessamento.ipynb` (seções 2 e 3).

**Materiais:** notebook 02, saídas do notebook 01.

**Objetivos:** corrigir efeitos de espalhamento e identificar espectros atípicos com critério.

**Tópicos:**

- SNV: efeito sobre a dispersão entre espectros e ausência de vazamento de informação (usa apenas estatísticas do próprio espectro).
- Outliers: z-score do espectro médio, T² de Hotelling e resíduo Q no PCA.
- Princípio: decidir pelos espectros, nunca pelo valor do atributo-alvo, e registrar o que for removido.

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 35 min: SNV e efeitos de espalhamento.
- 35 a 65 min: critérios de detecção de outliers (z-score, T² e Q).
- 65 a 100 min: execução comentada da detecção e inspeção das amostras sinalizadas.
- 100 a 115 min: sensibilidade dos limites.
- 115 a 120 min: resumo e entregável.

## Conteúdo

### SNV (*Standard Normal Variate*)

Para cada espectro, subtrai-se a sua média e divide-se pelo seu desvio-padrão. Remove diferenças de intensidade geral e de amplitude entre espectros, causadas por espalhamento (granulometria, compactação e empacotamento da amostra). Como usa apenas estatísticas do próprio espectro, não depende do conjunto de dados e **não vaza informação** entre calibração e validação.

Cuidado: o SNV não deve ser aplicado a um espectro constante (desvio-padrão zero), que resultaria em divisão por zero.

### Detecção de outliers

Espectros muito diferentes do conjunto prejudicam o PCA e os modelos. O notebook combina três critérios:

- **z-score do espectro médio:** distância da média de cada espectro à média geral, em desvios-padrão (limite `Z_OUTLIER = 3`). Pega espectros com intensidade global muito diferente.
- **T² de Hotelling:** distância de Mahalanobis da amostra ao centro da nuvem, no espaço dos primeiros componentes principais (`N_PCS_OUTLIER`). Detecta amostras extremas, mas coerentes com o padrão espectral.
- **Resíduo Q (resíduo de reconstrução):** parte do espectro que os componentes retidos não reproduzem. Detecta espectros com feições anômalas (por exemplo, contaminação ou erro de medição).

Os limites de T² e Q são o percentil `PERC_OUTLIER` (99). A amostra é sinalizada se ultrapassar qualquer um dos três limites.

### Pontos de método

- **Atenção:** por definição, um limite no percentil 99 sempre sinaliza cerca de 1% das amostras, mesmo que não haja outlier nenhum. Por isso, a sinalização é um ponto de partida, e **a inspeção visual é obrigatória** antes de remover.
- **Regra de ouro:** a decisão se baseia nos espectros, nunca no valor do atributo-alvo, para não selecionar amostras que favoreçam o modelo.
- Toda exclusão deve ser registrada (quantas, quais e por quê).

**Referência com os dados sintéticos:** 9 amostras sinalizadas pelo z-score, 9 por T² e 9 por Q, em um total de 17 sinalizadas. O banco tem 8 espectros anômalos inseridos de propósito. Após a remoção, restam 843 de 860 amostras.

## Prática guiada

1. Executar as seções 2 e 3 do notebook 02 (detecção de outliers).
2. No gráfico T² × Q (pontos vermelhos fora dos limites), interpretar as quatro regiões: baixo T² e baixo Q (normal); alto T² e baixo Q (extremo, mas coerente); baixo T² e alto Q (feição anômala); alto T² e alto Q (muito atípico).
3. Observar o gráfico dos espectros sinalizados (em vermelho) contra os normais.
4. Olhar a tabela das amostras removidas (`df.loc[out, cols_ref]`) e discutir cada uma.
5. **Inspecionar as amostras sinalizadas** em uma célula extra:

```python
idx_out = np.where(out)[0]
print("Sinalizadas:", len(idx_out))

resumo = pd.DataFrame({"z": z[idx_out], "T2": t2[idx_out], "Q": q[idx_out]}, index=df.index[idx_out])
display(resumo.sort_values("Q", ascending=False).head(10).round(3))

fig, ax = plt.subplots(1, 3, figsize=(15, 3.5), sharey=True)
for a, i in zip(ax, idx_out[:3]):
    a.plot(wl, X_suav[~out][:40].T, c="lightgray", lw=0.4)
    a.plot(wl, X_suav[i], c="red")
    a.set_title(f"Amostra {i}")
plt.show()
```

6. **Classificar cada amostra sinalizada** em: erro de medição, amostra extrema legítima (por exemplo, um solo realmente diferente) ou dúvida, e justificar a decisão de remover ou manter.

### Experimento: sensibilidade do limite

Em uma célula nova, depois de calcular `z`, `t2` e `q`, variar o percentil:

```python
for perc in (95, 99, 99.9):
    lt2, lq = np.percentile(t2, perc), np.percentile(q, perc)
    out_p = (z > cfg.Z_OUTLIER) | (t2 > lt2) | (q > lq)
    print(f'percentil {perc:>5}: {out_p.sum():>3} amostras sinalizadas')

# as 10 amostras de maior T2 e de maior Q
print('Maiores T2:', np.argsort(-t2)[:10])
print('Maiores Q: ', np.argsort(-q)[:10])
```

## Exercícios

1. Alterar `PERC_OUTLIER` para 95, 99 e 99,9 (ou executar o experimento acima) e registrar quantas amostras são sinalizadas em cada caso. Explicar por que o número diminui com limites mais altos. Qual limite é mais razoável e por quê?
2. Verificar se os espectros anômalos do banco sintético (gerados nas 8 primeiras linhas do arquivo original) foram detectados. Como algumas dessas linhas podem ter sido removidas na limpeza do notebook 01 (se o valor de `argila` estava ausente), a comparação deve usar o `id` das amostras:

```python
ids_anomalos = [f'S{i:04d}' for i in range(8)]
sinalizados = df.loc[out, 'id'].tolist()
print('Detectados:', [i for i in ids_anomalos if i in sinalizados])
print('Presentes no banco e não detectados:',
      [i for i in ids_anomalos if i in df['id'].values and i not in sinalizados])
```

3. Classificar cada amostra removida como erro de medição, amostra extrema legítima ou dúvida, e justificar a decisão de mantê-la ou removê-la.
4. Executar o pipeline mantendo e removendo as amostras sinalizadas e comparar o RMSECV do PLSR no notebook 04 (aula 7).
5. Explicar a diferença entre uma amostra com T² alto e Q baixo e uma com Q alto.
6. Discutir por que não se deve remover outliers olhando o valor da argila.

<details>
<summary>Gabarito comentado</summary>

- (1) Os números crescem à medida que o percentil diminui: limites de percentil mais altos sinalizam menos amostras. Com 99,9, quase só as anomalias evidentes são sinalizadas; com 95, muitas amostras normais entram. A escolha depende do tamanho do banco e do custo de perder amostras válidas.
- (2) Em um teste com os dados sintéticos, todos os 8 espectros anômalos foram detectados (17 amostras sinalizadas no total, no percentil 99), pois são aleatórios e não têm a forma típica de um espectro de solo.
- (3) No banco sintético, as amostras sinalizadas além dos anômalos costumam ser solos com valores extremos de argila ou de matéria orgânica, que seria sensato manter em um banco real, e esta é uma boa oportunidade para discutir que **nem todo ponto sinalizado é um erro**.
- (5) T² alto com Q baixo: amostra extrema, mas com formato de espectro compatível com o conjunto (por exemplo, um solo muito argiloso). Q alto: o espectro tem feições que os PCs não representam, sugerindo erro de medição ou material diferente.
- (6) Remover amostras com base no alvo seleciona justamente as que o modelo erra, e produz uma avaliação otimista e não confiável.

</details>

## Problemas comuns

- **Divisão por zero no SNV:** espectro constante (desvio-padrão zero). É sinal de medição inválida e deve ser removido.
- **Muitas amostras sinalizadas:** conferir o percentil e se o banco é naturalmente heterogêneo.
- **Índices desalinhados ao remover:** as máscaras booleanas devem ser aplicadas aos mesmos conjuntos (`X`, `y` e `df`); o notebook faz isso na seção 3.

## Perguntas de verificação

1. **Por que remover outliers pelo valor do atributo-alvo seria problemático?** Porque se estaria escolhendo as amostras que o modelo prevê bem, o que torna o desempenho artificialmente otimista.
2. **O que diferencia um T² alto de um Q alto?** O T² mede o quanto a amostra se afasta do centro dentro do espaço dos componentes retidos. O Q mede a parte do espectro que esses componentes não explicam.
3. **O SNV pode causar vazamento de informação?** Não, porque cada espectro é padronizado com a sua própria média e desvio-padrão, sem usar dados de outras amostras.

## Entregável

Tabela das amostras sinalizadas, com a classificação (erro, extrema legítima ou dúvida) e a decisão justificada de remoção ou manutenção, e a contagem de amostras antes e depois da limpeza.
