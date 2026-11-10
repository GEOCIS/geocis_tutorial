# Apêndice

[← Aula 10](aula_10_resultados_apresentacao.md) · [Plano do curso](README.md)

## Sequência de verificação rápida do pipeline

Antes de cada aula, o professor pode confirmar em poucos minutos que o ambiente está correto:

```bash
python gerar_dados_sinteticos.py          # cria dados/bssl.csv e dados/novas_amostras.csv
# executar os notebooks 01 a 05, na ordem, com "Run All"
```

Saídas esperadas em [`resultados/`](../pipeline_bssl/config.qmd#cb1-13): [`dados_brutos.npz`](../pipeline_bssl/01_leitura_exploratoria.ipynb#salvar), [`df_limpo.pkl`](../pipeline_bssl/01_leitura_exploratoria.ipynb#salvar), [`espectros_pp.npz`](../pipeline_bssl/02_preprocessamento.ipynb#remoção-e-salvamento), [`df_pp.pkl`](../pipeline_bssl/02_preprocessamento.ipynb#remoção-e-salvamento), [`cluster_model.joblib`](../pipeline_bssl/03_pca_clusterizacao.ipynb#k-means-final-e-caracterização-dos-grupos), [`modelo_solo.joblib`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento), [`metricas.csv`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento), [`predicoes_validacao.csv`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento), [`predicoes_novas_amostras.csv`](../pipeline_bssl/05_visualizacao_predicao.ipynb#predição-de-amostras-novas) e a pasta `figuras/` com os gráficos de cada etapa.

**Erros mais comuns em sala:**

- **[`ModuleNotFoundError: config`](../pipeline_bssl/index.qmd#como-usar):** o notebook foi aberto fora da pasta [`pipeline_bssl`](../pipeline_bssl/index.qmd). Abrir a pasta inteira no VS Code.
- **[`FileNotFoundError`](../pipeline_bssl/index.qmd#como-usar) para [`dados/bssl.csv`](../pipeline_bssl/gerar_dados_sinteticos.qmd#cb1-81):** os dados ainda não foram gerados ou o caminho em [`config.py`](../pipeline_bssl/config.qmd) está incorreto.
- **[`FileNotFoundError`](../pipeline_bssl/index.qmd#como-usar) para arquivos de [`resultados/`](../pipeline_bssl/config.qmd#cb1-13):** um notebook anterior não foi executado.
- **Notebook 04 muito lento:** reduzir [`N_ITER_BUSCA`](../pipeline_bssl/config.qmd#cb1-48) ou [`N_ARVORES`](../pipeline_bssl/config.qmd#cb1-49) em [`config.py`](../pipeline_bssl/config.qmd), ou usar uma subamostra do banco.
- **Resultados diferentes entre alunos:** conferir as versões das bibliotecas e se [`SEED`](../pipeline_bssl/config.qmd#cb1-22) não foi alterado.
