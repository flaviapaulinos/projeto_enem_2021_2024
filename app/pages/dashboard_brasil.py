from __future__ import annotations

import streamlit as st

from services.loaders import carregar_bases_brasil
from utils.helpers_filtros import filtrar_df
from utils.helpers_ui import plot
from utils.layout import linha_controles, divisor, info_fullwidth, get_estado_controles

from components.secoes_brasil import (
    render_subaba_social_demografica_br,
    render_subaba_notas_br,
    render_subaba_desempenho_estrutura_br,
)

from src.visualizacao.graficos_dash import (
    criar_painel_indicadores_gerais,
    gerar_mapa_enem,
)
def controles_sidebar_apoio_br(opcoes_geo, key_prefix="br"):
    import streamlit as st

    st.sidebar.caption("Ajustes rápidos")

    geo = st.sidebar.selectbox(
        "UF",
        [None] + opcoes_geo,
        format_func=lambda x: "Todos" if x is None else x,
        key=f"{key_prefix}_geo_sidebar"
    )

    escola = st.sidebar.selectbox(
        "Escola",
        ["Todas", "não informada", "pública", "privada"],
        key=f"{key_prefix}_escola_sidebar"
    )

    materia = st.sidebar.selectbox(
        "Matéria",
        ["Todas", "Matemática", "Linguagens"],
        key=f"{key_prefix}_materia_sidebar"
    )

    # 🔥 sincronização com topo
    st.session_state[f"{key_prefix}_geo"] = geo
    st.session_state[f"{key_prefix}_escola"] = escola
    st.session_state[f"{key_prefix}_materia"] = materia

@st.cache_data(show_spinner=False)
def get_mapa(df):
    return gerar_mapa_enem(df, "uf")


def render_dashboard_brasil():

    bases = carregar_bases_brasil()

    df_d = bases["demografico"]
    df_r = bases["resultados"]
    df_m = bases["merged"]

    subaba = st.session_state.get("br_subaba", "visão geral")

    if subaba == "visão geral":
        st.subheader("Visão Geral: ENEM — Brasil (2024)")
        
        info_fullwidth(
            """Visão agregada do desempenho e da composição dos participantes do Enem no Brasil em 2024. 
            
        Devido à disponibilização dos dados em bases separadas (perfil socioeconômico e resultados), as análises são realizadas em nível agregado, permitindo identificar padrões estruturais regionais.
        * Os dados socioeconômicos provêm de um questionário respondido pelos participantes no ato da inscrição no Enem.  
        """
    )
        st.caption(
            "O mapa do Brasil pode levar alguns instantes para carregar devido ao volume de dados processados. "
            "Aguarde o carregamento completo para uma melhor experiência."
        )
        
    elif subaba == "estrutura socioeconômica":
        st.subheader("Análise Social e Demográfica — Brasil")
        info_fullwidth(
            """Análise da composição socioeconômica dos participantes, considerando distribuições percentuais e relações estruturais entre variáveis como renda familiar, escolaridade e ocupação dos responsáveis."""
        )
    
    elif subaba == "desempenho":
        
        st.subheader("Análise de Desempenho — Brasil")
        st.caption("Base analítica: ENEM 2024")
        
        info_fullwidth(
            """Análise do desempenho dos participantes, com foco na identificação de padrões regionais, diferenças por tipo de escola e distribuição das notas.  
            
        Parte das visualizações utiliza dados agregados, enquanto outras utilizam amostra de dados individuais para análise de distribuição.
            """
        )
    
    elif subaba == "desempenho x estrutura":
        st.subheader("Desempenho e Estrutura Socioeconômica — Brasil")
        st.caption("Base analítica: ENEM 2024")
        
        info_fullwidth(
            """Análise da relação entre fatores socioeconômicos e desempenho em nível agregado, permitindo identificar associações estruturais entre perfil dos participantes e resultados educacionais.
            """
        )
        
    # =========================================================
    # CONTROLES (SIDEBAR + TOPO)
    # =========================================================
    
    # Sidebar (apoio)
    controles_sidebar_apoio_br(
        opcoes_geo=sorted(df_d["uf"].dropna().unique()),
        key_prefix="br"
    )
    
    # Topo (principal)
    subaba, uf, _, escola, materia = linha_controles(
        subabas=["visão geral", "estrutura socioeconômica", "desempenho", "desempenho x estrutura"],
        pagina_atual="brasil",
        opcoes_geo=sorted(df_d["uf"].dropna().unique()),
        key_prefix="br"
    )


    df_d = filtrar_df(df_d, uf=uf)
    df_r = filtrar_df(df_r, uf=uf)
    df_m = filtrar_df(df_m, uf=uf)

    divisor()

    if subaba == "visão geral":

        col1, col2 = st.columns(2)

        with col1:
            fig_ind, _ = criar_painel_indicadores_gerais(
                df_notas_filtrado=df_r,
                df_demografico_filtrado=df_d,
                escopo="br",
            )
            plot(fig_ind, "br_visao_ind")

        with col2:
            plot(get_mapa(df_r), "br_visao_mapa")
        st.caption(
            "O índice de consumo foi construído a partir da normalização de bens e infraestrutura domiciliar (ex.: eletrodomésticos, veículos e acesso a serviços), agregados em uma métrica única entre 0 e 1. Esse indicador atua como proxy de nível socioeconômico, permitindo capturar dimensões de bem-estar não refletidas diretamente pela renda declarada."
            )

    elif subaba == "estrutura socioeconômica":



        render_subaba_social_demografica_br(
            df_d_seg=df_d,
            df_r_seg=df_r,
            df_merged=df_m,
        )

    elif subaba == "desempenho":


        render_subaba_notas_br(
            df_d_seg=df_d,
            df_r_seg=df_r,
            df_merged=df_m,
            df_amostra=bases["amostra"],
            escola=escola,
            materia=materia,
        )
  

    elif subaba == "desempenho x estrutura":


        render_subaba_desempenho_estrutura_br(
            df_d_seg=df_d,
            df_r_seg=df_r,
            df_merged=df_m,
            df_amostra=bases["amostra"],
            regiao=uf,
            escola=escola,
            materia=materia,
        )