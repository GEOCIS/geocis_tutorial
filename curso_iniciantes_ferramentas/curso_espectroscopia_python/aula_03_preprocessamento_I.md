# Aula 3: Pré-processamento I (bordas, absorbância, suavização e derivada)

[← Aula 2](aula_02_leitura_exploratoria.md) · [Plano do curso](README.md) · [Aula 4 →](aula_04_preprocessamento_II.md)

**Capítulo:** Pré-processamento. **Notebook:** `02_preprocessamento.ipynb` (seção 1 e parte da 2).

**Materiais:** notebook 02, saídas do notebook 01 em `resultados/`.

**Objetivos:** aplicar e comparar tratamentos que reduzem ruído e realçam feições.

**Tópicos:**

- Corte das bordas ruidosas do espectro e escolha dos limites.
- Conversão de reflectância em absorbância, A = log10(1/R).
- Filtro de Savitzky-Golay: janela e grau do polinômio, e o equilíbrio entre remover ruído e distorcer feições.
- Primeira derivada: remoção de deslocamento de linha de base e sensibilidade ao ruído.

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: fontes de variação indesejada, a lógica de cada tratamento e o tratamento adequado a cada uma.
- 40 a 75 min: execução comentada da seção de tratamentos do notebook 02, até a figura das etapas.
- 75 a 110 min: experimentos com a janela e o grau do filtro.
- 110 a 120 min: discussão, resumo e entregável.

## Conteúdo

Um espectro bruto mistura a informação desejada (composição) com variações indesejadas. O pré-processamento reduz essas variações sem apagar a informação.

**Fontes de variação indesejada nos espectros:**

| Problema | Sintoma no gráfico | Tratamento |
| --- | --- | --- |
| Ruído nas extremidades | Oscilações no início e no fim do espectro | Corte das bordas |
| Ruído aleatório | Espectro "serrilhado" | Suavização (Savitzky-Golay) |
| Relação não linear com a concentração | Feições de absorção pouco destacadas | Absorbância |
| Deslocamento de linha de base | Espectros paralelos, em alturas diferentes | Derivadas |

### Corte das bordas (`utils.corta`)

A razão sinal/ruído é baixa no início do visível e acima de cerca de 2400 nm, regiões com pouca energia e muito ruído. No pipeline, `WL_MIN = 450` e `WL_MAX = 2450`. Os limites dependem do sensor e devem ser conferidos nos espectros brutos.

### Absorbância (A = log10(1/R))

Transforma a reflectância em uma grandeza que se relaciona de forma mais linear com a concentração dos constituintes e realça as feições de absorção. O `np.clip` evita logaritmo de zero ou de valores negativos.

### Filtro de Savitzky-Golay (suavização)

Em cada janela móvel de pontos vizinhos, ajusta-se um polinômio por mínimos quadrados, e o valor central é substituído pelo valor ajustado. Reduz ruído e preserva a forma das feições melhor que uma média móvel. Os parâmetros:

- **Janela** (`SG_JANELA`, ímpar): maior janela, mais suavização e mais risco de distorcer feições estreitas.
- **Grau do polinômio** (`SG_GRAU`): menor grau, mais suavização.

### Primeira derivada (Savitzky-Golay com `deriv=1`)

Remove o deslocamento aditivo da linha de base e realça (separa) feições sobrepostas. Em contrapartida, amplifica o ruído, e por isso é calculada pelo próprio filtro de Savitzky-Golay (que suaviza e deriva ao mesmo tempo), e não por diferença simples entre bandas. A janela é mais crítica do que na suavização.

### Os tratamentos no pipeline

São chamados por `utils.preprocessa(X, wl, tratamento)`, com `tratamento` igual a `'abs'`, `'sg'`, `'d1'` ou `'snv'`. O `'snv'` é visto na aula 4.

**Referência com os dados sintéticos:** após o corte, restam 401 bandas entre 450 e 2450 nm.

## Prática guiada

No notebook 02, executar as células da seção 1 e comentar:

1. `utils.corta` reduz a matriz de 431 para cerca de 401 bandas (de 450 a 2450 nm).
2. `utils.preprocessa(X, wl_orig, tratamento)` aplica a sequência completa.
3. A figura com cinco painéis mostra a progressão: reflectância cortada, absorbância, suavizado, 1ª derivada e SG + SNV. Pedir que os alunos descrevam o que mudou de um painel para o outro. Onde aparece o ruído da derivada?

### Experimento A: janelas de 5, 11 e 21 pontos (notebook separado)

Em um notebook novo (ou em uma célula extra), comparar janelas para um mesmo espectro:

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import config as cfg, utils

d = np.load(cfg.PASTA / "dados_brutos.npz")
X, wl_orig = d["X"], d["wl_orig"]
wl, Xabs = utils.preprocessa(X, wl_orig, "abs")

fig, ax = plt.subplots(2, 3, figsize=(15, 6), sharex=True)
for j, janela in enumerate((5, 11, 21)):
    suav = savgol_filter(Xabs[0], janela, 2)
    d1 = savgol_filter(Xabs[0], janela, 2, deriv=1)
    ax[0, j].plot(wl, Xabs[0], lw=0.5, c="gray", label="absorbância")
    ax[0, j].plot(wl, suav, label=f"SG (janela {janela})")
    ax[0, j].set_title(f"Suavização, janela {janela}"); ax[0, j].legend()
    ax[1, j].plot(wl, d1)
    ax[1, j].set_title(f"1ª derivada, janela {janela}")
