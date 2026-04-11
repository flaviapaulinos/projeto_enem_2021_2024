"""
src/processamento/contingencia.py
=================================

Funções para tabelas de contingência e percentuais usados no dashboard
e em EDA.

Padroniza:
- percentuais por grupo
- crosstab em formato longo
- tabela tridimensional normalizada
"""

from __future__ import annotations

from typing import List, Optional

import pandas as pd


def calcular_percentual(
    df: pd.DataFrame,
    grupo: str,
    categoria: str,
    coluna_peso: str = "participantes",
) -> pd.DataFrame:
    """
    Calcula percentuais de `categoria` dentro de cada `grupo`,
    ponderando por `coluna_peso` (ex.: participantes).

    Returns
    -------
    DataFrame com colunas [grupo, categoria, coluna_peso, perc]
    """
    df_group = (
        df.groupby([grupo, categoria], as_index=False)[coluna_peso]
        .sum()
    )
    df_group["perc"] = df_group.groupby(grupo)[coluna_peso].transform(lambda x: x / x.sum() * 100)
    return df_group


def calcular_percentual_ano(
    df: pd.DataFrame,
    grupo: str,
    categoria: str,
    ano: Optional[int] = None,
    coluna_ano: str = "ano",
    coluna_peso: str = "participantes",
) -> pd.DataFrame:
    """
    Mesmo que `calcular_percentual`, com filtro opcional por ano.
    """
    if ano is not None:
        df = df[df[coluna_ano] == ano]
    return calcular_percentual(df, grupo, categoria, coluna_peso=coluna_peso)


def criar_tabela_contingencia(
    df: pd.DataFrame,
    linha: str,
    coluna: str,
    normalize: str = "index",
    round_decimals: int = 2,
) -> pd.DataFrame:
    """
    Cria uma tabela de contingência normalizada (percentual) e retorna
    em formato longo.

    normalize:
      - 'index' (cada linha soma 100%)
      - 'columns'
      - 'all'
    """
    tabela = pd.crosstab(df[linha], df[coluna], normalize=normalize) * 100
    # normalização explícita para garantir soma = 100 por linha (evita drift por arredondamento)
    if normalize == "index":
        tabela = tabela.div(tabela.sum(axis=1), axis=0) * 100

    tabela_long = (
        tabela.reset_index()
        .melt(id_vars=linha, var_name=coluna, value_name="Percentual")
    )
    tabela_long["Percentual"] = tabela_long["Percentual"].round(round_decimals)
    return tabela_long


def criar_tabela_tridimensional_normalizada(
    df: pd.DataFrame,
    linhas: List[str],
    coluna: str,
    categorias_coluna: Optional[List[str]] = None,
    round_decimals: int = 2,
) -> pd.DataFrame:
    """
    Tabela tridimensional em formato longo, garantindo soma de Percentual = 100%
    para cada combinação das colunas em `linhas`.
    """
    if len(linhas) != 2:
        raise ValueError("`linhas` deve conter exatamente duas colunas.")

    contagem = df.groupby(linhas + [coluna]).size().reset_index(name="contagem")

    valores_linhas = [df[c].unique() for c in linhas]
    if categorias_coluna is None:
        categorias_coluna = list(df[coluna].unique())

    todos = pd.MultiIndex.from_product(
        valores_linhas + [categorias_coluna],
        names=linhas + [coluna],
    )
    contagem = (
        contagem.set_index(linhas + [coluna])
        .reindex(todos, fill_value=0)
        .reset_index()
    )

    totais = contagem.groupby(linhas)["contagem"].transform("sum")
    contagem["Percentual"] = (contagem["contagem"] / totais * 100).round(round_decimals)

    return contagem[linhas + [coluna, "Percentual"]]


def verificar_somas(
    tabela: pd.DataFrame,
    grupo: List[str],
    coluna_percentual: str = "Percentual",
) -> pd.DataFrame:
    """
    Verifica se os percentuais somam ~100% por grupo.
    """
    return tabela.groupby(grupo)[coluna_percentual].sum().reset_index()

# ---------------------------------------------------------------------
# Ajustes estruturais
# ---------------------------------------------------------------------

def ajustar_percentuais_escolaridade(
    tabela: pd.DataFrame,
    coluna_escolaridade: str,
    escolas_manter: list[str] | None = None,
) -> pd.DataFrame:
    """
    Re-normaliza percentuais de escola para somarem 100%
    dentro de cada grupo renda × escolaridade.
    """

    if escolas_manter is None:
        escolas_manter = ["pública", "privada"]

    tabela_filtrada = tabela[
        tabela["escola"].isin(escolas_manter)
    ].copy()

    somas = (
        tabela_filtrada
        .groupby(["renda_mens_seg", coluna_escolaridade])["Percentual"]
        .sum()
        .reset_index(name="soma_atual")
    )

    tabela_recalculada = tabela_filtrada.merge(
        somas,
        on=["renda_mens_seg", coluna_escolaridade],
    )

    tabela_recalculada["Percentual"] = (
        tabela_recalculada["Percentual"]
        / tabela_recalculada["soma_atual"]
        * 100
    ).round(2)

    return tabela_recalculada.drop(columns="soma_atual")