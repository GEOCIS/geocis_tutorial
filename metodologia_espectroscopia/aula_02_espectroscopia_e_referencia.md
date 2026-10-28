# Aula 2: Espectroscopia de solos e dado de referência

[← Aula 1](aula_01_delineamento.md) · [Plano do curso](README.md) · [Aula 3 →](aula_03_amostragem_qualidade_exploratoria.md)

**Questão central:** o que o espectro mede e qual o limite imposto pelo laboratório?

**Objetivos:** compreender o que o espectro mede, quais atributos têm resposta espectral direta ou indireta e como o erro do método de laboratório limita a precisão do modelo.

**Tópicos:**

- Reflectância difusa nas regiões Vis, NIR e SWIR: transições eletrônicas (óxidos de ferro, cor), sobretons e combinações de vibrações (água, hidroxila, argilominerais, grupos orgânicos).
- Atributos com resposta espectral direta (argila, matéria orgânica, óxidos) e atributos preditos por correlação indireta (alguns nutrientes, pH).
- Fatores de variabilidade não desejada: umidade, granulometria, rugosidade, instrumento e protocolo de medição.
- O dado de referência: método analítico, erro de laboratório e heterogeneidade entre laboratórios. O erro da referência limita o melhor RMSE possível.
- Bibliotecas espectrais (BSSL): vantagens (grande variabilidade) e riscos (heterogeneidade de origem, método e época).

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).


## Conteúdo

### Reflectância difusa

A luz que atinge uma amostra de solo seca e peneirada penetra poucos micrômetros, é em parte absorvida e em parte espalhada de volta. O espectrorradiômetro mede a razão entre a luz refletida pela amostra e por um padrão branco de referência em cada comprimento de onda, a **reflectância**. A forma do espectro resulta de dois fenômenos:

- **Absorção**, que carrega informação química e mineralógica.
- **Espalhamento**, que depende da granulometria, da rugosidade e da compactação, e altera a altura geral do espectro sem relação direta com o atributo de interesse. É a razão de tratamentos como o SNV.

A lei de Beer-Lambert vale para soluções, e não descreve bem sólidos particulados. Por isso, a transformação para absorbância, A = log10(1/R), é uma aproximação prática, e modelos mais físicos, como o de Kubelka-Munk, são alternativas usadas em alguns trabalhos.

### Origem física das feições

- **Transições eletrônicas** (visível e início do NIR): óxidos de ferro (goethita e hematita) e matéria orgânica determinam a cor e o formato do espectro no visível.
- **Sobretons e combinações de vibrações moleculares** (NIR e SWIR): bandas da água e da hidroxila perto de 1400 e 1900 nm, e dos grupos Al-OH de argilominerais (como a caulinita) perto de 2200 nm. Carbonatos aparecem perto de 2340 nm. Grupos orgânicos (C-H e N-H) têm sobretons e combinações mais fracos, sobrepostos a outros.

As feições de sobretons são largas e sobrepostas, e por isso se usa modelagem multivariada em vez de relacionar uma banda isolada ao atributo.

### Resposta espectral direta e indireta

| Atributo | Tipo de resposta | Base física ou estatística |
| --- | --- | --- |
| Argila | Direta e indireta | Feições de argilominerais e hidroxila; também afeta água e espalhamento |
| Matéria orgânica | Direta | Escurecimento no visível e grupos orgânicos |
| Óxidos de ferro | Direta | Absorções no visível e no início do NIR |
| CTC | Indireta | Correlação com argila, mineralogia e matéria orgânica |
| pH | Indireta | Correlação com mineralogia e matéria orgânica |
| Nutrientes (P, K, Ca, Mg) | Indireta, em geral | Correlações com atributos que têm resposta direta |

Atributos de resposta indireta costumam ser menos predizíveis e mais dependentes do conjunto de amostras: um modelo apoiado em correlações indiretas pode falhar quando a relação entre os constituintes muda de uma região para outra. Esse é um ponto de atenção ao interpretar e transferir modelos.

### Fatores que alteram o espectro e não são o atributo

