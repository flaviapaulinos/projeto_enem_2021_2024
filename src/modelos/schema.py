"""
schema.py
=========

Funções relacionadas ao alinhamento estrutural de datasets
entre treino e predição.
"""

import pandas as pd


def alinhar_schema(X_ref: pd.DataFrame, X_novo: pd.DataFrame) -> pd.DataFrame:
    """
    Alinha tipos de dados de um novo dataframe
    com o dataframe utilizado no treinamento.
    """
    return X_novo.astype(X_ref.dtypes.to_dict())