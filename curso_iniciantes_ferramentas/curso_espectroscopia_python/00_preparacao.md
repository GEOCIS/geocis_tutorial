# Preparação do professor

[Plano do curso](README.md) · [Aula 1 →](aula_01_espectroscopia_bssl_fluxo.md)

Cada aula de 2 horas corresponde a um capítulo do projeto e a um notebook do pipeline (pasta `pipeline_bssl`). O material de cada aula traz o roteiro com tempos, o conteúdo a expor, a prática guiada com código, os exercícios com gabarito, as perguntas de verificação com respostas e o entregável.

## Uma vez, antes do curso

1. **Pasta de trabalho:** copiar `pipeline_bssl` (cinco notebooks, `config.py`, `utils.py` e `gerar_dados_sinteticos.py`) e criar o ambiente virtual com `numpy`, `pandas`, `scipy`, `scikit-learn`, `matplotlib`, `joblib` e `ipykernel`.
2. **Dados:** executar `python gerar_dados_sinteticos.py` para criar `dados/bssl.csv` (900 amostras, 431 bandas de 350 a 2500 nm, atributos `argila` e `mo`, com valores faltantes e 8 espectros anômalos) e `dados/novas_amostras.csv`. Os dados são **sintéticos e servem apenas para treinar o método**. Os números obtidos com eles não são resultados científicos.
3. **Conferir o ambiente:** executar o pipeline completo com os dados sintéticos (os notebooks 01 a 05, em ordem). Ver também o [apêndice](apendice.md).
4. **Banco real:** se a turma usar a BSSL, ajustar `ARQUIVO`, `COL_ALVO` e `PREFIXO` em `config.py` e usá-lo nas aulas de interpretação. Em bancos com dezenas de milhares de amostras, o notebook 04 pode demorar muito. Para as aulas, reduzir o banco com uma subamostra logo após a limpeza no notebook 01 (por exemplo, `df = df.sample(5000, random_state=cfg.SEED).reset_index(drop=True)`, antes de definir `X` e `y`).

## Durante o curso

- **Ordem e dependências:** os notebooks passam arquivos pela pasta `resultados/` (01 gera os dados brutos, 02 os espectros tratados, 03 os grupos, 04 o modelo e 05 as predições). Em cada aula, quem faltou à anterior precisa executar os notebooks anteriores antes.
- **Tempo de execução:** com os dados sintéticos, o notebook 04 leva cerca de 1 a 2 minutos. Reservar esse tempo no roteiro.

## Valores de referência

Os números citados como "referência" em cada aula vêm da execução com os dados sintéticos gerados por `gerar_dados_sinteticos.py` (900 amostras, `SEED = 42`). Eles servem para o professor conferir se o ambiente funciona e podem variar levemente com as versões das bibliotecas. Como os dados são sintéticos e construídos de forma simples, o desempenho dos modelos é irrealisticamente alto (RPD acima de 7), e isso deve ser dito aos alunos. Com dados reais, os resultados serão menores.
