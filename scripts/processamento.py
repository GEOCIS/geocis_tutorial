"""Módulo 2 - Processamento espectral.

Funções puras (recebem e devolvem ``DataFrame`` ou ``ndarray`` com amostras nas
linhas e bandas nas colunas) e transformadores compatíveis com scikit-learn
para uso dentro de ``Pipeline`` (o MSC, por exemplo, aprende o espectro de
referência só no conjunto de treino, evitando vazamento de informação).

Equivalências com o R (pacote ``prospectr``):
    savitzkyGolay()      -> savgol()
    standardNormalVariate() -> snv()
    msc()                -> msc()
    detrend()            -> detrend()
    continuumRemoval()   -> continuum_removal()
    resample()           -> resample()
    binning()            -> binning()
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline


def _unwrap(X):
    """Devolve (array float, função para reembrulhar no formato de entrada)."""
    if isinstance(X, pd.DataFrame):
        index, columns = X.index, X.columns

        def wrap(arr, new_columns=None):
            cols = columns if new_columns is None else new_columns
            return pd.DataFrame(arr, index=index, columns=cols)
        return X.to_numpy(dtype=float), wrap
    arr = np.asarray(X, dtype=float)
    return (arr[None, :] if arr.ndim == 1 else arr), (lambda a, new_columns=None: a)


def spectral_axis(X) -> np.ndarray:
    """Eixo espectral (nm ou cm-1) a partir das colunas de um DataFrame."""
    return np.asarray(X.columns, dtype=float)


# ---------------------------------------------------------------------------
# Suavização e derivadas
# ---------------------------------------------------------------------------

def savgol(X, window: int = 11, polyorder: int = 2, deriv: int = 0, delta: float = 1.0):
    """Filtro Savitzky-Golay (suavização e/ou derivada).

    ``window`` - tamanho da janela (ímpar, em número de bandas);
    ``polyorder`` - grau do polinômio ajustado em cada janela;
    ``deriv`` - 0 suaviza, 1 = 1ª derivada, 2 = 2ª derivada;
    ``delta`` - espaçamento entre bandas (para derivadas em unidades físicas).
    """
    if window % 2 == 0:
        raise ValueError("window deve ser ímpar")
    arr, wrap = _unwrap(X)
    return wrap(savgol_filter(arr, window, polyorder, deriv=deriv, delta=delta, axis=1))


def derivative(X, order: int = 1, window: int = 11, polyorder: int = 2):
    """Derivada Savitzky-Golay de ordem ``order`` com espaçamento real do eixo, se houver."""
    delta = 1.0
    if isinstance(X, pd.DataFrame) and X.shape[1] > 1:
        delta = float(np.mean(np.abs(np.diff(spectral_axis(X)))))
    return savgol(X, window, max(polyorder, order), deriv=order, delta=delta)


def moving_average(X, window: int = 11):
    """Média móvel simples (comparação didática com o Savitzky-Golay)."""
    arr, wrap = _unwrap(X)
    kernel = np.ones(window) / window
    pad = window // 2
    padded = np.pad(arr, ((0, 0), (pad, pad)), mode="edge")
    out = np.apply_along_axis(lambda r: np.convolve(r, kernel, mode="valid"), 1, padded)
    return wrap(out)


# ---------------------------------------------------------------------------
# Correções de espalhamento e linha de base
# ---------------------------------------------------------------------------

def snv(X):
    """Standard Normal Variate: centra e escala cada espectro pela própria média e desvio."""
    arr, wrap = _unwrap(X)
    mean = arr.mean(axis=1, keepdims=True)
    std = arr.std(axis=1, ddof=1, keepdims=True)
    return wrap((arr - mean) / std)


def msc(X, reference=None, return_reference: bool = False):
    """Multiplicative Scatter Correction.

    Cada espectro x é regredido contra a referência r (x = a + b·r) e corrigido
    para (x - a) / b. Por padrão a referência é o espectro médio de ``X``.
    """
    arr, wrap = _unwrap(X)
    ref = arr.mean(axis=0) if reference is None else np.asarray(reference, dtype=float)
    design = np.column_stack([np.ones_like(ref), ref])
    coef, *_ = np.linalg.lstsq(design, arr.T, rcond=None)   # (2, n): intercepto, inclinação
    out = (arr - coef[0][:, None]) / coef[1][:, None]
    return (wrap(out), ref) if return_reference else wrap(out)


def detrend(X, degree: int = 1):
    """Remove tendência polinomial (linear por padrão) de cada espectro.

    ``degree=1`` reproduz ``detrend_transform`` do script R (resíduos de lm(x ~ índice)).
    Para o detrend clássico de Barnes et al. (1989), aplique ``snv`` antes e use ``degree=2``.
    """
    arr, wrap = _unwrap(X)
    idx = np.linspace(-1, 1, arr.shape[1])
    vander = np.vander(idx, degree + 1)
    coef, *_ = np.linalg.lstsq(vander, arr.T, rcond=None)
    return wrap(arr - (vander @ coef).T)


def _upper_hull(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Índices do envoltório convexo superior (algoritmo monotone chain)."""
    hull: list[int] = []
    for i in range(len(x)):
        while len(hull) >= 2:
            i0, i1 = hull[-2], hull[-1]
            cross = (x[i1] - x[i0]) * (y[i] - y[i0]) - (y[i1] - y[i0]) * (x[i] - x[i0])
            if cross >= 0:          # i1 está abaixo da reta i0-i -> sai do envoltório
                hull.pop()
            else:
                break
        hull.append(i)
    return np.array(hull)


