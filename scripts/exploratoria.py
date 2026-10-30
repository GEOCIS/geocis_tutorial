"""Módulo 3 - Análise exploratória: PCA e correlação de Pearson.

* :func:`run_pca` - escores, loadings e variância explicada;
* :func:`correlate_bands` - r de Pearson banda-a-banda com atributos (correlograma);
* :func:`correlate_with_attributes` - r e p-valor entre quaisquer colunas (ex.: PCs × atributos);
* :func:`mahalanobis_outliers` - amostras atípicas no espaço dos PCs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA


@dataclass
class PCAResult:
    scores: pd.DataFrame        # amostras × PCs
    loadings: pd.DataFrame      # bandas × PCs
    explained: pd.Series        # fração da variância por PC
    model: PCA
    mean: np.ndarray
    scale: np.ndarray | None

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Projeta novas amostras nos mesmos PCs (mesma centragem/escala)."""
        arr = (X.to_numpy(float) - self.mean)
        if self.scale is not None:
            arr = arr / self.scale
        return pd.DataFrame(self.model.transform(arr), index=X.index, columns=self.scores.columns)

    def summary(self) -> pd.DataFrame:
        return pd.DataFrame({"variancia_%": self.explained * 100,
                             "acumulada_%": self.explained.cumsum() * 100}).round(2)


def run_pca(X: pd.DataFrame, n_components: int = 10, scale: bool = False) -> PCAResult:
    """PCA em espectros. ``scale=True`` padroniza cada banda (PCA de correlação);
    o usual em espectroscopia é só centrar (``scale=False``), pois as bandas
    compartilham a mesma unidade.
    """
    arr = X.to_numpy(float)
    mean = arr.mean(axis=0)
    std = arr.std(axis=0, ddof=1) if scale else None
    centered = (arr - mean) / std if scale else arr - mean
    n_components = min(n_components, *centered.shape)
    model = PCA(n_components=n_components, svd_solver="full").fit(centered)
    cols = [f"PC{i}" for i in range(1, n_components + 1)]
    return PCAResult(
        scores=pd.DataFrame(model.transform(centered), index=X.index, columns=cols),
        loadings=pd.DataFrame(model.components_.T, index=X.columns, columns=cols),
        explained=pd.Series(model.explained_variance_ratio_, index=cols, name="variancia"),
        model=model, mean=mean, scale=std,
    )


def n_components_for(explained: pd.Series, threshold: float = 0.99) -> int:
    """Número mínimo de PCs para atingir ``threshold`` da variância acumulada."""
    return int(np.searchsorted(explained.cumsum().to_numpy(), threshold) + 1)


def pearson_with_pvalues(x, y) -> tuple[float, float, int]:
    """r de Pearson e p-valor (bicaudal) ignorando pares com NaN."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3:
        return np.nan, np.nan, int(ok.sum())
    r, p = stats.pearsonr(x[ok], y[ok])
    return float(r), float(p), int(ok.sum())


def correlate_bands(X: pd.DataFrame, attributes: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Correlação de Pearson de cada banda com cada atributo (vetorizada).

    Para cada atributo usa somente as amostras com valor observado.
    Retorna DataFrame bandas × atributos.
    """
    if isinstance(attributes, pd.Series):
        attributes = attributes.to_frame()
    attributes = attributes.reindex(X.index)
    arr = X.to_numpy(float)
    out = {}
    for col in attributes.columns:
        y = attributes[col].to_numpy(float)
        ok = np.isfinite(y)
        if ok.sum() < 3:
            continue
        xs = arr[ok] - arr[ok].mean(axis=0)
        ys = y[ok] - y[ok].mean()
        out[col] = (xs.T @ ys) / (np.sqrt((xs ** 2).sum(axis=0)) * np.sqrt((ys ** 2).sum()))
    return pd.DataFrame(out, index=X.columns)


def correlation_pvalue(r, n):
    """p-valor bicaudal de um r de Pearson com n observações (teste t)."""
    r = np.clip(np.asarray(r, float), -0.999999, 0.999999)
    t = r * np.sqrt((n - 2) / (1 - r ** 2))
    return 2 * stats.t.sf(np.abs(t), df=n - 2)


def correlate_with_attributes(left: pd.DataFrame, right: pd.DataFrame
                              ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """r, p-valor e n para todas as combinações colunas(left) × colunas(right).

    Uso típico: ``r, p, n = correlate_with_attributes(pca.scores.iloc[:, :5], ds.attributes)``.
    """
    right = right.reindex(left.index)
    r = pd.DataFrame(index=left.columns, columns=right.columns, dtype=float)
    p, n = r.copy(), r.copy()
    for a in left.columns:
        for b in right.columns:
            r.loc[a, b], p.loc[a, b], n.loc[a, b] = pearson_with_pvalues(left[a], right[b])
    return r, p, n


def top_bands(corr: pd.DataFrame, attribute: str, n: int = 10, min_distance: float = 20) -> pd.DataFrame:
    """Bandas de maior |r| para um atributo, separadas por pelo menos ``min_distance``
    unidades espectrais (evita listar 10 bandas vizinhas da mesma feição)."""
    s = corr[attribute].dropna()
    order = s.abs().sort_values(ascending=False).index
    chosen: list[float] = []
    for band in order:
        if all(abs(band - c) >= min_distance for c in chosen):
            chosen.append(band)
        if len(chosen) == n:
            break
    return pd.DataFrame({"banda": chosen, "r": s.loc[chosen].to_numpy()})


def mahalanobis_outliers(scores: pd.DataFrame, n_components: int | None = None,
                         alpha: float = 0.01) -> pd.DataFrame:
    """Distância de Mahalanobis no espaço dos PCs e indicação de outlier (qui-quadrado)."""
    S = scores.iloc[:, :n_components] if n_components else scores
    arr = S.to_numpy(float)
    centered = arr - arr.mean(axis=0)
    inv_cov = np.linalg.pinv(np.cov(centered, rowvar=False))
    d2 = np.einsum("ij,jk,ik->i", centered, inv_cov, centered)
    limit = stats.chi2.ppf(1 - alpha, df=S.shape[1])
    return pd.DataFrame({"d2": d2, "outlier": d2 > limit}, index=scores.index)


def describe_attributes(attributes: pd.DataFrame) -> pd.DataFrame:
    """Estatística descritiva com n, CV (%) e assimetria - primeira tabela de qualquer relatório."""
    d = attributes.describe().T
    d["cv_%"] = 100 * d["std"] / d["mean"]
    d["assimetria"] = attributes.skew()
    d = d.rename(columns={"count": "n"})
    return d[d["n"] > 0].round(2)
