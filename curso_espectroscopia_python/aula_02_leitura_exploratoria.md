# Aula 2: Leitura e análise exploratória

[← Aula 1](aula_01_espectroscopia_bssl_fluxo.md) · [Plano do curso](README.md) · [Aula 3 →](aula_03_preprocessamento_I.md)

**Capítulo:** Leitura e análise exploratória/descritiva. **Notebook:** `01_leitura_exploratoria.ipynb`.

**Materiais:** notebook 01, dados sintéticos (ou banco real).

**Objetivos:** conhecer a estrutura do banco e avaliar a qualidade dos dados antes de modelar.

**Tópicos:**

- Leitura do CSV com pandas e separação de colunas espectrais e de atributos.
- Estatística descritiva (`describe`), distribuição e assimetria do atributo-alvo.
- Valores faltantes: diagnóstico e decisão de tratamento.
- Espectros brutos: forma geral, feições de absorção, espectro médio ± desvio-padrão e correlação por banda com o atributo.

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 30 min: por que explorar antes de modelar; conceitos de análise exploratória e qualidade de dados.
- 30 a 90 min: execução comentada do notebook 01, seção por seção.
- 90 a 110 min: exercícios com outro atributo e com alteração de parâmetros.
- 110 a 120 min: resumo e entregável.

## Conteúdo

A análise exploratória responde, antes de modelar, a perguntas que decidem o resto do trabalho: o que há no banco? Há amostras suficientes? Os dados estão completos ou há algo faltando ou estranho? A distribuição do atributo é adequada? Os espectros têm a forma esperada e há anomalias? Os conceitos centrais são estatística descritiva (média, desvio-padrão, quartis e assimetria), valores faltantes e inspeção visual dos espectros.

Pontos a destacar:

- **Assimetria:** valores de assimetria muito distantes de zero indicam cauda longa. Para atributos como matéria orgânica, é comum. Isso pode justificar uma transformação (por exemplo, logaritmo) antes da modelagem.
- **Faltantes:** cada atributo é modelado com as amostras que têm o seu valor medido. Isso explica por que o tamanho da amostra varia entre atributos.
- **Espectros brutos:** servem para verificar a forma, o ruído nas extremidades e a presença de espectros estranhos.
- **Correlação por banda:** mostra em quais regiões o espectro se relaciona com o atributo, e antecipa onde o modelo vai se apoiar.

**O que cada seção do notebook faz e o que observar:**

- **Seção 1 (leitura):** lê o CSV e separa as colunas espectrais (nome numérico) das de atributos com `utils.identificar_colunas`, e extrai os comprimentos de onda com `utils.comprimentos_onda`, que exige ordem crescente. Observar: o número de bandas e a faixa espectral.
- **Seção 2 (estatística e faltantes):** `describe()` mostra média, desvio, mínimo, quartis e máximo; a tabela de faltantes mostra a proporção de valores ausentes. Observar valores impossíveis (por exemplo, argila acima de 100) e atributos com muita ausência.
- **Seção 3 (limpeza):** remove amostras sem o atributo-alvo e com bandas ausentes. Cada atributo usa o seu subconjunto de amostras. Observar a assimetria (`skew`): valores acima de 1 em módulo sugerem distribuição bem assimétrica.
- **Seção 4 (distribuição):** histograma e boxplot do atributo. Observar caudas longas e possíveis grupos.
- **Seção 5 (espectros brutos):** 50 espectros e o espectro médio com faixa de desvio-padrão. Observar feições, ruído nas pontas e espectros fora do padrão.
- **Seção 6 (correlação por banda):** correlação de cada banda com o atributo, calculada de forma vetorizada. Observar as regiões do espectro mais associadas ao atributo.
- **Seção 7 (salvar):** grava `dados_brutos.npz` e `df_limpo.pkl` para o notebook 02.

**Referência com os dados sintéticos:** 900 amostras com 431 bandas (350 a 2500 nm); 40 sem argila, restando 860; assimetria da argila de cerca de 0,75.

## Prática guiada: o notebook 01, célula a célula

Executar com `Shift+Enter`, comentando cada resultado e pedindo previsão antes de cada um ("o que vocês esperam ver?"):

1. **Leitura e separação de colunas.** A função `utils.identificar_colunas` classifica como espectrais as colunas cujo nome é numérico. Conferir que o resultado mostra 431 bandas, de 350 a 2500 nm, e as colunas de atributos `id`, `argila` e `mo`.
2. **Estatística descritiva e faltantes.** Observar `describe()` e a tabela de faltantes (`argila` tem cerca de 4,4% de valores ausentes, por construção).
3. **Limpeza.** Observar a mensagem de amostras antes e depois (900 para cerca de 860). Discutir por que as amostras sem alvo são removidas.
4. **Distribuição do alvo.** Interpretar o histograma e o boxplot, e a assimetria impressa.
5. **Espectros brutos.** Ver os 50 espectros e a média ± desvio-padrão. Notar a diferença de altura entre espectros (efeito de espalhamento) e o aumento da reflectância com o comprimento de onda.
6. **Correlação por banda.** No banco sintético, esperar correlação negativa em torno de 1400, 1900 e 2200 nm, pois mais argila reduz a reflectância nessas bandas.
7. **Saídas.** Conferir que `resultados/dados_brutos.npz` e `resultados/df_limpo.pkl` foram criados.