def continuum_removal(X, axis=None, mode: str = "reflectance"):
    """Remoção do contínuo pelo envoltório convexo.

    ``mode="reflectance"``: envoltório superior, espectro / contínuo (valores 0-1,
    1 = sem absorção). ``mode="absorbance"``: envoltório inferior, espectro - contínuo.
    """
    arr, wrap = _unwrap(X)
    if axis is None:
        axis = spectral_axis(X) if isinstance(X, pd.DataFrame) else np.arange(arr.shape[1], dtype=float)
    axis = np.asarray(axis, dtype=float)
    order = np.argsort(axis)
    x = axis[order]
    out = np.empty_like(arr)
    for i, row in enumerate(arr):
        y = row[order]
        if mode == "reflectance":
            h = _upper_hull(x, y)
            cont = np.interp(x, x[h], y[h])
            res = y / cont
        elif mode == "absorbance":
            h = _upper_hull(x, -y)
            cont = np.interp(x, x[h], y[h])
            res = y - cont
        else:
            raise ValueError("mode deve ser 'reflectance' ou 'absorbance'")
        out[i, order] = res
    return wrap(out)


def band_depth(X, center: float, window: tuple[float, float]) -> pd.Series | np.ndarray:
    """Profundidade da feição (1 - valor do contínuo removido) em ``center``,
    calculando o contínuo apenas dentro de ``window`` (ex.: caulinita 2200 nm)."""
    sub = trim(X, *window)
    cr = continuum_removal(sub)
    col = np.argmin(np.abs(spectral_axis(sub) - center))
    depth = 1 - cr.iloc[:, col]
    return depth.rename(f"profundidade_{center:g}")


# ---------------------------------------------------------------------------
# Conversões, recortes e reamostragem
# ---------------------------------------------------------------------------

def reflectance_to_absorbance(X):
    """A = log10(1/R)."""
    arr, wrap = _unwrap(X)
    return wrap(np.log10(1.0 / np.clip(arr, 1e-6, None)))


def absorbance_to_reflectance(X):
    arr, wrap = _unwrap(X)
    return wrap(10.0 ** (-arr))


def wavenumber_to_nm(wavenumber):
    """λ (nm) = 10^7 / ν (cm-1)."""
    return 1e7 / np.asarray(wavenumber, dtype=float)


def nm_to_wavenumber(nm):
    return 1e7 / np.asarray(nm, dtype=float)


def trim(X: pd.DataFrame, low: float, high: float) -> pd.DataFrame:
    """Mantém apenas as bandas entre ``low`` e ``high`` (independe da ordem do eixo)."""
    ax = spectral_axis(X)
    lo, hi = min(low, high), max(low, high)
    return X.loc[:, (ax >= lo) & (ax <= hi)]


def remove_bands(X: pd.DataFrame, ranges) -> pd.DataFrame:
    """Remove intervalos de bandas, p.ex. bordas ruidosas ou bandas de água."""
    ax = spectral_axis(X)
    keep = np.ones(len(ax), dtype=bool)
    for lo, hi in ranges:
        keep &= ~((ax >= min(lo, hi)) & (ax <= max(lo, hi)))
    return X.loc[:, keep]


