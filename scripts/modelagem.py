"""Módulo 5 - Modelagem preditiva (ML) e interpretação com SHAP.

Tradução para Python do pipeline ``r_original/mhpp_v4_updated.R`` (caret):

=============================  ==========================================
R (caret / prospectr)          Python (este módulo)
=============================  ==========================================
calculate_metrics()            :func:`metrics`
createDataPartition()          :func:`stratified_split`
train(method="pls")            ``make_model("pls")``  (PLSRegression)
train(method="ranger")         ``make_model("rf")``   (RandomForestRegressor)
train(method="xgbTree")        ``make_model("xgb")``  (XGBRegressor)
trainControl(method="cv", 5)   ``GridSearchCV(cv=KFold(5))``
laço preproc × algoritmo       :func:`compare_models`
fastshap::explain()            :func:`shap_values` (TreeExplainer / exato p/ PLS)
varImp()                       :func:`vip` (PLS) e :func:`spectral_importance`
saveRDS()                      :func:`save_model` (joblib)
=============================  ==========================================

Diferença intencional: o R escolhe o "melhor" modelo pelo maior R² **no teste**,
o que usa o teste na seleção e superestima o desempenho. Aqui o padrão é o menor
RMSE da **validação cruzada** (``select_by="CV_RMSE"``); use
``select_by="R2_test"`` para reproduzir exatamente o comportamento do R.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, KFold, cross_val_predict
from sklearn.pipeline import Pipeline

from . import config
from .processamento import make_preprocessor

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------


def metrics(obs, pred) -> dict:
    """Métricas de desempenho (mesmas definições do script R).

    R2   = r² de Pearson entre observado e predito (como no R: cor(obs, pred)^2)
    RMSE = raiz do erro quadrático médio
    MAE  = erro absoluto médio
    Bias = média(pred - obs)
    RPD  = DP(obs) / RMSE
    RPIQ = IIQ(obs) / RMSE  (Bellon-Maurel et al., 2010 - preferível ao RPD p/ dados assimétricos)
    CCC  = coeficiente de concordância de Lin
    """
    obs, pred = np.asarray(obs, float).ravel(), np.asarray(pred, float).ravel()
    ok = np.isfinite(obs) & np.isfinite(pred)
    obs, pred = obs[ok], pred[ok]
    if len(obs) < 2:
        return {}
    rmse = float(np.sqrt(np.mean((obs - pred) ** 2)))
    cov = np.cov(obs, pred)
    q75, q25 = np.percentile(obs, [75, 25])
    return {
        "R2": float(np.corrcoef(obs, pred)[0, 1] ** 2),
        "RMSE": rmse,
        "MAE": float(np.mean(np.abs(obs - pred))),
        "Bias": float(np.mean(pred - obs)),
        "RPD": float(np.std(obs, ddof=1) / rmse) if rmse > 0 else np.nan,
        "RPIQ": float((q75 - q25) / rmse) if rmse > 0 else np.nan,
        "CCC": float(2 * cov[0, 1] / (cov[0, 0] + cov[1, 1] + (obs.mean() - pred.mean()) ** 2)),
        "n": int(len(obs)),
    }


def classify_performance(r2: float) -> str:
    """Mesma classificação qualitativa usada no resumo do script R."""
    if r2 > 0.8:
        return "excelente"
    if r2 > 0.6:
        return "bom"
    if r2 > 0.4:
        return "moderado"
    return "fraco"


# ---------------------------------------------------------------------------
# Divisão calibração / validação
# ---------------------------------------------------------------------------


def stratified_split(y, test_size: float = 0.2, n_groups: int = 5, seed: int = config.SEED):
    """Equivalente ao ``caret::createDataPartition`` para y contínuo: sorteia
    ``test_size`` dentro de cada faixa de quantis de y, preservando a distribuição.
    Retorna (posições_treino, posições_teste)."""
    y = np.asarray(y, float)
    rng = np.random.default_rng(seed)
    groups = pd.qcut(y, q=min(n_groups, len(y)), labels=False, duplicates="drop")
    train, test = [], []
    for g in np.unique(groups):
        idx = np.flatnonzero(groups == g)
        rng.shuffle(idx)
        n_test = int(round(len(idx) * test_size))
        test.extend(idx[:n_test])
        train.extend(idx[n_test:])
    return np.sort(train), np.sort(test)


def kennard_stone(X, n_select: int) -> np.ndarray:
    """Algoritmo Kennard-Stone: escolhe ``n_select`` amostras que cobrem
    uniformemente o espaço de X (comum para definir o conjunto de calibração).
    Use sobre escores de PCA quando houver muitas amostras (custo O(n²))."""
    arr = X.to_numpy(float) if isinstance(X, pd.DataFrame) else np.asarray(X, float)
    n = len(arr)
    sq = (arr ** 2).sum(axis=1)
    dist = np.sqrt(np.maximum(sq[:, None] + sq[None] - 2 * arr @ arr.T, 0))
    i, j = np.unravel_index(dist.argmax(), dist.shape)
    selected = [i, j]
    min_dist = np.minimum(dist[i], dist[j])
    min_dist[selected] = -1
    while len(selected) < min(n_select, n):
        k = int(min_dist.argmax())
        selected.append(k)
        min_dist = np.minimum(min_dist, dist[k])
        min_dist[selected] = -1
    return np.array(selected)


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


def make_model(algo: str, seed: int = config.SEED, n_jobs: int = -1, max_pls: int = 25):
    """Estimador e grade de hiperparâmetros para cada algoritmo.

    pls -> nº de variáveis latentes 1..max_pls
    rf  -> fração de bandas por divisão (equivale ao mtry do ranger)
    xgb -> grade enxuta inspirada no tune_grid do script R
    """
    if algo == "pls":
        return PLSRegression(scale=False), {"n_components": list(range(1, max_pls + 1))}
    if algo == "rf":
        return (RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=n_jobs),
                {"max_features": ["sqrt", 0.1, 0.33]})
    if algo == "xgb":
        from xgboost import XGBRegressor
        return (XGBRegressor(subsample=0.8, colsample_bytree=0.8, min_child_weight=1, random_state=seed,
                             n_jobs=n_jobs, tree_method="hist"),
                {"n_estimators": [300], "max_depth": [3, 5], "learning_rate": [0.05, 0.1]})
    raise KeyError(f"Algoritmo '{algo}' desconhecido. Opções: pls, rf, xgb")


def build_pipeline(preproc: str, algo: str, seed: int = config.SEED, **kw):
    """Pipeline pré-processamento -> modelo, com grade já prefixada para GridSearchCV."""
    est, grid = make_model(algo, seed=seed, **kw)
    pipe = Pipeline([("prep", make_preprocessor(preproc)), ("model", est)])
    return pipe, {f"model__{k}": v for k, v in grid.items()}


def should_log(y, skew_limit: float = 1.0) -> bool:
    """Sugere modelar em escala log quando y é não negativo e muito assimétrico
    (C, P, K, Ca, Mg, CTC...). Assimetria > ``skew_limit``."""
    y = pd.Series(np.asarray(y, float)).dropna()
    return bool(len(y) > 2 and y.min() >= 0 and y.skew() > skew_limit)


def unwrap(model):
    """Pipeline interno (prep -> model) de um modelo ajustado, com ou sem alvo em log."""
    return model.regressor_ if isinstance(model, TransformedTargetRegressor) else model


def fit_model(X, y, preproc: str = "snv", algo: str = "pls", cv: int = 5, seed: int = config.SEED,
              n_jobs: int = -1, log_target: bool = False, **kw) -> GridSearchCV:
    """Ajusta um único pipeline com busca em grade e validação cruzada k-fold.

    ``log_target=True`` ajusta o modelo em log(1 + y) e devolve as predições na
    unidade original (expm1) - métricas e RMSE da VC ficam na unidade do atributo.

    Paralelismo: o Random Forest usa todos os núcleos internamente; para PLS e
    XGBoost é mais eficiente paralelizar as combinações da grade (processos).
    """
    inner = n_jobs if algo == "rf" else 1
    pipe, grid = build_pipeline(preproc, algo, seed=seed, n_jobs=inner, **kw)
    if log_target:
        pipe = TransformedTargetRegressor(regressor=pipe, func=np.log1p, inverse_func=np.expm1,
                                          check_inverse=False)
        grid = {f"regressor__{k}": v for k, v in grid.items()}
    search = GridSearchCV(pipe, grid, cv=KFold(cv, shuffle=True, random_state=seed),
                          scoring="neg_root_mean_squared_error", n_jobs=1 if algo == "rf" else n_jobs,
                          refit=True)
    search.fit(np.asarray(X, float), np.asarray(y, float))
    return search


@dataclass
class ComparisonResult:
    table: pd.DataFrame
    models: dict
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    best_key: tuple = field(default=None)

    @property
    def best_model(self):
        return self.models[self.best_key]

    def predictions(self, key=None) -> pd.DataFrame:
        model = self.models[key or self.best_key]
        return pd.DataFrame({"observado": self.y_test,
                             "predito": np.ravel(model.predict(self.X_test.to_numpy(float)))},
                            index=self.y_test.index)


def compare_models(X: pd.DataFrame, y: pd.Series, preprocs=("raw", "snv", "msc", "detrend"),
                   algos=("pls", "rf", "xgb"), test_size: float = 0.2, cv: int = 5,
                   seed: int = config.SEED, select_by: str = "CV_RMSE", verbose: bool = True,
                   log_target: bool = False, **kw) -> ComparisonResult:
    """Laço pré-processamento × algoritmo do script R (seção 4).

    Mesma partição treino/teste para todas as combinações; cada combinação é
    ajustada com GridSearchCV (k-fold) no treino e avaliada no teste.
    ``log_target`` - ver :func:`fit_model` (use :func:`should_log` para decidir).
    """
    y = pd.Series(y, index=X.index).astype(float)
    ok = y.notna().to_numpy() & np.isfinite(X.to_numpy(float)).all(axis=1)
    X, y = X[ok], y[ok]
    tr, te = stratified_split(y.to_numpy(), test_size, seed=seed)
    X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]

    rows, models = [], {}
    for preproc in preprocs:
        for algo in algos:
            t0 = time.time()
            try:
                search = fit_model(X_train, y_train, preproc, algo, cv=cv, seed=seed,
                                   log_target=log_target, **kw)
            except Exception as exc:          # mesmo comportamento tolerante do tryCatch do R
                if verbose:
                    print(f"  {preproc:>8} | {algo:<4} ERRO: {exc}")
                continue
            m_tr = metrics(y_train, search.predict(X_train.to_numpy(float)))
            m_te = metrics(y_test, search.predict(X_test.to_numpy(float)))
            best_cv = search.cv_results_["mean_test_score"][search.best_index_]
            rows.append({
                "Preprocessing": preproc, "Algorithm": algo,
                "R2_train": m_tr["R2"], "RMSE_train": m_tr["RMSE"],
                "R2_test": m_te["R2"], "RMSE_test": m_te["RMSE"], "RPD": m_te["RPD"],
                "RPIQ": m_te["RPIQ"], "CCC": m_te["CCC"], "Bias": m_te["Bias"],
                "CV_RMSE": -best_cv, "best_params": search.best_params_,
                "tempo_s": round(time.time() - t0, 1),
            })
            models[(preproc, algo)] = search.best_estimator_
            if verbose:
                print(f"  {preproc:>8} | {algo:<4} CV RMSE = {-best_cv:.3f} | R² teste = {m_te['R2']:.3f} "
                      f"({time.time() - t0:.0f} s)")
    table = pd.DataFrame(rows)
    if table.empty:
        raise RuntimeError("Nenhum modelo foi ajustado (verifique a variação de y e NaN nos espectros).")
    ascending = select_by in ("CV_RMSE", "RMSE_test")
    table = table.sort_values(select_by, ascending=ascending).reset_index(drop=True)
    best = table.iloc[0]
    return ComparisonResult(table=table, models=models, X_train=X_train, X_test=X_test,
                            y_train=y_train, y_test=y_test,
                            best_key=(best["Preprocessing"], best["Algorithm"]))


def pls_cv_curve(X, y, preproc: str = "snv", max_components: int = 25, cv: int = 5,
                 seed: int = config.SEED) -> pd.DataFrame:
    """RMSE da validação cruzada vs nº de variáveis latentes do PLS (escolha do nº de VLs)."""
    rows = []
    for k in range(1, max_components + 1):
        pipe = Pipeline([("prep", make_preprocessor(preproc)), ("model", PLSRegression(k, scale=False))])
        pred = cross_val_predict(pipe, np.asarray(X, float), np.asarray(y, float),
                                 cv=KFold(cv, shuffle=True, random_state=seed))
        rows.append({"n_vl": k, **metrics(y, pred)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Interpretação: VIP e SHAP
# ---------------------------------------------------------------------------


def vip(pls: PLSRegression) -> np.ndarray:
    """Variable Importance in Projection (Wold) para um PLS ajustado. VIP > 1 = banda relevante."""
    t, w, q = pls.x_scores_, pls.x_weights_, pls.y_loadings_
    p = w.shape[0]
    ss = (q ** 2).sum(axis=0) * (t ** 2).sum(axis=0)
    wn = (w / np.linalg.norm(w, axis=0)) ** 2
    return np.sqrt(p * (wn @ ss) / ss.sum())


def _split_pipeline(model):
    model = unwrap(model)
    prep = model.named_steps["prep"]
    est = model.named_steps["model"]
    transform = (lambda A: A) if prep == "passthrough" else prep.transform
    return transform, est


def shap_values(model: Pipeline, X_explain: pd.DataFrame, X_background: pd.DataFrame | None = None,
                max_background: int = 200, seed: int = config.SEED) -> pd.DataFrame:
    """Valores SHAP no espaço **pré-processado** (uma coluna por banda).

    * Árvores (RF, XGBoost): ``shap.TreeExplainer`` (exato e rápido);
    * PLS (modelo linear): SHAP exato = coef_j · (x_j - média_fundo_j);
    * outros: ``shap.Explainer`` genérico com amostra de fundo.

    A soma dos SHAP de uma amostra + valor-base = predição do modelo.
    Em modelos com alvo em log (``log_target=True``) os SHAP ficam na escala log(1 + y).
    """
    import shap

    transform, est = _split_pipeline(model)
    Xe = transform(X_explain.to_numpy(float))
    bg_df = X_background if X_background is not None else X_explain
    if len(bg_df) > max_background:
        bg_df = bg_df.sample(n=max_background, random_state=seed)
    Xb = transform(bg_df.to_numpy(float))

    if isinstance(est, PLSRegression):
        coef = np.ravel(est.coef_)
        values = (Xe - Xb.mean(axis=0)) * coef
        base = float(np.ravel(est.predict(Xb)).mean())
    elif isinstance(est, RandomForestRegressor) or type(est).__name__ == "XGBRegressor":
        explainer = shap.TreeExplainer(est)
        values = explainer.shap_values(Xe, check_additivity=False)
        base = float(np.ravel(explainer.expected_value)[0])
    else:
        explainer = shap.Explainer(est.predict, Xb)
        exp = explainer(Xe)
        values, base = exp.values, float(np.mean(exp.base_values))
    out = pd.DataFrame(values, index=X_explain.index, columns=X_explain.columns)
    out.attrs["base_value"] = base
    return out


def spectral_importance(shap_df: pd.DataFrame) -> pd.Series:
    """Média de |SHAP| por banda (importância global ao longo do espectro)."""
    return shap_df.abs().mean().rename("media_abs_shap")


def top_features(importance: pd.Series, n: int = 20) -> pd.DataFrame:
    """As ``n`` bandas mais importantes (formato da tabela 'shap_importance' do R)."""
    s = importance.sort_values(ascending=False).head(n)
    bands = pd.to_numeric(s.index, errors="coerce")       # nomes não numéricos (ex.: fusão "v1766") ficam como texto
    bands = s.index if bands.isna().any() else bands
    return pd.DataFrame({"banda": bands, importance.name or "importancia": s.to_numpy()})


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------


def save_model(model, name: str, folder: str | Path | None = None) -> Path:
    folder = Path(folder) if folder else config.OUTPUT_DIR / "modelos"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.joblib"
    joblib.dump(model, path)
    return path


def load_model(path: str | Path):
    return joblib.load(path)