- **Umidade:** a água absorve fortemente e mascara outras feições (as bandas de água dominam o espectro em amostras úmidas). Por isso as amostras são secas (por exemplo, em estufa a temperatura moderada ou ao ar) antes da medição.
- **Granulometria e rugosidade:** alteram o espalhamento e o nível geral do espectro.
- **Instrumento e protocolo:** resolução, passo, sonda, geometria de medição, calibração com referência branca, número de leituras, preparo da amostra (secagem, destorroamento e peneiramento) e deriva do equipamento. Diferenças entre laboratórios geram variações sistemáticas.

Por isso o protocolo de medição deve ser padronizado e registrado.

### O dado de referência

Os valores de laboratório que servem de "verdade" também têm erro (variabilidade entre repetições e entre laboratórios). Exemplos: a argila varia conforme o método (pipeta, densímetro), o preparo e a dispersão; a matéria orgânica depende do método (oxidação úmida ou combustão seca). Em uma biblioteca compilada, a variação entre laboratórios e métodos soma-se ao erro de cada um. O modelo espectral aprende a reproduzir esse valor, **incluindo o seu erro**.

Se o erro da referência (desvio-padrão σ) é independente do erro do modelo, os erros se somam em termos de variância, e o RMSE medido contra a referência é, aproximadamente:

```latex
RMSE_{obs}^{2} \approx RMSE_{modelo}^{2} + \sigma_{ref}^{2}
```

Consequências:

- **o melhor RMSE alcançável tem um piso imposto pelo erro de laboratório**, e o RPD tem um teto, por mais perfeito que seja o modelo;
- uma diferença pequena entre modelos pode ser apenas ruído da referência;
- atributos com métodos de referência mais variáveis (alguns químicos) tendem a ter desempenho menor.

### Bibliotecas espectrais compiladas

Bibliotecas como a BSSL reúnem dados de projetos diferentes, o que traz variabilidade útil, mas também heterogeneidade de método analítico, de protocolo espectral e de época. Registrar e, se possível, modelar a origem das amostras é uma boa prática.

## Atividade 1: anotar um espectro

Visualizar o espectro médio e marcar as regiões das feições esperadas:

```python
media = Xsg.mean(axis=0)       # absorbância suavizada média
plt.figure(figsize=(8, 3.6))
plt.plot(wl, media)
for nm, rotulo in [(1400, 'água / OH'), (1900, 'água'), (2200, 'Al-OH (argilominerais)')]:
    plt.axvline(nm, ls='--', c='gray')
    plt.text(nm - 15, media.max(), rotulo, rotation=90, va='top', ha='right')
plt.xlabel('Comprimento de onda (nm)'); plt.ylabel('Absorbância')
plt.tight_layout(); plt.show()
```

Pedir que os alunos descrevam o que aparece em cada região e que atributos esperam predizer bem. Observação: no banco sintético, só as feições de 1400, 1900 e 2200 nm foram simuladas. Em espectros reais há mais feições e sobreposições.

## Atividade 2: o erro da referência limita o desempenho

Simular o efeito de um erro de laboratório nos valores observados da validação, mantendo as predições do modelo (simulando laboratórios menos precisos).

**2a. Com o PLSR treinado na hora**, comparando com o valor previsto pela fórmula:

```python
pls = PLSRegression(nlv).fit(Xtr, ytr)
pred = pls.predict(Xte).ravel()

rng = np.random.default_rng(0)
linhas = []
for s in (0, 2, 4, 8):                         # desvio-padrão do erro de referência
    y_obs = yte + rng.normal(0, s, len(yte))
    r = utils.avalia(y_obs, pred)
    linhas.append({'DP do erro de referência': s, 'RMSE': r['RMSE'], 'R2': r['R2'], 'RPD': r['RPD']})

tab = pd.DataFrame(linhas)
tab['RMSE previsto pela fórmula'] = np.sqrt(tab.loc[0, 'RMSE'] ** 2 + tab['DP do erro de referência'] ** 2)
print(tab.round(2))
```

**Resultado de referência (dados sintéticos):** o RMSE sobe de cerca de 3,5 (sem erro adicional) para 4,0, 5,2 e 8,2 quando o desvio-padrão do erro de referência é 2, 4 e 8, e o R² cai de cerca de 0,97 para 0,86. Os valores previstos pela fórmula ficam próximos dos observados (cerca de 4,0, 5,3 e 8,7).

