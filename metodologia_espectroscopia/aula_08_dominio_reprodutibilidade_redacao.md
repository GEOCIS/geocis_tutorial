# Aula 8: Domínio de aplicação, reprodutibilidade e redação

[← Aula 7](aula_07_validacao_metricas_incerteza.md) · [Plano do curso](README.md)

**Questão central:** como garantir confiança e comunicar o método?

**Objetivos:** definir quando o modelo pode ser usado, garantir a reprodutibilidade e redigir a metodologia.

**Tópicos:**

- Domínio de aplicação: T², Q e alavancagem, limites definidos na calibração, e o tratamento de amostras fora do domínio (sinalizar, descartar, ampliar a calibração).
- Transferência entre instrumentos e protocolos: o problema e as soluções mais comuns (padronização, inclusão de amostras do novo instrumento).
- Reprodutibilidade: parâmetros centralizados em arquivo de configuração, sementes aleatórias, versões das bibliotecas (`requirements.txt`), notebooks executados de cima para baixo e controle de versão com Git.
- Gestão dos dados: o que pode ser publicado, licenças, e cuidado com dados de terceiros.
- Redação da seção de metodologia: material, pré-processamento, divisão dos dados, modelos, validação e métricas, com detalhe suficiente para que outra pessoa repita o trabalho.

