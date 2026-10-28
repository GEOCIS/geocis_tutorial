# Aula 5: Análise de componentes principais

[← Aula 4](aula_04_preprocessamento_II.md) · [Plano do curso](README.md) · [Aula 6 →](aula_06_cotovelo_kmeans.md)

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Resumo do plano

**Objetivos:** reduzir a dimensionalidade dos espectros e interpretar componentes.

**Conteúdo:**

- Ideia geométrica do PCA: eixos de máxima variância, escores e pesos (*loadings*).
- Variância explicada, gráfico de *scree* e critério de número de componentes.
- Gráfico de escores colorido pelo atributo e interpretação dos loadings segundo as feições espectrais.
- Cuidados: variância não é relevância, sensibilidade a outliers e ajuste do PCA só na calibração quando usado em modelos.

**Prática:** notebook 03 (seção 1). Identificar quantos componentes explicam 95% da variância e relacionar os picos dos loadings de PC1 a feições conhecidas.

**Entregável:** gráfico de escores e de loadings com interpretação em um parágrafo.

**Perguntas de verificação:** um atributo pode depender de um componente de baixa variância? Por que o PCA não substitui o PLSR?

## Material de aula: versão 1

**Capítulo:** Análise de Componentes Principais (PCA). **Notebook:** `03_pca_clusterizacao.ipynb` (seção 1).

**Materiais:** notebook 03, saídas do notebook 02.

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: ideia do PCA, escores, loadings e variância explicada.
- 40 a 65 min: execução da seção 1 do notebook 03.
- 65 a 100 min: interpretação dos gráficos e experimento de reconstrução.
- 100 a 120 min: discussão e entregável.

#### Conteúdo

Bandas vizinhas de um espectro medem praticamente a mesma coisa, de modo que as centenas de variáveis são altamente redundantes. O **PCA** encontra novos eixos, não correlacionados entre si, ordenados pela quantidade de variância que explicam.

**Conceitos centrais:**

- **Componente principal (PC):** combinação linear das bandas originais. O PC1 explica a maior variância possível, o PC2 a maior parte do que sobra, de forma perpendicular ao PC1, e assim por diante.
- **Escores:** coordenadas de cada amostra nos PCs. É o que se usa para plotar e agrupar amostras.
- **Pesos (*loadings*):** quanto cada banda contribui para cada PC. Plotados contra o comprimento de onda, indicam quais regiões do espectro definem o componente.
- **Variância explicada:** fração da variação total capturada por cada PC. Em espectros de solo, poucos PCs costumam explicar mais de 95% da variância.
- **Centralização:** o scikit-learn subtrai automaticamente a média de cada banda antes de calcular os PCs. Como as bandas têm a mesma unidade, não se padroniza cada banda.

**O que o notebook faz:** ajusta um PCA com `N_PCS_EXPLORA` componentes (10) sobre os espectros com SNV, mostra a variância explicada e acumulada, plota os escores de PC1 e PC2 coloridos pelo atributo e plota os loadings dos três primeiros PCs.

**Como ler os gráficos:**

- **Gradiente de cor nos escores:** o atributo está associado à variação espectral dominante e deve ser predizível.
- **Agrupamentos separados:** sugerem classes distintas de solo e motivam a clusterização da aula 6.
- **Pontos isolados:** candidatos a outlier.
- **Picos nos loadings:** relacionam o componente a feições conhecidas (água e hidroxila em 1400 e 1900 nm, argilominerais em 2200 nm, cor no visível).

**Cuidados:** variância explicada não é o mesmo que relevância para o atributo, pois um atributo pode depender de componentes de baixa variância. O PCA é sensível a outliers. E quando os escores forem usados em um modelo preditivo, o PCA deve ser ajustado apenas na calibração (o notebook 04 faz isso dentro de um `Pipeline`).

**Referência com os dados sintéticos:** o PC1 explica cerca de 94,1% da variância e 10 PCs acumulam cerca de 96,2%. O PC1 tão dominante reflete a simplicidade dos dados sintéticos, e em dados reais a variância costuma se distribuir em mais componentes.

#### Prática guiada

1. Executar a seção 1 do notebook 03 e comentar a figura de variância (barras e acumulada) e a de escores e loadings.
2. **Experimento de reconstrução:** mostrar que poucos PCs reconstroem bem o espectro (célula extra após a seção 1):

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

