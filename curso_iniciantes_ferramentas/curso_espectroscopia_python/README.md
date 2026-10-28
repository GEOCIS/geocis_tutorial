# Curso: Espectroscopia de solos com Python, do dado ao modelo preditivo

*Plano de aulas baseado nos capítulos do projeto de predição de atributos do solo com espectros Vis-NIR-SWIR (BSSL)*

## 1. Visão geral

**Público:** estudantes de agronomia, ciência do solo e áreas afins que já têm o ambiente configurado (VS Code, Python, Jupyter Notebook e bibliotecas) e noções básicas de Python. Quem ainda não tem essa base deve cursar antes o curso introdutório de instalação e uso das ferramentas.

**Objetivo geral:** ao final, o aluno será capaz de executar e interpretar um fluxo completo de análise de espectros de solo (exploração, pré-processamento, PCA, clusterização, modelagem com PLSR e Random Forest, avaliação e predição de novas amostras) e redigir o relatório técnico correspondente.

**Carga horária:** 10 aulas de 2 horas (20 horas), cada uma associada a um capítulo do documento do projeto e a um notebook do pipeline.

**Materiais:** capítulos do projeto, pasta `pipeline_bssl` (cinco notebooks, `config.py` e `utils.py`) e o gerador de dados sintéticos (`gerar_dados_sinteticos.py`), que permite praticar mesmo sem acesso ao banco real da BSSL.

**Estratégia didática:** cada aula alterna explicação curta do conceito, execução guiada do notebook, e um exercício em que o aluno modifica parâmetros e observa o efeito. Os dados sintéticos servem para ver o comportamento do método, e o banco real, para interpretar resultados.

## 2. Cronograma

| Aula | Tema | Capítulo de referência | Notebook | Entregável |
| --- | --- | --- | --- | --- |
| 1 | Espectroscopia de solos, BSSL e visão do fluxo | Material e metodologia | — | Diagrama do fluxo e lista de atributos escolhidos |
| 2 | Leitura e análise exploratória | Leitura e análise exploratória | 01 | Relatório exploratório curto |
| 3 | Pré-processamento I: bordas, absorbância, suavização e derivada | Pré-processamento | 02 (parte 1) | Comparação gráfica de tratamentos |
| 4 | Pré-processamento II: SNV e outliers | Pré-processamento | 02 (parte 2) | Lista de outliers justificada |
| 5 | Análise de componentes principais | PCA | 03 (parte 1) | Interpretação de escores e loadings |
| 6 | Cotovelo e k-means | Método do cotovelo e k-means | 03 (parte 2) | Caracterização dos grupos |
| 7 | PLSR e validação cruzada | Modelagem | 04 (parte 1) | Curva de RMSECV e modelo PLSR |
| 8 | Random Forest e métricas de avaliação | Modelagem | 04 (parte 2) | Tabela de métricas comparando modelos |
| 9 | Visualização, interpretação e predição | Material e metodologia, Resultados | 05 | Predição de amostras novas com domínio de aplicação |
| 10 | Resultados, conclusão e apresentação | Resultados e Conclusão | todos | Relatório final e apresentação |

## Arquivos do curso

| Arquivo | Conteúdo |
| --- | --- |
| [00_preparacao.md](00_preparacao.md) | Preparação do professor |
| [aula_01_espectroscopia_bssl_fluxo.md](aula_01_espectroscopia_bssl_fluxo.md) | Aula 1: Espectroscopia de solos, BSSL e visão do fluxo |
| [aula_02_leitura_exploratoria.md](aula_02_leitura_exploratoria.md) | Aula 2: Leitura e análise exploratória |
| [aula_03_preprocessamento_I.md](aula_03_preprocessamento_I.md) | Aula 3: Pré-processamento I (bordas, absorbância, suavização e derivada) |
| [aula_04_preprocessamento_II.md](aula_04_preprocessamento_II.md) | Aula 4: Pré-processamento II (SNV e outliers) |
| [aula_05_pca.md](aula_05_pca.md) | Aula 5: Análise de componentes principais |
| [aula_06_cotovelo_kmeans.md](aula_06_cotovelo_kmeans.md) | Aula 6: Método do cotovelo e k-means |
| [aula_07_plsr_validacao_cruzada.md](aula_07_plsr_validacao_cruzada.md) | Aula 7: PLSR e validação cruzada |
| [aula_08_random_forest_metricas.md](aula_08_random_forest_metricas.md) | Aula 8: Random Forest e métricas de avaliação |
| [aula_09_visualizacao_predicao.md](aula_09_visualizacao_predicao.md) | Aula 9: Visualização, interpretação e predição |
| [aula_10_resultados_apresentacao.md](aula_10_resultados_apresentacao.md) | Aula 10: Resultados, conclusão e apresentação |
| [apendice.md](apendice.md) | Sequência de verificação rápida do pipeline |

As aulas 1 a 8 têm duas versões do material desenvolvido no documento original; ambas foram mantidas integralmente em cada arquivo ("versão 1" e "versão 2"). As aulas 9 e 10 têm apenas uma versão.

## 3. Avaliação sugerida

- **Entregáveis das aulas (40%)**: um por aula, avaliados por completude e interpretação correta.
- **Relatório final (40%)**: coerência entre método, resultados e conclusão, e qualidade das figuras e das tabelas.
- **Apresentação e discussão (20%)**: clareza, domínio do conteúdo e senso crítico sobre as limitações.

**Critérios do relatório:** reprodutibilidade (qualquer pessoa consegue repetir com `config.py`), ausência de vazamento de informação, justificativa das escolhas de parâmetros e honestidade na interpretação das métricas.

## 4. Glossário de termos-chave

- **BSSL**: biblioteca espectral de solos do Brasil.
- **Absorbância**: log10(1/reflectância), usada para realçar feições de absorção.
- **Savitzky-Golay**: filtro polinomial móvel para suavização e derivadas.
- **SNV**: padronização de cada espectro pela sua média e desvio-padrão.
- **PCA**: técnica que resume a variação em componentes não correlacionados.
- **T² e Q**: distância ao centro e resíduo de reconstrução no PCA, usados para outliers e domínio de aplicação.
- **PLSR**: regressão por mínimos quadrados parciais, com variáveis latentes.
- **RMSECV**: erro de validação cruzada na calibração.
- **RPD e RPIQ**: razões entre a variabilidade do atributo (desvio-padrão ou distância interquartílica) e o RMSE.
- **Domínio de aplicação**: região do espaço espectral em que o modelo é confiável.

## 5. Orientações para quem ministra

1. Começar cada aula executando o notebook anterior, já que as etapas dependem das saídas da etapa anterior (pasta `resultados/`).
2. Usar os dados sintéticos para demonstrar o efeito de cada parâmetro, e deixar claro que os números obtidos com eles não são resultados científicos.
3. Pedir que cada aluno defina um atributo diferente (argila, matéria orgânica, CTC etc.) para comparar o desempenho entre atributos na aula final.
4. Insistir na separação entre calibração e validação em todas as decisões, pois é o erro metodológico mais comum.
5. Reservar tempo para discutir os resultados ruins, que são uma oportunidade de aprendizado sobre limites do método.
