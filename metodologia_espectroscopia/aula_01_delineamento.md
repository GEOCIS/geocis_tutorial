# Aula 1: Delineamento do estudo

[← Preparação](00_preparacao.md) · [Plano do curso](README.md) · [Aula 2 →](aula_02_espectroscopia_e_referencia.md)

**Questão central:** que pergunta o estudo responde e como saber se deu certo?

**Objetivos:** formular a pergunta de pesquisa, definir variáveis e critérios de sucesso antes de analisar os dados e escrever um protocolo de análise.

**Tópicos:**

- Da necessidade prática (reduzir análises de laboratório) à pergunta de pesquisa e aos objetivos específicos.
- Definição das variáveis: preditoras (espectros) e respostas (atributos físicos e químicos), e do uso pretendido do modelo (triagem, mapeamento, substituição de análise).
- Critérios de sucesso definidos a priori: por exemplo, RPD mínimo aceitável para o uso pretendido.
- Planejamento da análise antes de ver os resultados, como defesa contra resultados escolhidos *a posteriori*.
- Estrutura de um fluxo de trabalho: exploração, pré-processamento, modelagem, validação e aplicação.

Esta aula não usa código.

## Conteúdo

### Da necessidade à pergunta

Um estudo de predição por espectroscopia nasce de uma necessidade prática: as análises convencionais de solo são caras, lentas e geram resíduos químicos, e há demanda por estimativas rápidas (por exemplo, reduzir o custo e o tempo das análises de rotina de argila). Isso precisa virar uma pergunta de pesquisa respondível com dados, por exemplo: *"Espectros Vis-NIR-SWIR de amostras de solos brasileiros predizem o teor de argila com erro compatível com a triagem de amostras?"* Compare:

- **Objetivo fraco:** "aplicar aprendizado de máquina a espectros de solo". Descreve uma ferramenta, não um resultado.
- **Objetivo forte:** "avaliar se espectros Vis-NIR-SWIR da BSSL permitem predizer o teor de argila com erro compatível com a triagem de amostras, comparando PLSR e Random Forest em amostras independentes". Define o atributo, o dado, os métodos, o critério de comparação e o uso.

### O uso pretendido define a exigência

A mesma precisão pode ser suficiente para uma coisa e insuficiente para outra:

| Uso | Pergunta que a precisão deve responder |
| --- | --- |
| Triagem | O modelo separa amostras de teor baixo, médio e alto? |
| Mapeamento | O erro é pequeno comparado à variação espacial do atributo? |
| Apoio à rotina | O erro é compatível com a incerteza do método de laboratório? |
| Substituição da análise | O erro é aceitável para a decisão que se toma com o resultado? |

### Variáveis e unidade amostral

- **Preditoras:** o espectro (reflectância por banda).
- **Respostas:** os atributos de laboratório (cada um, um problema separado).
- **Auxiliares:** local, profundidade, classe de solo, data de coleta, laboratório de origem. Servem para entender a estrutura do banco e para desenhar a validação.
- **Unidade amostral e dependência.** Amostras do mesmo perfil, da mesma fazenda ou do mesmo projeto não são independentes: tendem a se parecer mais entre si. Isso afeta a validação (aula 7) e deve ser identificado já no delineamento.

### Elementos do protocolo de análise

Antes de abrir os dados, definir por escrito:

| Elemento | Pergunta a responder | Exemplo |
| --- | --- | --- |
| Objetivo | O que será estimado e para quê? | Predizer argila para triagem de amostras |
| População | A que solos o resultado se aplica? | Solos da região \[X\], horizonte superficial |
| Variável resposta | Qual atributo e qual método de referência? | Argila (g/kg) pelo método do densímetro |
| Preditores | Qual instrumento e faixa espectral? | Vis-NIR-SWIR, 450 a 2450 nm |
| Uso pretendido | Quem usará o resultado e como? | Decidir quais amostras vão ao laboratório |
| Critério de sucesso | Que desempenho mínimo é aceitável? | RPD mínimo e RMSE máximo acordados com o usuário |
| Divisão dos dados | Como separar calibração e validação? | 70/30 estratificada, definida antes da modelagem |
| Análises previstas | Quais métodos serão comparados? | PLSR e Random Forest |

