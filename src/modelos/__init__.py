"""
API pública do módulo de modelagem estrutural.
"""

# ---------------------------
# Pipeline
# ---------------------------
from .pipeline import (
    construir_pipeline_modelo_regressao,
    extrair_pipeline,
)

# ---------------------------
# Treinamento
# ---------------------------
from .treino import (
    CV_CONFIG,
    ESTABILIDADE_THRESHOLDS,
    RANDOM_STATE,
    avaliar_estabilidade,
    calcular_estatisticas_validacao,
    comparar_modelos_cv,
    grid_search_estratificado,
    organiza_resultados,
    treinar_e_validar_modelo_regressao,
    validacao_cruzada_estratificada,
    
    
)

# ---------------------------
# Interpretação estrutural
# ---------------------------
from .interpretacao import (
    dataframe_coeficientes,
    decompor_ide,
    elasticidade_padronizada,
    elasticidade_por_dimensao,
    indice_desigualdade_estrutural,
    impacto_por_dimensao,
    score_estrutural,
)

# ---------------------------
# Schema
# ---------------------------
from .schema import alinhar_schema


__all__ = [
    # pipeline
    "construir_pipeline_modelo_regressao",
    "extrair_pipeline",

    # treino
    "CV_CONFIG",
    "ESTABILIDADE_THRESHOLDS",
    "RANDOM_STATE",
    "avaliar_estabilidade",
    "calcular_estatisticas_validacao",
    'comparar_modelos_cv',
    "grid_search_estratificado",
    "treinar_e_validar_modelo_regressao",
    "organiza_resultados",
    "validacao_cruzada_estratificada",
    "calcular_estatisticas_validacao",

    # interpretação
    "dataframe_coeficientes",
    "elasticidade_padronizada",
    "elasticidade_por_dimensao",
    "impacto_por_dimensao",
    "decompor_ide",
    "indice_desigualdade_estrutural",
    "score_estrutural",

    # schema
    "alinhar_schema",
]
