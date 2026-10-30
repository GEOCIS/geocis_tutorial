"""Módulo 4 - Agrupamento (clustering) e métricas de similaridade espectral.

* :func:`kmeans` e :func:`select_k` - k-means e escolha de k (cotovelo, silhueta,
  Calinski-Harabasz, Davies-Bouldin);
* :func:`isodata` - ISODATA (k-means com divisão e fusão automáticas de clusters);
* métricas de similaridade: :func:`sam`, :func:`sid`, :func:`spectral_correlation`,
  :func:`euclidean` e :func:`pairwise` para matrizes amostras × referências;
* :func:`classify_by_reference` - atribui cada espectro à referência mais similar
  (ex.: espectros-padrão de classes de solo ou bibliotecas espectrais).

Recomendação: agrupe nos **escores de PCA** (ou espectros pré-processados e
reduzidos), não nas ~2000 bandas brutas - distâncias em alta dimensão ficam
dominadas por ruído e albedo.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score

from . import config


def _arr(X):
    return X.to_numpy(float) if isinstance(X, pd.DataFrame) else np.asarray(X, float)


# ---------------------------------------------------------------------------
# k-means
# ---------------------------------------------------------------------------

def kmeans(X, k: int, seed: int = config.SEED, angular: bool = False, n_init: int = 10):
    """k-means. ``angular=True`` normaliza cada espectro pela norma (k-means
    "esférico"), o que agrupa por **forma** e não por albedo - análogo ao SAM."""
    arr = _arr(X)
    if angular:
        arr = arr / np.linalg.norm(arr, axis=1, keepdims=True)
    model = KMeans(n_clusters=k, n_init=n_init, random_state=seed).fit(arr)
    labels = model.labels_
    if isinstance(X, pd.DataFrame):
        labels = pd.Series(labels, index=X.index, name="cluster")
    return labels, model


def select_k(X, k_range=range(2, 11), seed: int = config.SEED, sample_size: int = 3000) -> pd.DataFrame:
    """Tabela de critérios para escolher k.

    * inércia (cotovelo) - menor é melhor, procure a "dobra";
    * silhueta - maior é melhor (-1 a 1);
    * Calinski-Harabasz - maior é melhor;
    * Davies-Bouldin - menor é melhor.
    """
    arr = _arr(X)
    rows = []
    for k in k_range:
        model = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(arr)
        rows.append({
            "k": k, "inercia": model.inertia_,
            "silhueta": silhouette_score(arr, model.labels_, sample_size=min(sample_size, len(arr)),
                                         random_state=seed),
            "calinski_harabasz": calinski_harabasz_score(arr, model.labels_),
            "davies_bouldin": davies_bouldin_score(arr, model.labels_),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# ISODATA
# ---------------------------------------------------------------------------

@dataclass
class IsodataResult:
    labels: np.ndarray
    centers: np.ndarray
    history: list = field(default_factory=list)   # nº de clusters por iteração

    @property
    def n_clusters(self) -> int:
        return len(self.centers)


def isodata(X, k_init: int = 5, k_desired: int | None = None, max_iter: int = 30,
            min_samples: int = 20, max_std: float | None = None, min_dist: float | None = None,
            max_merge: int = 2, seed: int = config.SEED) -> IsodataResult:
    """ISODATA (Iterative Self-Organizing Data Analysis Technique; Ball & Hall, 1965).

    Parâmetros (nomes clássicos entre parênteses):
      k_init       nº inicial de clusters;
      k_desired    nº desejado (K); padrão = k_init;
      min_samples  nº mínimo de amostras por cluster (θN) - menores são eliminados;
      max_std      desvio-padrão máximo numa dimensão antes de dividir (θS);
                   padrão = 1,0 × desvio médio global das dimensões;
      min_dist     distância mínima entre centros antes de fundir (θC);
                   padrão = dispersão interna média dos clusters na iteração;
      max_merge    nº máximo de fusões por iteração (L).

    Com poucos clusters (≤ K/2) ou em iterações ímpares (com < 2K clusters) o
    algoritmo tenta DIVIDIR; nos demais casos tenta FUNDIR. Use de preferência sobre escores de PCA padronizados.
    """
    arr = _arr(X)
    rng = np.random.default_rng(seed)
    k_desired = k_desired or k_init
    centers = arr[rng.choice(len(arr), size=k_init, replace=False)]
    if max_std is None:
        max_std = float(arr.std(axis=0).mean())

    def assign(c):
        dist = np.linalg.norm(arr[:, None, :] - c[None, :, :], axis=2)
        return dist.argmin(axis=1)

    def update(c):
        lab = assign(c)
        return lab, np.vstack([arr[lab == j].mean(axis=0) for j in range(len(c))])

    history = []
    labels = assign(centers)
    for it in range(1, max_iter + 1):
        # 1) elimina clusters pequenos e reatribui suas amostras
        counts = np.bincount(assign(centers), minlength=len(centers))
        keep = counts >= min_samples
        keep[counts.argmax()] = True
        labels, centers = update(centers[keep])
        counts = np.bincount(labels, minlength=len(centers))

        # 2) dispersão interna: distância média das amostras ao centro
        within = np.array([np.linalg.norm(arr[labels == j] - centers[j], axis=1).mean()
                           for j in range(len(centers))])
        overall = float((within * counts).sum() / counts.sum())
        n = len(centers)

        if n <= k_desired / 2 or (it % 2 == 1 and n < 2 * k_desired):
            # 3) DIVISÃO de clusters muito dispersos ao longo da dimensão de maior DP
            new_centers = []
            for j in range(n):
                std = arr[labels == j].std(axis=0)
                dim = std.argmax()
                room = len(new_centers) + (n - j) < 2 * k_desired     # nunca passa de 2K
                if room and std[dim] > max_std and ((within[j] > overall and counts[j] > 2 * (min_samples + 1))
                                                    or n <= k_desired / 2):
                    shift = np.zeros(arr.shape[1])
                    shift[dim] = 0.5 * std[dim]
                    new_centers += [centers[j] + shift, centers[j] - shift]
                else:
                    new_centers.append(centers[j])
            centers = np.vstack(new_centers)
        elif n > 1:
            # 4) FUSÃO dos pares de centros mais próximos que min_dist
            #    (padrão: a dispersão interna média - clusters mais próximos que o
            #    "raio" típico de um cluster não estão realmente separados)
            #    Acima de 2K clusters, funde os pares mais próximos mesmo acima do limite.
            limit = np.inf if n > 2 * k_desired else (overall if min_dist is None else min_dist)
            d = np.linalg.norm(centers[:, None] - centers[None], axis=2)
            iu = np.triu_indices(n, 1)
            used, merged = set(), []
            for dist, a, b in sorted(zip(d[iu], iu[0], iu[1])):
                if dist >= limit or len(merged) >= max_merge:
                    break
                if a in used or b in used:
                    continue
                merged.append((centers[a] * counts[a] + centers[b] * counts[b]) / (counts[a] + counts[b]))
                used |= {a, b}
            if merged:
                centers = np.vstack([centers[j] for j in range(n) if j not in used] + merged)
        history.append(len(centers))
        if len(history) >= 4 and len(set(history[-4:])) == 1 and np.array_equal(assign(centers), labels):
            break

    labels, centers = update(centers)
    return IsodataResult(labels=labels, centers=centers, history=history)


# ---------------------------------------------------------------------------
# Similaridade espectral
# ---------------------------------------------------------------------------

def sam(a, b) -> float:
    """Spectral Angle Mapper: ângulo (radianos) entre dois espectros.
    Insensível a fator multiplicativo (albedo/iluminação); 0 = mesma forma."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    cos = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.arccos(np.clip(cos, -1, 1)))


