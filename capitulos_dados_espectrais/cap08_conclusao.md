# Conclusão

[← Capítulo 7](cap07_resultados.md) · [Índice](README.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

> Os valores entre colchetes \[ \] devem ser preenchidos com os resultados da execução do pipeline no banco real da BSSL.

## 1. Síntese do trabalho

Este trabalho teve como objetivo desenvolver e documentar um fluxo reprodutível, em Python e Jupyter Notebook, para predizer atributos físicos e químicos do solo a partir de espectros Vis-NIR-SWIR da Biblioteca Espectral de Solos do Brasil (BSSL). O fluxo abrangeu a leitura e a análise exploratória dos dados, o pré-processamento dos espectros (corte de bordas, absorbância, suavização de Savitzky-Golay, derivada, SNV e detecção de outliers), a redução de dimensionalidade por PCA, a clusterização pelo método do cotovelo e k-means, e a calibração de modelos PLSR e Random Forest, avaliados por R², RMSE, RPD e RPIQ em amostras independentes.

## 2. Principais conclusões

1. **Os espectros contêm informação suficiente para predizer o atributo estudado.** Para \[atributo\], o melhor modelo (\[PLSR / Random Forest\]) alcançou R² de \[valor\], RMSE de \[valor\] \[unidade\], RPD de \[valor\] e RPIQ de \[valor\] na validação, desempenho classificado como \[razoável / bom / excelente\].
2. **O pré-processamento foi determinante para a qualidade dos modelos.** O tratamento \[sg / d1 / snv\] apresentou o menor erro de validação cruzada, e a remoção de \[n\] espectros atípicos tornou os componentes principais e os modelos mais representativos do conjunto.
3. **A estrutura espectral do banco é heterogênea.** A análise de componentes principais e a clusterização identificaram \[k\] grupos de solos com comportamento espectral distinto, e o desempenho dos modelos variou entre eles, sendo \[melhor / pior\] no grupo \[x\].
4. **PLSR e Random Forest tiveram desempenhos \[semelhantes / distintos\].** O \[modelo\] foi superior, com diferença de \[valor\] no RMSE. O PLSR foi mais simples e interpretável, e o Random Forest \[capturou / não capturou\] ganhos associados a relações não lineares.
5. **As predições se apoiam em feições espectrais com sentido físico.** Os coeficientes e o VIP do PLSR concentraram-se em regiões associadas a \[água e hidroxila, argilominerais, cor e matéria orgânica\], o que dá maior confiança aos modelos.
6. **A verificação do domínio de aplicação é necessária.** Com os indicadores T² e Q, foi possível identificar amostras novas fora do domínio da calibração, cujas predições devem ser tratadas com cautela.

## 3. Contribuições

O principal produto é um pipeline modular, composto por cinco notebooks, um arquivo de configuração e funções reutilizáveis, que pode ser aplicado a outros atributos do solo alterando apenas a coluna-alvo e os parâmetros em `config.py`. O modelo ajustado, as métricas e as figuras são salvos automaticamente, o que facilita a replicação, a auditoria e a comunicação dos resultados. A abordagem pode apoiar a triagem de amostras, o mapeamento de solos e a redução de análises convencionais, mais caras e demoradas.

## 4. Limitações

Os resultados devem ser interpretados considerando que a validação foi feita em uma única divisão estratificada, que a BSSL reúne dados de diferentes origens e métodos analíticos, e que os modelos só são confiáveis dentro do domínio espectral da calibração. \[Acrescentar limitações específicas da execução.\]

## 5. Recomendações e perspectivas

Recomenda-se estender o pipeline aos demais atributos da BSSL, testar outros algoritmos (como SVR, Cubist e redes neurais) e outros pré-tratamentos, comparar modelos globais e locais por grupo, validar os modelos em um conjunto de um projeto independente e incorporar covariáveis ambientais. Essas etapas permitirão avaliar a capacidade de generalização e ampliar a aplicação prática da espectroscopia de solos no Brasil.

## 6. Considerações finais

O trabalho demonstrou que a combinação de espectroscopia Vis-NIR-SWIR, pré-processamento adequado e modelagem multivariada é uma alternativa promissora para a estimativa rápida de atributos do solo. Além dos resultados quantitativos, o projeto consolidou competências em Python, Jupyter Notebook e ciência de dados aplicada à agronomia, e deixou uma base reprodutível para novos estudos.
