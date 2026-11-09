# pipeline_bssl

Pipeline em Python e Jupyter Notebook para predizer atributos do solo a partir de espectros
Vis-NIR-SWIR, usado no **Curso prático**, nos **Fundamentos** e no **Texto de referência**
do site [Espectroscopia de Solos com Python](https://geocis.github.io/geocis_tutorial/).

## Conteúdo

| Arquivo | Função |
|---|---|
| `config.py` | Caminhos e parâmetros de todas as etapas (corte, Savitzky-Golay, outliers, PCA, k, modelagem, domínio) |
| `utils.py` | Funções: leitura, pré-processamento, métricas, T² e Q, VIP e reamostragem |
| `gerar_dados_sinteticos.py` | Gera um banco sintético no formato da BSSL, para praticar sem o banco real |
| `01_leitura_exploratoria.ipynb` | Leitura, estatística descritiva, limpeza e correlação por banda |
| `02_preprocessamento.ipynb` | Corte, absorbância, Savitzky-Golay, 1ª derivada, SNV e outliers (z-score, T² e Q) |
| `03_pca_clusterizacao.ipynb` | PCA, cotovelo, silhueta e k-means |
| `04_modelagem.ipynb` | PLSR (tratamento e nº de VLs por validação cruzada), Random Forest, métricas e domínio |
| `05_visualizacao_predicao.ipynb` | Observado × predito, resíduos, VIP, predição de amostras novas com T² e Q |

## Como usar

```bash
pip install -r requirements.txt
python gerar_dados_sinteticos.py      # cria dados/bssl.csv e dados/novas_amostras.csv
```

Depois abra os notebooks **na ordem (01 a 05)** e execute todas as células. Cada notebook lê
os arquivos salvos pelo anterior na pasta `resultados/`, e as figuras vão para
`resultados/figuras/`. Execute sempre a partir da pasta `pipeline_bssl` (o `config.py` precisa
estar na mesma pasta dos notebooks). Com os dados sintéticos, os cinco notebooks rodam em
cerca de 1 minuto.

## Usando o banco real (BSSL ou outro)

1. Coloque o arquivo em `dados/` com uma coluna `id`, as colunas de atributos e uma coluna por
   comprimento de onda, nomeada pelo valor em nm (por exemplo `350`, `351`, ...), em ordem crescente.
2. Em `config.py`, ajuste `ARQUIVO`, `COL_ALVO` e, se as colunas espectrais tiverem prefixo
   (por exemplo `X350`), `PREFIXO`.
3. Revise os parâmetros (`WL_MIN`, `WL_MAX`, `SG_JANELA`, `K` etc.) conforme o sensor e os dados.

## Sobre os dados sintéticos

Os espectros sintéticos têm feições simuladas apenas perto de 1400, 1900 e 2200 nm, ligadas à
argila; a matéria orgânica (`mo`) e o espalhamento escurecem o espectro inteiro. Há 40 amostras
sem argila e 8 espectros anômalos de propósito (S0000 a S0007). Os dados são "bem comportados"
para mostrar o efeito de cada etapa: o desempenho é muito mais alto do que com dados reais, e
**os números obtidos com eles não são resultados científicos**.

Valores de referência (SEED = 42): 860 amostras após a limpeza; 16 outliers sinalizados
(z-score 7, T² 9, Q 9), incluindo os 8 anômalos; 844 amostras após a remoção; PC1 com 96,1%
da variância; tratamento escolhido `sg` com 2 variáveis latentes; PLSR na validação com
R² 0,982, RMSE 2,99 e RPD 7,4; 48 de 50 amostras novas dentro do domínio.
