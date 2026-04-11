import streamlit as st
import pandas as pd
import joblib

from src.config import PASTA_RESULTADOS

from src.modelos.interpretacao import score_estrutural

from src.preprocessamento.categorias import (
    ORDEM_SAL_MIN,
    ORDEM_OCUPACAO,
    ORDEM_PAIS_ESCOLARIDADE,
    ORDEM_ESCOLA
)

from utils.layout import linha_controles, divisor


def render_aba_modelo():

    # =========================
    # CARREGAR MODELO
    # =========================
    @st.cache_resource
    def carregar_modelo():
        caminho = PASTA_RESULTADOS / "modelo_produto.joblib"
        return joblib.load(caminho)

    modelo = carregar_modelo()


    # =========================
    # FORMULÁRIO
    # =========================
    info_fullwidth(
        """ O modelo desenvolvido neste projeto tem como objetivo estimar a nota média esperada a partir de um perfil socioeconômico, com foco em uma interpretação estrutural e agregada. 
        
        Cada observação do modelo representa um grupo definido por:
        * faixa de renda familiar (em salários mínimos),
        * escolaridade dos responsáveis,
        * ocupação dos responsáveis,
        * tipo de escola frequentada,
        * características demográficas.
        
        Essa agregação reduz o ruído individual e permite analisar relações mais estáveis entre contexto social e desempenho educacional."""
    )

    col1, col2 = st.columns(2)

    with col1:
        salmin = st.selectbox("Renda familiar", ORDEM_SAL_MIN)
        escola = st.selectbox("Tipo de escola", ORDEM_ESCOLA)
        cel = st.selectbox("Celulares", [0, 1, 2, 3, "4 ou mais"])
        comp = st.selectbox("Computadores", [0, 1, 2, 3, "4 ou mais"])
        pessoas = st.slider("Pessoas na residência", 1, 10, 3)

    with col2:
        ocup_pai = st.selectbox("Ocupação pai", ORDEM_OCUPACAO)
        ocup_mae = st.selectbox("Ocupação mãe", ORDEM_OCUPACAO)
        esc_pai = st.selectbox("Escolaridade pai", ORDEM_PAIS_ESCOLARIDADE)
        esc_mae = st.selectbox("Escolaridade mãe", ORDEM_PAIS_ESCOLARIDADE)

    # =========================
    # TRATAMENTO
    # =========================
    def tratar(x):
        return 4 if x == "4 ou mais" else x

    cel = tratar(cel)
    comp = tratar(comp)

    def cat_num(v, ordem):
        return ordem.index(v)

    ocup_media = (
        cat_num(ocup_pai, ORDEM_OCUPACAO) +
        cat_num(ocup_mae, ORDEM_OCUPACAO)
    ) / 2

    esc_media = (
        cat_num(esc_pai, ORDEM_PAIS_ESCOLARIDADE) +
        cat_num(esc_mae, ORDEM_PAIS_ESCOLARIDADE)
    ) / 2

    # =========================
    # DATAFRAME
    # =========================

    
    dados = pd.DataFrame([{
        "SalMin": salmin,
        "Escola": escola,
        "OcupPaisMedia": ocup_media,
        "EscolaridadePaisMedia": esc_media,
        "Cel": cel,
        "Comptdr": comp,
        "PessoasResd": pessoas
    }])

    divisor()

    colunas_modelo = [
        "SalMin",
        "Escola",
        "OcupPaisMedia",
        "EscolaridadePaisMedia",
        "Cel",
        "Comptdr",
        "PessoasResd"
    ]

    dados = dados[colunas_modelo]

    # =========================
    # PREDIÇÃO
    # =========================
    if st.button("Prever nota"):

        try:
            dados_modelo = dados

            nota = modelo.predict(dados_modelo)[0]
            score = score_estrutural(modelo, dados_modelo)[0]

            st.success(f"Nota prevista: {nota:.1f}")

            st.metric(
                label="Score estrutural",
                value=f"{score:.2f}"
            )

            # interpretação
            if score < -5:
                st.warning("Perfil menos favorecido")
            elif score < 5:
                st.info("Perfil intermediário")
            else:
                st.success("Perfil favorecido")
             
            st.caption(
                "O score estrutural representa a contribuição linear das condições sociais previstas pelo modelo. Valores negativos indicam contexto estrutural menos favorecido relativamente à média observada."
                )

        except Exception as e:
            st.error(f"Erro na predição: {e}")
            
            