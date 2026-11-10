# Preparação do professor

[← Plano do curso](README.md) · [Aula 1 →](aula_01_delineamento.md)

## Pré-requisitos

- **Pipeline executado:** a turma deve ter a pasta [`pipeline_bssl`](../pipeline_bssl/index.qmd) com os dados sintéticos gerados (`python gerar_dados_sinteticos.py`) e os notebooks 01 a 04 executados, com os dados sintéticos ou com a BSSL. As atividades reutilizam os arquivos da pasta [`resultados/`](../pipeline_bssl/config.qmd#cb1-13): [`dados_brutos.npz`](../pipeline_bssl/01_leitura_exploratoria.ipynb#salvar), [`df_limpo.pkl`](../pipeline_bssl/01_leitura_exploratoria.ipynb#salvar), [`df_pp.pkl`](../pipeline_bssl/02_preprocessamento.ipynb#remoção-e-salvamento), [`espectros_pp.npz`](../pipeline_bssl/02_preprocessamento.ipynb#remoção-e-salvamento), [`modelo_solo.joblib`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento) e [`predicoes_validacao.csv`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento).
- **Dados sintéticos:** foram gerados apenas para treinar o método. São muito "bem comportados" (relação praticamente linear e ruído baixo), então o desempenho é alto. Isso é útil para mostrar o efeito de cada decisão, mas **os números não são resultados científicos** e não devem ser relatados como tais.
- **Valores de referência:** os números citados nos gabaritos vêm de execuções de teste com os dados sintéticos, com [`SEED = 42`](../pipeline_bssl/config.qmd#cb1-22) e as bibliotecas instaladas na época. Servem como ordem de grandeza: os alunos obterão valores parecidos, mas não idênticos, e eles devem ser conferidos antes da aula. O que importa em cada atividade é o **padrão** observado, e não o valor exato.
- **Banco real:** com a BSSL, ajustar [`config.py`](../pipeline_bssl/config.qmd) e a coluna de identificação das amostras ([`id`](../pipeline_bssl/gerar_dados_sinteticos.qmd#cb1-74)) usada na célula de preparação. Em bancos grandes, usar uma subamostra se as atividades ficarem lentas.

## Célula de preparação (executar no início das aulas 2 a 8)

Em um notebook novo na pasta [`pipeline_bssl`](../pipeline_bssl/index.qmd) (por exemplo, `metodologia_aula02.ipynb`), executar:

```python
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, joblib
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import KFold, cross_val_predict, train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
import config as cfg, utils                           # cfg.PASTA aponta para a pasta resultados/

# --- dados brutos, só com as amostras mantidas após a remoção de outliers (notebook 02) ---
d = np.load(cfg.PASTA / 'dados_brutos.npz')
Xraw, y, wl_orig = d['X'], d['y'], d['wl_orig']
df = pd.read_pickle(cfg.PASTA / 'df_limpo.pkl')
df_pp = pd.read_pickle(cfg.PASTA / 'df_pp.pkl')        # banco sem outliers (notebook 02)
mant = df['id'].isin(df_pp['id']).values              # ajustar 'id' à coluna de identificação
Xraw, y, df = Xraw[mant], y[mant], df[mant].reset_index(drop=True)

# tratamentos calculados a partir do dado bruto
wl, X_abs = utils.preprocessa(Xraw, wl_orig, 'abs')
_,  X_sg  = utils.preprocessa(Xraw, wl_orig, 'sg')
_,  X_snv = utils.preprocessa(Xraw, wl_orig, 'snv')
Xabs = X_abs                                          # nome usado em algumas atividades

# --- espectros tratados salvos pelo notebook 02 e modelo salvo pelo notebook 04 ---
pp = np.load(cfg.PASTA / 'espectros_pp.npz')
Xsg, Xd1, Xsnv = pp['X_suav'], pp['X_d1'], pp['X_snv']
assert np.allclose(pp['y'], y), 'as amostras dos dois arquivos não estão na mesma ordem'
modelo = joblib.load(cfg.PASTA / 'modelo_solo.joblib')

# --- validação cruzada, divisão e funções auxiliares ---
cv = KFold(10, shuffle=True, random_state=cfg.SEED)
rmse = lambda a, b: np.sqrt(mean_squared_error(a, b))
Xtr, Xte, ytr, yte = train_test_split(X_snv, y, test_size=cfg.TEST_SIZE, random_state=cfg.SEED)

def rmsecv(modelo_, X, alvo):
    p = cross_val_predict(modelo_, X, alvo, cv=cv, n_jobs=-1).ravel()
    return rmse(alvo, p)

curva = [rmsecv(PLSRegression(n), Xtr, ytr) for n in range(1, 16)]
nlv = int(np.argmin(curva)) + 1
print('Amostras:', len(y), '| variáveis latentes pela validação cruzada:', nlv)
```

Variáveis disponíveis depois da célula:

| Variável | Conteúdo |
| --- | --- |
| `Xraw`, [`wl_orig`](../pipeline_bssl/01_leitura_exploratoria.ipynb#leitura) | Reflectância bruta e comprimentos de onda originais |
| [`X_abs`](../pipeline_bssl/02_preprocessamento.ipynb#tratamentos-espectrais) / `Xabs` | Absorbância, sem suavização |
| `X_sg`, [`X_snv`](../pipeline_bssl/02_preprocessamento.ipynb#tratamentos-espectrais) | Absorbância suavizada (Savitzky-Golay), com e sem SNV, calculadas na hora |
| `Xsg`, `Xd1`, `Xsnv` | Os mesmos tratamentos (e a 1ª derivada) salvos pelo notebook 02 |
| [`y`](../pipeline_bssl/01_leitura_exploratoria.ipynb#limpeza), [`wl`](../pipeline_bssl/02_preprocessamento.ipynb#tratamentos-espectrais) | Atributo-alvo (argila) e comprimentos de onda após o corte |
| [`df`](../pipeline_bssl/01_leitura_exploratoria.ipynb#leitura), [`df_pp`](../pipeline_bssl/02_preprocessamento.ipynb#remoção-e-salvamento) | Tabelas do banco limpo e do banco sem outliers (com a coluna [`cluster`](../pipeline_bssl/03_pca_clusterizacao.ipynb#k-means-final-e-caracterização-dos-grupos)) |
| [`modelo`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento) | Dicionário do modelo final do notebook 04 ([`nlv`](../pipeline_bssl/04_modelagem.ipynb#plsr-final), [`tratamento`](../pipeline_bssl/04_modelagem.ipynb#domínio-de-aplicação-e-salvamento) etc.) |
| [`Xtr`](../pipeline_bssl/04_modelagem.ipynb#plsr-final), [`Xte`](../pipeline_bssl/04_modelagem.ipynb#plsr-final), [`ytr`](../pipeline_bssl/04_modelagem.ipynb#divisão-calibraçãovalidação), [`yte`](../pipeline_bssl/04_modelagem.ipynb#divisão-calibraçãovalidação) | Divisão calibração/validação sobre [`X_snv`](../pipeline_bssl/02_preprocessamento.ipynb#tratamentos-espectrais) |
| [`cv`](../pipeline_bssl/04_modelagem.ipynb#comparação-de-tratamentos-rmsecv-do-plsr), `rmse`, `rmsecv`, [`nlv`](../pipeline_bssl/04_modelagem.ipynb#plsr-final) | Validação cruzada de 10 partições, funções de erro e nº de LVs escolhido |

Os dados desta célula **já têm os outliers removidos** (notebook 02), o que importa: com espectros anômalos no conjunto, os resultados das atividades mudam muito.

> Observação: no material original havia duas células de preparação (uma carregando os arquivos com [`cfg.PASTA`](../pipeline_bssl/config.qmd#cb1-13) e outra com `'resultados/...'`). Elas foram unificadas aqui. O `assert` confirma que os espectros salvos e os recalculados correspondem às mesmas amostras; se ele falhar, verificar a coluna de identificação usada em `mant`.