i = 0   # amostra a reconstruir
plt.figure(figsize=(8, 3.5))
plt.plot(wl, X_snv[i], c="black", lw=1.5, label="original (SNV)")
for k in (1, 3, 10):
    p = PCA(n_components=k).fit(X_snv)
    rec = p.inverse_transform(p.transform(X_snv[i:i+1]))[0]
    erro = np.sqrt(np.mean((X_snv[i] - rec) ** 2))
    plt.plot(wl, rec, lw=0.9, label=f"{k} PC(s), erro {erro:.3f}")
plt.xlabel("Comprimento de onda (nm)"); plt.legend(); plt.show()
```

3. **Número de componentes por variância acumulada:**

```python
acum = pca.explained_variance_ratio_.cumsum()
n95 = int(np.argmax(acum >= 0.95)) + 1
print("PCs para 95% da variância:", n95)
```

#### Exercícios

1. Colorir os escores de PC1 e PC2 pelo atributo `mo` em vez de `argila` (alterando `COL_ALVO` e reexecutando os notebooks 01 e 02, ou carregando a coluna manualmente) e comparar os padrões.
2. Identificar a região do espectro de maior peso absoluto no PC1 e no PC2 e relacioná-la a uma feição conhecida.
3. Fazer o PCA sem aplicar o SNV (usando `X_suav`) e comparar a variância explicada pelo PC1.
4. Explicar por que o PCA, sozinho, não garante um bom modelo preditivo do atributo.

**Gabarito comentado:**

- (2) Em `pca.components_[0]`, `wl[np.argmax(np.abs(pca.components_[0]))]` indica a banda de maior peso. Com dados reais, é comum encontrar pesos fortes perto de 2200 nm (argilominerais) e no visível.
- (3) Sem o SNV, o PC1 costuma capturar principalmente a diferença global de intensidade entre amostras (efeito de espalhamento), explicando uma fração maior da variância, mas com menos relação com a composição.
- (4) O PCA maximiza a variância dos espectros, não a covariância com o atributo. A informação sobre o atributo pode estar em componentes de menor variância, e por isso o número de PCs deve ser decidido pelo desempenho do modelo.

#### Problemas comuns

- **Interpretar um PC como um constituinte específico:** os PCs são combinações de bandas e podem misturar efeitos físicos e químicos.
- **Escolher o número de PCs só pela variância:** combinar com validação cruzada.
- **Ajustar o PCA em todos os dados antes de dividir calibração e validação para um modelo preditivo:** causa vazamento de informação.

#### Entregável

Gráfico de escores colorido pelo atributo, gráfico de loadings dos três primeiros PCs e um parágrafo interpretando o PC1 em termos de feições espectrais.

## Material de aula: versão 2

**Capítulo:** Análise de Componentes Principais (PCA). **Notebook:** `03_pca_clusterizacao.ipynb` (seção 1).

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 45 min: ideia do PCA, escores, pesos e variância explicada.
- 45 a 85 min: execução comentada da seção 1 do notebook 03.
- 85 a 110 min: exercícios (PCA bruto versus SNV e interpretação de loadings).
- 110 a 120 min: resumo e entregável.

#### Conteúdo

**Por que reduzir a dimensionalidade?** Os espectros têm centenas de bandas fortemente correlacionadas. O PCA encontra novos eixos, ortogonais entre si, nos quais a variância é máxima. Cada espectro passa a ser descrito por poucos **escores** (suas coordenadas nos componentes), e cada componente é definido por seus **pesos** (*loadings*), que mostram quanto cada banda contribui.

Para explicar a ideia, usar a analogia de fotografar um objeto tridimensional: o primeiro componente é o ângulo que mostra a maior dispersão do objeto, o segundo é o melhor ângulo perpendicular, e assim por diante.

**Pontos conceituais:**

- **Variância explicada:** fração da variação total capturada por cada componente. A variância acumulada orienta quantos componentes reter.
- **Centragem:** o `PCA` do scikit-learn subtrai a média de cada banda antes de calcular.
- **Interpretação:** os loadings relacionam os componentes às feições espectrais (1400, 1900 e 2200 nm e a região do visível).
- **Limitações:** variância não é o mesmo que relevância para o atributo, o PCA é sensível a outliers, e a combinação linear das bandas não corresponde necessariamente a um constituinte químico.
- **Vazamento:** em modelos preditivos, o PCA deve ser ajustado só na calibração. Na etapa exploratória, pode ser ajustado ao conjunto todo.

#### Prática guiada: notebook 03, seção 1

1. Carregar `espectros_pp.npz` e `df_pp.pkl` (células iniciais).
2. Ajustar `PCA(n_components=cfg.N_PCS_EXPLORA)` aos espectros com SNV (`X_snv`).
3. Ler a variância explicada e a acumulada impressas, e o gráfico de *scree*.
4. Interpretar o gráfico de escores (PC1 × PC2) colorido pelo atributo: há gradiente? Há agrupamentos? Há pontos isolados?
5. Interpretar os loadings dos três primeiros componentes: em que comprimentos de onda aparecem picos e vales?

#### Exercícios

1. Determinar o número mínimo de componentes para explicar 95% e 99% da variância:

```python
acum = var.cumsum()
for alvo in (0.95, 0.99):
    if (acum >= alvo).any():
        print(f'{alvo:.0%}:', int(np.argmax(acum >= alvo)) + 1, 'componentes')
    else:
        print(f'{alvo:.0%}: não atingido com', len(acum), 'componentes')
