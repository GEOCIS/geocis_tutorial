"""Módulo 1 - Visualização de dados espectrais.

Todas as funções aceitam ``ax=`` (eixo matplotlib existente) e devolvem o eixo,
para que possam ser combinadas em figuras de vários painéis. O eixo espectral é
detectado pelas colunas: VIS-NIR-SWIR em nm (crescente) e MIR em cm-1
(decrescente, desenhado da esquerda para a direita como nos espectrômetros).

Convenção de cores (fixa em todo o projeto):
* categorias -> ``CATEGORICAL`` sempre na mesma ordem;
* magnitude (ex.: teor de argila) -> ``SEQUENTIAL`` (um só matiz, claro -> escuro);
* correlação / valores com sinal -> ``DIVERGING`` (azul - cinza - vermelho).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize

from . import config

CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQUENTIAL = LinearSegmentedColormap.from_list("geocis_seq", ["#cfe0f6", "#2a78d6", "#0b2f5e"])
DIVERGING = LinearSegmentedColormap.from_list("geocis_div", ["#1d5fae", "#d9d8d4", "#c4302f"])
NEUTRAL = "#52514e"
REGION_COLORS = {"VIS": "#f3efe2", "NIR": "#e9eef5", "SWIR": "#eaf3ee"}


def set_style() -> None:
    """Estilo padrão GeoCiS para figuras (fundo branco, grade discreta)."""
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 300, "savefig.bbox": "tight",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6,
        "axes.edgecolor": "#8a8984", "axes.labelcolor": "#0b0b0b",
        "xtick.color": NEUTRAL, "ytick.color": NEUTRAL,
        "axes.titleweight": "bold", "axes.titlesize": 12, "font.size": 10,
        "legend.frameon": False, "lines.linewidth": 1.2,
        "axes.prop_cycle": mpl.cycler(color=CATEGORICAL),
    })


def savefig(fig, name: str, folder: str | Path | None = None) -> Path:
    """Salva a figura em ``outputs/figuras`` (PNG, 300 dpi)."""
    folder = Path(folder) if folder else config.OUTPUT_DIR / "figuras"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (name if name.endswith(".png") else f"{name}.png")
    fig.savefig(path)
    return path


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------

def is_wavenumber(X_or_axis) -> bool:
    """True se o eixo estiver em número de onda (decrescente, típico do MIR)."""
    ax = np.asarray(X_or_axis.columns if isinstance(X_or_axis, pd.DataFrame) else X_or_axis, float)
    return ax[0] > ax[-1]


def axis_label(X_or_axis) -> str:
    return "Número de onda (cm$^{-1}$)" if is_wavenumber(X_or_axis) else "Comprimento de onda (nm)"


def _prepare_axis(ax, X_or_axis, ylabel: str | None):
    ax.set_xlabel(axis_label(X_or_axis))
    if ylabel:
        ax.set_ylabel(ylabel)
    if is_wavenumber(X_or_axis) and not ax.xaxis_inverted():
        ax.invert_xaxis()


def _new_ax(ax, figsize=(9, 4)):
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    return ax


def shade_regions(ax, regions: dict | None = None, label: bool = True):
    """Sombreia as regiões VIS/NIR/SWIR no fundo do gráfico."""
    regions = config.VNIR_REGIONS if regions is None else regions
    for name, (lo, hi) in regions.items():
        ax.axvspan(lo, hi, color=REGION_COLORS.get(name, "#f1f0ec"), zorder=0, lw=0)
        if label:
            ax.text((lo + hi) / 2, 1.0, name, transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=8, color=NEUTRAL)
    return ax


def mark_features(ax, features: dict | None = None, mir: bool = False):
    """Marca feições diagnósticas (faixas verticais tracejadas com rótulo)."""
    features = (config.MIR_FEATURES if mir else config.VNIR_FEATURES) if features is None else features
    for i, (name, (lo, hi)) in enumerate(features.items()):
        center = (lo + hi) / 2
        ax.axvline(center, color="#8a8984", ls="--", lw=0.7, zorder=1)
        ax.text(center, 0.98 - 0.07 * (i % 3), name, transform=ax.get_xaxis_transform(),
                rotation=0, ha="center", va="top", fontsize=7, color=NEUTRAL,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
    return ax


# ---------------------------------------------------------------------------
# Espectros
# ---------------------------------------------------------------------------

def plot_spectra(X: pd.DataFrame, color_by=None, n_max: int = 300, ax=None, alpha: float = 0.35,
                 ylabel: str = "Reflectância", title: str | None = None, seed: int = config.SEED,
                 regions: bool = False, features: bool = False, colorbar_label: str | None = None):
    """Desenha espectros individuais.

    ``color_by``: ``None`` (uma cor), Series categórica (uma cor por classe, com
    legenda) ou Series numérica (gradiente sequencial, com barra de cores).
    Para legibilidade, no máximo ``n_max`` espectros são sorteados.
    """
    ax = _new_ax(ax)
    if len(X) > n_max:
        X = X.sample(n=n_max, random_state=seed)
    x = np.asarray(X.columns, dtype=float)
    if regions and not is_wavenumber(X):
        shade_regions(ax)

    if color_by is None:
        ax.plot(x, X.to_numpy().T, color=CATEGORICAL[0], alpha=alpha, lw=0.7)
    else:
        values = pd.Series(color_by).reindex(X.index)
        if not pd.api.types.is_numeric_dtype(values) or isinstance(values.dtype, pd.CategoricalDtype):
            cats = values.astype("category").cat.categories
            for i, cat in enumerate(cats):
                sel = (values == cat).to_numpy()
                if sel.any():
                    ax.plot(x, X.to_numpy()[sel].T, color=CATEGORICAL[i % 8], alpha=alpha, lw=0.7)
                    ax.plot([], [], color=CATEGORICAL[i % 8], lw=2, label=f"{cat} (n={sel.sum()})")
            ax.legend(loc="best", fontsize=8)
        else:
            norm = Normalize(np.nanpercentile(values, 2), np.nanpercentile(values, 98))
            order = np.argsort(values.to_numpy())
            for i in order:
                if np.isfinite(values.iloc[i]):
                    ax.plot(x, X.iloc[i].to_numpy(), color=SEQUENTIAL(norm(values.iloc[i])), alpha=0.6, lw=0.7)
            sm = mpl.cm.ScalarMappable(norm=norm, cmap=SEQUENTIAL)
            plt.colorbar(sm, ax=ax, pad=0.01, label=colorbar_label or values.name)

    if features:
        mark_features(ax, mir=is_wavenumber(X))
    _prepare_axis(ax, X, ylabel)
    ax.set_xlim(x.min(), x.max()) if not is_wavenumber(X) else ax.set_xlim(x.max(), x.min())
    if title:
        ax.set_title(title, loc="left")
    return ax


def plot_mean_std(X: pd.DataFrame, groups=None, ax=None, ylabel: str = "Reflectância",
                  title: str | None = None, band: str = "std", regions: bool = False):
    """Espectro médio ± desvio-padrão (``band='std'``) ou percentis 10-90 (``band='p10_90'``),
    opcionalmente por grupo (Series categórica)."""
    ax = _new_ax(ax)
    x = np.asarray(X.columns, dtype=float)
    if regions and not is_wavenumber(X):
        shade_regions(ax)
    if groups is None:
        groups = pd.Series("Todas", index=X.index)
    groups = pd.Series(groups).reindex(X.index).astype("category")
    for i, cat in enumerate(groups.cat.categories):
        sub = X[(groups == cat).to_numpy()]
        if sub.empty:
            continue
        mean = sub.mean().to_numpy()
        if band == "std":
            lo, hi = mean - sub.std().to_numpy(), mean + sub.std().to_numpy()
        else:
            lo, hi = sub.quantile(0.1).to_numpy(), sub.quantile(0.9).to_numpy()
        color = CATEGORICAL[i % 8]
        ax.fill_between(x, lo, hi, color=color, alpha=0.15, lw=0)
        ax.plot(x, mean, color=color, lw=2, label=f"{cat} (n={len(sub)})")
    if len(groups.cat.categories) > 1:
        ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1))
    _prepare_axis(ax, X, ylabel)
    if title:
        ax.set_title(title, loc="left")
    return ax


def plot_vnir_mir(ds, color_by=None, n_max: int = 200, figsize=(13, 4), suptitle: str | None = None,
                  mir_ylabel: str = "Reflectância (MIR)"):
    """Painel lado a lado: VIS-NIR-SWIR (nm) | MIR (cm-1) das mesmas amostras."""
    fig, axes = plt.subplots(1, 2, figsize=figsize, gridspec_kw={"width_ratios": [1.1, 1]})
    idx = ds.meta.sample(n=min(n_max, len(ds)), random_state=config.SEED).index
    cb = None if color_by is None else pd.Series(color_by, index=ds.meta.index).loc[idx]
    plot_spectra(ds.vnir.loc[idx], color_by=cb, ax=axes[0], title="VIS-NIR-SWIR", regions=True)
    plot_spectra(ds.mir.loc[idx], color_by=cb, ax=axes[1], title="MIR", ylabel=mir_ylabel)
    if axes[1].get_legend():
        axes[1].get_legend().remove()
    if suptitle:
        fig.suptitle(suptitle, x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    return fig, axes


def plot_heatmap(X: pd.DataFrame, ax=None, sort_by=None, title: str | None = None,
                 cbar_label: str = "Reflectância", max_rows: int = 1000):
    """Matriz amostras × bandas como imagem (bom para ver o conjunto inteiro e outliers)."""
    ax = _new_ax(ax, figsize=(9, 5))
    if sort_by is not None:
        X = X.loc[pd.Series(sort_by).reindex(X.index).sort_values().index]
    if len(X) > max_rows:
        X = X.iloc[np.linspace(0, len(X) - 1, max_rows).astype(int)]
    x = np.asarray(X.columns, dtype=float)
    im = ax.imshow(X.to_numpy(), aspect="auto", cmap=SEQUENTIAL, interpolation="nearest",
                   extent=[x[0], x[-1], len(X), 0])
    plt.colorbar(im, ax=ax, pad=0.01, label=cbar_label)
    ax.set_xlabel(axis_label(X))
    ax.set_ylabel("Amostras" + (f" (ordenadas por {getattr(sort_by, 'name', '')})" if sort_by is not None else ""))
    ax.grid(False)
    if title:
        ax.set_title(title, loc="left")
    return ax


def plot_processing_steps(steps: dict, sample_ids=None, n: int = 5, figsize=None):
    """Compara etapas de processamento: ``steps = {"Bruto": X, "SNV": snv(X), ...}``."""
    names = list(steps)
    first = steps[names[0]]
    if sample_ids is None:
        sample_ids = first.sample(n=min(n, len(first)), random_state=config.SEED).index
    ncols = min(3, len(names))
    nrows = int(np.ceil(len(names) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize or (4.6 * ncols, 3.2 * nrows), squeeze=False)
    for ax, name in zip(axes.flat, names):
        X = steps[name].loc[sample_ids]
        x = np.asarray(X.columns, dtype=float)
        for i, (_, row) in enumerate(X.iterrows()):
            ax.plot(x, row.to_numpy(), color=CATEGORICAL[i % 8], lw=1)
        _prepare_axis(ax, X, None)
        ax.set_title(name, loc="left")
    for ax in axes.flat[len(names):]:
        ax.set_visible(False)
    fig.tight_layout()
    return fig, axes


# ---------------------------------------------------------------------------
# Análise exploratória
# ---------------------------------------------------------------------------

def plot_scree(explained: pd.Series, ax=None, n: int = 10):
    """Variância explicada (barras) e acumulada (linha) dos componentes principais."""
    ax = _new_ax(ax, figsize=(6, 3.5))
    e = explained.iloc[:n] * 100
    ax.bar(range(1, len(e) + 1), e, color=CATEGORICAL[0], width=0.6)
    ax.plot(range(1, len(e) + 1), e.cumsum(), color=NEUTRAL, marker="o", ms=4, lw=1.2, label="Acumulada")
    for i, v in enumerate(e.cumsum(), start=1):
        if i in (1, 2, 3, len(e)):
            ax.annotate(f"{v:.0f}%", (i, v), textcoords="offset points", xytext=(0, 6),
                        ha="center", fontsize=8, color=NEUTRAL)
    ax.set_xticks(range(1, len(e) + 1), [f"PC{i}" for i in range(1, len(e) + 1)])
    ax.set_ylabel("Variância explicada (%)")
    ax.set_ylim(0, 105)
    ax.legend(loc="center right")
    return ax


def plot_scores(scores: pd.DataFrame, color_by=None, pcs=(1, 2), explained: pd.Series | None = None,
                ax=None, title: str | None = None, s: float = 10):
    """Gráfico de escores (PC_i × PC_j) colorido por classe ou por atributo numérico."""
    ax = _new_ax(ax, figsize=(5.5, 4.5))
    cx, cy = f"PC{pcs[0]}", f"PC{pcs[1]}"
    if color_by is None:
        ax.scatter(scores[cx], scores[cy], s=s, color=CATEGORICAL[0], alpha=0.6, lw=0)
    else:
        values = pd.Series(color_by).reindex(scores.index)
        if not pd.api.types.is_numeric_dtype(values) or isinstance(values.dtype, pd.CategoricalDtype):
            cats = values.astype("category").cat.categories
            for i, cat in enumerate(cats):
                sel = (values == cat).to_numpy()
                ax.scatter(scores.loc[sel, cx], scores.loc[sel, cy], s=s, alpha=0.7, lw=0,
                           color=CATEGORICAL[i % 8], label=f"{cat} (n={sel.sum()})")
            ax.legend(fontsize=8, markerscale=1.5)
        else:
            ok = values.notna().to_numpy()
            ax.scatter(scores.loc[~ok, cx], scores.loc[~ok, cy], s=s * 0.6, color="#d9d8d4", lw=0)
            sc = ax.scatter(scores.loc[ok, cx], scores.loc[ok, cy], c=values[ok], s=s, cmap=SEQUENTIAL,
                            vmin=np.nanpercentile(values, 2), vmax=np.nanpercentile(values, 98), lw=0)
            plt.colorbar(sc, ax=ax, pad=0.01, label=values.name)
    lab = (lambda c, k: f"{c} ({explained.iloc[k - 1] * 100:.1f}%)") if explained is not None else (lambda c, k: c)
    ax.set_xlabel(lab(cx, pcs[0]))
    ax.set_ylabel(lab(cy, pcs[1]))
    ax.axhline(0, color="#b5b4ae", lw=0.6)
    ax.axvline(0, color="#b5b4ae", lw=0.6)
    if title:
        ax.set_title(title, loc="left")
    return ax


def plot_loadings(loadings: pd.DataFrame, pcs=(1, 2, 3), ax=None, ylabel: str = "Loading"):
    """Loadings dos PCs ao longo do eixo espectral (onde cada PC 'olha' no espectro)."""
    ax = _new_ax(ax)
    x = np.asarray(loadings.index, dtype=float)
    for i, k in enumerate(pcs):
        ax.plot(x, loadings[f"PC{k}"], color=CATEGORICAL[i], lw=1.4, label=f"PC{k}")
    ax.axhline(0, color="#b5b4ae", lw=0.6)
    ax.legend(fontsize=8)
    _prepare_axis(ax, x, ylabel)
    return ax


def plot_correlogram(corr: pd.DataFrame, ax=None, title: str | None = None, threshold: float | None = None):
    """Correlação de Pearson banda-a-banda com cada atributo (colunas de ``corr``)."""
    ax = _new_ax(ax)
    x = np.asarray(corr.index, dtype=float)
    for i, col in enumerate(corr.columns):
        ax.plot(x, corr[col], color=CATEGORICAL[i % 8], lw=1.5, label=col)
    ax.axhline(0, color="#8a8984", lw=0.7)
    if threshold:
        for t in (-threshold, threshold):
            ax.axhline(t, color="#8a8984", lw=0.6, ls=":")
    ax.set_ylim(-1, 1)
    ax.legend(fontsize=8, ncol=min(4, len(corr.columns)))
    _prepare_axis(ax, x, "r de Pearson")
    if title:
        ax.set_title(title, loc="left")
    return ax


def plot_corr_matrix(corr: pd.DataFrame, ax=None, annotate: bool = True, title: str | None = None,
                     pvalues: pd.DataFrame | None = None, alpha: float = 0.05):
    """Matriz de correlação (ex.: PCs × atributos) com escala divergente centrada em 0.
    Se ``pvalues`` for dado, células não significativas recebem '·' em vez do valor."""
    ax = _new_ax(ax, figsize=(1 + 0.8 * corr.shape[1], 0.8 + 0.45 * corr.shape[0]))
    im = ax.imshow(corr.to_numpy(dtype=float), cmap=DIVERGING, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(corr.shape[1]), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(corr.shape[0]), corr.index)
    ax.grid(False)
    if annotate:
        for i in range(corr.shape[0]):
            for j in range(corr.shape[1]):
                v = corr.iat[i, j]
                if np.isnan(v):
                    continue
                sig = pvalues is None or pvalues.iat[i, j] < alpha
                ax.text(j, i, f"{v:.2f}" if sig else "·", ha="center", va="center", fontsize=8,
                        color="white" if abs(v) > 0.6 else "#0b0b0b")
    plt.colorbar(im, ax=ax, pad=0.01, label="r de Pearson")
    if title:
        ax.set_title(title, loc="left")
    return ax


# ---------------------------------------------------------------------------
# Agrupamento e modelagem
# ---------------------------------------------------------------------------

def plot_cluster_means(X: pd.DataFrame, labels, ax=None, ylabel: str = "Reflectância", title: str | None = None):
    """Espectro médio de cada cluster (com faixa de percentis 10-90)."""
    labels = pd.Series(labels, index=X.index).astype("category")
    labels = labels.cat.rename_categories([f"Cluster {c}" for c in labels.cat.categories])
    return plot_mean_std(X, groups=labels, ax=ax, ylabel=ylabel, title=title, band="p10_90")


def plot_k_selection(table: pd.DataFrame, axes=None):
    """Curva do cotovelo (inércia) e silhueta em função de k."""
    if axes is None:
        _, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    axes[0].plot(table["k"], table["inercia"], marker="o", color=CATEGORICAL[0])
    axes[0].set(xlabel="k", ylabel="Inércia (SQ intra)", title="Cotovelo")
    axes[1].plot(table["k"], table["silhueta"], marker="o", color=CATEGORICAL[1])
    axes[1].set(xlabel="k", ylabel="Silhueta média", title="Silhueta")
    for ax in axes:
        ax.title.set_ha("left")
        ax.set_title(ax.get_title(), loc="left")
    return axes


def plot_obs_pred(obs, pred, ax=None, metrics: dict | None = None, title: str | None = None,
                  unit: str = "", label: str = "Teste"):
    """Observado × predito com linha 1:1 e métricas no canto."""
    ax = _new_ax(ax, figsize=(4.6, 4.4))
    obs, pred = np.asarray(obs, float), np.asarray(pred, float)
    lim = [min(obs.min(), pred.min()), max(obs.max(), pred.max())]
    pad = 0.04 * (lim[1] - lim[0])
    lim = [lim[0] - pad, lim[1] + pad]
    ax.plot(lim, lim, color=NEUTRAL, lw=1, ls="--", label="1:1")
    ax.scatter(obs, pred, s=12, alpha=0.6, color=CATEGORICAL[0], lw=0, label=label)
    ax.set(xlim=lim, ylim=lim, xlabel=f"Observado {unit}".strip(), ylabel=f"Predito {unit}".strip())
    ax.set_aspect("equal")
    if metrics:
        txt = "\n".join(f"{k} = {metrics[k]:.2f}" for k in ("R2", "RMSE", "RPIQ", "CCC", "Bias") if k in metrics)
        ax.text(0.03, 0.97, txt, transform=ax.transAxes, va="top", fontsize=8,
                bbox=dict(boxstyle="round", fc="white", ec="#d9d8d4"))
    if title:
        ax.set_title(title, loc="left")
    return ax


def plot_spectral_importance(importance: pd.Series, reference_spectrum: pd.Series | None = None,
                             ax=None, title: str | None = None, ylabel: str = "Média |SHAP|",
                             features: bool = True):
    """Importância por banda (ex.: média |SHAP|) ao longo do espectro.

    Com ``reference_spectrum`` (e ``ax=None``), cria dois painéis com o mesmo eixo x:
    espectro médio em cima e importância embaixo, para relacionar com as feições.
    """
    x = np.asarray(importance.index, dtype=float)
    if reference_spectrum is not None and ax is None:
        fig, (ax_ref, ax) = plt.subplots(2, 1, figsize=(9, 5), sharex=True,
                                         gridspec_kw={"height_ratios": [1, 1.4]})
        ax_ref.plot(np.asarray(reference_spectrum.index, float), reference_spectrum.to_numpy(),
                    color=NEUTRAL, lw=1.4)
        ax_ref.set_ylabel("Espectro médio")
        if title:
            ax_ref.set_title(title, loc="left")
            title = None
    ax = _new_ax(ax)
    ax.fill_between(x, 0, importance.to_numpy(), color=CATEGORICAL[1], alpha=0.35, lw=0)
    ax.plot(x, importance.to_numpy(), color=CATEGORICAL[1], lw=1.2)
    if features:
        mark_features(ax, mir=is_wavenumber(x))
    _prepare_axis(ax, x, ylabel)
    if title:
        ax.set_title(title, loc="left")
    return ax
