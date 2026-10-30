"""Funções de apoio do curso de espectroscopia de solos.

Cada aula importa daqui as funções das aulas ANTERIORES, para que o
notebook rode sozinho. A função da aula atual é escrita pelo aluno.
"""
from pathlib import Path
import importlib.util
import json
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'Data'
OUT_DIR = ROOT / 'Outputs' / 'curso'
FIG_DIR = OUT_DIR / 'Figures'

NIR_FILE = 'Atributos_VIS.NIR_SP.csv'
MIR_FILE = 'Atributos_MIR_SP.csv'
ALVOS = ['Clay_gkg', 'Sand_gkg', 'C_gkg', 'OM_gkg']


# ---------------------------------------------------------------- Aula 1
def checar_dependencias(pacotes):
    return [pip for pip, mod in pacotes.items() if importlib.util.find_spec(mod) is None]


def preparar_pastas():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- Aula 2
def ler_csv_auto(path):
    for enc in ('utf-8', 'latin1', 'cp1252'):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False), enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f'Não foi possível ler {path} com utf-8, latin1 ou cp1252.')


def separar_colunas(df):
    meta, espec, wl = [], [], []
    for c in df.columns:
        try:
            wl.append(float(c))
            espec.append(c)
        except ValueError:
            meta.append(c)
    return meta, espec, np.array(wl)


def carregar_dominio(nome_arquivo):
    """Lê um CSV de Data/ e devolve (meta, X, wl)."""
    path = DATA_DIR / nome_arquivo
    if not path.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {path}. Coloque os CSVs em {DATA_DIR}.')
    df, _ = ler_csv_auto(path)
    meta, espec, wl = separar_colunas(df)
    X = df[espec].apply(pd.to_numeric, errors='coerce').to_numpy(float)
    return df[meta].reset_index(drop=True), X, wl


def preencher_nan(X):
    """Substitui NaN pela média da coluna (banda)."""
    X = X.copy()
    medias = np.nanmean(X, axis=0)
    linhas, colunas = np.where(~np.isfinite(X))
    X[linhas, colunas] = medias[colunas]
    return X


# ---------------------------------------------------------------- Aula 3
def validar(X, espec, nome):
    criticos, avisos = [], []
    if len(espec) == 0:
        criticos.append('Nenhuma coluna espectral encontrada.')
    if X.ndim != 2 or X.shape[1] <= 1:
        criticos.append('Só uma coluna lida: verifique o delimitador (; ou ,).')
    n_neg = int(np.sum(X[np.isfinite(X)] < 0))
    if n_neg:
        criticos.append(f'{n_neg} valores negativos.')
    frac_nan = float(np.mean(~np.isfinite(X))) if X.size else 1.0
    if frac_nan > 0.01:
        avisos.append(f'{frac_nan:.1%} de valores faltantes.')
    for a in avisos:
        print(f'[{nome}] AVISO: {a}')
    if criticos:
        raise ValueError(f'[{nome}] ' + ' | '.join(criticos))
    print(f'[{nome}] validação OK: {X.shape[0]} amostras x {X.shape[1]} bandas')


# ---------------------------------------------------------------- Aula 4
def plot_qc(wl, X, titulo, inverter=False, unidade='nm'):
    import matplotlib.pyplot as plt
    m, s = X.mean(0), X.std(0)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(wl, X[:200].T, alpha=0.05, color='tab:blue')
    ax[0].set_title(f'{titulo}: espectros brutos')
    ax[1].plot(wl, m, color='tab:blue')
    ax[1].fill_between(wl, m - s, m + s, alpha=0.2)
    ax[1].set_title(f'{titulo}: média ± 1 DP')
    for a in ax:
        a.set_xlabel(f'Comprimento/número de onda ({unidade})')
        a.set_ylabel('Reflectância')
        a.grid(alpha=0.2)
        if inverter:
            a.invert_xaxis()
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- Aula 5
def subamostra(meta, X, n=500, seed=42):
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(len(X), size=min(n, len(X)), replace=False))
    return meta.iloc[idx].reset_index(drop=True), X[idx]


