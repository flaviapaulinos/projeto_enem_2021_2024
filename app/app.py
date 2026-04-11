from __future__ import annotations
import sys
from pathlib import Path
import base64

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.append(str(ROOT_PATH))

import streamlit as st

from pages.dashboard_brasil import render_dashboard_brasil
from pages.dashboard_mg import render_dashboard_mg
from pages.projeto import render_aba_projeto
from pages.modelo import render_aba_modelo

from utils.layout import (
    menu_paginas,
    banner,
    get_pagina,
    PAGINA_BRASIL,
    PAGINA_MG,
    PAGINA_PROJETO,
    PAGINA_MODELO,
)

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="ENEM Análise",
    page_icon="📊",
    layout="wide",
)

# =========================================================
# HIDE SIDEBAR
# =========================================================
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# MENU
# =========================================================
st.markdown(
    """
    <style>
    /* RADIO GROUP (GLOBAL) */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;        
        gap: 8px;
        align-items: center;
    }
    
    /* CADA OPÇÃO */
    div[role="radiogroup"] label {
        white-space: nowrap;   
        padding: 4px 8px;
    }
    
    /* TEXTO */
    div[role="radiogroup"] span {
        white-space: nowrap;
    }
    
    </style>
    """, unsafe_allow_html=True)
menu_paginas()

pagina = get_pagina()

# =========================================================
# BANNER
# =========================================================
if pagina == PAGINA_BRASIL:
    banner("relatorios/imagens/banner_dashboard_br.png")

elif pagina == PAGINA_MG:
    banner("relatorios/imagens/banner_dashboard_mg.png")

elif pagina == PAGINA_PROJETO:
    banner("relatorios/imagens/banner_projeto.png")

elif pagina == PAGINA_MODELO:
    banner("relatorios/imagens/banner_modelo.png")
    
st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True) 
st.caption("Recomendado para visualização em modo claro.")

# =========================================================
# RENDER
# =========================================================
if pagina == PAGINA_BRASIL:
    render_dashboard_brasil()

elif pagina == PAGINA_MG:
    render_dashboard_mg()

elif pagina == PAGINA_PROJETO:
    render_aba_projeto()

elif pagina == PAGINA_MODELO:
    render_aba_modelo()

img_path = ROOT_PATH / "relatorios/imagens/banner_assinatura.png"

# converter para base64
with open(img_path, "rb") as f:
    img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode()

# HTML com imagem embutida
st.markdown(
    f"""
    <a href="https://github.com/flaviapaulinos" target="_blank">
        <img src="data:image/png;base64,{img_base64}" style="width:100%; cursor:pointer;">
    </a>
    """,
    unsafe_allow_html=True
)