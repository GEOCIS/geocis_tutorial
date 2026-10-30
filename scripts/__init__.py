"""geocis_espectral - rotinas reutilizáveis de análise espectral de solos (GeoCiS).

Módulos temáticos:
    dados          leitura dos CSV, base pareada VIS-NIR-SWIR + MIR, dados sintéticos
    visualizacao   gráficos de espectros, PCA, correlação, clusters e modelos
    processamento  Savitzky-Golay, derivadas, SNV, MSC, detrend, remoção do contínuo
    exploratoria   PCA e correlação de Pearson (espectros/PCs × atributos)
    agrupamento    k-means, ISODATA e métricas de similaridade espectral (SAM, SID, ...)
    modelagem      PLSR / Random Forest / XGBoost, métricas e interpretação SHAP

USO INTERNO DO GeoCiS - não compartilhar dados ou códigos sem autorização.
"""

from . import agrupamento, config, dados, exploratoria, modelagem, processamento, visualizacao

__version__ = "0.1.0"
__all__ = ["agrupamento", "config", "dados", "exploratoria", "modelagem", "processamento", "visualizacao"]
