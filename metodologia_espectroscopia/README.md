# Curso: Metodologia da predição de atributos do solo por espectroscopia

*Plano de aulas sobre os fundamentos e as decisões metodológicas do projeto: por que cada etapa é feita, quais alternativas existem e como justificar as escolhas*

## Arquivos do curso

| Arquivo | Conteúdo |
| --- | --- |
| [00_preparacao.md](00_preparacao.md) | Preparação do professor e célula de preparação usada nas aulas 2 a 8 |
| [aula_01_delineamento.md](aula_01_delineamento.md) | Aula 1: Delineamento do estudo |
| [aula_02_espectroscopia_e_referencia.md](aula_02_espectroscopia_e_referencia.md) | Aula 2: Espectroscopia de solos e dado de referência |
| [aula_03_amostragem_qualidade_exploratoria.md](aula_03_amostragem_qualidade_exploratoria.md) | Aula 3: Amostragem, qualidade dos dados e análise exploratória |
| [aula_04_preprocessamento.md](aula_04_preprocessamento.md) | Aula 4: Metodologia de pré-processamento |
| [aula_05_dimensionalidade_agrupamento.md](aula_05_dimensionalidade_agrupamento.md) | Aula 5: Redução de dimensionalidade e agrupamento |
| [aula_06_modelagem.md](aula_06_modelagem.md) | Aula 6: Modelagem preditiva |
| [aula_07_validacao_metricas_incerteza.md](aula_07_validacao_metricas_incerteza.md) | Aula 7: Validação, métricas e incerteza |
| [aula_08_dominio_reprodutibilidade_redacao.md](aula_08_dominio_reprodutibilidade_redacao.md) | Aula 8: Domínio de aplicação, reprodutibilidade e redação (inclui o encerramento) |

Cada aula de 2 horas tem objetivos, roteiro com tempos, conteúdo conceitual desenvolvido, atividades práticas que demonstram a decisão metodológica em questão, exercícios ou pontos de discussão com gabarito, perguntas de verificação com respostas, leituras e entregável. A lógica do curso é **decidir, justificar e demonstrar**: cada escolha do pipeline é discutida e depois testada com dados.

## 1. Visão geral

**Público:** estudantes de graduação e pós-graduação em agronomia, ciência do solo e áreas afins, com noções básicas de estatística e de Python.

**Como este curso se diferencia:** o curso organizado por capítulos ensina a executar cada notebook do pipeline. Este curso trata do raciocínio metodológico por trás dele: como planejar o estudo, que armadilhas evitar, como escolher e justificar métodos e como relatar tudo de forma reprodutível. Os dois cursos se complementam.

**Objetivo geral:** ao final, o aluno será capaz de delinear um estudo de predição de atributos do solo com espectros, escolher e justificar as etapas de pré-processamento, redução de dimensionalidade e modelagem, validar os modelos sem viés otimista e redigir a seção de metodologia de um trabalho científico.

**Carga horária:** 8 aulas de 2 horas (16 horas), com discussão de artigos e atividades de decisão em dados sintéticos e reais.

**Materiais:** capítulos do projeto (material e metodologia, pré-processamento, PCA, k-means, modelagem), pasta `pipeline_bssl` e gerador de dados sintéticos.

## 2. Cronograma

| Aula | Tema | Questão central |
| --- | --- | --- |
| 1 | Delineamento do estudo | Que pergunta o estudo responde e como saber se deu certo? |
| 2 | Espectroscopia de solos e dado de referência | O que o espectro mede e qual o limite imposto pelo laboratório? |
| 3 | Amostragem, qualidade dos dados e análise exploratória | Os dados são adequados para modelar? |
| 4 | Metodologia de pré-processamento | Qual tratamento usar e como decidir? |
| 5 | Redução de dimensionalidade e agrupamento | Como resumir e organizar a variabilidade espectral? |
| 6 | Modelagem preditiva | Como escolher e ajustar um modelo sem sobreajuste? |
| 7 | Validação, métricas e incerteza | Como estimar o desempenho real? |
| 8 | Domínio de aplicação, reprodutibilidade e redação | Como garantir confiança e comunicar o método? |