```

Se `N_PCS_EXPLORA` for pequeno demais para atingir 99%, aumentá-lo em `config.py`.

2. **PCA nos espectros sem SNV versus com SNV.** Comparar a variância explicada por PC1:

```python
for nome, M in [('sg (sem SNV)', d['X_suav']), ('snv', X_snv)]:
    p = PCA(n_components=5).fit(M)
    print(f'{nome:>14}: PC1 = {p.explained_variance_ratio_[0]*100:.1f}%  |  5 PCs = {p.explained_variance_ratio_.sum()*100:.1f}%')
```

3. **Reconstrução.** Reconstruir um espectro com 2, 5 e 10 componentes e comparar com o original:

```python
i = 0
pca_full = PCA(n_components=10).fit(X_snv)
sc = pca_full.transform(X_snv[i:i+1])
plt.plot(wl, X_snv[i], c='lightgray', lw=2, label='Original (SNV)')
for k in (2, 5, 10):
    rec = sc[:, :k] @ pca_full.components_[:k] + pca_full.mean_
    plt.plot(wl, rec.ravel(), lw=1, label=f'{k} componentes')
plt.legend(); plt.xlabel('nm'); plt.show()
```

4. Colorir o gráfico de escores pelo grupo (depois da aula 6) ou por um segundo atributo (`mo`), e comparar os padrões.

**Gabarito e observações:** (1) em espectros de solo, poucos componentes costumam explicar mais de 95% da variância. No banco sintético, 95% é atingido com cerca de 3 componentes, e 99% não é atingido com 10, o que mostra que a escolha do limiar muda bastante o número de componentes. (2) Sem o SNV, o PC1 costuma concentrar uma fração maior da variância, porque a diferença de intensidade geral entre espectros domina. Com o SNV, a variância se distribui mais entre os componentes, e eles passam a refletir a forma do espectro. (3) Com poucos componentes, a reconstrução acompanha a forma geral, e com mais componentes se aproxima das feições finas, o que mostra que os primeiros componentes resumem a informação principal.

#### Perguntas de verificação

1. **Um atributo pode depender de um componente de baixa variância?** Sim. Componentes de baixa variância podem conter a informação do atributo, e por isso o número de componentes deve ser definido também pelo desempenho preditivo.
2. **Por que o PCA não substitui o PLSR?** O PCA resume a variância dos espectros sem usar o atributo. O PLSR constrói variáveis latentes orientadas à predição do atributo.
3. **Por que o PCA deve ser ajustado só na calibração quando alimenta um modelo?** Para que nenhuma informação das amostras de validação influencie as variáveis do modelo, o que tornaria o desempenho otimista.

#### Entregável

Gráficos de variância explicada, de escores e de loadings, com um parágrafo interpretando os picos dos loadings de PC1 e a relação do gráfico de escores com o atributo.