### Critérios de sucesso definidos *a priori*

O desempenho "bom" depende do uso: uma triagem tolera erros maiores do que a substituição de uma análise de rotina. Antes de ver os resultados, definir o que será considerado suficiente, por exemplo "RPD de validação igual ou maior que 2,0 e RMSE menor que \[valor\] % de argila". O critério deve ser combinado com quem vai usar o modelo, com o orientador e com a literatura. A classificação de Chang et al. (2001) é uma referência para o RPD (abaixo de 1,4, pouco confiável; de 1,4 a 2,0, razoável; acima de 2,0, bom a excelente), e não uma regra universal. Fixar o critério depois do resultado leva a declarar sucesso sempre.

### Plano de análise e o risco das decisões *a posteriori*

Em uma análise com muitas decisões (janela do filtro, tratamento, número de componentes, remoção de amostras, divisão dos dados, algoritmo), existe a tentação de testar muitas combinações e relatar a melhor. Se a escolha for feita olhando o conjunto de validação, o desempenho relatado fica otimista, mesmo sem má-fé, e a combinação "vencedora" pode ser apenas sorte. A defesa é metodológica:

1. escrever antes o conjunto de alternativas a serem comparadas;
2. decidir apenas com dados de calibração (validação cruzada);
3. usar a validação uma única vez, ao final.

Na prática, isso é o que o notebook 04 faz. Em alguns campos, usa-se o pré-registro do protocolo. Em um projeto como este, uma versão simples é escrever e datar o protocolo e versioná-lo junto com o código.

### Viabilidade

Verificar antes de começar: número de amostras do atributo, cobertura da variação de interesse, qualidade e origem do dado de referência, e permissões de uso e citação dos dados (no caso da BSSL, citar a fonte adequada).

### Estrutura do fluxo

Exploração, pré-processamento, modelagem, validação e aplicação. Cada etapa do protocolo corresponde a uma etapa do pipeline e a uma decisão registrável em `config.py`.

## Modelo de protocolo de análise

```markdown
# Protocolo de análise

**Pergunta de pesquisa:**
**Objetivo geral e específicos:**
**Uso pretendido do modelo:** (triagem, mapeamento, apoio à rotina, substituição)
**População:** (solos, região, profundidade)
**Atributo(s), unidade e método de referência:**
**Dados:** fonte, nº de amostras, instrumento, faixa espectral
**Unidade amostral e possíveis dependências:** (perfil, local, projeto)
**Critério de sucesso (definido antes dos resultados):** (métrica, valor, conjunto de avaliação)
**Divisão dos dados:** (proporção e forma)
**Alternativas a comparar:** (tratamentos, modelos e seus hiperparâmetros)
**Como as escolhas serão feitas:** (validação cruzada na calibração)
**Como o desempenho final será avaliado:** (divisão, métricas)
**Riscos e limitações previstos:**
```

## Atividade: escrever e revisar o protocolo

1. Cada aluno (ou dupla) escolhe um atributo (argila, matéria orgânica ou outro) e preenche o protocolo, em no máximo uma página, definindo explicitamente:
   - o critério de sucesso (RPD e RMSE mínimos aceitáveis) e a justificativa;
   - a proporção e a forma da divisão dos dados;
   - três decisões que **não** serão tomadas com base na validação (número de LVs, pré-tratamento e hiperparâmetros).
2. Em duplas, cada aluno revisa o protocolo do colega com este roteiro:
   - (a) o objetivo diz o que será medido e comparado? É mensurável?
   - (b) o critério de sucesso está definido sem olhar resultados e é compatível com o uso?
   - (c) as decisões serão tomadas sem usar a validação?
   - (d) a população está clara?
   - (e) há dependências entre amostras que a divisão deveria respeitar?
