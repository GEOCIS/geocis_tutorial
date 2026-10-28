# Resultados e produtos (outcomes)

[← Capítulo 6](cap06_material_metodologia.md) · [Índice](README.md) · [Capítulo 8 →](cap08_conclusao.md)

*Capítulo do projeto de predição de atributos físicos e químicos do solo com espectroscopia Vis-NIR-SWIR (BSSL), em Python e Jupyter Notebook*

> Os valores entre colchetes \[ \] devem ser preenchidos com os resultados da execução do pipeline no banco real da BSSL. Cada trecho indica o arquivo de onde o número ou a figura deve ser retirado (pasta `resultados/`). Os dados sintéticos usados apenas para testar o código não devem ser relatados como resultado.

## 1. Caracterização do banco de dados

Após a leitura e a limpeza (notebook 01), o conjunto para o atributo \[atributo\] ficou com \[n\] amostras, de um total inicial de \[n inicial\], sendo \[n removidas\] excluídas por ausência do valor medido em laboratório. Os espectros possuem \[n bandas\] bandas, entre \[350\] e \[2500\] nm.

O atributo apresentou média de \[valor\] \[unidade\], desvio-padrão de \[valor\], mínimo de \[valor\] e máximo de \[valor\], com assimetria de \[valor\] (`df_limpo.pkl`, saída de `describe()`). A distribuição foi \[simétrica / assimétrica à direita / bimodal\] (figura `01_distribuicao_alvo.png`), o que \[justificou / não justificou\] transformação da variável resposta.

Os espectros brutos (figura `01_espectros_brutos.png`) apresentaram as feições esperadas para solos: aumento da reflectância do visível para o infravermelho próximo e absorções em torno de 1400, 1900 e 2200 nm, associadas à água, à hidroxila e aos argilominerais. As bandas mais correlacionadas com o atributo se concentraram em \[regiões espectrais\] (figura `01_correlacao_bandas.png`).

## 2. Efeito do pré-processamento

O corte das bordas manteve \[n bandas\] bandas entre \[450\] e \[2450\] nm. A comparação das etapas (figura `02_etapas_preprocessamento.png`) mostrou que \[descrever: por exemplo, a suavização reduziu o ruído, o SNV diminuiu a dispersão vertical entre espectros e a derivada removeu o deslocamento de linha de base\].

A detecção de outliers sinalizou \[n\] amostras (\[%\] do total) pelos critérios combinados (z-score: \[n\]; T²: \[n\]; Q: \[n\]). Após inspeção dos espectros, foram removidas \[n\] amostras, restando \[n final\] para as etapas seguintes (figura `02_outliers.png`). \[Descrever a natureza das amostras removidas, se identificada.\]

## 3. Estrutura espectral: PCA

Os dois primeiros componentes principais explicaram \[%\] e \[%\] da variância, e os \[n\] primeiros acumularam \[%\] (figura `03_variancia_pca.png`). O gráfico de escores (figura `03_escores_loadings.png`) mostrou \[gradiente do atributo ao longo de PC1 / agrupamentos / ausência de padrão claro\]. Os pesos de PC1 indicaram contribuição principal de \[regiões espectrais\], consistente com \[constituinte ou feição: matéria orgânica e cor, argilominerais, água etc.\].

## 4. Agrupamentos (cotovelo e k-means)

O método do cotovelo e o coeficiente de silhueta (figura `03_cotovelo_silhueta.png`) indicaram \[k\] grupos, com silhueta média de \[valor\]. Os grupos tiveram \[n1\], \[n2\] e \[n3\] amostras e diferiram quanto ao atributo, com médias de \[valores\] (tabela por grupo, notebook 03). Os espectros médios (figura `03_clusters.png`) distinguiram os grupos principalmente por \[albedo / intensidade da feição de 2200 nm / região do visível\]. Esses grupos foram usados para estratificar a divisão entre calibração e validação.

## 5. Desempenho dos modelos

### 5.1 Escolha do pré-tratamento e dos parâmetros