def resample(X: pd.DataFrame, new_axis) -> pd.DataFrame:
    """Interpola linearmente cada espectro para ``new_axis``."""
    ax = spectral_axis(X)
    new_axis = np.asarray(new_axis, dtype=float)
    order = np.argsort(ax)
    arr = X.to_numpy(dtype=float)[:, order]
    out = np.vstack([np.interp(new_axis, ax[order], row) for row in arr])
    return pd.DataFrame(out, index=X.index, columns=new_axis)


def binning(X: pd.DataFrame, bin_size: int = 10) -> pd.DataFrame:
    """Média de blocos de ``bin_size`` bandas consecutivas (reduz dimensão e ruído)."""
    n_bins = X.shape[1] // bin_size
    arr = X.to_numpy(dtype=float)[:, : n_bins * bin_size].reshape(len(X), n_bins, bin_size).mean(axis=2)
    ax = spectral_axis(X)[: n_bins * bin_size].reshape(n_bins, bin_size).mean(axis=1)
    return pd.DataFrame(arr, index=X.index, columns=ax)


def noise_level(X, window: int = 11, polyorder: int = 2):
    """Ruído estimado por banda: desvio-padrão do resíduo (bruto - Savitzky-Golay)."""
    arr, _ = _unwrap(X)
    resid = arr - savgol_filter(arr, window, polyorder, axis=1)
    std = resid.std(axis=0)
    if isinstance(X, pd.DataFrame):
        return pd.Series(std, index=X.columns, name="ruido")
    return std


# ---------------------------------------------------------------------------
# Transformadores scikit-learn (para Pipelines de modelagem)
# ---------------------------------------------------------------------------

class _Stateless(TransformerMixin, BaseEstimator):
    """Base para transformações por espectro (nada a aprender no ``fit``)."""

    def fit(self, X, y=None):
        self.n_features_in_ = np.asarray(X).shape[1]
        return self


class SNV(_Stateless):
    def transform(self, X):
        return np.asarray(snv(np.asarray(X, dtype=float)))


class MSC(TransformerMixin, BaseEstimator):
    """MSC cuja referência (espectro médio) é aprendida somente no ``fit``."""

    def fit(self, X, y=None):
        self.reference_ = np.asarray(X, dtype=float).mean(axis=0)
        self.n_features_in_ = len(self.reference_)
        return self

    def transform(self, X):
        return msc(np.asarray(X, dtype=float), reference=self.reference_)


class Detrend(_Stateless):
    def __init__(self, degree: int = 1):
        self.degree = degree

    def transform(self, X):
        return detrend(np.asarray(X, dtype=float), self.degree)


class SavitzkyGolay(_Stateless):
    def __init__(self, window: int = 11, polyorder: int = 2, deriv: int = 0):
        self.window = window
        self.polyorder = polyorder
        self.deriv = deriv

    def transform(self, X):
        return savgol(np.asarray(X, dtype=float), self.window, self.polyorder, self.deriv)


class ContinuumRemoval(_Stateless):
    def __init__(self, mode: str = "reflectance"):
        self.mode = mode

    def transform(self, X):
        return continuum_removal(np.asarray(X, dtype=float), mode=self.mode)


PREPROCESSORS = {
    "raw": lambda: [],
    "snv": lambda: [SNV()],
    "msc": lambda: [MSC()],
    "detrend": lambda: [Detrend()],
    "sg": lambda: [SavitzkyGolay(11, 2, 0)],
    "sg1d": lambda: [SavitzkyGolay(11, 2, 1)],
    "sg2d": lambda: [SavitzkyGolay(15, 2, 2)],
    "snv_sg1d": lambda: [SNV(), SavitzkyGolay(11, 2, 1)],
    "cr": lambda: [ContinuumRemoval()],
}


def make_preprocessor(name: str):
    """Pipeline de pré-processamento por nome (ver ``PREPROCESSORS``)."""
    if name not in PREPROCESSORS:
        raise KeyError(f"Pré-processamento '{name}' desconhecido. Opções: {list(PREPROCESSORS)}")
    steps = PREPROCESSORS[name]()
    if not steps:
        return "passthrough"
    return steps[0] if len(steps) == 1 else make_pipeline(*steps)
