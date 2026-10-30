"""Caminhos e constantes do projeto.

Todos os caminhos podem ser sobrescritos por variáveis de ambiente, de modo que
o mesmo código rode na máquina de cada membro do GeoCiS sem edição:

    GEOCIS_RAW_DIR        pasta com os CSV brutos (raw_nir_data_*.csv, raw_mir_data_*.csv)
    GEOCIS_PROCESSED_DIR  pasta com a base preparada (saída de scripts/preparar_dados.py)
    GEOCIS_OUTPUT_DIR     pasta para figuras e tabelas geradas
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_VNIR_FILE = "raw_nir_data_Saturin.csv"  # 350-2500 nm (reflectância)
RAW_MIR_FILE = "raw_mir_data_Saturin.csv"   # 4000-400 cm-1


def _find_raw_dir() -> Path:
    """Pasta dos CSV brutos: GEOCIS_RAW_DIR, senão data/raw/, senão a pasta-mãe do projeto."""
    if "GEOCIS_RAW_DIR" in os.environ:
        return Path(os.environ["GEOCIS_RAW_DIR"])
    for candidate in (PROJECT_ROOT / "data" / "raw", PROJECT_ROOT.parent):
        if (candidate / RAW_VNIR_FILE).exists() and (candidate / RAW_MIR_FILE).exists():
            return candidate
    return PROJECT_ROOT / "data" / "raw"


RAW_DIR = _find_raw_dir()
PROCESSED_DIR = Path(os.environ.get("GEOCIS_PROCESSED_DIR", PROJECT_ROOT / "data" / "processed"))
OUTPUT_DIR = Path(os.environ.get("GEOCIS_OUTPUT_DIR", PROJECT_ROOT / "outputs"))
RAW_ENCODING = "latin-1"
PAIRED_FILE = "base_pareada_vnir_mir.pkl"

# Colunas não espectrais presentes nos CSV brutos (na ordem do arquivo)
ID_COL = "ID_Unico"
META_COLS = ["ID_Unico", "Owner", "X", "Y", "Country", "Upper_depth_cm", "Lower_depth_cm"]
ATTRIBUTE_COLS = [
    "Sand_gkg", "Silt_gkg", "Clay_gkg", "Density_kgdm3", "C_gkg", "OM_gkg", "P_mgkg",
    "pH_H2O", "Ca_mmolkg", "Mg_mmolkg", "K_mmolkg", "CEC_Ph7_mmolkg", "CEC_Efe_mmolkg",
    "MacroN_g_kg",
]

SEED = 42

# Regiões espectrais de referência (nm) e feições diagnósticas usadas nos gráficos
VNIR_REGIONS = {"VIS": (350, 700), "NIR": (700, 1400), "SWIR": (1400, 2500)}
VNIR_FEATURES = {
    "Fe (hematita/goethita)": (480, 530),
    "Goethita ~900": (850, 950),
    "H2O/OH 1400": (1380, 1450),
    "H2O 1900": (1880, 1960),
    "Caulinita/Al-OH 2200": (2160, 2220),
    "Gibbsita 2265": (2250, 2280),
    "Mg/Fe-OH, carbonato 2330": (2320, 2350),
}
MIR_FEATURES = {
    "OH caulinita 3695/3620": (3600, 3710),
    "C-H alifático 2920": (2850, 2950),
    "Carbonato 2520": (2500, 2540),
    "Quartzo 2000-1790": (1780, 2000),
    "C=O / C=C 1600": (1580, 1650),
    "Si-O 1000": (950, 1100),
}
