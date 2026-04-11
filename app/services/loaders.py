from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import (
    DADOS_AGG_2024,
    RESULTADOS_AGG_2024,
    MERGED_2024,
    AMOSTRAG_RESULTADOS_2024,
    DADOS_AGG_MG,
    RESULTADOS_AGG_MG,
    MERGED_MG,
    AMOSTRAG_RESULTADOS_MG,
    DADOS_AGG_MG_21_23,
)


@st.cache_data(show_spinner=False)
def carregar_bases_brasil() -> dict[str, pd.DataFrame]:
    return {
        "demografico": pd.read_parquet(DADOS_AGG_2024),
        "resultados": pd.read_parquet(RESULTADOS_AGG_2024),
        "merged": pd.read_parquet(MERGED_2024),
        "amostra": pd.read_parquet(AMOSTRAG_RESULTADOS_2024),
    }


@st.cache_data(show_spinner=False)
def carregar_bases_mg() -> dict[str, pd.DataFrame]:
    return {
        "demografico": pd.read_parquet(DADOS_AGG_MG),
        "resultados": pd.read_parquet(RESULTADOS_AGG_MG),
        "merged": pd.read_parquet(MERGED_MG),
        "amostra": pd.read_parquet(AMOSTRAG_RESULTADOS_MG),
        "21_23": pd.read_parquet(DADOS_AGG_MG_21_23),
    }