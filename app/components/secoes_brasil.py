import streamlit as st
import pandas as pd

from utils.helpers_ui import (
    plot,
    txt_r2,
    txt_renda_nota_mg,
    txt_tecnologia
)

from src.config import MAPA_MATERIA_LABEL_PARA_COLUNA

from src.visualizacao.graficos_dash import (
    analise_acesso_tecnologia,
    boxplot_notas_por_regiao,
    bubble_chart_4d,
    grafico_barras_percentual,
    grafico_coluna_empilhada_percentual,
    grafico_combinado_notas_renda,
    grafico_comparativo_pais,
    grafico_comparativo_escola_privada_pais,
    grafico_notas_por_regiao,
    grafico_notas_linhas_max,
    grafico_notas_violino,
    grafico_renda_responsavel,
    tabela_plotly_gradiente,
    tabela_notas_maximas,
    treemap_escola_renda,
    treemap_nota_escola,
)

# =========================================================
# SOCIAL — BRASIL
# =========================================================

def render_subaba_social_demografica_br(
    df_d_seg: pd.DataFrame,
    df_r_seg: pd.DataFrame,
    df_merged: pd.DataFrame,
):

    container_categoria = st.container()

    with container_categoria:
        col_titulo, col_radio = st.columns([2, 5], gap="xsmall")

        with col_titulo:
            st.markdown("##### Distribuição Percentual")

        with col_radio:
            categoria = st.radio(
                "",
                options=["escola", "sal_min", "sexo", "cor_raca"],
                format_func=lambda x: {
                    "sexo": "Sexo",
                    "cor_raca": "Cor/Raça",
                    "escola": "Escola",
                    "sal_min": "Renda Mensal Familiar (salários mínimos)",
                }[x],
                horizontal=True,
                key="br_social_categoria",
            )

    fig_barras, _ = grafico_barras_percentual(
        df=df_d_seg,
        categoria=categoria,
        escopo="br",
        weight_col="participantes",
    )
    plot(fig_barras, "br_social_barras")

    col1, col2 = st.columns([1, 1], gap="small")

    with col1:
        fig_emp, _ = grafico_coluna_empilhada_percentual(
            df=df_d_seg,
            eixo_x="sal_min",
            eixo_cor="escola",
            escopo="br",
            weight_col="participantes",
        )
        plot(fig_emp, "br_social_emp")

    with col2:
        fig_tab, _ = tabela_plotly_gradiente(
            df=df_d_seg,
            linha="ano",
            coluna=categoria,
            valor="renda_media",
            escopo="br",
        )
        plot(fig_tab, "br_social_tab")

    fig_tree, _ = treemap_escola_renda(
        df=df_d_seg,
        escopo="br",
    )
    plot(fig_tree, "br_social_tree")

    fig_priv, _ = grafico_comparativo_escola_privada_pais(
        df=df_d_seg,
        escopo="br",
        weight_col="participantes",
    )
    plot(fig_priv, "br_social_priv")

    container_pais = st.container()
    with container_pais:
        col_titulo, col_radio = st.columns([1, 3], gap="small")

        with col_titulo:
            st.markdown("##### Comparativo Pais/Responsáveis - Brasil")

        with col_radio:
            tipo = st.radio(
                "",
                options=["escolaridade", "ocupacao"],
                format_func=lambda x: {
                    "escolaridade": "Escolaridade",
                    "ocupacao": "Ocupação",
                }[x],
                horizontal=True,
                key="mg_social_pais_toggle",
            )

    col3, col4 = st.columns([2, 1], gap="small")

    with col3:
        fig_comp, _ = grafico_comparativo_pais(
            df=df_d_seg,
            tipo=tipo,
            escopo="br",
            weight_col="participantes",
        )
        plot(fig_comp, "br_social_comp")

    with col4:
        fig_renda, _ = grafico_renda_responsavel(
            df=df_d_seg,
            variavel=tipo,
            escopo="br",
            weight_col="participantes",
        )
        plot(fig_renda, "br_social_renda")


# =========================================================
# NOTAS — BRASIL
# =========================================================

def render_subaba_notas_br(
    df_d_seg,
    df_r_seg,
    df_merged,
    df_amostra,
    escola,
    materia,
):

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    materia_coluna = None
    if materia:
        materia_coluna = MAPA_MATERIA_LABEL_PARA_COLUNA[materia]

    if escola and escola != "Todas":
        df_r_seg = df_r_seg[df_r_seg["escola"] == escola]

    fig_box, _ = boxplot_notas_por_regiao(
        df=df_amostra,
        escopo="br",
        weight_col="participantes",
    )
    plot(fig_box, "br_box")

    col1, col2 = st.columns([1, 2], gap="xsmall")

    with col1:
        fig_tab, _ = tabela_notas_maximas(
            df=df_r_seg,
            escopo="br",
        )
        plot(fig_tab, "br_tab")

    with col2:
        fig_regiao, _ = grafico_notas_por_regiao(
            df=df_r_seg,
            escola_selecionada=escola,
            materia_selecionada=materia_coluna,
            escopo="br",
        )
        plot(fig_regiao, "br_regiao")


# =========================================================
# DESEMPENHO X ESTRUTURA — BRASIL
# =========================================================

def render_subaba_desempenho_estrutura_br(
    df_d_seg,
    df_r_seg,
    df_merged,
    df_amostra,
    regiao,
    escola,
    materia,
):

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    materia_coluna = None
    if materia:
        materia_coluna = MAPA_MATERIA_LABEL_PARA_COLUNA[materia]

    fig_bubble, _, _ = bubble_chart_4d(
        df=df_merged,
        filtro_geo=regiao,
        escopo="br",
    )
    plot(fig_bubble, "br_dx_bubble")
    txt_r2()

    fig_comb, _, _ = grafico_combinado_notas_renda(
        df=df_merged,
        escopo="br",
    )
    plot(fig_comb, "br_dx_renda")
    txt_renda_nota_mg()

    col1, col2 = st.columns(2)

    with col1:
        fig_linhas, _ = grafico_notas_linhas_max(
            df=df_r_seg,
            escopo="br",
        )
        plot(fig_linhas, "br_dx_linhas")

    with col2:
        fig_violino = grafico_notas_violino(
            df=df_amostra,
            escopo="br",
        )
        plot(fig_violino, "br_dx_violino")

    fig_tec, _ = analise_acesso_tecnologia(
        df=df_merged,
        escopo="br",
        weight_col="participantes",
    )
    plot(fig_tec, "br_dx_tec")
    txt_tecnologia()

    fig_priv, _ = grafico_comparativo_escola_privada_pais(
        df=df_d_seg,
        escopo="br",
        weight_col="participantes",
    )
    plot(fig_priv, "br_dx_priv")

    fig_tree, _ = treemap_nota_escola(
        df=df_r_seg,
        materia=materia,
        escopo="br",
    )
    plot(fig_tree, "br_dx_tree")
