# Aula 9: Visualização, interpretação e predição

[← Aula 8](aula_08_random_forest_metricas.md) · [Plano do curso](README.md) · [Aula 10 →](aula_10_resultados_apresentacao.md)

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Resumo do plano

**Objetivos:** interpretar os modelos e aplicá-los a amostras novas com segurança.

**Conteúdo:**

- Gráficos de observado versus predito e análise de resíduos.
- Interpretação espectral: coeficientes de regressão e VIP do PLSR, e importância dos componentes no Random Forest.
- Predição de novas amostras: mesmo pré-processamento, reamostragem da grade espectral quando necessário e uso do modelo salvo.
- Domínio de aplicação: T² e Q com limites definidos na calibração e tratamento das amostras fora do domínio.

**Prática:** notebook 05. Aplicar o modelo às novas amostras, identificar as que ficam fora do domínio e discutir se as predições devem ser aceitas.

**Entregável:** tabela de predições com indicação do domínio e figura das novas amostras sobre a nuvem de calibração.

**Perguntas de verificação:** por que predizer uma amostra fora do domínio é extrapolação? O que um VIP maior que 1 indica?

## Material de aula

**Capítulo:** Material e metodologia (visualização e predição) e Resultados. **Notebook:** `05_visualizacao_predicao.ipynb`.

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 35 min: leitura de gráficos de desempenho e interpretação espectral.
- 35 a 75 min: execução comentada das seções 1 a 3 do notebook 05.
- 75 a 105 min: predição de amostras novas e domínio de aplicação (seções 4 e 5).
- 105 a 120 min: exercícios e entregável.

#### Conteúdo

**Observado × predito.** Os pontos devem se distribuir em torno da linha 1:1. Padrões a procurar: compressão dos extremos (subestimação dos valores altos e superestimação dos baixos, comum no Random Forest), dispersão crescente com o valor do atributo (sugere transformação) e grupos com desempenho diferente (no notebook, os pontos são coloridos pelo grupo).

**Resíduos.** O histograma deve ser aproximadamente centrado em zero, e o gráfico de resíduos contra o observado não deve mostrar tendência. Uma tendência indica erro sistemático, e a dispersão crescente indica erro proporcional ao valor.

**Interpretação espectral do PLSR.** Os **coeficientes de regressão** mostram o peso de cada banda na predição, com sinal. O **VIP** (*Variable Importance in Projection*) resume a importância de cada banda, e valores acima de 1 são considerados importantes. O objetivo é conferir se as regiões importantes coincidem com feições conhecidas (1400, 1900 e 2200 nm e a região do visível), o que dá confiança de que o modelo usa informação com sentido físico.

**Importância no Random Forest.** Mostra quais componentes principais mais contribuem. Como cada componente é uma combinação das bandas, a interpretação espectral exige cruzar com os loadings da aula 5.

**Predição de amostras novas.** Três cuidados: (1) aplicar **o mesmo pré-processamento**, na mesma ordem e com os mesmos parâmetros, o que é garantido por `utils.preprocessa` e pelo tratamento guardado no modelo; (2) garantir que as bandas coincidam com as da calibração, e interpolar quando a grade espectral for diferente (`utils.reamostra`); (3) verificar o **domínio de aplicação**.

**Domínio de aplicação.** Um modelo só é confiável para amostras semelhantes às da calibração. Calcula-se o T² e o Q das novas amostras com o PCA do domínio ajustado na calibração e comparam-se com os limites guardados (percentil 99 da calibração). Amostras acima dos limites estão fora do domínio, e suas predições são extrapolações, que devem ser sinalizadas, tratadas com cautela ou descartadas.

#### Prática guiada: notebook 05

1. **Seção 1.** Interpretar os dois gráficos de observado × predito e os títulos com as métricas.
2. **Seção 2.** Interpretar os resíduos e a tabela de RMSE por grupo.
3. **Seção 3.** Interpretar o coeficiente e o VIP do PLSR e a importância dos componentes do Random Forest. No banco sintético, esperar importância nas regiões de 1400, 1900 e 2200 nm para a argila.
4. **Seção 4.** Ler `dados/novas_amostras.csv`, pré-processar e predizer. Observar as colunas `T2`, `Q` e `dentro_dominio` do resultado.
5. **Seção 5.** Interpretar o gráfico das novas amostras sobre a nuvem de calibração.

#### Exercícios

1. **Forçar uma amostra fora do domínio.** Em uma célula nova, depois de ler `Xn`, substituir uma das novas amostras por um espectro aleatório (que não parece um solo) e verificar que ele é sinalizado:

```python
rng = np.random.default_rng(0)
Xn_teste = Xn.copy()
Xn_teste[0] = rng.uniform(0.05, 0.6, Xn.shape[1])     # espectro anômalo

_, Xn_teste_pp = utils.preprocessa(Xn_teste, wl_cal, modelo['tratamento'])
t2_t, q_t = utils.t2_q(modelo['pca_dom'], Xn_teste_pp)
print('Amostra 0: T2 =', t2_t[0].round(1), '| limite =', round(modelo['lim_t2'], 1))
print('Amostra 0: Q  =', q_t[0].round(3), '| limite =', round(modelo['lim_q'], 3))
print('Dentro do domínio?', bool((t2_t[0] <= modelo['lim_t2']) and (q_t[0] <= modelo['lim_q'])))
```

2. **Reamostragem.** Simular uma nova amostra medida com passo de 10 nm (apenas uma banda a cada duas) e verificar que a função reamostra para a grade original:

```python
wl_10 = wl_cal[::2]
Xn_10 = Xn[:, ::2]
Xn_rea = utils.reamostra(Xn_10, wl_10, wl_cal)
print(Xn_rea.shape, '=', Xn.shape)
print('Erro máximo de reamostragem:', np.abs(Xn_rea - Xn).max().round(4))
```

3. **Concordância entre modelos.** Comparar as predições do PLSR e do Random Forest para as novas amostras:

```python
col_pls, col_rf = f'{modelo["alvo"]}_PLSR', f'{modelo["alvo"]}_RF'
print('Correlação:', saida[col_pls].corr(saida[col_rf]).round(3))
print('Diferença média absoluta:', (saida[col_pls] - saida[col_rf]).abs().mean().round(2))
```

4. Escolher uma amostra fora do domínio e outra dentro, e explicar por que cada uma foi classificada assim.

**Gabarito e observações:** (1) o espectro aleatório tem forma muito diferente dos de solo, e o resíduo Q (e normalmente também o T²) fica muito acima do limite, sendo sinalizado. (2) O erro de reamostragem é pequeno, pois os espectros são suaves. (3) A concordância entre os dois modelos é um indicativo de robustez, e grandes diferenças em uma amostra sugerem que ela está perto do limite do domínio. Nesta atividade, as novas amostras do banco sintético vêm da mesma distribuição da calibração, e por isso quase todas ficam dentro do domínio.

#### Perguntas de verificação

1. **Por que predizer uma amostra fora do domínio é extrapolação?** Porque o modelo só viu amostras semelhantes às da calibração e não tem base para prever fora dessa região do espaço espectral.
2. **O que um VIP maior que 1 indica?** Que a banda contribui mais do que a média para o modelo.
3. **Por que os limites de T² e Q são definidos na calibração e não nas novas amostras?** Para que o critério de pertencimento seja independente das amostras que estão sendo avaliadas.

#### Entregável

Tabela de predições com a indicação de domínio, figura das novas amostras sobre a nuvem de calibração e um parágrafo interpretando a importância espectral do modelo.
