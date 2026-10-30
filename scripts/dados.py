"""Módulo 0 - Leitura, organização e preparação dos dados espectrais.

Estrutura central: :class:`SoilSpectra`, que guarda três tabelas alinhadas pelo
mesmo índice (``ID_Unico``):

* ``meta``  - metadados e atributos laboratoriais (argila, C, pH, ...);
* ``vnir``  - espectros VIS-NIR-SWIR, colunas = comprimento de onda (nm, float);
* ``mir``   - espectros MIR, colunas = número de onda (cm-1, float, decrescente).

Fluxo típico::

    from geocis_espectral import dados
    ds = dados.load_dataset()            # base pareada, ou sintética se não houver
    ds.vnir.shape, ds.mir.shape
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import config


@dataclass
class SoilSpectra:
    """Conjunto de amostras com metadados, atributos e espectros alinhados."""

    meta: pd.DataFrame
    vnir: pd.DataFrame | None = None
    mir: pd.DataFrame | None = None
    info: dict = field(default_factory=dict)

    def __post_init__(self):
        for name in ("vnir", "mir"):
            block = getattr(self, name)
            if block is not None and not block.index.equals(self.meta.index):
                raise ValueError(f"Índice de '{name}' não coincide com o de 'meta'.")

    def __len__(self) -> int:
        return len(self.meta)

    def __repr__(self) -> str:
        parts = [f"SoilSpectra(n={len(self)}"]
        if self.vnir is not None:
            parts.append(f"vnir={self.vnir.shape[1]} bandas "
                         f"[{self.vnir.columns.min():.0f}-{self.vnir.columns.max():.0f} nm]")
        if self.mir is not None:
            parts.append(f"mir={self.mir.shape[1]} bandas "
                         f"[{self.mir.columns.max():.0f}-{self.mir.columns.min():.0f} cm-1]")
        return ", ".join(parts) + ")"

    @property
    def attributes(self) -> pd.DataFrame:
        """Somente as colunas de atributos laboratoriais presentes."""
        return self.meta[[c for c in config.ATTRIBUTE_COLS if c in self.meta.columns]]

    def subset(self, rows) -> "SoilSpectra":
        """Seleciona amostras por máscara booleana ou por rótulos do índice (ID_Unico)."""
        rows = np.asarray(rows)
        idx = self.meta.index[rows] if rows.dtype == bool else pd.Index(rows)
        return SoilSpectra(
            meta=self.meta.loc[idx],
            vnir=None if self.vnir is None else self.vnir.loc[idx],
            mir=None if self.mir is None else self.mir.loc[idx],
            info=dict(self.info),
        )

    def sample(self, n: int, seed: int = config.SEED) -> "SoilSpectra":
        """Amostra aleatória de ``n`` amostras (útil para aulas e testes rápidos)."""
        n = min(n, len(self))
        idx = self.meta.sample(n=n, random_state=seed).index
        return self.subset(idx)

    def dropna_attribute(self, attribute: str) -> "SoilSpectra":
        """Remove as amostras sem valor para ``attribute``."""
        return self.subset(self.meta[attribute].notna().to_numpy())

    def combined(self) -> pd.DataFrame:
        """VIS-NIR-SWIR seguido do MIR em uma única matriz (colunas 'vnir_350', 'mir_4000', ...)."""
        blocks = []
        if self.vnir is not None:
            blocks.append(self.vnir.set_axis([f"vnir_{c:g}" for c in self.vnir.columns], axis=1))
        if self.mir is not None:
            blocks.append(self.mir.set_axis([f"mir_{c:g}" for c in self.mir.columns], axis=1))
        return pd.concat(blocks, axis=1)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as fh:
            pickle.dump(self, fh, protocol=pickle.HIGHEST_PROTOCOL)
        return path

    @staticmethod
    def load(path: str | Path) -> "SoilSpectra":
        with open(path, "rb") as fh:
            return pickle.load(fh)


# ---------------------------------------------------------------------------
# Leitura dos CSV brutos
# ---------------------------------------------------------------------------

def split_columns(columns) -> tuple[list[str], list[str]]:
    """Separa colunas não espectrais (texto) das espectrais (nomes numéricos)."""
    spectral, other = [], []
    for c in columns:
        try:
            float(c)
            spectral.append(c)
        except ValueError:
            other.append(c)
    return other, spectral


def read_raw(path: str | Path, ids=None, chunksize: int = 2000,
             encoding: str = config.RAW_ENCODING) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê um CSV bruto (metadados + espectros) em blocos, opcionalmente filtrando por ID.

    A leitura em blocos evita carregar ~1 GB de texto de uma vez. Os espectros são
    convertidos para float32 (metade da memória, precisão mais que suficiente).

    Retorna ``(meta, spectra)`` indexados por ``ID_Unico``.
    """
    path = Path(path)
    header = pd.read_csv(path, nrows=0, encoding=encoding).columns
    other, spectral = split_columns(header)
    other = [c for c in other if not c.startswith("Unnamed") and c != ""]
    dtypes = {c: np.float32 for c in spectral}
    dtypes.update({"Owner": str, "Country": str})

    ids = None if ids is None else set(ids)
    metas, specs = [], []
    reader = pd.read_csv(path, usecols=other + spectral, dtype=dtypes, encoding=encoding,
                         chunksize=chunksize)
    for chunk in reader:
        if ids is not None:
            chunk = chunk[chunk[config.ID_COL].isin(ids)]
        if chunk.empty:
            continue
        chunk = chunk.set_index(config.ID_COL)
        metas.append(chunk[[c for c in other if c != config.ID_COL]])
        specs.append(chunk[spectral])
    meta = pd.concat(metas)
    spectra = pd.concat(specs)
    spectra.columns = spectra.columns.astype(float)
    return meta, spectra


