from pathlib import Path
import streamlit as st

ROOT_PATH = Path(__file__).resolve().parents[2] 

# =========================================================
# 🔹 CONSTANTES DE PÁGINA (PADRÃO GLOBAL)
# =========================================================
PAGINA_BRASIL = "brasil"
PAGINA_MG = "minas_gerais"
PAGINA_MODELO = "modelo"
PAGINA_PROJETO = "projeto"

PAGINAS_LABEL = {
    PAGINA_BRASIL: "Brasil",
    PAGINA_MG: "MG",
    PAGINA_MODELO: "Modelo",
    PAGINA_PROJETO: "Projeto",
}


# =========================================================
# 🔹 ESTADO GLOBAL DO APP
# =========================================================
def get_pagina() -> str:
    return st.session_state.get("pagina", PAGINA_MG)


def set_pagina(pagina: str) -> None:
    st.session_state["pagina"] = pagina


# =========================================================
# 🔹 MENU SUPERIOR (NAVEGAÇÃO PRINCIPAL)
# =========================================================
def menu_paginas() -> None:
    """
    Renderiza o menu superior de navegação do app.
    Controla exclusivamente a mudança de páginas.
    """

    col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 6])

    if col1.button(PAGINAS_LABEL[PAGINA_MG]):
        set_pagina(PAGINA_MG)

    if col2.button(PAGINAS_LABEL[PAGINA_BRASIL]):
        set_pagina(PAGINA_BRASIL)

    if col3.button(PAGINAS_LABEL[PAGINA_MODELO]):
        set_pagina(PAGINA_MODELO)

    if col4.button(PAGINAS_LABEL[PAGINA_PROJETO]):
        set_pagina(PAGINA_PROJETO)


# =========================================================
# 🔹 BANNER
# =========================================================
def banner(caminho: str) -> None:
    caminho_completo = ROOT_PATH / caminho

    if not caminho_completo.exists():
        st.warning(f"Imagem não encontrada: {caminho}")
        return

    st.image(str(caminho_completo), width="stretch")
# =========================================================
# 🔹 LINHA DE CONTROLES (SEM NAVEGAÇÃO)
# =========================================================
def linha_controles(
    subabas: list[str],
    pagina_atual: str,
    opcoes_geo: list[str],
    key_prefix: str,
    opcoes_ano: list[str] | None = None,
):

    subaba = st.session_state.get(f"{key_prefix}_subaba", subabas[0])

    # =========================
    # CONFIG DINÂMICA
    # =========================
    mostrar_escola = subaba in [
        "estrutura socioeconômica",
        "desempenho",
        "desempenho x estrutura",
    ]

    mostrar_materia = subaba in [
        "desempenho",
        "desempenho x estrutura",
    ]

    n_cols = 3  # subaba + região

    if opcoes_ano:
        n_cols += 1
    if mostrar_escola:
        n_cols += 1
    if mostrar_materia:
        n_cols += 1

    cols = st.columns(n_cols)

    i = 0

    # =========================
    # SUBABA
    # =========================
    with cols[i]:
        subaba = st.selectbox(
            "",
            options=subabas,
            key=f"{key_prefix}_subaba",
        )
    i += 1

    # =========================
    # REGIÃO / UF
    # =========================
    with cols[i]:
        geo = st.selectbox(
            "Região" if pagina_atual == "minas_gerais" else "UF",
            options=[None] + opcoes_geo,
            format_func=lambda x: "Todos" if x is None else x,
            key=f"{key_prefix}_geo",
        )
    i += 1

    # =========================
    # ANO
    # =========================
    ano = None
    if opcoes_ano:
        with cols[i]:
            ano = st.selectbox(
                "Ano",
                options=[None] + opcoes_ano,
                format_func=lambda x: "Todos" if x is None else x,
                key=f"{key_prefix}_ano",
            )
        i += 1

    # =========================
    # TIPO DE ESCOLA
    # =========================
    escola = None
    if mostrar_escola:
        with cols[i]:
            escola = st.selectbox(
                "Escola",
                options=["Todas", "não informada", "pública", "privada"],
                key=f"{key_prefix}_escola",
            )
        i += 1

    # =========================
    # MATÉRIA
    # =========================
    materia = None
    if mostrar_materia:
        from src.config import MAPA_MATERIA_LABEL_PARA_COLUNA

        with cols[i]:
            materia = st.selectbox(
                "Matéria",
                options=list(MAPA_MATERIA_LABEL_PARA_COLUNA.keys()),
                key=f"{key_prefix}_materia",
            )

    return subaba.lower(), geo, ano, escola, materia

# =========================================================
# 🔹 DIVISOR
# =========================================================
def divisor() -> None:
    st.markdown("---")

# =========================================================
# 🔹 ALINHAMENTO DO TEXTO
# =========================================================
def info_fullwidth(texto: str) -> None:
    st.markdown(
        f"""
        <div style='
            text-align: justify;
            width: 100%;
            padding: 12px;
            background-color: rgba(0,0,0,0.03);
            border-radius: 8px;
            margin-bottom: 10px;
        '>
            {texto}
        </div>
        """,
        unsafe_allow_html=True
    )

def get_estado_controles(key_prefix: str):
    subaba = st.session_state.get(f"{key_prefix}_subaba", "visão geral")
    return subaba