plt.tight_layout(); plt.show()
```

Discutir: com janela 5, a derivada fica ruidosa; com janela 21, as feições estreitas ficam achatadas. A escolha final (janela 11, grau 2) é um ponto de partida que será comparado por validação cruzada na aula 7.

### Experimento B: janelas de 5 a 51 pontos, com o resíduo (dentro do notebook 02)

Em uma célula nova do notebook 02 (depois de calcular `X_abs`), comparar janelas em um espectro:

```python
from scipy.signal import savgol_filter

i = 10   # amostra qualquer
fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
ax[0].plot(wl, X_abs[i], c='lightgray', label='Absorbância')
for janela in (5, 11, 21, 51):
    sg = savgol_filter(X_abs[i], janela, cfg.SG_GRAU, axis=0)
    ax[0].plot(wl, sg, lw=1, label=f'janela {janela}')
    rud = (X_abs[i] - sg).std()
    print(f'janela {janela:>2}: desvio-padrão do resíduo = {rud:.5f}')
ax[0].legend(); ax[0].set(xlabel='nm', title='Suavização')

for janela in (5, 11, 21, 51):
    d1 = savgol_filter(X_abs[i], janela, cfg.SG_GRAU, deriv=1, axis=0)
    ax[1].plot(wl, d1, lw=0.8, label=f'janela {janela}')
ax[1].legend(); ax[1].set(xlabel='nm', title='1ª derivada')
plt.tight_layout(); plt.show()
```

O desvio-padrão do resíduo (absorbância menos suavizado) aumenta com a janela, pois o filtro remove cada vez mais variação. A pergunta é onde o aumento deixa de ser ruído e passa a ser sinal removido. Na derivada, a janela pequena produz uma curva muito ruidosa, e a janela grande, uma curva suave, porém com feições alargadas.

## Exercícios

1. Em `config.py`, alterar `SG_JANELA` para 5 e depois para 21, reexecutar o notebook 02 e descrever as diferenças, comparando o painel "SG + SNV" de cada caso. Descrever em duas frases qual janela preserva melhor as feições perto de 2200 nm.
2. Testar `SG_GRAU` igual a 2 e a 4, mantendo a janela em 11, e explicar o efeito.
3. Calcular, para um espectro, o desvio-padrão da diferença entre o espectro bruto e o suavizado, como medida do ruído removido, para cada janela.
4. Estimar o ruído médio dos espectros com a janela padrão:

```python
ruido = (X_abs - X_suav).std(axis=1)
print('Ruído médio:', ruido.mean().round(5), '| máximo:', ruido.max().round(5))
```

5. Verificar o efeito de **não** cortar as bordas: calcular a absorbância com `utils.preprocessa` alterando temporariamente `cfg.WL_MIN` para 350 e `cfg.WL_MAX` para 2500, e comparar o ruído médio com o do exercício 4.
6. Responder: por que a derivada pode melhorar a predição mesmo amplificando o ruído?

<details>
<summary>Gabarito comentado</summary>

- (1) Janelas de 5 pontos deixam bastante ruído, e janelas de 21 ou mais alisam as feições estreitas. Em dados de passo de 5 nm, a janela de 11 pontos cobre 50 nm, o que costuma preservar as feições largas dos argilominerais.
- (2) Com grau mais alto, o polinômio acompanha melhor o sinal, inclusive o ruído, e a suavização diminui. Com grau 2, a suavização é mais forte.
- (3) `np.std(Xabs[0] - savgol_filter(Xabs[0], janela, 2))` aumenta com o tamanho da janela, pois uma janela maior remove mais variação (inclusive parte do sinal).
- (4) O valor exato depende dos dados.
- (5) Sem o corte, o ruído médio é maior, porque as extremidades foram geradas com ruído amplificado no banco sintético.
- (6) A derivada elimina o deslocamento de linha de base entre amostras, que é variação sem relação com o atributo. O ganho em remover essa variação pode superar a perda causada pelo ruído, desde que a janela seja bem escolhida.

**Observação importante:** o passo espectral muda o significado da janela. Em um banco com 1 nm de passo, uma janela de 11 pontos cobre só 11 nm. Ao usar a BSSL real, a janela deve ser reavaliada.

</details>

## Problemas comuns

- **Erro `window_length must be odd` ou maior que o grau:** a janela precisa ser ímpar e maior que `polyorder`.
- **Bordas ainda ruidosas:** revisar `WL_MIN` e `WL_MAX` conforme a inspeção dos espectros.
- **Valores negativos de reflectância:** indicam ruído ou problema de medição; investigar antes de mascarar com `np.clip`.

## Perguntas de verificação

1. **Por que a janela do filtro precisa ser ímpar?** Para que exista um ponto central, que é o valor substituído pelo ajuste.
2. **Por que a derivada amplifica o ruído?** Ela mede variações entre bandas vizinhas, e o ruído aleatório é justamente variação de uma banda para outra.
3. **Por que usar o filtro para calcular a derivada, em vez de subtrair bandas vizinhas?** Porque o filtro ajusta um polinômio em uma janela e deriva o ajuste, o que suaviza e deriva ao mesmo tempo.

## Entregável

Figura comparando reflectância, absorbância, suavizado e derivada para um espectro (com a janela escolhida), com legenda interpretativa e um parágrafo justificando os parâmetros do filtro.