def read_ids(path: str | Path, encoding: str = config.RAW_ENCODING) -> pd.Series:
    """Lê apenas a coluna de IDs (rápido) - útil para cruzar arquivos."""
    return pd.read_csv(path, usecols=[config.ID_COL], encoding=encoding)[config.ID_COL]


def fill_spectral_gaps(spectra: pd.DataFrame, max_missing_frac: float = 0.05,
                       max_band_missing: float = 0.2) -> tuple[pd.DataFrame, pd.Index]:
    """Trata lacunas (NaN) em duas etapas.

    1. Remove **bandas** ausentes em mais de ``max_band_missing`` das amostras
       (ex.: 600-400 cm-1 do MIR, que a maioria dos equipamentos não mede);
    2. Remove **amostras** com mais de ``max_missing_frac`` das bandas restantes
       ausentes e interpola as lacunas pequenas ao longo do eixo espectral.

    Retorna ``(espectros_preenchidos, ids_descartados)``.
    """
    spectra = spectra.loc[:, spectra.isna().mean(axis=0) <= max_band_missing]
    frac = spectra.isna().mean(axis=1)
    dropped = spectra.index[frac > max_missing_frac]
    kept = spectra.loc[frac <= max_missing_frac]
    if kept.isna().any().any():
        kept = kept.interpolate(axis=1, limit_direction="both")
    return kept.astype(np.float32), dropped


def prepare_paired(raw_dir: str | Path = config.RAW_DIR,
                   vnir_file: str = config.RAW_VNIR_FILE,
                   mir_file: str = config.RAW_MIR_FILE,
                   max_missing_frac: float = 0.05) -> SoilSpectra:
    """Monta a base pareada: amostras com espectro VIS-NIR-SWIR **e** MIR.

    Os atributos são tomados do arquivo VIS-NIR-SWIR e completados com os do MIR
    quando ausentes (os dois arquivos compartilham as mesmas colunas).
    """
    raw_dir = Path(raw_dir)
    vnir_path, mir_path = raw_dir / vnir_file, raw_dir / mir_file
    common = sorted(set(read_ids(vnir_path)) & set(read_ids(mir_path)))
    if not common:
        raise ValueError("Nenhum ID_Unico em comum entre os arquivos VIS-NIR-SWIR e MIR.")

    meta_v, vnir = read_raw(vnir_path, ids=common)
    meta_m, mir = read_raw(mir_path, ids=common)

    vnir, drop_v = fill_spectral_gaps(vnir, max_missing_frac)
    mir, drop_m = fill_spectral_gaps(mir, max_missing_frac)
    keep = vnir.index.intersection(mir.index).sort_values()

    meta = meta_v.loc[keep].combine_first(meta_m.loc[keep])[meta_v.columns]
    meta["Textura"] = texture_class(meta["Clay_gkg"], meta["Sand_gkg"])
    info = {
        "fonte_vnir": vnir_path.name, "fonte_mir": mir_path.name,
        "ids_em_comum": len(common), "descartados_lacunas": len(drop_v.union(drop_m)),
        "unidade_vnir": "nm (reflectância)", "unidade_mir": "cm-1",
    }
    return SoilSpectra(meta=meta, vnir=vnir.loc[keep], mir=mir.loc[keep], info=info)