def sid(a, b, eps: float = 1e-12) -> float:
    """Spectral Information Divergence (Chang, 2000): divergência de Kullback-Leibler
    simétrica entre os espectros tratados como distribuições de probabilidade."""
    a = np.clip(np.asarray(a, float), eps, None)
    b = np.clip(np.asarray(b, float), eps, None)
    p, q = a / a.sum(), b / b.sum()
    return float(np.sum(p * np.log(p / q)) + np.sum(q * np.log(q / p)))


def spectral_correlation(a, b) -> float:
    """Spectral Correlation Mapper: r de Pearson entre espectros (forma, removendo média)."""
    return float(np.corrcoef(np.asarray(a, float), np.asarray(b, float))[0, 1])


def euclidean(a, b) -> float:
    return float(np.linalg.norm(np.asarray(a, float) - np.asarray(b, float)))


METRICS = {"sam": sam, "sid": sid, "scm": spectral_correlation, "euclidean": euclidean}


def pairwise(X, references, metric: str = "sam") -> pd.DataFrame:
    """Matriz de similaridade/distância amostras × referências (vetorizada)."""
    A, B = _arr(X), _arr(references)
    if metric == "sam":
        cos = (A @ B.T) / (np.linalg.norm(A, axis=1)[:, None] * np.linalg.norm(B, axis=1)[None])
        out = np.arccos(np.clip(cos, -1, 1))
    elif metric == "scm":
        Ac = A - A.mean(axis=1, keepdims=True)
        Bc = B - B.mean(axis=1, keepdims=True)
        out = (Ac @ Bc.T) / (np.linalg.norm(Ac, axis=1)[:, None] * np.linalg.norm(Bc, axis=1)[None])
    elif metric == "euclidean":
        out = np.sqrt(((A[:, None, :] - B[None]) ** 2).sum(axis=2))
    elif metric == "sid":
        P = np.clip(A, 1e-12, None)
        P /= P.sum(axis=1, keepdims=True)
        Q = np.clip(B, 1e-12, None)
        Q /= Q.sum(axis=1, keepdims=True)
        out = ((P[:, None] - Q[None]) * (np.log(P)[:, None] - np.log(Q)[None])).sum(axis=2)
    else:
        raise KeyError(f"Métrica '{metric}' desconhecida. Opções: {list(METRICS)}")
    index = X.index if isinstance(X, pd.DataFrame) else None
    columns = references.index if isinstance(references, pd.DataFrame) else None
    return pd.DataFrame(out, index=index, columns=columns)


def classify_by_reference(X, references: pd.DataFrame, metric: str = "sam") -> pd.DataFrame:
    """Atribui cada espectro à referência mais similar.

    Para SCM (correlação) "mais similar" = maior valor; para as demais = menor.
    Retorna DataFrame com a classe atribuída e o valor da métrica.
    """
    m = pairwise(X, references, metric)
    best = m.idxmax(axis=1) if metric == "scm" else m.idxmin(axis=1)
    value = m.max(axis=1) if metric == "scm" else m.min(axis=1)
    return pd.DataFrame({"classe": best, metric: value})


def cluster_profile(labels, attributes: pd.DataFrame) -> pd.DataFrame:
    """Média (e n) dos atributos por cluster - para interpretar o significado de cada grupo."""
    labels = pd.Series(labels, index=attributes.index, name="cluster")
    prof = attributes.groupby(labels).mean().round(1)
    prof.insert(0, "n", labels.value_counts().sort_index())
    return prof
