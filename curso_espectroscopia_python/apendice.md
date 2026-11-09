# Apêndice

[← Aula 10](aula_10_resultados_apresentacao.md) · [Plano do curso](README.md)

## Sequência de verificação rápida do pipeline

Antes de cada aula, o professor pode confirmar em poucos minutos que o ambiente está correto:

```bash
python gerar_dados_sinteticos.py          # cria dados/bssl.csv e dados/novas_amostras.csv
# executar os notebooks 01 a 05, na ordem, com "Run All"
```

Saídas esperadas em [`resultados/`](../pipeline_bssl/config.qmd#cb1-13): `dados_brutos.npz`, `df_limpo.pkl`, `espectros_pp.npz`, `df_pp.pkl`, `cluster_model.joblib`, `modelo_solo.joblib`, `metricas.csv`, `predicoes_validacao.csv`, `predicoes_novas_amostras.csv` e a pasta `figuras/` com os gráficos de cada etapa.

**Erros mais comuns em sala:**

- **`ModuleNotFoundError: config`:** o notebook foi aberto fora da pasta [`pipeline_bssl`](../pipeline_bssl/index.qmd). Abrir a pasta inteira no VS Code.
- **`FileNotFoundError` para [`dados/bssl.csv`](../pipeline_bssl/gerar_dados_sinteticos.qmd#cb1-81):** os dados ainda não foram gerados ou o caminho em [`config.py`](../pipeline_bssl/config.qmd) está incorreto.
- **`FileNotFoundError` para arquivos de [`resultados/`](../pipeline_bssl/config.qmd#cb1-13):** um notebook anterior não foi executado.
- **Notebook 04 muito lento:** reduzir `N_ITER_BUSCA` ou `N_ARVORES` em [`config.py`](../pipeline_bssl/config.qmd), ou usar uma subamostra do banco.
- **Resultados diferentes entre alunos:** conferir as versões das bibliotecas e se `SEED` não foi alterado.