# ---------------------------------------------------------------------------
# Carregamento para análises e aulas
# ---------------------------------------------------------------------------

def paired_path() -> Path:
    return config.PROCESSED_DIR / config.PAIRED_FILE


def build_paired_cache(raw_dir: str | Path | None = None, out: str | Path | None = None,
                       max_missing_frac: float = 0.05, verbose: bool = True) -> SoilSpectra:
    """Lê os CSV brutos, monta a base pareada e salva o .pkl + resumo dos atributos."""
    raw_dir = Path(raw_dir or config.RAW_DIR)
    out = Path(out or paired_path())
    if verbose:
        print(f"Preparando a base pareada a partir de {raw_dir} (cerca de 30 s)...")
    ds = prepare_paired(raw_dir, max_missing_frac=max_missing_frac)
    ds.save(out)
    summary = ds.attributes.describe().T
    summary["n_validos"] = ds.attributes.notna().sum()
    summary.to_csv(out.with_name("resumo_atributos.csv"))
    if verbose:
        print(f"Base salva em {out}")
    return ds


def _cache_is_stale(path: Path) -> bool:
    """True se o .pkl não existe ou é mais antigo que algum CSV bruto."""
    if not path.exists():
        return True
    raws = [config.RAW_DIR / config.RAW_VNIR_FILE, config.RAW_DIR / config.RAW_MIR_FILE]
    return any(r.exists() and r.stat().st_mtime > path.stat().st_mtime for r in raws)


def load_dataset(source: str = "paired", n_synthetic: int = 600) -> SoilSpectra:
    """Carrega a base de trabalho.

    ``source``:
      * ``"paired"``    - base do GeoCiS (padrão). Na primeira vez - ou se os CSV brutos
        mudarem - a base é preparada automaticamente a partir de
        ``raw_nir_data_Saturin.csv`` e ``raw_mir_data_Saturin.csv``;
      * ``"synthetic"`` - base sintética (sem dados confidenciais, para demonstrações).
    """
    if source == "synthetic":
        return make_synthetic(n_synthetic)
    if source not in ("paired", "auto"):
        raise ValueError("source deve ser 'paired' ou 'synthetic'")
    path = paired_path()
    if _cache_is_stale(path):
        missing = [f for f in (config.RAW_VNIR_FILE, config.RAW_MIR_FILE)
                   if not (config.RAW_DIR / f).exists()]
        if missing:
            raise FileNotFoundError(
                f"CSV brutos não encontrados em {config.RAW_DIR}: {missing}. Coloque-os em "
                f"data/raw/ ou na pasta-mãe do projeto, ou defina GEOCIS_RAW_DIR.")
        return build_paired_cache()
    return SoilSpectra.load(path)


