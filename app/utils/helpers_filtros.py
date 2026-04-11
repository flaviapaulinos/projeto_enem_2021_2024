from __future__ import annotations

import pandas as pd


def filtrar_df(
    df: pd.DataFrame,
    ano: str | None = None,
    regiao: str | None = None,
    uf: str | None = None,
    escola: str | None = None,  # 👈 NOVO
) -> pd.DataFrame:
    """
    Filtro genérico para dashboards.

    Parâmetros:
    - ano: filtra por ano (string)
    - regiao: filtra por região (MG)
    - uf: filtra por estado (Brasil)
    - escola: filtra por tipo de escola
    """

    df_filtrado = df.copy()

    # =========================
    # ANO
    # =========================
    if ano is not None and "ano" in df_filtrado.columns:
        df_filtrado["ano"] = df_filtrado["ano"].astype(str)
        df_filtrado = df_filtrado[df_filtrado["ano"] == str(ano)]

    # =========================
    # REGIÃO
    # =========================
    if regiao is not None and "regiao" in df_filtrado.columns:
        df_filtrado["regiao"] = df_filtrado["regiao"].astype(str).str.strip()
        df_filtrado = df_filtrado[df_filtrado["regiao"] == regiao.strip()]

    # =========================
    # UF
    # =========================
    if uf is not None and "uf" in df_filtrado.columns:
        df_filtrado["uf"] = df_filtrado["uf"].astype(str).str.strip()
        df_filtrado = df_filtrado[df_filtrado["uf"] == uf.strip()]

    # =========================
    # TIPO DE ESCOLA (NOVO)
    # =========================
    if (
        escola is not None
        and escola != "Todas"
        and "escola" in df_filtrado.columns
    ):
        df_filtrado["escola"] = df_filtrado["escola"].astype(str).str.strip()
        df_filtrado = df_filtrado[df_filtrado["escola"] == escola.strip()]

    return df_filtrado