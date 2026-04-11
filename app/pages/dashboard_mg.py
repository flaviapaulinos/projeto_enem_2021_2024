from __future__ import annotations
import streamlit as st

from services.loaders import carregar_bases_mg
from utils.helpers_filtros import filtrar_df
from utils.helpers_ui import plot
from utils.layout import linha_controles, divisor, info_fullwidth, get_estado_controles

from components.secoes_mg import (
    render_subaba_social_demografica_mg,
    render_subaba_notas_mg,
    render_subaba_desempenho_estrutura_mg,  
)

from src.visualizacao.graficos_dash import (
    criar_painel_indicadores_gerais,
    gerar_mapa_enem,
    grafico_evolucao_temporal_acurado,
)


@st.cache_data(show_spinner=False)
def get_mapa(df):
    return gerar_mapa_enem(df, "regiao_mg", ano_selecionado=None)


def render_dashboard_mg():

    bases = carregar_bases_mg()

    df_d = bases["demografico"]
    df_r = bases["resultados"]
    df_m = bases["merged"]
    df_a = bases["amostra"]
    df_21_23=bases["21_23"]

  
    anos = sorted(df_d["ano"].dropna().astype(str).unique())


    subaba_display = st.session_state.get("mg_subaba", "visão geral")

# =========================================================
# HEADER + CONTEXTO
# =========================================================

    if subaba_display == "visão geral":
        
    # 🔹 APRESENTAÇÃO DO PROJETO
        info_fullwidth(
            """Análise dos fatores socioeconômicos e sua relação com o desempenho dos participantes do ENEM ao longo da série histórica (2021–2024), com foco no estado de Minas Gerais. O projeto integra dashboard interativo e modelo preditivo para interpretação estrutural dos dados.
        
    Este dashboard analisa a relação entre fatores socioeconômicos e desempenho no ENEM,com foco em Minas Gerais e comparação com o Brasil.
        
    A abordagem combina análise descritiva, agregações ponderadas por participantes e visualizações multivariadas para identificar padrões estruturais na desigualdade educacional.

            
    🔎 Explore as abas para analisar diferentes dimensões do desempenho educacional.
    
    **Mais informações na página Projeto.**"""
        )
        
        st.subheader("Visão Geral: ENEM — Minas Gerais (2021–2024)")
        
        info_fullwidth(
        """Visão consolidada do ENEM em Minas Gerais ao longo da série histórica.  
        Devido à disponibilização dos dados em bases separadas em 2024 (perfil socioeconômico e desempenho), as análises são realizadas em nível agregado, 
        permitindo identificar padrões estruturais regionais.
        * Os dados socioeconômicos provêm de um questionário respondido pelos participantes no ato da isncrição no Enem.  """
        )
    
    elif subaba_display == "estrutura socioeconômica":
        
        st.subheader("Análise Social e Demográfica — Minas Gerais")
        
        info_fullwidth(
            """Análise da estrutura socioeconômica dos participantes, considerando distribuições percentuais e relações entre variáveis como renda familiar, 
        escolaridade e ocupação dos responsáveis."""
        )
    
    elif subaba_display == "desempenho":
        st.subheader("Análise de Desempenho — Minas Gerais")
        st.caption("Base analítica: ENEM 2021–2024")
        
        info_fullwidth(
            """Análise do desempenho dos participantes, com foco na identificação de padrões regionais, diferenças por tipo de escola e distribuição das notas.  
            Parte das visualizações utiliza dados agregados, enquanto outras utilizam amostra de dados individuais para análise de distribuição."""
        )
    
    elif subaba_display == "desempenho x estrutura":
        st.subheader("Desempenho e Estrutura Socioeconômica — Minas Gerais")
        st.caption("Base analítica: ENEM 2021–2024")
        info_fullwidth(
            """Análise integrada da relação entre fatores socioeconômicos e desempenho ao longo do tempo, permitindo observar padrões estruturais persistentes 
        e possíveis mecanismos associados às desigualdades educacionais."""
        )
    subaba, regiao, ano, escola, materia = linha_controles(
        subabas=["visão geral", "estrutura socioeconômica", "desempenho", "desempenho x estrutura"],
        pagina_atual="minas_gerais",
        opcoes_geo=sorted(df_d["regiao"].dropna().unique()),
        key_prefix="mg",
        opcoes_ano=anos,  
    )
    
    df_d = filtrar_df(df_d, regiao=regiao, ano=ano, escola=escola)
    df_r = filtrar_df(df_r, regiao=regiao, ano=ano, escola=escola)
    df_m = filtrar_df(df_m, regiao=regiao, ano=ano, escola=escola)
    df_a = filtrar_df(df_a, regiao=regiao, ano=ano, escola=escola)

    # =========================================================
    # VISÃO GERAL
    # =========================================================
    if subaba == "visão geral":


        col1, col2 = st.columns(2)

        with col1:
            fig, _ = criar_painel_indicadores_gerais(
                df_notas_filtrado=df_r,
                df_demografico_filtrado=df_d,
                escopo="mg",
                ano_selecionado=None,
            )
            plot(fig, "mg_visao_painel")

        with col2:
            plot(get_mapa(df_r), "mg_visao_mapa")
        st.caption(
                "O índice de consumo foi construído a partir da normalização de bens e infraestrutura domiciliar (ex.: eletrodomésticos, veículos e acesso a serviços), agregados em uma métrica única entre 0 e 1. Esse indicador atua como proxy de nível socioeconômico, permitindo capturar dimensões de bem-estar não refletidas diretamente pela renda declarada."
            )
        fig_evolucao, _ = grafico_evolucao_temporal_acurado(
            df=df_m,
            escopo="mg",
            filtro_geo=regiao,
            materias_selecionadas=None,
            weight_col="participantes",
            titulo=None,
        )
        plot(fig_evolucao, "mg_visao_evolucao")

    # =========================================================
    # SOCIAL
    # =========================================================
    elif subaba == "estrutura socioeconômica":

        divisor()

        render_subaba_social_demografica_mg(
            df_d_seg=df_d,
            df_r_seg=df_r,
            df_merged=df_m,
        )

    # =========================================================
    # DESEMPENHO
    # =========================================================
    elif subaba == "desempenho":
        
        divisor()
        
        render_subaba_notas_mg(
            df_d_seg=df_d,
            df_r_seg=df_r,
            df_merged=df_m,
            df_amostra=df_a,
            escola=escola,
            materia=materia,
        )

        st.info(
        """
        Alguns gráficos utilizam amostras individuais para distribuição.
        """
        )

    # =========================================================
    # NOVA SUBABA
    # =========================================================
    elif subaba == "desempenho x estrutura":
        
        divisor()
        
        render_subaba_desempenho_estrutura_mg(
            df_d_seg=df_d,
            df_r_seg=df_r,
            df_merged=df_m,
            df_amostra=df_a,
            df_agg_21_23=df_21_23,
            regiao=regiao,
            escola=escola,
            materia=materia,
        )

        