Na calibração (\[n\] amostras), o pré-tratamento com menor RMSECV no PLSR foi \[sg / d1 / snv\] (RMSECV de \[valor\]), como mostra a comparação dos três tratamentos (figura `04_rmsecv_plsr.png`). O número de variáveis latentes escolhido foi \[n\]. Para o Random Forest, a busca de hiperparâmetros selecionou \[n\] componentes principais, `max_features` de \[valor\] e `min_samples_leaf` de \[valor\] (RMSECV de \[valor\]).

### 5.2 Métricas

O desempenho nas \[n\] amostras de validação independentes é apresentado abaixo (`metricas.csv`).

| Modelo | Conjunto | n | R² | RMSE | RPD | RPIQ | Viés |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PLSR | Calibração | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| PLSR | Validação cruzada | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| PLSR | Validação | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| Random Forest | Calibração | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |
| Random Forest | Validação | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] | \[ \] |

Para interpretar o RPD, usa-se a classificação de Chang et al. (2001): abaixo de 1,4, modelo pouco confiável; de 1,4 a 2,0, modelo razoável, adequado para triagem; acima de 2,0, modelo bom a excelente. Com base nela, o modelo \[PLSR / Random Forest\] para \[atributo\] foi classificado como \[categoria\] (RPD de \[valor\] e RPIQ de \[valor\]).

### 5.3 Comparação entre PLSR e Random Forest

Na validação, o \[PLSR / Random Forest\] obteve melhor desempenho, com RMSE de \[valor\] contra \[valor\] do outro modelo, uma diferença de \[valor\]. A diferença entre as métricas de calibração e de validação foi \[pequena / grande\] no PLSR e \[pequena / grande\] no Random Forest, o que indica \[ausência / presença\] de sobreajuste. O gráfico de observado versus predito (figura `05_observado_predito.png`) mostrou \[pontos próximos à linha 1:1 / compressão dos extremos / maior dispersão nos valores altos\], e o viés foi de \[valor\], indicando \[superestimação / subestimação / ausência de tendência\].

O erro por grupo (tabela do notebook 05) foi menor no grupo \[x\] (RMSE de \[valor\]) e maior no grupo \[y\] (\[valor\]), sugerindo que \[interpretar: por exemplo, o desempenho depende da variabilidade e do número de amostras de cada grupo\].

## 6. Interpretação espectral dos modelos

Os coeficientes de regressão e o VIP do PLSR (figura `05_plsr_coef_vip.png`) destacaram as regiões de \[intervalos em nm\] como as mais importantes para predizer \[atributo\], com VIP acima de 1 em \[regiões\]. Essas regiões coincidem com \[feições conhecidas: água e hidroxila em 1400 e 1900 nm, argilominerais em 2200 nm, cor e matéria orgânica no visível\], o que indica que o modelo explora informação com sentido físico e químico, e não artefatos. No Random Forest, os componentes principais de maior importância foram \[PC x, PC y\] (figura `05_rf_importancia.png`), associados a \[interpretação dos pesos\].

## 7. Predição de novas amostras e domínio de aplicação

O modelo salvo (`modelo_solo.joblib`) foi aplicado a \[n\] amostras novas. Pelos indicadores T² e Q, \[n\] amostras (\[%\]) ficaram dentro do domínio de aplicação definido na calibração e \[n\] ficaram fora (figura `05_novas_vs_calibracao.png`). As predições das amostras fora do domínio foram \[sinalizadas / descartadas\], por representarem extrapolação. Os valores preditos pelos dois modelos tiveram concordância de \[valor\] (diferença média de \[valor\] \[unidade\]), registrada em `predicoes_novas_amostras.csv`.

## 8. Discussão

Os resultados \[confirmam / não confirmam\] que a espectroscopia Vis-NIR-SWIR permite predizer \[atributo\] com precisão \[adequada / limitada\] para \[uso pretendido\]. O desempenho foi \[melhor / pior\] do que o de \[atributos físicos ou químicos\] discutidos na literatura para a BSSL \[citar e comparar com a literatura\]. Em geral, atributos com relação direta com feições espectrais, como argila e matéria orgânica, tendem a ser mais bem preditos do que atributos sem resposta espectral direta, como alguns nutrientes, cuja predição depende de correlações indiretas com a mineralogia e a matéria orgânica.