def make_synthetic(n: int = 600, seed: int = config.SEED) -> SoilSpectra:
    """Gera espectros sintéticos de solo com feições fisicamente plausíveis.

    Os espectros respondem aos atributos (argila -> 2200 nm e OH do MIR;
    carbono -> albedo e C-H a 2920 cm-1; Fe -> 480-530 e 900 nm; areia -> quartzo
    no MIR), de modo que todas as rotinas (PCA, correlação, clusters, modelos)
    produzam resultados interpretáveis sem expor dados reais.
    """
    rng = np.random.default_rng(seed)

    # --- atributos ---
    group = rng.choice(3, size=n, p=[0.35, 0.4, 0.25])          # arenoso, médio, argiloso
    clay = np.clip(rng.normal([90, 300, 600], [40, 80, 100])[group], 10, 900)
    sand = np.clip(rng.normal([800, 450, 150], [60, 90, 70])[group], 20, 980)
    sand = np.minimum(sand, 1000 - clay - 10)
    silt = 1000 - clay - sand
    carbon = np.exp(rng.normal(np.log(8 + clay / 40), 0.45))
    iron = np.clip(rng.normal(20 + clay / 12, 12), 1, None)       # g/kg (oculto)
    kaol = rng.uniform(0.4, 1.0, n)                              # fração caulinítica (oculta)
    ph = np.clip(rng.normal(5.6 - carbon / 150 + (sand - 400) / 2000, 0.6), 3.8, 8.5)
    moisture = rng.uniform(0.2, 1.0, n)

    # --- VIS-NIR-SWIR (reflectância) ---
    wl = np.arange(350, 2501, 1.0)

    def gauss(x, center, width):
        return np.exp(-0.5 * ((x - center) / width) ** 2)

    albedo = 0.62 - 0.18 * clay / 1000 - 0.09 * np.log1p(carbon) / np.log1p(60)
    shape = 1 - 0.85 * np.exp(-(wl - 330) / 260)
    fe = iron[:, None] / 120
    absorb = (
        fe * (0.9 * gauss(wl, 500, 60) + 0.45 * gauss(wl, 900, 110))
        + moisture[:, None] * (0.10 * gauss(wl, 1415, 25) + 0.22 * gauss(wl, 1915, 45))
        + (clay / 1000 * kaol)[:, None] * 0.45 * gauss(wl, 2207, 22)
        + (clay / 1000 * (1 - kaol))[:, None] * 0.35 * gauss(wl, 2265, 18)
        + 0.04 * gauss(wl, 2340, 30)
    )
    vnir = albedo[:, None] * shape[None, :] * np.exp(-absorb)
    vnir += rng.normal(0, 0.002, vnir.shape)
    edges = (wl < 400) | (wl > 2450)
    vnir[:, edges] += rng.normal(0, 0.012, (n, edges.sum()))
    vnir = np.clip(vnir, 0.005, 1)

    # --- MIR (absorbância) ---
    wn = np.arange(4000, 399, -4.0)
    mir = (
        0.15 + 0.10 * (4000 - wn)[None, :] / 3600
        + (clay / 1000 * kaol)[:, None] * (0.35 * gauss(wn, 3695, 12) + 0.25 * gauss(wn, 3620, 12))
        + (carbon / 60)[:, None] * 0.25 * gauss(wn, 2925, 30)
        + (sand / 1000)[:, None] * (0.25 * gauss(wn, 1990, 25) + 0.22 * gauss(wn, 1870, 25)
                                    + 0.20 * gauss(wn, 1790, 20))
        + moisture[:, None] * 0.12 * gauss(wn, 1630, 40)
        + 0.45 * gauss(wn, 1030, 90)[None, :]
    )
    mir += rng.normal(0, 0.003, mir.shape)

    ids = pd.Index(np.arange(1, n + 1), name=config.ID_COL)
    meta = pd.DataFrame({
        "Owner": "SINTETICO", "Country": "Sintético",
        "X": rng.uniform(-50, -45, n), "Y": rng.uniform(-23, -20, n),
        "Upper_depth_cm": 0.0, "Lower_depth_cm": 20.0,
        "Sand_gkg": sand, "Silt_gkg": silt, "Clay_gkg": clay, "C_gkg": carbon,
        "pH_H2O": ph, "Textura": pd.Categorical(np.array(["Arenosa", "Média", "Argilosa"])[group],
                                                 categories=["Arenosa", "Média", "Argilosa"]),
    }, index=ids)
    return SoilSpectra(
        meta=meta,
        vnir=pd.DataFrame(vnir.astype(np.float32), index=ids, columns=wl),
        mir=pd.DataFrame(mir.astype(np.float32), index=ids, columns=wn),
        info={"fonte": "sintética", "unidade_vnir": "nm (reflectância)", "unidade_mir": "cm-1"},
    )


def texture_class(clay_gkg, sand_gkg) -> pd.Categorical:
    """Agrupamento textural simplificado (SiBCS): arenosa, média, argilosa, muito argilosa."""
    clay = np.asarray(clay_gkg, dtype=float)
    sand = np.asarray(sand_gkg, dtype=float)
    labels = np.full(clay.shape, None, dtype=object)
    labels[(clay < 150) & (sand - clay > 700)] = "Arenosa"
    labels[(clay >= 350) & (clay < 600)] = "Argilosa"
    labels[clay >= 600] = "Muito argilosa"
    labels[(labels == None) & ~np.isnan(clay)] = "Média"  # noqa: E711
    return pd.Categorical(labels, categories=["Arenosa", "Média", "Argilosa", "Muito argilosa"])
