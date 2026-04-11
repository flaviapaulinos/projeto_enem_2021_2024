from __future__ import annotations

import pandas as pd
import streamlit as st

from src.visualizacao.graficos_dash import NOMES_AMIGAVEIS


CATEGORIAS_DEMOGRAFICAS_BR = {
    "sal_min": NOMES_AMIGAVEIS.get("sal_min", "Renda Mensal Familiar (salários mínimos)"),
    "sexo": NOMES_AMIGAVEIS.get("sexo", "Sexo"),
    "escola": NOMES_AMIGAVEIS.get("escola", "Escola"),
    "faixa_etaria": NOMES_AMIGAVEIS.get("faixa_etaria", "Faixa Etária"),
    "raca_cor": NOMES_AMIGAVEIS.get("raca_cor", "Raça/Cor"),
    "regiao": "Região"
}


def _opcoes_ordenadas(df: pd.DataFrame, coluna: str) -> list[str]:
    if coluna not in df.columns:
        return []
    valores = (
        df[coluna]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
    return sorted(valores)


def filtros_subaba_social_br(df_d_seg: pd.DataFrame) -> dict:
    """
    Filtros da subaba Social / Demográfica do dashboard BR.
    O recorte Brasil trabalha apenas com 2024.
    """
    with st.sidebar:
        st.markdown("## Filtros — BR Social/Demográfica")
        st.caption("Recorte fixo: ENEM 2024")

        categoria_barras = st.selectbox(
            "Categoria do gráfico de barras",
            options=list(CATEGORIAS_DEMOGRAFICAS_BR.keys()),
            format_func=lambda x: CATEGORIAS_DEMOGRAFICAS_BR[x],
            index=0,
            key="br_social_categoria_barras",
        )

        ufs = _opcoes_ordenadas(df_d_seg, "uf")
        uf_opcoes = [None] + ufs

        uf_renda_resp = st.selectbox(
            "UF — Renda por responsável",
            options=uf_opcoes,
            format_func=lambda x: "Brasil" if x is None else x,
            key="br_social_uf_renda_resp",
        )

        uf_empilhado = st.selectbox(
            "UF — Coluna empilhada",
            options=uf_opcoes,
            format_func=lambda x: "Brasil" if x is None else x,
            key="br_social_uf_empilhado",
        )

        uf_comparativo = st.selectbox(
            "UF — Comparativo pais",
            options=uf_opcoes,
            format_func=lambda x: "Brasil" if x is None else x,
            key="br_social_uf_comparativo",
        )

        tipo_comparativo_pais = st.selectbox(
            "Comparativo dos pais",
            options=["escolaridade", "ocupacao"],
            format_func=lambda x: "Escolaridade" if x == "escolaridade" else "Ocupação",
            key="br_social_tipo_comparativo_pais",
        )

        uf_tabela = st.selectbox(
            "UF — Tabela gradiente",
            options=uf_opcoes,
            format_func=lambda x: "Brasil" if x is None else x,
            key="br_social_uf_tabela",
        )

        uf_raca_renda = st.selectbox(
            "UF — Raça/Cor por renda",
            options=uf_opcoes,
            format_func=lambda x: "Brasil" if x is None else x,
            key="br_social_uf_raca_renda",
        )

    return {
        "categoria_barras": categoria_barras,
        "uf_renda_resp": uf_renda_resp,
        "uf_empilhado": uf_empilhado,
        "uf_comparativo": uf_comparativo,
        "tipo_comparativo_pais": tipo_comparativo_pais,
        "uf_tabela": uf_tabela,
        "uf_raca_renda": uf_raca_renda,
    }

def filtros_dashboard_mg(df_d_seg: pd.DataFrame) -> dict:
    """
    Filtros globais do dashboard MG.
    """
    with st.sidebar:
        st.markdown("## Filtros — Minas Gerais")

        anos = _opcoes_ordenadas(df_d_seg, "ano")
        ano = st.selectbox(
            "Ano",
            options=[None] + anos,
            format_func=lambda x: "Todos os anos" if x is None else x,
            key="mg_dashboard_ano",
        )

        regioes = _opcoes_ordenadas(df_d_seg, "regiao")
        regiao = st.selectbox(
            "Região",
            options=[None] + regioes,
            format_func=lambda x: "Minas Gerais" if x is None else x,
            key="mg_dashboard_regiao",
        )

    return {
        "ano": ano,
        "regiao": regiao,
    }


def filtros_subaba_notas_mg() -> dict:
    """
    Filtros específicos da subaba de notas do MG.
    """
    categorias = [
        "escolaridade_mae",
        "escolaridade_pai",
        "ocup_mae",
        "ocup_pai",
        "sal_min",
    ]

    with st.sidebar:
        st.markdown("### Filtros — Notas MG")

        categoria_analise = st.selectbox(
            "Categoria de análise",
            options=categorias,
            format_func=lambda x: NOMES_AMIGAVEIS.get(x, x.replace("_", " ").title()),
            key="mg_notas_categoria",
        )

    return {
        "categoria_analise": categoria_analise,
    }

def filtros_subaba_social_mg() -> dict:
    """
    Filtros específicos da subaba Social / Demográfica do MG.
    """

    categorias_barras = [
        "sal_min",
        "sexo",
        "escola",
        "faixa_etaria",
        "raca_cor",
    ]

    colunas_tabela = [
        "cor_raca",
        "escola",
    ]

    with st.sidebar:
        st.markdown("### Filtros — Social MG")

        categoria_barras = st.selectbox(
            "Categoria do gráfico de barras",
            options=categorias_barras,
            format_func=lambda x: NOMES_AMIGAVEIS.get(x, x.replace("_", " ").title()),
            key="mg_social_categoria_barras",
        )

        tipo_comparativo_pais = st.selectbox(
            "Comparativo dos pais",
            options=["escolaridade", "ocupacao"],
            format_func=lambda x: "Escolaridade" if x == "escolaridade" else "Ocupação",
            key="mg_social_tipo_comparativo_pais",
        )

        coluna_tabela = st.selectbox(
            "Tabela gradiente por",
            options=colunas_tabela,
            format_func=lambda x: NOMES_AMIGAVEIS.get(x, x.replace("_", " ").title()),
            key="mg_social_coluna_tabela",
        )

    return {
        "categoria_barras": categoria_barras,
        "tipo_comparativo_pais": tipo_comparativo_pais,
        "coluna_tabela": coluna_tabela,
    }