Depois, em uma célula extra, mostrar como investigar um valor suspeito:

```python
# amostras com argila fora de 0 a 100 (se existirem)
suspeitas = df[(df[cfg.COL_ALVO] < 0) | (df[cfg.COL_ALVO] > 100)]
print(len(suspeitas), "amostras suspeitas")

# distribuição por intervalos
print(pd.cut(df[cfg.COL_ALVO], bins=[0, 15, 35, 60, 100]).value_counts().sort_index())
```

## Exercícios

1. Trocar `COL_ALVO` para `"mo"` em `config.py` e executar de novo o notebook. Comparar a distribuição e a assimetria com a da argila. A matéria orgânica exigiria transformação?
2. Comparar o gráfico de correlação por banda dos dois atributos. Em que regiões a correlação muda de sinal ou é mais forte?
3. Calcular o coeficiente de variação (desvio-padrão dividido pela média) de cada atributo e discutir qual teria mais variabilidade a ser explicada.
4. Explicar por que remover amostras apenas para o atributo modelado, e não de todo o banco, é uma boa prática.
5. Em uma célula nova, calcular quantas amostras têm reflectância máxima acima de 0,6 e plotar uma delas:

```python
max_por_amostra = X.max(axis=1)
print((max_por_amostra > 0.6).sum(), 'amostras com reflectância máxima acima de 0,6')

i = max_por_amostra.argmax()
plt.plot(wl_orig, X[i]); plt.xlabel('nm'); plt.ylabel('Reflectância')
plt.title(f'Amostra {i}'); plt.show()
```

6. Em uma célula nova, listar as cinco bandas de maior correlação absoluta com o alvo:

```python
idx = np.argsort(-np.abs(corr))[:5]
for i in idx:
    print(f'{wl_orig[i]:.0f} nm  r = {corr[i]:.2f}')
```

<details>
<summary>Gabarito comentado</summary>

- (1) Com os dados sintéticos, a matéria orgânica tem distribuição mais assimétrica e valores mais altos. Se a assimetria for forte e as caudas longas, uma transformação logarítmica pode ser testada, avaliando o efeito nas métricas.
- (2) A matéria orgânica no banco sintético escurece o espectro inteiro (efeito multiplicativo), então a correlação tende a ser negativa e mais distribuída ao longo do espectro, enquanto a argila concentra a correlação nas bandas de absorção.
- (3) `df[cols_ref].std() / df[cols_ref].mean()` dá o coeficiente de variação (para colunas numéricas).
- (4) O mesmo banco serve a vários atributos, cada um com suas ausências, e descartar amostras de todo o banco por falta de um atributo desperdiçaria informação.
- (5) Os espectros anômalos gerados aleatoriamente costumam ter reflectâncias altas e formas irregulares.
- (6) As bandas de maior correlação ficam em torno das feições de 1400, 1900 e 2200 nm.

</details>

## Problemas comuns

- **A coluna alvo não é encontrada:** o nome em `COL_ALVO` precisa ser idêntico ao do CSV, com atenção a maiúsculas e acentos.
- **Colunas espectrais não reconhecidas:** os nomes das bandas devem ser numéricos; se houver prefixo (por exemplo, `X350`), preencher `PREFIXO`.
- **Erro de ordem das bandas:** `comprimentos_onda` exige ordem crescente; reordenar as colunas se necessário.
- **Números lidos como texto:** CSV com vírgula decimal exige `pd.read_csv(..., decimal=",", sep=";")`.

## Perguntas de verificação

1. **Quando uma distribuição assimétrica pede transformação?** Quando a cauda longa faz poucos valores altos dominarem o erro, ou quando os resíduos do modelo ficam heterogêneos. Transformações como o logaritmo reduzem a assimetria, mas as métricas passam a ser calculadas na escala transformada, a menos que se retorne à escala original.
2. **Por que remover amostras sem o atributo apenas para aquele atributo?** Porque descartar amostras de todos os atributos reduziria o banco sem necessidade. Cada modelo usa o que tem de dado válido.
3. **O que uma correlação alta entre banda e atributo garante?** Indica associação, mas não causalidade nem predição fora da amostra. O modelo é que verifica o poder preditivo.

## Entregável

Relatório de uma página com a tabela descritiva do atributo, o histograma, o gráfico dos espectros brutos comentado e dois parágrafos de interpretação (qualidade dos dados e regiões espectrais mais relacionadas ao atributo, incluindo as bandas mais correlacionadas).