3. Discussão em grupo dos problemas mais comuns encontrados.

## Estudo de caso para discussão

Dois cenários:

- **A:** um laboratório quer usar um modelo para estimar a matéria orgânica e dispensar a análise convencional em todas as amostras de rotina.
- **B:** um grupo de pesquisa quer mapear o teor de argila de uma região usando espectros de milhares de pontos amostrados.

Pedir que a turma discuta, para cada cenário, que critério de sucesso é razoável, que erro é tolerável, quais as consequências de uma predição errada e se a mesma divisão de dados serve nos dois casos.

**Pontos de discussão:** no cenário A, o custo do erro é maior (decisões individuais por amostra), e o critério deve ser mais exigente, com monitoramento contínuo e reanálise periódica de amostras. No cenário B, o erro médio importa mais do que o erro individual, e uma incerteza maior pode ser aceitável. Em ambos, a representatividade da calibração em relação às amostras futuras é crítica.

## Exercícios

1. Reescrever os três objetivos fracos a seguir como objetivos fortes: (a) "usar Python para analisar espectros"; (b) "melhorar a predição de matéria orgânica"; (c) "testar vários modelos".
2. Classificar cada frase como objetivo, hipótese ou critério de sucesso: (a) "o RPD de validação será maior que 2,0"; (b) "o PLSR e o Random Forest terão desempenho diferente na predição da argila"; (c) "comparar PLSR e Random Forest na predição da argila".
3. Um banco tem 600 amostras de 30 perfis, com 20 profundidades por perfil. Que problema isso traz para a divisão aleatória entre calibração e validação? Como evitá-lo?

<details>
<summary>Gabarito</summary>

1. Exemplos: (a) "avaliar se o PLSR aplicado a espectros Vis-NIR-SWIR prediz o teor de argila com RPD de validação maior que 2,0"; (b) "comparar o PLSR com tratamento de derivada e o Random Forest na predição da matéria orgânica, pelo RMSE em amostras independentes"; (c) "comparar PLSR e Random Forest, com hiperparâmetros definidos por validação cruzada, quanto a RMSE, RPD e RPIQ na validação".
2. (a) critério de sucesso; (b) hipótese; (c) objetivo.
3. Amostras do mesmo perfil são parecidas entre si, e uma divisão aleatória coloca profundidades do mesmo perfil na calibração e na validação, o que torna a validação otimista. Evita-se dividindo por perfil, de modo que todas as amostras de um perfil fiquem no mesmo conjunto (validação por grupos).

</details>

## Perguntas de verificação

1. **Por que definir o critério de sucesso antes da análise?** Para que o resultado seja julgado por um padrão independente dele, e não ajustado depois para parecer bom, o que levaria a afirmar sucesso a partir de um resultado ocasional ou de uma escolha conveniente.
2. **O que é uma decisão *a posteriori* e por que é um problema?** É uma escolha metodológica feita depois de ver os resultados na validação. Ela contamina a estimativa de desempenho, que deixa de ser independente.
3. **Qual é o risco de testar muitas combinações e relatar a melhor?** O desempenho relatado fica otimista e a combinação pode não se repetir em amostras novas. A defesa é decidir só com a calibração e usar a validação uma única vez.
4. **Por que a unidade amostral importa?** Porque amostras dependentes entre si (mesmo perfil, local ou projeto) tornam a validação otimista se forem separadas entre calibração e validação.
5. **Por que a população de interesse precisa estar descrita?** Porque o modelo só é válido para solos semelhantes aos da calibração, e isso define os limites das conclusões.

## Leituras

CHANG et al. (2001), para o contexto de interpretação do RPD. DEMATTÊ et al. (2019), para a BSSL. (Conferir os dados completos das referências.)

## Entregável

Protocolo de análise de uma página, revisado por um colega, com o critério de sucesso e as alternativas a comparar.