def cortar(X, wl, minimo):
    m = wl >= minimo
    return X[:, m], wl[m]


def suavizar(X, wl, w=11, p=2, deriv=0):
    delta = float(np.median(np.abs(np.diff(wl))))
    return savgol_filter(X, w, p, deriv=deriv, delta=delta, axis=1)


# ---------------------------------------------------------------- Aula 6
def snv(X):
    return (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)


def outliers_pca(X, k=8, q=0.99):
    Xc = X - X.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    T = U[:, :k] * S[:k]
    lam = (S[:k] ** 2) / (len(X) - 1)
    T2 = np.sum(T ** 2 / lam, axis=1)
    resid = Xc - T @ Vt[:k]
    Q = np.sum(resid ** 2, axis=1)
    return (T2 > np.quantile(T2, q)) | (Q > np.quantile(Q, q)), T2, Q


def preparar_nir(n=500, minimo=450, seed=42):
    """Aulas 2 a 6 em uma chamada: devolve (meta, X_snv_sem_outliers, wl)."""
    meta, X, wl = carregar_dominio(NIR_FILE)
    X = preencher_nan(X)
    meta, X = subamostra(meta, X, n=n, seed=seed)
    X, wl = cortar(X, wl, minimo)
    X = snv(suavizar(X, wl))
    out, _, _ = outliers_pca(X)
    return meta.loc[~out].reset_index(drop=True), X[~out], wl


# ---------------------------------------------------------------- Aula 7
def pca_svd(X, k):
    Xc = X - X.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = S ** 2 / np.sum(S ** 2)
    return U[:, :k] * S[:k], Vt[:k], var[:k]


def correlacoes(scores, meta, alvos):
    linhas = {}
    for alvo in alvos:
        if alvo not in meta.columns:
            continue
        y = pd.to_numeric(meta[alvo], errors='coerce').to_numpy(float)
        ok = np.isfinite(y)
        linhas[alvo] = [np.corrcoef(scores[ok, j], y[ok])[0, 1] for j in range(scores.shape[1])]
    return pd.DataFrame(linhas, index=[f'PC{j + 1}' for j in range(scores.shape[1])]).T


# ---------------------------------------------------------------- Aula 8
def kmeans_grid(Z, ks):
    from sklearn.cluster import KMeans
    return np.array([KMeans(int(k), n_init=20, random_state=42).fit(Z).inertia_ for k in ks])


def cotovelo_shi(ks, inercias):
    ks = np.asarray(ks, float)
    inercias = np.asarray(inercias, float)
    k = (ks - ks.min()) / np.ptp(ks)
    i = (inercias - inercias.min()) / np.ptp(inercias)
    angulos = np.full(len(ks), np.nan)
    for j in range(1, len(ks) - 1):
        v1 = [k[j - 1] - k[j], i[j - 1] - i[j]]
        v2 = [k[j + 1] - k[j], i[j + 1] - i[j]]
        c = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angulos[j] = np.degrees(np.arccos(np.clip(c, -1, 1)))
    return int(ks[np.nanargmin(angulos)]), angulos


# ---------------------------------------------------------------- Aula 9
def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(p) - np.asarray(y)) ** 2)))


def rpiq(y, p):
    q1, q3 = np.percentile(y, [25, 75])
    return float((q3 - q1) / rmse(y, p))


def ccc(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    cov = np.mean((y - y.mean()) * (p - p.mean()))
    return float(2 * cov / (y.var() + p.var() + (y.mean() - p.mean()) ** 2))


# ---------------------------------------------------------------- Aula 10
def run_stamp(etapa, payload):
    return {'stage': etapa,
            'timestamp': datetime.now().isoformat(),
            'python': sys.version,
            **payload}


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