**2b. Com as predições salvas pelo notebook 04:**

```python
rng = np.random.default_rng(0)
pred = pd.read_csv(cfg.PASTA / 'predicoes_validacao.csv')

for sd in (0, 1, 2, 4, 8):                       # desvio-padrão do erro da referência
    obs_ruido = pred.observado + rng.normal(0, sd, len(pred))
    m = utils.avalia(obs_ruido, pred.pred_PLSR)
    print(f'erro de referência = {sd}: RMSE = {m["RMSE"]:.2f} | R² = {m["R2"]:.3f} | RPD = {m["RPD"]:.2f}')
```

**Resultado de referência:** o RMSE passou de cerca de 2,9 (sem erro de referência) para cerca de 8,5 com desvio-padrão de 8, e o RPD caiu de cerca de 7 para cerca de 2,6, sem nenhuma mudança no modelo. Conferir a relação: com desvio de 8, a raiz de 2,9² + 8² dá cerca de 8,5.

**Lição:** em dados reais, parte do erro atribuído ao modelo vem do laboratório, e o RPD de dados reais depende da qualidade da referência.

## Atividade 3: análise de um protocolo de medição

Em duplas, listar o que deve ser padronizado em um protocolo de medição (secagem, peneira, referência branca, número de repetições, ordem das medições) e justificar cada item pelo tipo de variabilidade que ele controla.

## Exercícios

1. Para o atributo escolhido na aula 1, listar o método de laboratório usado, a incerteza típica do método (consultando a literatura ou o laboratório) e discutir o que isso implica para o RMSE esperado.
2. Usando a fórmula, calcular o RMSE esperado de um modelo com RMSE verdadeiro de 3,0 contra uma referência com desvio-padrão de 4,0. E o RPD, se o desvio-padrão do atributo for 15?
3. Duas equipes comparam modelos para matéria orgânica e obtêm RMSE de 4,8 e 5,0. A referência tem desvio-padrão de 4,0. A diferença é relevante?

<details>
<summary>Gabarito</summary>

2. RMSE esperado = raiz de (9 + 16) = 5,0, e o RPD = 15/5,0 = 3,0.
3. Não necessariamente. O erro da referência já explica boa parte do RMSE (a raiz de 4,8² - 4,0² é cerca de 2,7, e a de 5,0² - 4,0² é 3,0), e uma diferença de 0,2 no RMSE observado é pequena em relação à variabilidade entre divisões dos dados (aula 7). Recomenda-se repetir a avaliação e analisar a incerteza antes de concluir.

</details>

## Perguntas de verificação

1. **Por que não se usa uma única banda para predizer o atributo?** Porque as feições são largas e sobrepostas, e o sinal de um constituinte se espalha por várias bandas. A modelagem multivariada combina essa informação.
2. **O que significa predizer um atributo por correlação indireta e qual o risco?** O atributo não tem feição própria e é predito por sua associação com um constituinte que tem. Se a associação mudar entre regiões ou solos, o modelo perde desempenho.
3. **Como o erro do laboratório afeta o RPD?** Soma-se à variância do erro do modelo, aumentando o RMSE observado e reduzindo o RPD, independentemente da qualidade do modelo.
4. **O que a fórmula do RMSE indica sobre a comparação entre modelos?** Que o erro da referência impõe um piso ao RMSE, e que diferenças pequenas entre modelos podem estar dentro do ruído do laboratório.
5. **Como o espalhamento afeta o espectro e o que se faz a respeito?** Altera a altura e a inclinação gerais do espectro sem relação com o atributo, e é tratado com SNV, MSC ou derivadas.

## Leituras

STENBERG et al. (2010), revisão sobre espectroscopia Vis-NIR em ciência do solo. (Conferir os dados completos da referência.)

## Entregável

Quadro que relaciona o atributo escolhido, a feição espectral esperada, o tipo de resposta (direta ou indireta), o método de referência, sua incerteza e a expectativa de desempenho, com justificativa, e o resultado da atividade 2 com um parágrafo de interpretação.
