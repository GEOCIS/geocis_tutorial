# Aula 10: Resultados, conclusão e apresentação

[← Aula 9](aula_09_visualizacao_predicao.md) · [Plano do curso](README.md) · [Apêndice →](apendice.md)

**Antes da aula:** ver a [preparação do professor](00_preparacao.md).

## Resumo do plano

**Objetivos:** comunicar resultados de forma clara, honesta e reprodutível.

**Conteúdo:**

- Como redigir resultados: números e figuras reais do pipeline, sem mistura com dados de teste ou sintéticos.
- Discussão: comparação com a literatura, explicação do desempenho e limitações (divisão única, heterogeneidade da BSSL, domínio de aplicação).
- Produtos (*outcomes*), aplicações e trabalhos futuros.
- Conclusão: respostas diretas ao objetivo, sem repetir toda a metodologia.
- Apresentação oral: estrutura de 10 minutos e boas práticas para gráficos.

**Prática:** cada aluno ou dupla preenche os capítulos de resultados e conclusão com os números do seu próprio atributo e apresenta.

**Entregável:** relatório final e apresentação oral.

**Perguntas de verificação:** como relatar um modelo com RPD abaixo de 1,4? Por que é importante informar o número de amostras removidas em cada etapa?

## Material de aula

**Capítulo:** Resultados e produtos; Conclusão. **Notebooks:** todos (consolidação).

#### Roteiro (120 min)

- 0 a 10 min: revisão e dúvidas.
- 10 a 40 min: como transformar as saídas do pipeline em texto de resultados.
- 40 a 60 min: discussão, limitações e conclusão.
- 60 a 75 min: estrutura da apresentação oral.
- 75 a 120 min: apresentações (5 a 8 minutos por aluno ou dupla, com perguntas).

#### Conteúdo

**Do arquivo ao texto.** Os resultados vêm de arquivos em `resultados/`: a tabela de métricas (`metricas.csv`), as figuras (`resultados/figuras/`) e as predições (`predicoes_validacao.csv` e `predicoes_novas_amostras.csv`). O texto deve citar esses números e figuras, nunca valores de memória nem de dados sintéticos de teste.

Para montar a tabela de métricas do relatório a partir do arquivo:

```python
import pandas as pd

m = pd.read_csv('resultados/metricas.csv', index_col=[0, 1])
print(m.round(3).to_string())

val = m.loc[('PLSR', 'Validação')]
print(f'PLSR na validação: R² = {val.R2:.2f}, RMSE = {val.RMSE:.2f}, RPD = {val.RPD:.2f}, RPIQ = {val.RPIQ:.2f}')
```

**Estrutura de um texto de resultados.** Seguir a ordem do fluxo:

1. Caracterização do banco (n de amostras, estatísticas do atributo, faltantes).
2. Efeito do pré-processamento e amostras removidas.
3. Estrutura espectral (PCA e grupos).
4. Desempenho dos modelos (tabela de métricas, comparação e sobreajuste).
5. Interpretação espectral.
6. Predição de novas amostras e domínio de aplicação.

Cada parágrafo traz um número ou uma figura e uma interpretação, e não apenas a descrição.

**Discussão.** Responder a quatro perguntas: o desempenho atende ao uso pretendido? Como se compara à literatura? Por que um modelo foi melhor? Quais as limitações (divisão única, heterogeneidade da BSSL, domínio de aplicação, erro de laboratório)?

**Conclusão.** Responde ao objetivo em poucos parágrafos: o que foi feito, o desempenho obtido, o modelo recomendado e as limitações. Não repete a metodologia nem introduz resultados novos.

**Produtos (*outcomes*).** O pipeline reprodutível, o modelo salvo, as tabelas e figuras, as predições e a documentação. Discutir também as aplicações (triagem, mapeamento e redução de análises) e os trabalhos futuros (outros atributos, outros algoritmos, validação independente, covariáveis ambientais).

#### A apresentação oral (5 a 8 minutos)

| Bloco | Tempo | Conteúdo |
| --- | --- | --- |
| Problema e objetivo | 1 min | Por que predizer o atributo por espectroscopia |
| Dados e método | 1,5 min | BSSL, pré-processamento e modelos, em um diagrama |
| Resultados | 2,5 min | Tabela de métricas, observado × predito e um gráfico espectral |
| Limitações e conclusão | 1 min | O que o modelo faz bem, onde não é confiável |
| Perguntas | 1 min | Discussão |

Boas práticas: um gráfico por ideia, rótulos legíveis, números com unidades e a mensagem principal no título de cada slide.

#### Atividade da aula

Cada aluno ou dupla apresenta o próprio atributo e entrega o relatório. Os colegas fazem ao menos uma pergunta usando o roteiro abaixo.

**Banco de perguntas para a discussão:**

1. O RPD alcançado é suficiente para o uso que você propõe? Por quê?
2. O modelo mais simples teria bastado?
3. Que amostras foram removidas e com que critério?
4. O desempenho é parecido em todos os grupos?
5. O que aconteceria com amostras de uma região não representada na calibração?
6. Quais as limitações do dado de referência?

#### Critérios de avaliação do relatório e da apresentação

| Critério | Peso | O que se observa |
| --- | --- | --- |
| Coerência método, resultados e conclusão | 30% | O texto responde ao objetivo com base nos dados |
| Qualidade das figuras e tabelas | 20% | Legendas, unidades e interpretação |
| Reprodutibilidade | 20% | `config.py`, ordem dos notebooks e saídas organizadas |
| Senso crítico | 20% | Limitações, sobreajuste e domínio de aplicação |
| Clareza da apresentação | 10% | Tempo, estrutura e respostas |

#### Encerramento do curso

Retomar o fluxo (dado, tratamento, estrutura, modelo, validação, predição e relato), perguntar a cada aluno qual decisão metodológica considera mais importante e indicar os próximos passos: o curso de metodologia e a extensão do pipeline para outros atributos e algoritmos.

#### Entregável

Relatório final com os capítulos de resultados e conclusão preenchidos com os números do próprio atributo, e a apresentação.
