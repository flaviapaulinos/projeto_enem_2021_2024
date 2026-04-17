import streamlit as st
import pandas as pd

from utils.helpers_ui import (
    plot,
    txt_distribuicao,
    txt_escolaridade_escola,
    txt_renda_pais,
    txt_bubble_relacao,
    txt_renda_nota_simples,
    txt_desigualdade,
    txt_tecnologia,
    txt_conclusao
)

from src.config import MAPA_MATERIA_LABEL_PARA_COLUNA

from src.visualizacao.graficos_dash import (
    analise_acesso_tecnologia,
    analise_mobilidade_ranking,
    boxplot_notas_por_regiao,
    bubble_chart_4d,
    grafico_barras_percentual,
    grafico_coluna_empilhada_percentual,
    grafico_combinado_notas_renda,
    grafico_comparativo_pais,
    grafico_comparativo_escola_privada_pais,
    grafico_nota_media_por_categoria_escola_ano,
    grafico_notas_linhas_max,
    grafico_notas_violino,
    grafico_raca_por_renda_barras,
    grafico_renda_responsavel,
    tabela_plotly_gradiente,
    tabela_notas_maximas,
    treemap_escola_renda,
    treemap_nota_escola,
)

# =========================================================
# SOCIAL / DEMOGRÁFICA — MG
# =========================================================

def render_subaba_social_demografica_mg(
    df_d_seg: pd.DataFrame,
    df_r_seg: pd.DataFrame,
    df_merged: pd.DataFrame,
):
    container_categoria = st.container()

    with container_categoria:
        col_titulo, col_radio = st.columns([2, 4], gap="xsmall")

        with col_titulo:
            st.markdown("##### Distribuição Percentual")

        with col_radio:
            categoria = st.radio(
                "",
                options=["escola", "sal_min", "sexo", "cor_raca", "faixa_etaria"],
                format_func=lambda x: {
                    "sexo": "sexo",
                    "cor_raca": "cor/raça",
                    "escola": "escola",
                    "sal_min": "renda mensal familiar (salários mínimos)",
                    "faixa_etaria": "faixa etária",
                }[x],
                horizontal=True,
                key="mg_social_categoria",
            )

    fig_barras, _ = grafico_barras_percentual(
        df=df_d_seg,
        categoria=categoria,
        escopo="mg",
        weight_col="participantes",
    )
    plot(fig_barras, "mg_social_barras")
    txt_distribuicao()

    col1, col2 = st.columns([1, 1], gap="small")

    with col1:
        fig_emp, _ = grafico_coluna_empilhada_percentual(
            df=df_d_seg,
            eixo_x="sal_min",
            eixo_cor="escola",
            escopo="mg",
            weight_col="participantes",
        )
        plot(fig_emp, "mg_social_emp")

    with col2:
        fig_tab, _ = tabela_plotly_gradiente(
            df=df_d_seg,
            linha="ano",
            coluna=categoria,
            valor="renda_media",
            escopo="mg",
        )
        plot(fig_tab, "mg_social_tab")

    fig_distrib_renda, _ = grafico_raca_por_renda_barras(
        df_d_seg,
        escopo="mg",
    )
    plot(fig_distrib_renda, "mg_distrib_renda")


    fig_tree, _ = treemap_escola_renda(
        df=df_d_seg,
        escopo="mg",
    )
    plot(fig_tree, "mg_social_tree")

    fig_priv, _ = grafico_comparativo_escola_privada_pais(
        df=df_d_seg,
        escopo="mg",
        weight_col="participantes",
    )
    plot(fig_priv, "mg_social_priv")
    txt_escolaridade_escola()

    container_pais = st.container()
    with container_pais:
        col_titulo, col_radio = st.columns([1, 2], gap="small")

        with col_titulo:
            st.markdown("##### Comparativo Pais/Responsáveis - MG")

        with col_radio:
            tipo_comp = st.radio(
                "",
                options=["escolaridade", "ocupacao"],
                format_func=lambda x: {
                    "escolaridade": "Escolaridade",
                    "ocupacao": "Ocupação",
                }[x],
                horizontal=True,
                key="mg_social_pais_toggle",
            )

    col3, col4 = st.columns([2, 1], gap="xxsmall")

    with col3:
        fig_comp, _ = grafico_comparativo_pais(
            df=df_d_seg,
            tipo=tipo_comp,
            ano_selecionado=None,
            escopo="mg",
            weight_col="participantes",
        )
        plot(fig_comp, "mg_social_comp")

    with col4:
        fig_renda, _ = grafico_renda_responsavel(
            df=df_d_seg,
            variavel=tipo_comp,
            ano_selecionado=None,
            escopo="mg",
            weight_col="participantes",
        )
        plot(fig_renda, "mg_social_renda")
        txt_renda_pais()


# =========================================================
# NOTAS — MG
# =========================================================

def render_subaba_notas_mg(
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
        escopo="mg",
    )
    plot(fig_box, "mg_box")

    col1, col2 = st.columns([1, 2], gap="xsmall")

    with col1:
        fig_tab, _ = tabela_notas_maximas(
            df=df_r_seg,
            escopo="mg",
        )
        plot(fig_tab, "mg_tab")

    with col2:
        fig_regiao, _ = analise_mobilidade_ranking(
            df=df_r_seg,
            materia_selecionada=materia_coluna,
            titulo="Evolução das notas por região",
        )
        plot(fig_regiao, "mg_regiao")


# =========================================================
# DESEMPENHO X ESTRUTURA — MG
# =========================================================

def render_subaba_desempenho_estrutura_mg(
    df_d_seg,
    df_r_seg,
    df_merged,
    df_amostra,
    df_agg_21_23,
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
        escopo="mg",
    )
    plot(fig_bubble, "mg_bubble")
    txt_bubble_relacao()

    fig_comb, _, _ = grafico_combinado_notas_renda(
        df=df_merged,
        escopo="mg",
    )
    plot(fig_comb, "mg_comb")
    txt_renda_nota_simples()

    fig_cat, _ = grafico_nota_media_por_categoria_escola_ano(
        df_agg_21_23,
        categoria="sal_min",
        escopo="mg",
    )
    plot(fig_cat, "mg_cat")
    txt_desigualdade()

    col1, col2 = st.columns(2)

    with col1:
        fig_linhas, _ = grafico_notas_linhas_max(
            df=df_r_seg,
            escopo="mg",
        )
        plot(fig_linhas, "mg_linhas")

    with col2:
        fig_violino = grafico_notas_violino(
            df=df_amostra,
            escopo="mg",
        )
        plot(fig_violino, "mg_violino")

    fig_tec, _ = analise_acesso_tecnologia(
        df=df_merged,
        escopo="mg",
        weight_col="participantes",
    )
    plot(fig_tec, "mg_tec")
    txt_tecnologia()

    fig_tree, _ = treemap_nota_escola(
        df=df_r_seg,
        materia=materia,
        escopo="mg",
    )
    plot(fig_tree, "mg_tree")

    txt_conclusao()