O \[PLSR / Random Forest\] foi superior para \[atributo\]. O PLSR tem a vantagem da interpretabilidade e da simplicidade, enquanto o Random Forest pode capturar relações não lineares quando há grande heterogeneidade entre as amostras. \[Explicar o resultado obtido à luz dessas características.\]

### Limitações

- A validação foi feita em uma única divisão aleatória estratificada. Repetir o procedimento com diferentes sementes forneceria média e variabilidade das métricas.
- A BSSL reúne amostras de diferentes origens, laboratórios e épocas, e variações de método analítico entre fontes podem aumentar o erro de referência e limitar o desempenho.
- O modelo só é confiável para amostras com espectros semelhantes aos da calibração, como verificado pelo domínio de aplicação. Solos de regiões ou classes pouco representadas no banco exigem cautela.
- &#91;Outras limitações observadas na execução, como número reduzido de amostras em algum grupo.\]

## 9. Produtos obtidos (outcomes)

O projeto resultou nos seguintes produtos:

- **Pipeline reprodutível em cinco notebooks**: leitura e exploração, pré-processamento, PCA e clusterização, modelagem, e visualização e predição, controlados por um único arquivo de configuração (`config.py`) e por funções reutilizáveis (`utils.py`), que permitem repetir a análise para outros atributos alterando apenas a coluna-alvo.
- **Modelo de predição salvo** (`modelo_solo.joblib`), com pré-tratamento, número de variáveis latentes, PCA do domínio e limites de T² e Q, pronto para aplicação a novas amostras.
- **Resultados quantitativos**: tabela de métricas (R², RMSE, RPD, RPIQ e viés) para PLSR e Random Forest em calibração, validação cruzada e validação.
- **Figuras** para relatórios e apresentações, salvas em `resultados/figuras/`.
- **Predições** para amostras novas, com indicação de pertencimento ao domínio de aplicação.
- **Documentação metodológica** em forma de capítulos, cobrindo o material, os métodos e a interpretação dos resultados.

### Aplicações e contribuições

O fluxo desenvolvido permite estimar \[atributo\] a partir de um único espectro, em segundos e sem reagentes, como alternativa de triagem às análises convencionais, que são mais caras e demoradas. Isso é útil para mapeamento de solos em grande escala, agricultura de precisão e redução do número de amostras enviadas ao laboratório, que podem ser reservadas para as amostras fora do domínio ou para a confirmação dos resultados. Do ponto de vista formativo, o trabalho consolidou o uso de Python, Jupyter Notebook e bibliotecas de ciência de dados em um problema aplicado de agronomia.

### Recomendações e trabalhos futuros

1. Modelar os demais atributos físicos e químicos da BSSL com o mesmo pipeline e comparar o desempenho entre eles.
2. Testar outros métodos, como regressão por vetores de suporte, Cubist e redes neurais, e outros pré-tratamentos, como a segunda derivada e a remoção do contínuo.
3. Avaliar modelos locais por grupo contra o modelo global.
4. Realizar validação em amostras de um projeto independente, para estimar a capacidade de generalização do modelo.
5. Incorporar covariáveis ambientais (clima, relevo, material de origem) aos espectros.

## 10. Conclusões

O pipeline implementado, do tratamento dos espectros da BSSL à predição de amostras novas, produziu modelos com desempenho \[classificação\] para \[atributo\] (RPD de \[valor\] e RMSE de \[valor\] \[unidade\] na validação). O \[modelo\] foi o mais adequado, e a interpretação espectral confirmou que as predições se apoiam em feições associadas a \[constituintes\]. Com a verificação do domínio de aplicação e a documentação reprodutível, os resultados indicam que a abordagem é viável como ferramenta de apoio à análise de solos, respeitadas as limitações discutidas.

## Referência

CHANG, C.-W. et al. Near-infrared reflectance spectroscopy–principal components regression analyses of soil properties. *Soil Science Society of America Journal*, v. 65, n. 2, p. 480-490, 2001. \[conferir os dados completos da referência\]