**Antes da aula:** executar a [célula de preparação](00_preparacao.md#célula-de-preparação-executar-no-início-das-aulas-2-a-8).


## Conteúdo

### Domínio de aplicação

O modelo é confiável para amostras semelhantes às da calibração. Para decidir se uma amostra nova está no domínio, comparam-se os seus T² e Q (aula 3 do curso por capítulos) com limites definidos **na calibração** (por exemplo, o percentil 99). Opções para as amostras fora do domínio: sinalizar e relatar a predição como extrapolação, descartar, ou analisar em laboratório e **incorporá-las à calibração** (atualização do modelo). A escolha do limite equilibra o risco de aceitar predições ruins e o de rejeitar predições boas.

### Transferência entre instrumentos e protocolos

Um modelo calibrado com espectros de um equipamento e de um protocolo pode perder desempenho com espectros de outro equipamento, por diferenças de resolução, geometria e resposta. Soluções comuns: padronizar o protocolo, usar amostras de referência medidas nos dois equipamentos (padronização direta ou por transformação), reamostrar a grade espectral e incluir amostras do novo equipamento na calibração. A solução mais simples é medir tudo no mesmo equipamento e protocolo.

### Reprodutibilidade

Um estudo é reprodutível quando outra pessoa, com os mesmos dados e a descrição, obtém os mesmos resultados. Práticas:

- **Parâmetros em um arquivo de configuração** (`config.py`) e **sementes aleatórias** fixas.
- **Ambiente registrado:** versão do Python e das bibliotecas (`pip freeze > requirements.txt`).
- **Notebooks executados de cima para baixo** e saídas geradas por código.
- **Controle de versão** (Git) e um repositório com README.
- **Metadados da execução:** data, versões e parâmetros salvos junto com os resultados.

### Gestão e compartilhamento de dados

Verificar a licença e as permissões de uso dos dados (a BSSL reúne dados de várias fontes), a existência de dados sensíveis ou de terceiros e as exigências do orientador, da instituição e do periódico. Quando os dados não puderem ser publicados, descrever como obtê-los e publicar o código e os dados sintéticos de exemplo.

### Redação da metodologia

O texto deve ter detalhe suficiente para a reprodução, e ser organizado na ordem do fluxo:

1. **Material:** origem dos dados, número de amostras, atributos e métodos de referência, instrumento e protocolo espectral.
2. **Pré-processamento:** corte, transformação, suavização (janela e grau), derivada, correção de espalhamento e critérios de remoção de outliers, com o número de amostras antes e depois.
3. **Divisão dos dados:** proporção, método (aleatório, estratificado, por grupos) e semente.
4. **Modelos:** algoritmos, bibliotecas e versões, escolha de hiperparâmetros (critério e faixa pesquisada).
5. **Validação e métricas:** esquema de validação, métricas calculadas, escala e como foram calculadas.
6. **Domínio de aplicação e software:** critério de domínio, ambiente computacional e disponibilidade do código.

## Atividade 1: domínio de aplicação na prática

Calibrar com os 70% menores valores do atributo e testar com os 30% maiores, que estão fora da faixa de calibração, e verificar se o critério de domínio os identifica:

```python
from sklearn.decomposition import PCA

lim = np.percentile(y, 70)
tr, te = np.where(y <= lim)[0], np.where(y > lim)[0]

pca_d = PCA(n_components=cfg.N_PCS_DOMINIO).fit(Xsg[tr])
t2_tr, q_tr = utils.t2_q(pca_d, Xsg[tr])
lim_t2, lim_q = np.percentile(t2_tr, cfg.PERC_DOMINIO), np.percentile(q_tr, cfg.PERC_DOMINIO)

t2_te, q_te = utils.t2_q(pca_d, Xsg[te])
fora = (t2_te > lim_t2) | (q_te > lim_q)

m = PLSRegression(modelo['nlv']).fit(Xsg[tr], y[tr])
erro = np.abs(m.predict(Xsg[te]).ravel() - y[te])

print('Calibração fora do limite:', f'{((t2_tr > lim_t2) | (q_tr > lim_q)).mean():.1%}')
print(f'Teste fora do domínio: {fora.sum()} de {len(te)}')
print('Erro absoluto médio dentro do domínio:', erro[~fora].mean().round(2))
print('Erro absoluto médio fora do domínio  :', erro[fora].mean().round(2))
```

**Gabarito e observações:** na execução de teste, cerca de 2% da calibração ficou acima do limite (o esperado pelo percentil 99), e 74 das 253 amostras de teste foram sinalizadas como fora do domínio. O erro absoluto médio foi de cerca de 2,6 dentro do domínio e de cerca de 5,4 fora dele, ou seja, o critério identifica as amostras em que o modelo erra mais. Discutir: o critério não é perfeito (há amostras sinalizadas com erro baixo e amostras dentro do domínio com erro alto), e o limite deve ser ajustado ao uso.

## Atividade 2: metadados da execução

Salvar os parâmetros e as versões junto com o modelo, para registrar as condições da análise:

```python
import json, platform, datetime, sklearn, scipy

meta = {
    'data_execucao': datetime.datetime.now().isoformat(timespec='seconds'),
    'python': platform.python_version(),
    'bibliotecas': {'numpy': np.__version__, 'pandas': pd.__version__,
                    'scipy': scipy.__version__, 'scikit-learn': sklearn.__version__},
    'parametros': {k: getattr(cfg, k) for k in
                   ('COL_ALVO', 'WL_MIN', 'WL_MAX', 'SG_JANELA', 'SG_GRAU', 'K',
                    'TEST_SIZE', 'SEED', 'CV_FOLDS', 'MAX_LV')},
    'tratamento': modelo['tratamento'],
    'n_variaveis_latentes': int(modelo['nlv']),
}
with open(cfg.PASTA / 'metadados_execucao.json', 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=2, ensure_ascii=False)
print(json.dumps(meta, indent=2, ensure_ascii=False))
```

A tarefa é verificar que o arquivo foi criado e discutir o que mais deveria ser registrado (por exemplo, o código de versão do Git).

## Atividade 3: escrever a seção de metodologia

Cada aluno escreve a seção de metodologia do seu estudo seguindo os seis blocos acima, em cerca de uma página. Modelo de parágrafo para o bloco de modelos:

> "Os modelos foram implementados em Python \[versão\] com a biblioteca scikit-learn \[versão\]. O PLSR teve o número de variáveis latentes (1 a 20) definido pelo menor RMSE de validação cruzada em 10 partições, aplicada apenas ao conjunto de calibração (n = \[ \]). O Random Forest (\[ \] árvores) foi treinado sobre os \[ \] primeiros componentes principais, com o PCA ajustado apenas na calibração, e seus hiperparâmetros foram escolhidos por busca aleatória com validação cruzada em 5 partições. A semente aleatória foi \[ \]."

## Atividade 4: reprodução cruzada

Em duplas, o colega recebe **apenas o texto da metodologia e o repositório** e tenta reproduzir as métricas do autor. Ele anota o que faltou na descrição (parâmetro não informado, versão, caminho de dados) e o autor corrige o texto e o repositório. Este é o teste mais direto de reprodutibilidade.

## Perguntas de verificação

1. **Por que o limite de T² e Q é definido na calibração?** Para que o critério de pertencimento ao domínio seja independente das amostras que se está avaliando.
2. **O que fazer com amostras novas fora do domínio?** Sinalizar a predição como extrapolação, descartar, ou analisar em laboratório e incorporar à calibração.
3. **O que torna um estudo reprodutível?** Dados (ou descrição de acesso), código versionado, parâmetros e sementes registrados, ambiente documentado e descrição metodológica completa.

## Seminário final

Cada aluno apresenta (8 a 10 minutos) uma decisão metodológica do seu estudo, mostrando as alternativas consideradas, a evidência que embasou a escolha e a limitação associada. Os colegas fazem perguntas usando o [quadro de decisões](README.md#3-quadro-de-decisões-metodológicas-do-projeto) do plano do curso.

## Entregável

Seção de metodologia revisada, repositório reprodutível, arquivo de metadados da execução e relatório da reprodução cruzada.

## Encerramento do curso

Retomar o quadro de decisões metodológicas, pedir que cada aluno indique a decisão que mais mudaria o seu resultado e a que ele tomaria de forma diferente depois do curso, e orientar os próximos passos: modelar outros atributos com o pipeline, testar outros algoritmos e validar em um conjunto independente. Reforçar a mensagem central do curso: o resultado de um modelo vale tanto quanto a qualidade das decisões e da validação que o sustentam.