## 3. Quadro de decisões metodológicas do projeto

O quadro abaixo resume as decisões do pipeline e deve ser usado ao longo do curso para discutir justificativas e alternativas.

| Decisão | Escolha no projeto | Justificativa | Alternativas |
| --- | --- | --- | --- |
| Faixa espectral | 450 a 2450 nm | Remove bordas ruidosas | Outros limites conforme o sensor |
| Transformação | Absorbância | Lineariza parcialmente a relação com a concentração | Reflectância, Kubelka-Munk |
| Suavização | Savitzky-Golay (11, grau 2) | Preserva a forma das feições | Média móvel, *binning* |
| Espalhamento | SNV | Por espectro, sem vazamento | MSC, derivadas |
| Outliers | z-score, T² e Q | Critérios espectrais complementares | Distribuição qui-quadrado, alavancagem |
| Agrupamento | k-means sobre 5 PCs | Simplicidade e interpretação | Hierárquico, misturas gaussianas |
| Divisão | 70/30 estratificada | Representação de todos os grupos | Kennard-Stone, validação por grupos |
| PLSR | LV por validação cruzada de 10 partições | Evita sobreajuste | Regra do erro-padrão |
| Random Forest | Sobre escores de PCA, busca aleatória | Reduz dimensão e tempo | SVR, Cubist, redes neurais |
| Métricas | R², RMSE, RPD, RPIQ e viés | Complementares | CCC de Lin |
| Domínio | T² e Q no percentil 99 | Sinaliza extrapolação | Distância espectral, alavancagem |

## 4. Avaliação

| Critério | Peso | O que se observa |
| --- | --- | --- |
| Protocolo e justificativas (aulas 1 a 6) | 40% | Decisões justificadas, critérios definidos a priori e evidência da calibração |
| Validação e incerteza (aula 7) | 20% | Métricas repetidas, esquema adequado ao uso e interpretação de incerteza |
| Metodologia e reprodutibilidade (aula 8) | 30% | Texto completo, repositório, metadados e resultado da reprodução cruzada |
| Seminário e senso crítico | 10% | Clareza e reconhecimento de limitações |

**Alternativa mais simples** (proposta no plano original):

- **Entregáveis das aulas (40%)**: um por aula, avaliados pela qualidade da justificativa e não só pela execução.
- **Seção de metodologia e repositório (40%)**: clareza, completude e reprodutibilidade, verificada por outro colega.
- **Seminário de discussão (20%)**: apresentação e análise crítica de um artigo de espectroscopia de solos, identificando as decisões metodológicas e suas limitações.

## 5. Leituras sugeridas

Conferir os dados completos das referências antes de distribuí-las.

- DEMATTÊ, J. A. M. et al. The Brazilian Soil Spectral Library (BSSL). *Geoderma*, 2019.
- CHANG, C.-W. et al. Near-infrared reflectance spectroscopy–principal components regression analyses of soil properties. *Soil Science Society of America Journal*, 2001.
- STENBERG, B. et al. Visible and near infrared spectroscopy in soil science. *Advances in Agronomy*, 2010.
- WOLD, S.; SJÖSTRÖM, M.; ERIKSSON, L. PLS-regression: a basic tool of chemometrics. *Chemometrics and Intelligent Laboratory Systems*, 2001.
- Documentação do scikit-learn sobre validação cruzada, `Pipeline` e métricas de regressão.

## 6. Orientações para quem ministra

1. Em cada aula, pedir que o aluno primeiro formule a decisão e a justificativa, e só depois execute o código.
2. Usar os dados sintéticos para mostrar o efeito de erros metodológicos de propósito, como o vazamento de informação ou a escolha de parâmetros na validação, e ver como as métricas ficam otimistas.
3. Dar espaço a resultados ruins e ao que eles ensinam sobre os limites do método.
4. Retomar o quadro de decisões ao final de cada aula, atualizando-o com as alternativas discutidas.
5. Relacionar sempre cada etapa ao objetivo e ao uso pretendido definidos na aula 1.
