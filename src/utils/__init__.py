"""
Subpacote de visualização.

Este subpacote concentra funções de gráficos e figuras do projeto, separando:

- graficos_analiticos: gráficos voltados para modelagem/diagnóstico/interpretação
- graficos_dash: gráficos voltados para EDA e dashboard (Streamlit)

Uso recomendado:
    from src.visualizacao import plot_coeficientes, plot_mapa_estrutural
    from src.visualizacao import dash_plot_algum_grafico
"""

from __future__ import annotations

# -----------------------------------------
# Analíticos (modelagem / diagnóstico)
# -----------------------------------------
from .graficos_analiticos import (
    plot_coeficientes,
    plot_comparar_metricas_modelos,
    plot_elasticidade_dimensao,
    plot_impacto_dimensoes,
    plot_mapa_estrutural,
    plot_residuos,
    plot_residuos_estimador,
    plot_residuos_vs_estrutura,
)

# -----------------------------------------
# Dashboard (EDA / Streamlit)
# -----------------------------------------
# Ajuste os nomes abaixo para refletirem as funções existentes em graficos_dash.py.
# Se ainda não existir nada lá, você pode deixar vazio por enquanto.
try:
    from .graficos_dash import (
        # Exemplo (troque pelos seus nomes reais):
        # plot_distribuicao_participantes,
        # plot_series_temporais,
        # plot_mapa_municipios,
    )
except Exception:
    # Evita quebrar imports do pacote caso o módulo do dash esteja incompleto
    pass


__all__ = [
    # Analíticos
    "plot_coeficientes",
    "plot_comparar_metricas_modelos",
    "plot_elasticidade_dimensao",
    "plot_impacto_dimensoes",
    "plot_mapa_estrutural",
    "plot_residuos",
    "plot_residuos_estimador",
    "plot_residuos_vs_estrutura",
    # Dash (adicione aqui quando definir os nomes reais)
]