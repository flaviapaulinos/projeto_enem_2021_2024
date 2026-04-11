"""
graficos_dash.py
===============

Módulo unificado de visualizações para o dashboard interativo do ENEM.

Este módulo consolida todas as funções de gráficos dos arquivos:
- graficos.py (análises gerais)
- graficos_br.py (análises Brasil)
- graficos_mg.py (análises Minas Gerais)

Todas as funções agora aceitam o parâmetro 'escopo' que pode ser:
- 'br' (Brasil)
- 'mg' (Minas Gerais)
- 'caxambu' (Município de Caxambu)

Autor: Flavia Paulinos
Projeto: ENEM 2021–2024
"""

import geopandas as gpd
import geobr
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from typing import Optional, List, Dict, Tuple, Union
import unicodedata

    
# Importar categorias e mapeamentos
from src.preprocessamento.categorias import (
    ORDEM_ANOS,
    ORDEM_ESCOLA,
    ORDEM_FAIXA_ETARIA,
    ORDEM_SAL_MIN,
    ORDEM_PAIS_ESCOLARIDADE,
    ORDEM_OCUPACAO,
    ORDEM_RACA,
    ORDEM_SEXO,
    ORDEM_ESTADO_CIVIL,
    ORDEM_LINGUA,
    ORDEM_SAL_MIN,
   
)

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

SEQUENCIA_CORES = [
    "khaki", "teal", "cornflowerblue", "lightsalmon", "deepskyblue",
    "darkolivegreen", "lightseagreen", "gold", "navy", "darkgreen",
    "goldenrod", "springgreen", "rosybrown", "darkslateblue"
]

COLOR_MAP_RENDA_COMP = {
    "(?)": "linen",
    "até 1": "khaki",
    "1 a 3": "teal",
    "3 a 5": "cornflowerblue",
    "5 a 10": "deepskyblue",
    "10 a 15": "lightsalmon",
    "15 a 20": "deepskyblue",
    "acima de 20": "darkolivegreen",
}

MAPA_CORES_ESCOLA = {
    "não informada": "khaki",
    "pública": "teal",
    "privada": "cornflowerblue"
}

MATERIAS = {
    "nota_cn": "Ciências da Natureza",
    "nota_ch": "Ciências Humanas",
    "nota_lc": "Linguagens e Códigos",
    "nota_mt": "Matemática",
    "nota_redacao": "Redação"
}

NOMES_AMIGAVEIS = {
    "sal_min": "Renda Mensal Familiar (salários mínimos)",
    "cor_raca": "Raça/Cor",
    "escola": "Escola",
    "sexo": "Sexo",
    "faixa_etaria": "Faixa Etária",
    "escolaridade_pai": "Escolaridade do Pai",
    "escolaridade_mae": "Escolaridade da Mãe",
    "ocup_pai": "Ocupação do Pai",
    "ocup_mae": "Ocupação da Mãe",
    "nota_cn": "Ciências Natureza",
    "nota_ch": "Ciências Humanas",
    "nota_lc": "Linguagens",
    "nota_mt": "Matemática",
    "nota_redacao": "Redação",
    "cel": "Celular",
    "comptdr": "Computador",
    "indice_consumo": "Índice de Consumo",
    "renda_media": "Renda Média Familiar"
}


# =============================================================================
# FORMATAÇÃO BR
# =============================================================================

def formatar_numero_br(valor: Union[int, float], casas_decimais: int = 0) -> str:
    """
    Formata número com ponto como separador de milhar e vírgula decimal.
    """
    if pd.isna(valor) or valor is None:
        return "0"

    if casas_decimais == 0:
        return f"{int(valor):,}".replace(",", ".")

    valor_arredondado = round(valor, casas_decimais)
    partes = f"{valor_arredondado:.{casas_decimais}f}".split(".")
    inteiro = f"{int(partes[0]):,}".replace(",", ".")
    return f"{inteiro},{partes[1]}"


def formatar_decimal_br(valor: float, casas_decimais: int = 1) -> str:
    """
    Formata número decimal no padrão brasileiro.
    Ex.: 532.4 -> '532,4'
    """
    if pd.isna(valor) or valor is None:
        return "0"
    return f"{valor:.{casas_decimais}f}".replace(".", ",")


def formatar_percentual_br(valor: float, casas_decimais: int = 1) -> str:
    """
    Formata valor percentual em padrão brasileiro.
    Espera valor em decimal. Ex.: 0.856 -> '85,6%'
    """
    if pd.isna(valor) or valor is None:
        return "0%"
    return f"{formatar_decimal_br(valor * 100, casas_decimais)}%"


def formatar_moeda_br(valor: float, casas_decimais: int = 2) -> str:
    """
    Formata valor monetário em padrão brasileiro.
    """
    if pd.isna(valor) or valor is None:
        return "R$ 0"
    return f"R$ {formatar_numero_br(valor, casas_decimais)}"


def adicionar_colunas_hover_br(
    df: pd.DataFrame,
    mapeamento: Dict[str, Tuple[str, int, str]]
) -> pd.DataFrame:
    """
    Adiciona múltiplas colunas formatadas em padrão brasileiro.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    mapeamento : dict
        Formato:
        {
            "coluna_destino": ("coluna_origem", casas_decimais, tipo)
        }

        tipos aceitos:
        - "numero"
        - "decimal"
        - "percentual"
        - "moeda"
    """
    df = df.copy()

    funcoes_formatacao = {
        "numero": formatar_numero_br,
        "decimal": formatar_decimal_br,
        "percentual": formatar_percentual_br,
        "moeda": formatar_moeda_br,
    }

    for coluna_destino, (coluna_origem, casas_decimais, tipo) in mapeamento.items():
        if coluna_origem not in df.columns:
            raise KeyError(f"Coluna '{coluna_origem}' não encontrada no DataFrame.")

        if tipo not in funcoes_formatacao:
            raise ValueError(
                "tipo deve ser 'numero', 'decimal', 'percentual' ou 'moeda'."
            )

        func = funcoes_formatacao[tipo]
        df[coluna_destino] = df[coluna_origem].apply(lambda x: func(x, casas_decimais))

    return df


def adicionar_coluna_formatada_br(
    df: pd.DataFrame,
    coluna_origem: str,
    coluna_destino: str,
    casas_decimais: int = 1,
    tipo: str = "numero"
) -> pd.DataFrame:
    """
    Wrapper para adicionar uma única coluna formatada.
    """
    return adicionar_colunas_hover_br(
        df,
        {coluna_destino: (coluna_origem, casas_decimais, tipo)}
    )


def adicionar_colunas_formatadas_hover(
    df: pd.DataFrame,
    coluna_valor: str,
    coluna_participantes: str = "total_participantes"
) -> pd.DataFrame:
    """
    Atalho padronizado para casos frequentes de hover:
    - valor_fmt
    - participantes_fmt
    """
    return adicionar_colunas_hover_br(
        df,
        {
            "valor_fmt": (coluna_valor, 2, "numero"),
            "participantes_fmt": (coluna_participantes, 0, "numero")
        }
    )


def aplicar_eixos_br_plotly(
    fig: go.Figure,
    eixo_x_decimal: bool = False,
    eixo_y_decimal: bool = False,
    casas_decimais_x: int = 1,
    casas_decimais_y: int = 1
) -> go.Figure:
    """
    Aplica formatação de ticks nos eixos do Plotly.
    """
    fig.update_layout(separators=".,")

    if eixo_x_decimal:
        fig.update_xaxes(tickformat=f",.{casas_decimais_x}f")
    else:
        fig.update_xaxes(tickformat=",d")

    if eixo_y_decimal:
        fig.update_yaxes(tickformat=f",.{casas_decimais_y}f")
    else:
        fig.update_yaxes(tickformat=",d")

    return fig


# =============================================================================
# TEXTO / VALORES NOS GRÁFICOS PLOTLY
# =============================================================================

def aplicar_texto_plotly(
    fig: go.Figure,
    textposition: str = "auto",
    textfont_size: int = 11,
    textfont_color: Optional[str] = None,
    textfont_family: str = "Arial Bold, Arial, sans-serif",
    texttemplate: Optional[str] = None
) -> go.Figure:
    """
    Padroniza a exibição de textos nos traces Plotly.
    """
    for trace in fig.data:
        trace_type = getattr(trace, "type", None)

        if textposition == "auto":
            if trace_type == "bar":
                trace.textposition = "inside"
            elif trace_type == "scatter":
                trace.textposition = "top center"
            else:
                trace.textposition = "middle center"
        else:
            trace.textposition = textposition

        if texttemplate is not None:
            trace.texttemplate = texttemplate

        font_dict = {
            "family": textfont_family,
            "size": textfont_size
        }

        if textfont_color is not None:
            font_dict["color"] = textfont_color

        trace.textfont = font_dict

    return fig


def aplicar_texto_negrito_plotly(
    fig: go.Figure,
    textposition: str = "auto",
    textfont_size: int = 11,
    texttemplate: Optional[str] = None
) -> go.Figure:
    """
    Wrapper para texto em negrito sem forçar cor.
    """
    return aplicar_texto_plotly(
        fig=fig,
        textposition=textposition,
        textfont_size=textfont_size,
        textfont_family="Arial Bold, Arial, sans-serif",
        texttemplate=texttemplate
    )


def aplicar_texto_valores_br_plotly(
    fig: go.Figure,
    textposition: str = "inside",
    textfont_size: int = 11,
    textfont_color: str = "white"
) -> go.Figure:
    """
    Wrapper para valores destacados no gráfico.
    """
    return aplicar_texto_plotly(
        fig=fig,
        textposition=textposition,
        textfont_size=textfont_size,
        textfont_color=textfont_color,
        textfont_family="Arial Black"
    )


def aplicar_texto_negrito_barras(
    fig: go.Figure,
    textfont_size: int = 11
) -> go.Figure:
    """
    Wrapper para barras.
    """
    return aplicar_texto_plotly(
        fig=fig,
        textposition="inside",
        textfont_size=textfont_size,
        textfont_family="Arial Bold, Arial, sans-serif"
    )


def aplicar_texto_negrito_linhas(
    fig: go.Figure,
    textfont_size: int = 11,
    textposition: str = "top center"
) -> go.Figure:
    """
    Wrapper para linhas/scatter.
    """
    return aplicar_texto_plotly(
        fig=fig,
        textposition=textposition,
        textfont_size=textfont_size,
        textfont_family="Arial Bold, Arial, sans-serif"
    )


# =============================================================================
# FUNÇÕES AUXILIARES DE CATEGORIA / CORES / NOMES
# =============================================================================

def obter_ordem_padrao(categoria: str) -> Optional[List[str]]:
    """
    Retorna a ordem padrão baseada no nome da categoria.
    """
    ordens = {
        "sal_min": ORDEM_SAL_MIN,
        "cor_raca": ORDEM_RACA,
        "escolaridade_pai": ORDEM_PAIS_ESCOLARIDADE,
        "escolaridade_mae": ORDEM_PAIS_ESCOLARIDADE,
        "ocup_pai": ORDEM_OCUPACAO,
        "ocup_mae": ORDEM_OCUPACAO,
        "sexo": ORDEM_SEXO,
        "escola": ORDEM_ESCOLA,
        "faixa_etaria": ORDEM_FAIXA_ETARIA,
        "ano": ORDEM_ANOS,
        "lingua": ORDEM_LINGUA,
        "estado_civil": ORDEM_ESTADO_CIVIL,
    }
    return ordens.get(categoria)


def obter_mapa_cores(categoria: str, subcategoria: Optional[str] = None) -> Optional[Dict]:
    """
    Retorna o mapa de cores apropriado para a categoria.
    """
    if categoria in {"sal_min", "renda"}:
        return COLOR_MAP_RENDA_COMP

    if categoria == "escola":
        return MAPA_CORES_ESCOLA

    if categoria in {"raça", "cor_raca"}:
        return {
            "não informada": "khaki",
            "negra": "cornflowerblue",
            "branca": "teal",
            "amarela": "lightsalmon",
            "indígena": "deepskyblue"
        }

    if categoria == "sexo":
        return {
            "feminino": "cornflowerblue",
            "masculino": "teal"
        }

    if categoria == "faixa_etaria":
        return {
            "até 19": "teal",
            "20-25": "cornflowerblue",
            "26-35": "khaki",
            "36-45": "lightsalmon",
            "46-60": "deepskyblue",
            "acima de 61": "darkolivegreen"
        }

    return None


def obter_nome_escopo(escopo: str) -> str:
    """
    Retorna nome amigável do escopo.
    """
    return {
        "br": "Brasil",
        "mg": "Minas Gerais",
        "caxambu": "Caxambu"
    }.get(escopo, escopo.upper())


def obter_rotulo_geo(escopo: str) -> str:
    """
    Retorna o rótulo geográfico apropriado.
    """
    if escopo == "br":
        return "UF"
    if escopo == "mg":
        return "Região"
    if escopo == "caxambu":
        return "Município"
    return "Localidade"


def montar_complemento_filtro_geo(escopo: str, filtro_geo: Optional[str]) -> str:
    """
    Retorna complemento textual para títulos.
    """
    if not filtro_geo:
        return ""

    if escopo == "br":
        return f" (UF: {filtro_geo})"
    if escopo == "mg":
        return f" (Região: {filtro_geo})"
    if escopo == "caxambu":
        return f" ({filtro_geo})"

    return f" ({filtro_geo})"


def obter_nivel_geografico_treemap(df: pd.DataFrame, escopo: str) -> str:
    """
    Retorna a coluna geográfica mais apropriada para treemap.
    """
    if escopo == "br" and "uf" in df.columns:
        return "uf"
    if escopo == "mg" and "regiao" in df.columns:
        return "regiao"
    if escopo == "caxambu":
        if "municipio" in df.columns:
            return "municipio"
        if "cidade" in df.columns:
            return "cidade"
    if "regiao" in df.columns:
        return "regiao"
    if "uf" in df.columns:
        return "uf"
    return "escola"

def _normalizar_texto_regiao(texto: str) -> str:
    if pd.isna(texto):
        return ""

    texto = str(texto).strip().lower()

    # remover acentos
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    # expandir abreviações mais comuns
    texto = texto.replace("metrop.", "metropolitana")
    texto = texto.replace("triang.", "triangulo")
    texto = texto.replace("min.", "mineiro")
    texto = texto.replace("paran.", "paranaiba")

    # separadores
    texto = texto.replace("/", " ")
    texto = texto.replace("-", " ")
    texto = texto.replace(".", " ")

    # remover caracteres residuais
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    # equivalências específicas MG
    equivalencias = {
        "centro de minas": "central mineira",
        "vale do jequitinhonha": "jequitinhonha",
        "triangulo mineiro e alto paranaiba": "triangulo mineiro alto paranaiba",
        "triangulo mineiro alto paranaiba": "triangulo mineiro alto paranaiba",
        "sul de minas": "sul sudoeste de minas",
        "sudoeste de minas": "sul sudoeste de minas",
        "sul sudoeste de minas": "sul sudoeste de minas",
    }

    return equivalencias.get(texto, texto)
# =============================================================================
# FILTROS
# =============================================================================

def filtrar_por_escopo(df: pd.DataFrame, escopo: str = "mg") -> pd.DataFrame:
    """
    Filtra o DataFrame de acordo com o escopo.
    """
    df_filtrado = df.copy()

    if escopo == "mg":
        if "uf" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["uf"] == "MG"]

    elif escopo == "caxambu":
        if "municipio" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["municipio"].astype(str).str.contains("Caxambu", na=False)]
        elif "cidade" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["cidade"].astype(str).str.contains("Caxambu", na=False)]

    return df_filtrado


def filtrar_geografia_opcional(
    df: pd.DataFrame,
    escopo: str,
    filtro_geo: Optional[str] = None
) -> pd.DataFrame:
    """
    Aplica filtro geográfico adicional.
    """
    if filtro_geo is None:
        return df.copy()

    df_filtrado = df.copy()

    if escopo == "br" and "uf" in df_filtrado.columns:
        return df_filtrado[df_filtrado["uf"] == filtro_geo]

    if escopo == "mg" and "regiao" in df_filtrado.columns:
        return df_filtrado[df_filtrado["regiao"] == filtro_geo]

    if escopo == "caxambu":
        if "municipio" in df_filtrado.columns:
            return df_filtrado[df_filtrado["municipio"] == filtro_geo]
        if "cidade" in df_filtrado.columns:
            return df_filtrado[df_filtrado["cidade"] == filtro_geo]

    return df_filtrado


def aplicar_filtros_dashboard(
    df: pd.DataFrame,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None
) -> pd.DataFrame:
    """
    Aplica filtros padrão do dashboard:
    - escopo
    - ano
    - filtro geográfico adicional
    """
    df_filtrado = filtrar_por_escopo(df, escopo)

    if ano_selecionado is not None and "ano" in df_filtrado.columns:
        df_filtrado = df_filtrado.copy()
        df_filtrado["ano"] = df_filtrado["ano"].astype(str)
        df_filtrado = df_filtrado[df_filtrado["ano"] == str(ano_selecionado)]

    df_filtrado = filtrar_geografia_opcional(
        df=df_filtrado,
        escopo=escopo,
        filtro_geo=filtro_geo
    )

    return df_filtrado


# =============================================================================
# CÁLCULOS
# =============================================================================



def media_ponderada(
    df: pd.DataFrame,
    coluna_valor: str,
    coluna_peso: str = "participantes"
) -> float:
    """
    Calcula média ponderada de forma robusta.
    """
    if df.empty:
        return 0.0

    if coluna_valor not in df.columns or coluna_peso not in df.columns:
        return 0.0

    valores = pd.to_numeric(df[coluna_valor], errors="coerce")
    pesos = pd.to_numeric(df[coluna_peso], errors="coerce")

    mascara_valida = valores.notna() & pesos.notna() & (pesos != 0)

    if not mascara_valida.any():
        return 0.0

    valores_validos = valores[mascara_valida]
    pesos_validos = pesos[mascara_valida]

    soma_pesos = pesos_validos.sum()
    if soma_pesos == 0:
        return 0.0

    return float(np.average(valores_validos, weights=pesos_validos))


def media_ponderada_por_grupo(
    df: pd.DataFrame,
    coluna_grupo: str,
    coluna_valor: str,
    coluna_peso: str = "participantes"
) -> pd.DataFrame:
    """
    Calcula média ponderada por grupo.
    """
    colunas_necessarias = {coluna_grupo, coluna_valor, coluna_peso}
    if df.empty or not colunas_necessarias.issubset(df.columns):
        return pd.DataFrame(columns=[coluna_grupo, "valor_medio", "total_participantes"])

    df_aux = df[[coluna_grupo, coluna_valor, coluna_peso]].copy()
    df_aux[coluna_valor] = pd.to_numeric(df_aux[coluna_valor], errors="coerce")
    df_aux[coluna_peso] = pd.to_numeric(df_aux[coluna_peso], errors="coerce")

    df_aux = df_aux.dropna(subset=[coluna_grupo, coluna_valor, coluna_peso])
    df_aux = df_aux[df_aux[coluna_peso] > 0]

    if df_aux.empty:
        return pd.DataFrame(columns=[coluna_grupo, "valor_medio", "total_participantes"])

    df_aux["valor_x_peso"] = df_aux[coluna_valor] * df_aux[coluna_peso]

    agrupado = (
        df_aux
        .groupby(coluna_grupo, observed=True, as_index=False)
        .agg(
            soma_valor=("valor_x_peso", "sum"),
            total_participantes=(coluna_peso, "sum")
        )
    )

    agrupado["valor_medio"] = agrupado["soma_valor"] / agrupado["total_participantes"]

    return agrupado[[coluna_grupo, "valor_medio", "total_participantes"]]


def calcular_percentual_ponderado(
    df: pd.DataFrame,
    grupo: str,
    categoria: str,
    weight_col: str = "participantes"
) -> pd.DataFrame:
    """
    Calcula percentuais ponderados para gráficos.
    """
    df_group = (
        df.groupby([grupo, categoria], observed=True, as_index=False)
        .agg({weight_col: "sum"})
    )

    df_group["perc"] = (
        df_group.groupby(grupo, observed=True)[weight_col]
        .transform(lambda x: x / x.sum() * 100)
    )

    return df_group


def calcular_notas_por_materia(
    df: pd.DataFrame,
    materias_cols: Dict[str, str],
    coluna_peso: str = "participantes"
) -> Dict[str, float]:
    """
    Calcula notas médias ponderadas por matéria.
    """
    return {
        materia: media_ponderada(df, coluna, coluna_peso)
        for materia, coluna in materias_cols.items()
    }


def melhor_pior_categoria(
    df: pd.DataFrame,
    coluna_categoria: str,
    coluna_valor: str = "nota_media",
    coluna_peso: str = "participantes"
) -> Tuple[str, float, str, float]:
    """
    Retorna:
    (melhor_categoria, melhor_valor, pior_categoria, pior_valor)
    com base em média ponderada.
    """
    colunas = {coluna_categoria, coluna_valor, coluna_peso}
    if df.empty or not colunas.issubset(df.columns):
        return "N/A", 0.0, "N/A", 0.0

    df_aux = df.copy()
    df_aux["valor_ponderado"] = df_aux[coluna_valor] * df_aux[coluna_peso]

    agrupado = (
        df_aux
        .groupby(coluna_categoria, observed=True)
        .agg(
            soma_valor=("valor_ponderado", "sum"),
            soma_peso=(coluna_peso, "sum")
        )
    )

    if agrupado.empty:
        return "N/A", 0.0, "N/A", 0.0

    agrupado["media"] = agrupado["soma_valor"] / agrupado["soma_peso"]

    melhor_categoria = agrupado["media"].idxmax()
    pior_categoria = agrupado["media"].idxmin()

    return (
        str(melhor_categoria),
        float(agrupado.loc[melhor_categoria, "media"]),
        str(pior_categoria),
        float(agrupado.loc[pior_categoria, "media"]),
    )


def criar_tabela_tridimensional_normalizada_ponderada(
    df: pd.DataFrame,
    linhas: List[str],
    coluna: str,
    weight_col: str = "participantes",
    categorias_coluna: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Cria tabela tridimensional com contagem ponderada e percentual.
    """
    if df.empty:
        return pd.DataFrame(columns=linhas + [coluna, weight_col, "Percentual"])

    colunas_necessarias = set(linhas + [coluna, weight_col])
    if not colunas_necessarias.issubset(df.columns):
        return pd.DataFrame(columns=linhas + [coluna, weight_col, "Percentual"])

    contagem = (
        df.groupby(linhas + [coluna], observed=False)
        .agg(soma_ponderada=(weight_col, "sum"))
    )

    valores_linhas = [df[c].dropna().unique() for c in linhas]

    if categorias_coluna is None:
        categorias_coluna = df[coluna].dropna().unique()

    from pandas import MultiIndex

    todos_os_grupos = MultiIndex.from_product(
        valores_linhas + [categorias_coluna],
        names=linhas + [coluna]
    )

    contagem = contagem.reindex(todos_os_grupos, fill_value=0).reset_index()

    totais = contagem.groupby(linhas, observed=False)["soma_ponderada"].transform("sum")

    contagem["Percentual"] = np.where(
        totais > 0,
        (contagem["soma_ponderada"] / totais * 100).round(2),
        0
    )

    contagem = contagem.rename(columns={"soma_ponderada": weight_col})

    return contagem[linhas + [coluna, weight_col, "Percentual"]]


# =============================================================================
# FUNÇÕES DE AGREGAÇÃO ESPECÍFICAS
# =============================================================================

def agregar_valor(
    df: pd.DataFrame,
    grupo: str,
    coluna_valor: str,
    weight_col: str = "participantes",
    metodo: str = "ponderado",  # "ponderado" ou "simples"
) -> pd.DataFrame:
    """
    Agrega valores por grupo de forma padronizada.

    Parameters
    ----------
    df : DataFrame
    grupo : str
        Coluna de agrupamento (ex: 'regiao', 'uf')
    coluna_valor : str
        Variável a ser agregada
    weight_col : str
        Coluna de peso
    metodo : str
        'ponderado' ou 'simples'

    Returns
    -------
    DataFrame com coluna 'valor_agregado'
    """

    if metodo == "ponderado" and weight_col in df.columns:
        df_ag = (
            df.groupby(grupo, observed=True)
            .apply(lambda g: media_ponderada(g, coluna_valor, weight_col))
            .reset_index(name="valor_agregado")
        )
    else:
        df_ag = (
            df.groupby(grupo, observed=True)[coluna_valor]
            .mean()
            .reset_index(name="valor_agregado")
        )

    return df_ag
    
def calcular_media_ponderada_por_responsavel(
    df: pd.DataFrame,
    col_pai: str,
    col_mae: str,
    coluna_valor: str,
    nome_eixo: str,
    weight_col: str = "participantes"
) -> pd.DataFrame:
    """
    Calcula média ponderada de uma variável por categoria,
    separando Pai e Mãe.
    """
    def agregar(df_base: pd.DataFrame, coluna_categoria: str, responsavel: str) -> pd.DataFrame:
        resultado = media_ponderada_por_grupo(
            df=df_base,
            coluna_grupo=coluna_categoria,
            coluna_valor=coluna_valor,
            coluna_peso=weight_col
        )

        if resultado.empty:
            return pd.DataFrame(columns=[nome_eixo, "valor_medio", "total_participantes", "Responsável"])

        resultado["Responsável"] = responsavel
        resultado = resultado.rename(columns={coluna_categoria: nome_eixo})

        return resultado[[nome_eixo, "valor_medio", "total_participantes", "Responsável"]]

    df_pai = agregar(df, col_pai, "Pai")
    df_mae = agregar(df, col_mae, "Mãe")

    return pd.concat([df_pai, df_mae], ignore_index=True)


def calcular_renda_media_por_categoria(
    df: pd.DataFrame,
    coluna_categoria: str,
    nome_eixo: str,
    responsavel: str,
    weight_col: str = "participantes"
) -> pd.DataFrame:
    """
    Calcula renda média ponderada por categoria e responsável.
    """
    resultado = media_ponderada_por_grupo(
        df=df,
        coluna_grupo=coluna_categoria,
        coluna_valor="renda_media",
        coluna_peso=weight_col
    )

    if resultado.empty:
        return pd.DataFrame(columns=[nome_eixo, "renda_media", "total_participantes", "Responsável"])

    resultado["Responsável"] = responsavel
    resultado = resultado.rename(
        columns={
            coluna_categoria: nome_eixo,
            "valor_medio": "renda_media"
        }
    )

    return resultado[[nome_eixo, "renda_media", "total_participantes", "Responsável"]]


# =============================================================================
# PREPARAÇÃO DE TABELAS PARA GRÁFICOS
# =============================================================================

def preparar_tabela_percentual(
    df: pd.DataFrame,
    eixo_x: str,
    eixo_cor: str,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    weight_col: str = "participantes",
    remover_nao_respondeu_escola: bool = True
) -> pd.DataFrame:
    """
    Prepara tabela percentual ponderada para gráficos de barras empilhadas.
    """
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        return pd.DataFrame(columns=[eixo_x, eixo_cor, weight_col, "perc"])

    for col in [eixo_x, eixo_cor]:
        if col in df_filtrado.columns:
            df_filtrado[col] = df_filtrado[col].astype(str).str.strip()

    if remover_nao_respondeu_escola:
        for col in [eixo_x, eixo_cor]:
            if col == "escola" and col in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    ~df_filtrado[col].str.lower().isin(["não respondeu", "não informada"])
                ]

    if df_filtrado.empty:
        return pd.DataFrame(columns=[eixo_x, eixo_cor, weight_col, "perc"])

    df_percentual = calcular_percentual_ponderado(
        df=df_filtrado,
        grupo=eixo_x,
        categoria=eixo_cor,
        weight_col=weight_col
    ).copy()

    ordem_x = obter_ordem_padrao(eixo_x)
    ordem_cor = obter_ordem_padrao(eixo_cor)

    if ordem_x is not None and eixo_x in df_percentual.columns:
        df_percentual[eixo_x] = pd.Categorical(
            df_percentual[eixo_x],
            categories=ordem_x,
            ordered=True
        )

    if ordem_cor is not None and eixo_cor in df_percentual.columns:
        df_percentual[eixo_cor] = pd.Categorical(
            df_percentual[eixo_cor],
            categories=ordem_cor,
            ordered=True
        )

    df_percentual = df_percentual.sort_values([eixo_x, eixo_cor])

    df_percentual = adicionar_colunas_hover_br(
        df_percentual,
        {
            "perc_fmt": ("perc", 1, "numero"),
            "participantes_fmt": (weight_col, 0, "numero")
        }
    )

    return df_percentual


def preparar_distribuicao_raca_renda(
    df: pd.DataFrame,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    weight_col: str = "participantes"
) -> pd.DataFrame:
    """
    Prepara a distribuição de renda dentro de cada grupo racial.
    """
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    colunas_necessarias = {"cor_raca", "sal_min", weight_col}
    if df_filtrado.empty or not colunas_necessarias.issubset(df_filtrado.columns):
        return pd.DataFrame(columns=["cor_raca", "sal_min", weight_col, "perc"])

    df_filtrado["cor_raca"] = df_filtrado["cor_raca"].astype(str).str.strip()
    df_filtrado["sal_min"] = df_filtrado["sal_min"].astype(str).str.strip()

    tabela = (
        df_filtrado
        .groupby(["cor_raca", "sal_min"], observed=True, as_index=False)[weight_col]
        .sum()
    )

    if tabela.empty:
        return pd.DataFrame(columns=["cor_raca", "sal_min", weight_col, "perc"])

    tabela["perc"] = (
        tabela.groupby("cor_raca", observed=True)[weight_col]
        .transform(lambda x: x / x.sum() * 100)
        .round(2)
    )

    ordem_raca = obter_ordem_padrao("cor_raca")
    ordem_renda = obter_ordem_padrao("sal_min")

    if ordem_raca is not None:
        tabela["cor_raca"] = pd.Categorical(
            tabela["cor_raca"],
            categories=ordem_raca,
            ordered=True
        )

    if ordem_renda is not None:
        tabela["sal_min"] = pd.Categorical(
            tabela["sal_min"],
            categories=ordem_renda,
            ordered=True
        )

    tabela = tabela.sort_values(["cor_raca", "sal_min"]).copy()

    tabela = adicionar_colunas_hover_br(
        tabela,
        {
            "perc_fmt": ("perc", 1, "numero"),
            "participantes_fmt": (weight_col, 0, "numero")
        }
    )

    return tabela


# =============================================================================
# OUTRAS AUXILIARES
# =============================================================================
def montar_titulo_tabela_gradiente(
    linha: str,
    coluna: str,
    valor: str,
    aggfunc: str = "mean",
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
) -> str:
    """
    Monta título automático para a tabela_plotly_gradiente em duas linhas.

    Regras
    ------
    - Linha 1: métrica + dimensões da tabela
    - Linha 2: escopo + filtro geográfico + ano
    - Se linha='ano', o ano já faz parte da tabela e não entra no sufixo.
    - Se o nome amigável do valor já contém 'média', evita duplicação.
    """

    nome_linha = NOMES_AMIGAVEIS.get(linha, linha.replace("_", " ").title())
    nome_coluna = NOMES_AMIGAVEIS.get(coluna, coluna.replace("_", " ").title())
    nome_valor = NOMES_AMIGAVEIS.get(valor, valor.replace("_", " ").title())

    if aggfunc == "mean":
        if "média" in nome_valor.lower() or "medio" in nome_valor.lower():
            metrica = nome_valor
        else:
            metrica = f"Média de {nome_valor}"
    elif aggfunc == "sum":
        metrica = f"Soma de {nome_valor}"
    elif aggfunc == "count":
        metrica = f"Contagem de {nome_valor}"
    elif aggfunc == "median":
        metrica = f"Mediana de {nome_valor}"
    else:
        metrica = f"{nome_valor} ({aggfunc})"

    titulo_linha_1 = f"{metrica} por {nome_coluna}"

    if linha != "ano":
        titulo_linha_1 += f" e {nome_linha}"

    titulo_linha_2 = obter_nome_escopo(escopo)
    complemento_geo = montar_complemento_filtro_geo(escopo, filtro_geo)

    if complemento_geo:
        titulo_linha_2 += complemento_geo

    if ano_selecionado is not None and linha != "ano":
        titulo_linha_2 += f" - {ano_selecionado}"

    return f"{titulo_linha_1}<br><sup>{titulo_linha_2}</sup>"
    
def quebrar_nome_meio(texto: str) -> str:
    """
    Quebra o texto em duas linhas no espaço mais próximo do meio.
    """
    if not texto or not isinstance(texto, str):
        return ""

    texto = texto.strip()

    if " " not in texto:
        return texto

    meio = len(texto) // 2
    espaco_esquerda = texto.rfind(" ", 0, meio)
    espaco_direita = texto.find(" ", meio)

    if espaco_esquerda == -1 and espaco_direita == -1:
        return texto

    if espaco_esquerda == -1:
        pos = espaco_direita
    elif espaco_direita == -1:
        pos = espaco_esquerda
    else:
        pos = espaco_esquerda if (meio - espaco_esquerda) <= (espaco_direita - meio) else espaco_direita

    return texto[:pos] + "<br>" + texto[pos + 1:]


def ajustar_eixo_zero(fig: go.Figure, df: pd.DataFrame, coluna: str, margem: float = 1.1) -> go.Figure:
    """
    Ajusta o eixo Y para começar em zero com margem superior.
    """
    valor_max = df[coluna].max()
    fig.update_yaxes(range=[0, valor_max * margem])
    return fig


def montar_indicador_escola(
    valor: float,
    nome_escola: str,
    cor: str,
    incluir_delta: bool = False,
    referencia_delta: float = 0.0,
    espacamento_extra_titulo: bool = False
) -> go.Indicator:
    """
    Cria indicador padronizado para escola com valor em formato BR.
    Ajustado para evitar sobreposição entre título do subplot e conteúdo do card.
    """
    nome_quebrado = quebrar_nome_meio(nome_escola)
    valor_fmt = formatar_decimal_br(valor, 1)
    
    espacamento_valor = "<br>"

    if espacamento_extra_titulo:
        estilo_extra = "margin-top: -8px"
        # Construção do título com controle de margem
        texto_titulo = (
            f"{espacamento_valor}"
            f"<b style='font-size:13px'>escola {nome_quebrado}</b>"
            f"<br><span style='font-size:18px; color:{cor}; {estilo_extra}'><b>{valor_fmt}</b></span>"
        )
       
    else:
        estilo_extra = ""
        # Construção do título com controle de margem
        texto_titulo = (
            f"<b style='font-size:13px'>escola {nome_quebrado}<br>"
            f"{espacamento_valor}"
            f"<span style='font-size:18px; color:{cor}; {estilo_extra}'><b>{valor_fmt}</b></span>"
            f"{espacamento_valor}"
        )
    
    if incluir_delta:
        delta_valor = valor - referencia_delta
        sinal = "+" if delta_valor > 0 else ""
        delta_fmt = f"{sinal}{formatar_decimal_br(delta_valor, 1)}"
        texto_titulo += (
            f"<br><span style='font-size:11px; color:gray; margin-top: -4px;'>Δ {delta_fmt}</span>"
        )
    
    indicador = {
        "mode": "number",
        "value": 0,
        "title": {
            "text": texto_titulo,
            "font": {"size": 13}
        },
        "number": {
            "font": {"size": 1, "color": "rgba(0,0,0,0)"}
        }
    }
    
    return go.Indicator(**indicador)

# =============================================================================
# FUNÇÕES DE GRÁFICOS - BARRAS PERCENTUAIS (GENÉRICAS)
# =============================================================================

def grafico_barras_percentual(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    categoria: str = "sal_min",
    nivel_geografico: str = "regiao",
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico de barras percentuais com cálculo ponderado por participantes.
    """

    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
            xref="paper", yref="paper"
        )
        return fig, pd.DataFrame()

    # ajuste automático do nível geográfico se necessário
    if nivel_geografico not in df_filtrado.columns:
        if escopo == "br" and "uf" in df_filtrado.columns:
            nivel_geografico = "uf"
        elif escopo == "mg" and "regiao" in df_filtrado.columns:
            nivel_geografico = "regiao"
        elif escopo == "caxambu" and "municipio" in df_filtrado.columns:
            nivel_geografico = "municipio"
        elif escopo == "caxambu" and "cidade" in df_filtrado.columns:
            nivel_geografico = "cidade"
        else:
            raise ValueError(f"A coluna geográfica '{nivel_geografico}' não está disponível.")

    colunas_necessarias = {nivel_geografico, categoria, weight_col}
    faltantes = colunas_necessarias - set(df_filtrado.columns)
    if faltantes:
        raise KeyError(f"Colunas ausentes no DataFrame: {sorted(faltantes)}")

    ordem_categoria = obter_ordem_padrao(categoria)
    mapa_cores = obter_mapa_cores(categoria)

    nome_categoria = NOMES_AMIGAVEIS.get(
        categoria,
        categoria.replace("_", " ").title()
    )

    df_percentual = calcular_percentual_ponderado(
        df_filtrado,
        grupo=nivel_geografico,
        categoria=categoria,
        weight_col=weight_col
    )

    if df_percentual.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem resultados após agregação",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    if titulo is None:
        escopo_nome = obter_nome_escopo(escopo)
        titulo = f"{nome_categoria}"
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"

    rotulo_geo = obter_rotulo_geo(escopo)

    df_percentual = adicionar_colunas_hover_br(
        df_percentual,
        {
            "participantes_fmt": (weight_col, 0, "numero"),
            "perc_fmt": ("perc", 1, "decimal")
        }
    )

    textos_formatados = (df_percentual["perc_fmt"] + "%").tolist()

    fig = px.bar(
        df_percentual,
        x=nivel_geografico,
        y="perc",
        color=categoria,
        title=titulo,
        category_orders={categoria: ordem_categoria} if ordem_categoria else None,
        color_discrete_map=mapa_cores,
        color_discrete_sequence=SEQUENCIA_CORES if mapa_cores is None else None,
        labels={
            nivel_geografico: rotulo_geo,
            "perc": "Porcentagem (%)",
            categoria: nome_categoria
        },
        text=textos_formatados,
        custom_data=["participantes_fmt", "perc_fmt"]
    )

    fig.update_layout(
        height=400,
        barmode="stack",
        title=dict(x=0.5, 
                   y=0.95, 
                   xanchor="center",
                   font=dict(size=18)
                  ),
        showlegend=True,
        legend=dict(
            title=nome_categoria,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        margin=dict(t=100),
        separators=".,"
    )

    fig = aplicar_texto_negrito_plotly(
        fig,
        textposition="inside",
        textfont_size=11,
        texttemplate="%{text}"
    )

    fig.update_traces(
        hovertemplate=(
            f"<b>{rotulo_geo}:</b> %{{x}}<br>"
            f"<b>{nome_categoria}:</b> %{{fullData.name}}<br>"
            "<b>Percentual:</b> %{customdata[1]}%<br>"
            "<b>Participantes:</b> %{customdata[0]}<br>"
            "<extra></extra>"
        )
    )

    return fig, df_percentual
# =============================================================================
# FUNÇÕES DE GRÁFICOS - COMPOSIÇÃO ANUAL
# =============================================================================

def grafico_composicao_anual(df: pd.DataFrame, categoria: str = 'sal_min',
                               escola_selecionada: Optional[str] = None,
                               titulo: Optional[str] = None,
                               legenda: Optional[str] = None,
                               escopo: str = 'mg',
                               weight_col: str = 'participantes') -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico de composição anual (barras empilhadas por ano)
    """
    # Filtrar por escopo
    df_filtrado = filtrar_por_escopo(df, escopo)
    
    # Filtrar por escola
    if escola_selecionada and escola_selecionada != "Todas" and 'escola' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["escola"] == escola_selecionada]
    
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado encontrado",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    # Garantir que ano seja string
    if 'ano' in df_filtrado.columns:
        df_filtrado['ano'] = df_filtrado['ano'].astype(str)
    
    # Determinar ordem e cores
    ordem_categoria = obter_ordem_padrao(categoria)
    mapa_cores = obter_mapa_cores(categoria)
    
    # Calcular composição ponderada
    composicao = df_filtrado.groupby(['ano', categoria], observed=True, as_index=False).agg({
        weight_col: 'sum'
    })
    composicao = composicao.rename(columns={weight_col: 'count'})
    
    # Calcular totais e percentuais
    total_por_ano = composicao.groupby('ano', observed=True)['count'].sum().reset_index(name='total_ano')
    composicao = pd.merge(composicao, total_por_ano, on='ano', how='left')
    composicao['percentual'] = (composicao['count'] / composicao['total_ano'] * 100).round(1)
    
    # Ordenar categorias
    if ordem_categoria:
        composicao[categoria] = pd.Categorical(composicao[categoria], categories=ordem_categoria, ordered=True)
    composicao = composicao.sort_values(['ano', categoria])
    
    nome_categoria = NOMES_AMIGAVEIS.get(categoria, categoria.replace('_', ' ').title())
    
    # Título
    if titulo is None:
        escopo_nome = {
            'br': 'Brasil',
            'mg': 'Minas Gerais',
            'caxambu': 'Caxambu'
        }.get(escopo, escopo.upper())
        
        titulo = f"Composição de {nome_categoria} por Ano - {escopo_nome}"
        if escola_selecionada and escola_selecionada != "Todas":
            titulo += f" (Escola {escola_selecionada})"
    
    # Criar gráfico
    fig = px.bar(
        composicao,
        x='ano',
        y='percentual',
        color=categoria,
        title=titulo,
        text='percentual',
        color_discrete_map=mapa_cores,
        color_discrete_sequence=SEQUENCIA_CORES if mapa_cores is None else None,
        barmode='stack',
        category_orders={categoria: ordem_categoria} if ordem_categoria else None,
        hover_data=['count']
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside',
        textfont=dict(color='white', size=10),
        hovertemplate=(
            '📅 <b>Ano:</b> %{x}<br>'
            f'🏷️ <b>{nome_categoria}:</b> %{{fullData.name}}<br>'
            '📊 <b>Percentual:</b> %{y:.1f}%<br>'
            '👥 <b>Participantes:</b> %{customdata[0]:,}<br>'
            '<extra></extra>'
        )
    )
    
    fig.update_layout(
        xaxis_title='Ano',
        yaxis_title='Percentual (%)',
        title=dict(x=0.5, y=0.95, font=dict(size=18)),
        showlegend=True,
        legend=dict(
            title=legenda or nome_categoria,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        template='plotly_white',
        margin=dict(t=100)
    )
    
    return fig, composicao


# =============================================================================
# FUNÇÕES DE GRÁFICOS - COMPARATIVO PAIS (ESCOLARIDADE/OCUPAÇÃO)
# =============================================================================

def grafico_comparativo_pais(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    filtro_cor_raca: Optional[str] = None,
    filtro_escola: Optional[str] = None,
    nivel_geografico: str = 'regiao',
    tipo: str = 'escolaridade',
    titulo: Optional[str] = None,
    escopo: str = 'mg',
    weight_col: str = 'participantes'
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Cria gráfico comparativo (Pai x Mãe) da distribuição percentual ponderada
    de escolaridade ou ocupação, com gráficos empilhados verticalmente.

    Filtros adicionais:
    - filtro_cor_raca
    - filtro_escola
    """

    # ---------------------------------------------------------------------
    # 1. CONFIGURAÇÃO DO TIPO
    # ---------------------------------------------------------------------
    if tipo == 'escolaridade':
        var_pai = 'escolaridade_pai'
        var_mae = 'escolaridade_mae'
        titulo_variavel = 'Escolaridade'
        ordem_categoria = ORDEM_PAIS_ESCOLARIDADE
        nome_categoria = 'Escolaridade'
    elif tipo == 'ocupacao':
        var_pai = 'ocup_pai'
        var_mae = 'ocup_mae'
        titulo_variavel = 'Ocupação'
        ordem_categoria = ORDEM_OCUPACAO
        nome_categoria = 'Ocupação'
    else:
        raise ValueError("tipo deve ser 'escolaridade' ou 'ocupacao'")

    # ---------------------------------------------------------------------
    # 2. FILTROS
    # ---------------------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    # filtro adicional por cor/raça
    if filtro_cor_raca is not None and "cor_raca" in df_filtrado.columns:
        df_filtrado["cor_raca"] = df_filtrado["cor_raca"].astype(str).str.strip()
        df_filtrado = df_filtrado[df_filtrado["cor_raca"] == str(filtro_cor_raca).strip()]

    # filtro adicional por escola
    if filtro_escola is not None and "escola" in df_filtrado.columns:
        df_filtrado["escola"] = df_filtrado["escola"].astype(str).str.strip()
        df_filtrado = df_filtrado[df_filtrado["escola"] == str(filtro_escola).strip()]

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
            xref="paper", yref="paper"
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------------------
    # 3. AJUSTAR NÍVEL GEOGRÁFICO QUANDO NECESSÁRIO
    # ---------------------------------------------------------------------
    if nivel_geografico not in df_filtrado.columns:
        if escopo == "br" and "uf" in df_filtrado.columns:
            nivel_geografico = "uf"
        elif escopo == "mg" and "regiao" in df_filtrado.columns:
            nivel_geografico = "regiao"
        elif "uf" in df_filtrado.columns:
            nivel_geografico = "uf"
        else:
            raise ValueError(f"A coluna '{nivel_geografico}' não está disponível no DataFrame.")

    # ---------------------------------------------------------------------
    # 4. CÁLCULO DAS DISTRIBUIÇÕES PONDERADAS
    # ---------------------------------------------------------------------
    df_pai = calcular_percentual_ponderado(
        df_filtrado,
        grupo=nivel_geografico,
        categoria=var_pai,
        weight_col=weight_col
    ).copy()
    df_pai["Responsável"] = "Pai"
    df_pai = df_pai.rename(columns={var_pai: "Categoria", weight_col: "participantes_ponderados"})

    df_mae = calcular_percentual_ponderado(
        df_filtrado,
        grupo=nivel_geografico,
        categoria=var_mae,
        weight_col=weight_col
    ).copy()
    df_mae["Responsável"] = "Mãe"
    df_mae = df_mae.rename(columns={var_mae: "Categoria", weight_col: "participantes_ponderados"})

    df_comparativo = pd.concat([df_pai, df_mae], ignore_index=True)

    if ordem_categoria:
        df_comparativo["Categoria"] = pd.Categorical(
            df_comparativo["Categoria"],
            categories=ordem_categoria,
            ordered=True
        )
        df_comparativo = df_comparativo.sort_values(["Responsável", "Categoria"])
        
    df_comparativo["participantes_fmt"] = df_comparativo["participantes_ponderados"].apply(
        lambda x: formatar_numero_br(x, 0)
    )
    df_comparativo["perc_fmt"] = df_comparativo["perc"].apply(
        lambda x: formatar_decimal_br(x, 1)
    )

    # ---------------------------------------------------------------------
    # 5. CORES
    # ---------------------------------------------------------------------
    mapa_cores = obter_mapa_cores(tipo)

    if mapa_cores is None:
        cores_disponiveis = SEQUENCIA_CORES.copy()
        mapa_cores = {}
        categorias_ref = ordem_categoria if ordem_categoria else df_comparativo["Categoria"].dropna().unique()
        for i, cat in enumerate(categorias_ref):
            mapa_cores[cat] = cores_disponiveis[i % len(cores_disponiveis)]

    # ---------------------------------------------------------------------
    # 6. TÍTULO
    # ---------------------------------------------------------------------
    if titulo is None:
        titulo = f"{titulo_variavel} dos Pais"# - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)

        if filtro_cor_raca:
            titulo += f" | Raça/Cor: {filtro_cor_raca}"

        if filtro_escola:
            titulo += f" | Escola: {filtro_escola}"

        if ano_selecionado:
            titulo += f" - {ano_selecionado}"

    rotulo_geo = obter_rotulo_geo(escopo)

    # ---------------------------------------------------------------------
    # 7. DADOS PARA CADA SUBPLOT
    # ---------------------------------------------------------------------
    df_pai_plot = df_comparativo[df_comparativo["Responsável"] == "Pai"].copy()
    df_mae_plot = df_comparativo[df_comparativo["Responsável"] == "Mãe"].copy()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Pai", "Mãe"),
        vertical_spacing=0.15,
        shared_xaxes=True,
        x_title=""
    )

    def adicionar_barras_subplot(
        fig_obj: go.Figure,
        df_plot: pd.DataFrame,
        row: int,
        showlegend: bool
    ) -> None:
        categorias_ref = ordem_categoria if ordem_categoria else df_plot["Categoria"].dropna().unique()

        for categoria_atual in categorias_ref:
            df_cat = df_plot[df_plot["Categoria"] == categoria_atual].copy()
            if df_cat.empty:
                continue

            cor = mapa_cores.get(categoria_atual, SEQUENCIA_CORES[0])

             # Textos formatados
            textos = (df_cat["perc"].apply(lambda x: formatar_decimal_br(x, 1) + "%")).tolist()

            fig_obj.add_trace(
                go.Bar(
                    x=df_cat[nivel_geografico],
                    y=df_cat["perc"],
                    name=str(categoria_atual),
                    marker_color=cor,
                    text=textos,
                    textposition="inside",
                    textfont=dict(
                        family="Arial Bold, Arial, sans-serif",
                        size=11
                        
                    ),
                    legendgroup=str(categoria_atual),
                    showlegend=showlegend,
                    customdata=df_cat[["participantes_fmt", "perc_fmt"]].values,
                    hovertemplate=(
                        f"<b>{rotulo_geo}:</b> %{{x}}<br>"
                        f"<b>{nome_categoria}:</b> {categoria_atual}<br>"
                        "<b>Percentual:</b> %{customdata[1]}%<br>"
                        "<b>Participantes:</b> %{customdata[0]}<br>"
                        "<extra></extra>"
                    )
                ),
                row=row, col=1
            )

    adicionar_barras_subplot(fig, df_pai_plot, row=1, showlegend=True)
    adicionar_barras_subplot(fig, df_mae_plot, row=2, showlegend=False)

    # ---------------------------------------------------------------------
    # 8. LAYOUT
    # ---------------------------------------------------------------------
    fig.update_layout(
        height=700,
        title=dict(
            text=titulo,
            x=0.5,
            y=0.98,
            xanchor="center",
            font=dict(size=18, family="Arial", color="#2C3E50")  # Mantendo original
        ),
        barmode="stack",
        legend=dict(
            title=dict(text=nome_categoria, font=dict(size=12)),
            orientation="h",
            yanchor="top",
            y=1.14,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            
        ),
        template="plotly_white",
        margin=dict(t=100, b=120, l=80, r=40),
        separators=",."
    )
    
    fig.add_annotation(
        x=-0.07,
        y=0.5,
        xref="paper",
        yref="paper",
        text="Percentual (%)",
        showarrow=False,
        textangle=-90,
        font=dict(size=14, color="#2C3E50"),
        xanchor="center",
        yanchor="middle"
    )

    fig.update_xaxes(title_text="", tickangle=45, row=1, col=1)
    fig.update_xaxes(title_text="", tickangle=45, row=2, col=1)

    for i, annotation in enumerate(fig.layout.annotations):
        if i == 0:
            annotation.update(
                y=1.02,
                font=dict(size=14, color="#2C3E50")
            )
        elif i == 1:
            annotation.update(
                y=0.48,
                font=dict(size=14, color="#2C3E50")
            )

    return fig, df_comparativo    

# =============================================================================
# FUNÇÕES DE GRÁFICOS - COMPARATIVO ESCOLA PRIVADA POR ESCOLARIDADE
# =============================================================================

def grafico_comparativo_escola_privada_pais(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    ymax: int = 100,
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico comparativo de escolaridade dos pais para escola privada.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com os dados
    ano_selecionado : str, optional
        Ano para filtrar
    filtro_geo : str, optional
        Para escopo='br': UF específica (ex: 'MG', 'SP')
        Para escopo='mg': região específica (ex: 'Sul de Minas')
    titulo : str, optional
        Título personalizado
    escopo : str
        'br', 'mg' ou 'caxambu'
    ymax : int
        Valor máximo do eixo Y
    weight_col : str
        Coluna de pesos
    
    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Gráfico e DataFrame com os dados
    """
    # ---------------------------------------------------------------------
    # 1. FILTRAGEM
    # ---------------------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    )

    if "escola" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["escola"].isin(["pública", "privada"])]

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
            xref="paper", yref="paper"
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------------------
    # 2. TABELAS PAI / MÃE
    # ---------------------------------------------------------------------
    tabela_pai = criar_tabela_tridimensional_normalizada_ponderada(
        df_filtrado,
        linhas=["sal_min", "escolaridade_pai"],
        coluna="escola",
        weight_col=weight_col
    )
    tabela_pai = tabela_pai[tabela_pai["escola"] == "privada"].copy()
    tabela_pai["parente"] = "Pai"
    tabela_pai = tabela_pai.rename(columns={"escolaridade_pai": "escolaridade"})

    tabela_mae = criar_tabela_tridimensional_normalizada_ponderada(
        df_filtrado,
        linhas=["sal_min", "escolaridade_mae"],
        coluna="escola",
        weight_col=weight_col
    )
    tabela_mae = tabela_mae[tabela_mae["escola"] == "privada"].copy()
    tabela_mae["parente"] = "Mãe"
    tabela_mae = tabela_mae.rename(columns={"escolaridade_mae": "escolaridade"})

    tabela_comparativo = pd.concat([tabela_pai, tabela_mae], ignore_index=True)

    if tabela_comparativo.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis após agregação",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
            xref="paper", yref="paper"
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------------------
    # 3. ORDENAÇÃO
    # ---------------------------------------------------------------------
    ordem_escolaridade = obter_ordem_padrao("escolaridade_pai") or ORDEM_PAIS_ESCOLARIDADE
    ordem_renda = obter_ordem_padrao("sal_min") or ORDEM_SAL_MIN

    tabela_comparativo["escolaridade"] = pd.Categorical(
        tabela_comparativo["escolaridade"],
        categories=ordem_escolaridade,
        ordered=True
    )
    tabela_comparativo["sal_min"] = pd.Categorical(
        tabela_comparativo["sal_min"],
        categories=ordem_renda,
        ordered=True
    )

    tabela_comparativo = tabela_comparativo.sort_values(
        ["sal_min", "escolaridade", "parente"]
    )

    # ---------------------------------------------------------------------
    # 4. COLUNAS FORMATADAS PARA HOVER
    # ---------------------------------------------------------------------
    tabela_comparativo["participantes_fmt"] = tabela_comparativo[weight_col].apply(
        lambda x: formatar_numero_br(x, 0)
    )
    tabela_comparativo["percentual_fmt"] = tabela_comparativo["Percentual"].apply(
        lambda x: formatar_numero_br(x, 1)
    )

    # ---------------------------------------------------------------------
    # 5. TÍTULO
    # ---------------------------------------------------------------------
    if titulo is None:
        titulo = f"Percentual em Escola Privada <br> por Renda e Escolaridade dos Pais - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" - {ano_selecionado}"

    # ---------------------------------------------------------------------
    # 6. GRÁFICO
    # ---------------------------------------------------------------------
    cores = {"Pai": SEQUENCIA_CORES[0], "Mãe": SEQUENCIA_CORES[1]}

    fig = px.bar(
        tabela_comparativo,
        x="sal_min",
        y="Percentual",
        color="parente",
        facet_col="escolaridade",
        facet_col_wrap=3,
        facet_row_spacing=0.08,
        barmode="group",
        title=titulo,
        labels={
            "escolaridade": "Escolaridade",
            "Percentual": "% em Escola Privada",
            "sal_min": "Renda Mensal (salários mínimos)",
            "parente": "Parente"
        },
        color_discrete_map=cores,
        category_orders={
            "escolaridade": ordem_escolaridade,
            "sal_min": ordem_renda
        },
        custom_data=["escolaridade", "parente", "participantes_fmt", "percentual_fmt"],
        text=None
    )

    # ---------------------------------------------------------------------
    # 7. FORMATAÇÃO
    # ---------------------------------------------------------------------
    fig.update_traces(
        text=None,
        textposition="none",
        hovertemplate=(
            "<b>Renda:</b> %{x}<br>"
            "<b>Escolaridade:</b> %{customdata[0]}<br>"
            "<b>Parente:</b> %{customdata[1]}<br>"
            "<b>Percentual:</b> %{customdata[3]}%<br>"
            "<b>Participantes:</b> %{customdata[2]}<br>"
            "<extra></extra>"
        )
    )

    fig.update_yaxes(range=[0, ymax])
    fig.for_each_xaxis(lambda x: x.update(tickangle=45))
    fig.for_each_yaxis(lambda axis: axis.update(title=""))
    fig.for_each_xaxis(lambda axis: axis.update(title=""))

    fig.add_annotation(
        x=-0.05,
        y=0.5,
        xref="paper",
        yref="paper",
        text="% em Escola Privada",
        showarrow=False,
        textangle=-90,
        font=dict(size=14, color="#2C3E50"),
        xanchor="center",
        yanchor="middle"
    )

    fig.add_annotation(
        x=0.5,
        y=-0.2,
        xref="paper",
        yref="paper",
        text="Renda Mensal Familiar (salários mínimos)",
        showarrow=False,
        font=dict(size=14, color="#2C3E50"),
        xanchor="center",
        yanchor="top"
    )

    for annotation in fig.layout.annotations:
        if "escolaridade=" in annotation.text.lower():
            partes = annotation.text.split("=")
            if len(partes) > 1:
                valor_escolaridade = partes[1].strip()
                annotation.text = f"Escolaridade: {valor_escolaridade}"
                annotation.font.size = 12
                annotation.y += 0.02

    fig.update_layout(
        height=500,
        width=700,
        title=dict(
            text=titulo,
            x=0.5,
            y=0.91,
            xanchor="center",
            font=dict(size=18, family="Arial", color="#2C3E50")
        ),
        template="plotly_white",
        margin=dict(t=100, b=100, l=80, r=40),
        separators=",."
    )

    return fig, tabela_comparativo

# =============================================================================
# FUNÇÕES DE GRÁFICOS - RENDA MÉDIA POR OCUPAÇÃO/ESCOLARIDADE
# =============================================================================

def grafico_renda_responsavel(
    df: pd.DataFrame,
    variavel: str = "ocupacao",   # 'ocupacao' ou 'escolaridade'
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico de renda média ponderada por ocupação ou escolaridade
    dos pais/responsáveis.
    """

    configuracoes = {
        "ocupacao": {
            "col_pai": "ocup_pai",
            "col_mae": "ocup_mae",
            "nome_eixo": "Ocupação",
            "ordem": ORDEM_OCUPACAO,
            "titulo_base": "Renda Média <br>por Ocupação dos Pais"
        },
        "escolaridade": {
            "col_pai": "escolaridade_pai",
            "col_mae": "escolaridade_mae",
            "nome_eixo": "Escolaridade",
            "ordem": ORDEM_PAIS_ESCOLARIDADE,
            "titulo_base": "Renda Média por Escolaridade dos Pais"
        }
    }

    if variavel not in configuracoes:
        raise ValueError("variavel deve ser 'ocupacao' ou 'escolaridade'")

    cfg = configuracoes[variavel]

    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    )

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    df_combinado = calcular_media_ponderada_por_responsavel(
        df=df_filtrado,
        col_pai=cfg["col_pai"],
        col_mae=cfg["col_mae"],
        coluna_valor="renda_media",
        nome_eixo=cfg["nome_eixo"],
        weight_col=weight_col
    )

    if df_combinado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis após agregação",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    df_combinado[cfg["nome_eixo"]] = pd.Categorical(
        df_combinado[cfg["nome_eixo"]],
        categories=cfg["ordem"],
        ordered=True
    )
    df_combinado = df_combinado.sort_values([cfg["nome_eixo"], "Responsável"])

    df_combinado = adicionar_colunas_formatadas_hover(
        df_combinado,
        coluna_valor="valor_medio",
        coluna_participantes="total_participantes"
    )

    if titulo is None:
        titulo = f"{cfg['titulo_base']}"#- {obter_nome_escopo(escopo)}"
        #titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" - {ano_selecionado}"
        
    df_combinado["texto_barra"] = df_combinado["valor_medio"].apply(
        lambda x: formatar_decimal_br(x, 2)
    )        
    fig = px.bar(
        df_combinado,
        x=cfg["nome_eixo"],
        y="valor_medio",
        color="Responsável",
        barmode="group",
        title=titulo,
        color_discrete_sequence=[SEQUENCIA_CORES[0], SEQUENCIA_CORES[1]],
        labels={"valor_medio": "Renda Média (salários mínimos)"},
        custom_data=["Responsável", "valor_fmt", "participantes_fmt"],
        text=df_combinado["texto_barra"].tolist()
    )

    # Aplicar negrito nas barras
    fig.update_traces(
        textposition="inside",
        textangle=-90,
        textfont=dict(
            family="Arial Bold, Arial, sans-serif",
            size=11
            # Sem cor definida - Plotly escolhe automaticamente
        ),
        insidetextanchor="middle",
        hovertemplate=(
            f"<b>{cfg['nome_eixo']}:</b> %{{x}}<br>"
            "<b>Responsável:</b> %{customdata[0]}<br>"
            "<b>Renda Média:</b> %{customdata[1]} salários mínimos<br>"
            "<b>Participantes:</b> %{customdata[2]}<br>"
            "<extra></extra>"
        )
    )

    # Layout com título original
    fig.update_layout(
       
        title=dict(
            x=0.5, 
            y=0.97,
            xanchor="center",
            font=dict(size=18)),
        xaxis_title=cfg["nome_eixo"],
        yaxis=dict(
            title="Renda Média (salários mínimos)",
            visible=False,
        ),
        legend=dict(
            title="Responsável",
            orientation="h",
            yanchor="bottom",
            xanchor="center",
            y=0.9,
            x=0.5,
            font=dict(size=11)
        ),
        margin=dict(t=100),
        separators=",.",
        
    )

    return fig, df_combinado

#=============================================================================
# FUNÇÕES DE GRÁFICOS COLUNAS PERCENTUAIS
# ===============================================================================
def grafico_coluna_empilhada_percentual(
    df: pd.DataFrame,
    eixo_x: str,
    eixo_cor: str,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes",
    label_x: Optional[str] = None,
    label_cor: Optional[str] = None,
    nome_legenda: Optional[str] = None,
    remover_nao_respondeu_escola: bool = True
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Cria gráfico de colunas empilhadas com percentuais ponderados.
    """

    tabela = preparar_tabela_percentual(
        df=df,
        eixo_x=eixo_x,
        eixo_cor=eixo_cor,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo,
        weight_col=weight_col,
        remover_nao_respondeu_escola=remover_nao_respondeu_escola
    )

    if tabela.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
            xref="paper", yref="paper"
        )
        return fig, pd.DataFrame()

    ordem_x = obter_ordem_padrao(eixo_x)
    ordem_cor = obter_ordem_padrao(eixo_cor)
    mapa_cores = obter_mapa_cores(eixo_cor)

    nome_x = label_x or NOMES_AMIGAVEIS.get(eixo_x, eixo_x.replace("_", " ").title())
    nome_cor = label_cor or NOMES_AMIGAVEIS.get(eixo_cor, eixo_cor.replace("_", " ").title())

    if titulo is None:
        titulo = f"Distribuição de {nome_cor}<br> por {nome_x} - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" - {ano_selecionado}"

    fig = px.bar(
        tabela,
        x=eixo_x,
        y="perc",
        color=eixo_cor,
        title=titulo,
        labels={
            eixo_x: nome_x,
            "perc": "Percentual (%)",
            eixo_cor: nome_cor
        },
        category_orders={
            eixo_x: ordem_x,
            eixo_cor: ordem_cor
        },
        color_discrete_map=mapa_cores,
        color_discrete_sequence=SEQUENCIA_CORES if mapa_cores is None else None,
        text="perc_fmt",
        custom_data=["participantes_fmt"]
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="inside",
        textfont=dict(color="white", size=10),
        hovertemplate=(
            f"<b>{nome_x}:</b> %{{x}}<br>"
            f"<b>{nome_cor}:</b> %{{fullData.name}}<br>"
            "<b>Percentual:</b> %{y:.1f}%<br>"
            "<b>Participantes:</b> %{customdata[0]}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title=nome_x,
        yaxis_title="Percentual (%)",
        legend_title=nome_legenda or nome_cor,
        height=350,
        title=dict(
            x=0.5,
            y=0.94,
            xanchor="center",
            font=dict(size=18)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        #margin=dict(t=150),
        separators=",."
    )

    # eixo começando em 0
    fig.update_yaxes(range=[0, 100])

    return fig, tabela

#=============================================================================
# FUNÇÕES DE GRÁFICOS HORIZONTAIS
# ===============================================================================

def grafico_raca_por_renda_barras(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico de barras horizontais empilhadas mostrando
    como cada grupo racial se distribui entre as faixas de renda.

    Cada linha (raça) soma 100%.
    """

    tabela = preparar_distribuicao_raca_renda(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo,
        weight_col=weight_col
    )

    if tabela.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    if titulo is None:
        titulo_linha_1 = "Distribuição de Renda por Cor/Raça"

        titulo_linha_2 = obter_nome_escopo(escopo)
        complemento_geo = montar_complemento_filtro_geo(escopo, filtro_geo)

        if complemento_geo:
            titulo_linha_2 += complemento_geo

        if ano_selecionado:
            titulo_linha_2 += f" - {ano_selecionado}"

        titulo = f"{titulo_linha_1}<br><sup>{titulo_linha_2}</sup>"

    mapa_cores = obter_mapa_cores("sal_min")

    fig = px.bar(
        tabela,
        y="cor_raca",
        x="perc",
        color="sal_min",
        orientation="h",
        title=titulo,
        labels={
            "cor_raca": "Raça/Cor",
            "perc": "Percentual (%)",
            "sal_min": "Faixa de Renda"
        },
        category_orders={
            "cor_raca": obter_ordem_padrao("cor_raca"),
            "sal_min": obter_ordem_padrao("sal_min")
        },
        color_discrete_map=mapa_cores,
        color_discrete_sequence=SEQUENCIA_CORES if mapa_cores is None else None,
        text="perc_fmt",
        custom_data=["participantes_fmt", "perc_fmt"]
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="inside",
        textfont=dict(
            family="Arial Bold, Arial, sans-serif",
            size=11
        ),
        hovertemplate=(
            "<b>Raça/Cor:</b> %{y}<br>"
            "<b>Faixa de renda:</b> %{fullData.name}<br>"
            "<b>Percentual:</b> %{customdata[1]}%<br>"
            "<b>Participantes:</b> %{customdata[0]}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(
            x=0.5, 
            y=0.9,
            xanchor="center",
            font=dict(size=18)),
        xaxis_title="Percentual (%)",
        yaxis_title="Raça/Cor",
        legend_title="Faixa de Renda",
        #template="plotly_white",
        separators=".,",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.95,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
    )

    fig.update_xaxes(range=[0, 100])

    return fig, tabela

#=============================================================================
# FUNÇÕES DE TABELAS
# ===============================================================================
def tabela_plotly_gradiente(
    df: pd.DataFrame,
    linha: str,
    coluna: str,
    valor: str,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    aggfunc: str = "mean",
    cmap: str = "RdYlGn",
    weight_col: str = "participantes",
    incluir_total_linha: bool = False,
    incluir_total_coluna: bool = False,
    casas_decimais: int = 1
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Cria uma tabela com gradiente de cores baseada em agregação.
    Para aggfunc='mean', usa média ponderada por participantes.
    """

    # ---------------------------------------------------------
    # Aplicar filtros do dashboard
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    colunas_validas = {"sexo", "cor_raca", "escola"}
    
    if coluna is None:
        coluna = "cor_raca"
    else:
        coluna = coluna.strip().lower()
        if coluna not in colunas_validas:
            coluna = "cor_raca"

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados para os filtros selecionados",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title=dict(text=titulo, x=0.5, font=dict(size=16)),
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # Validações
    # ---------------------------------------------------------
    colunas_necessarias = {linha, coluna, valor}
    if aggfunc == "mean":
        colunas_necessarias.add(weight_col)

    faltantes = colunas_necessarias - set(df_filtrado.columns)
    if faltantes:
        raise KeyError(f"Colunas ausentes no DataFrame: {sorted(faltantes)}")

    # ---------------------------------------------------------
    # Padronizar categorias
    # ---------------------------------------------------------
    for col in [linha, coluna]:
        if col in df_filtrado.columns:
            df_filtrado[col] = df_filtrado[col].astype(str).str.strip()

    # ---------------------------------------------------------
    # Criar tabela base
    # ---------------------------------------------------------
    tabela_pesos = None

    if aggfunc == "mean":
        df_temp = df_filtrado.copy()
        df_temp[valor] = pd.to_numeric(df_temp[valor], errors="coerce")
        df_temp[weight_col] = pd.to_numeric(df_temp[weight_col], errors="coerce")

        df_temp = df_temp.dropna(subset=[valor, weight_col])
        df_temp = df_temp[df_temp[weight_col] > 0]

        df_temp["valor_x_peso"] = df_temp[valor] * df_temp[weight_col]

        tabela_valores = pd.crosstab(
            index=df_temp[linha],
            columns=df_temp[coluna],
            values=df_temp["valor_x_peso"],
            aggfunc="sum",
            dropna=False
        )

        tabela_pesos = pd.crosstab(
            index=df_temp[linha],
            columns=df_temp[coluna],
            values=df_temp[weight_col],
            aggfunc="sum",
            dropna=False
        )

        tabela = tabela_valores / tabela_pesos.replace(0, np.nan)

    else:
        tabela = pd.crosstab(
            index=df_filtrado[linha],
            columns=df_filtrado[coluna],
            values=df_filtrado[valor],
            aggfunc=aggfunc,
            dropna=False
        )

    tabela = tabela.fillna(0)

    # ---------------------------------------------------------
    # Aplicar ordem das categorias
    # ---------------------------------------------------------
    ordem_linha = obter_ordem_padrao(linha)
    ordem_coluna = obter_ordem_padrao(coluna)

    if ordem_linha is not None:
        categorias_existentes = [cat for cat in ordem_linha if cat in tabela.index]
        if categorias_existentes:
            tabela = tabela.loc[categorias_existentes]
            if tabela_pesos is not None:
                tabela_pesos = tabela_pesos.loc[categorias_existentes]

    if ordem_coluna is not None:
        categorias_existentes = [cat for cat in ordem_coluna if cat in tabela.columns]
        if categorias_existentes:
            tabela = tabela[categorias_existentes]
            if tabela_pesos is not None:
                tabela_pesos = tabela_pesos[categorias_existentes]

    # ---------------------------------------------------------
    # Adicionar totais
    # ---------------------------------------------------------
    if aggfunc == "mean" and tabela_pesos is not None:
        if incluir_total_linha:
            soma_valores_linha = (tabela * tabela_pesos).sum(axis=1)
            soma_pesos_linha = tabela_pesos.sum(axis=1).replace(0, np.nan)
            tabela["Total"] = (soma_valores_linha / soma_pesos_linha).fillna(0)

        if incluir_total_coluna:
            soma_valores_coluna = (tabela.iloc[:, :-1] * tabela_pesos).sum(axis=0) if incluir_total_linha else (tabela * tabela_pesos).sum(axis=0)
            soma_pesos_coluna = tabela_pesos.sum(axis=0).replace(0, np.nan)
            linha_total = (soma_valores_coluna / soma_pesos_coluna).fillna(0)

            if incluir_total_linha:
                total_geral_valor = tabela_pesos.values * tabela.iloc[:, :-1].values
                total_geral = total_geral_valor.sum() / tabela_pesos.values.sum() if tabela_pesos.values.sum() > 0 else 0
                linha_total["Total"] = total_geral

            tabela.loc["Total"] = linha_total

    else:
        if incluir_total_coluna:
            tabela.loc["Total"] = tabela.sum()

        if incluir_total_linha:
            tabela["Total"] = tabela.sum(axis=1)

    # ---------------------------------------------------------
    # Tabela formatada
    # ---------------------------------------------------------
    tabela_formatada = pd.DataFrame(index=tabela.index, columns=tabela.columns)

    for i in range(len(tabela_formatada.index)):
        for j in range(len(tabela_formatada.columns)):
            valor_celula = tabela.iloc[i, j]
            if not pd.isna(valor_celula):
                tabela_formatada.iloc[i, j] = formatar_numero_br(valor_celula, casas_decimais)
            else:
                tabela_formatada.iloc[i, j] = "-"

    # ---------------------------------------------------------
    # Escala de cores
    # ---------------------------------------------------------
    valores_para_escala = tabela.values.copy()

    if incluir_total_coluna:
        valores_para_escala = valores_para_escala[:-1, :]
    if incluir_total_linha:
        valores_para_escala = valores_para_escala[:, :-1]

    valores_validos = valores_para_escala[~np.isnan(valores_para_escala)]

    if len(valores_validos) > 0:
        vmin = np.nanmin(valores_validos)
        vmax = np.nanmax(valores_validos)
        if vmin == vmax:
            vmin = vmin - 0.1 if vmin > 0 else 0
            vmax = vmax + 0.1
    else:
        vmin, vmax = 0, 1

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap_obj = cm.get_cmap(cmap)

    # ---------------------------------------------------------
    # Matriz de cores
    # ---------------------------------------------------------
    n_linhas = len(tabela)
    n_colunas = len(tabela.columns)

    cores_fundo = []
    cores_texto = []

    for i in range(n_linhas):
        linha_cores_fundo = []
        linha_cores_texto = []

        for j in range(n_colunas):
            is_total_linha = incluir_total_coluna and i == n_linhas - 1
            is_total_coluna = incluir_total_linha and j == n_colunas - 1
            is_total = is_total_linha or is_total_coluna

            valor_celula = tabela.iloc[i, j]

            if pd.isna(valor_celula) or is_total:
                cor_fundo = "#F5F5F5" if is_total else "white"
                cor_texto = "black"
            else:
                rgba = cmap_obj(norm(valor_celula))
                cor_fundo = mcolors.to_hex(rgba)
                r, g, b = rgba[:3]
                luminancia = (0.299 * r + 0.587 * g + 0.114 * b)
                cor_texto = "white" if luminancia < 0.5 else "black"

            linha_cores_fundo.append(cor_fundo)
            linha_cores_texto.append(cor_texto)

        cores_fundo.append(linha_cores_fundo)
        cores_texto.append(linha_cores_texto)

    cores_fundo_por_coluna = list(map(list, zip(*cores_fundo)))
    cores_texto_por_coluna = list(map(list, zip(*cores_texto)))

    # ---------------------------------------------------------
    # Cabeçalhos e valores
    # ---------------------------------------------------------
    nome_linha = NOMES_AMIGAVEIS.get(linha, linha.replace("_", " ").title())

    cabecalhos = [f"<b>{nome_linha}</b>"] + [
        f"<b>{quebrar_nome_meio(str(col))}</b>" for col in tabela_formatada.columns
    ]

    indices_formatados = [str(idx) for idx in tabela_formatada.index]
    valores_celulas_formatados = [tabela_formatada[col].tolist() for col in tabela_formatada.columns]
    valores_tabela = [indices_formatados] + valores_celulas_formatados

    cores_texto_primeira_coluna = ["black"] * len(tabela)
    cores_texto_todas_colunas = [cores_texto_primeira_coluna] + cores_texto_por_coluna

    # ---------------------------------------------------------
    # Figura
    # ---------------------------------------------------------
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=cabecalhos,
                    fill_color="#2C3E50",
                    font=dict(color="white", size=13, family="Arial Bold, Arial, sans-serif"),
                    align="center",
                    height=40,
                    line=dict(width=1, color="white")
                ),
                cells=dict(
                    values=valores_tabela,
                    fill_color=[["#F8F9F9"] * len(tabela)] + cores_fundo_por_coluna,
                    font=dict(
                        color=cores_texto_todas_colunas,
                        size=12,
                        family="Arial Bold, Arial, sans-serif"
                    ),
                    align="center",
                    height=30,
                    line=dict(width=1, color="lightgray"),
                    format=[None] * len(valores_tabela)
                )
            )
        ]
    )

    # ---------------------------------------------------------
    # Título
    # ---------------------------------------------------------
    if titulo is None:
        titulo_completo = montar_titulo_tabela_gradiente(
            linha=linha,
            coluna=coluna,
            valor=valor,
            aggfunc=aggfunc,
            escopo=escopo,
            ano_selecionado=ano_selecionado,
            filtro_geo=filtro_geo
        )
    else:
        titulo_completo = titulo

    fig.update_layout(
        title=dict(
            text=titulo_completo,
            x=0.5,
            y=0.96,
            xanchor="center",
            font=dict(size=18, family="Arial Bold, Arial, sans-serif")
        ),
        margin=dict(l=50, r=50, t=100, b=50),
        font=dict(family="Arial, sans-serif")
    )

    return fig, tabela
#=============================================================================
# FUNÇÕES LINHA _NOTA RENDA
# ===============================================================================
def grafico_combinado_notas_renda(
    df: pd.DataFrame,
    materias_selecionadas: Optional[List[str]] = None,
    escolas_selecionadas: Optional[List[str]] = None,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame, pd.DataFrame]:
    """
    Combina dois gráficos de linha:
    - notas médias
    - renda média

    Agrega por ano + geografia com média ponderada por participantes.
    """

    # ---------------------------------------------------------
    # 1) Filtros
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if escolas_selecionadas and "escola" in df_filtrado.columns:
        df_filtrado["escola"] = df_filtrado["escola"].astype(str).str.strip()
        escolas_selecionadas = [e.strip() for e in escolas_selecionadas]
        df_filtrado = df_filtrado[df_filtrado["escola"].isin(escolas_selecionadas)]

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame(), pd.DataFrame()

    # ---------------------------------------------------------
    # 2) Matérias
    # ---------------------------------------------------------
    materias_disponiveis = {
        "Ciências da Natureza": "nota_cn",
        "Ciências Humanas": "nota_ch",
        "Linguagens e Códigos": "nota_lc",
        "Matemática": "nota_mt",
        "Redação": "nota_redacao"
    }

    if materias_selecionadas is None:
        materias_selecionadas = list(materias_disponiveis.keys())

    materias_validas = [m for m in materias_selecionadas if m in materias_disponiveis]
    if not materias_validas:
        raise ValueError("Nenhuma matéria válida foi selecionada.")

    colunas_notas = [
        materias_disponiveis[m]
        for m in materias_validas
        if materias_disponiveis[m] in df_filtrado.columns
    ]
    if not colunas_notas:
        raise ValueError("As colunas de notas selecionadas não estão disponíveis no DataFrame.")

    # ---------------------------------------------------------
    # 3) Nível geográfico
    # ---------------------------------------------------------
    if escopo == "br" and "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    elif escopo == "mg" and "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif escopo == "caxambu":
        df_filtrado["geo_label"] = "Caxambu"
        nivel_geo = "geo_label"
    elif "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    else:
        df_filtrado["geo_label"] = obter_nome_escopo(escopo)
        nivel_geo = "geo_label"

    rotulo_geo = obter_rotulo_geo(escopo)

    # ---------------------------------------------------------
    # 4) Preparação numérica
    # ---------------------------------------------------------
    df_aux = df_filtrado.copy()
    df_aux["ano"] = df_aux["ano"].astype(str)

    for col in colunas_notas + ["renda_media", weight_col]:
        if col in df_aux.columns:
            df_aux[col] = pd.to_numeric(df_aux[col], errors="coerce")

    df_aux["nota_media_selecionada"] = df_aux[colunas_notas].mean(axis=1)

    # ---------------------------------------------------------
    # 5) Agregação ponderada por ano + geo
    # ---------------------------------------------------------
    grupos = sorted(
        df_aux[["ano", nivel_geo]]
        .dropna()
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    notas_reg = []
    renda_reg = []

    for ano, geo in grupos:
        df_g = df_aux[(df_aux["ano"] == ano) & (df_aux[nivel_geo] == geo)].copy()
        total_part = pd.to_numeric(df_g[weight_col], errors="coerce").sum()

        notas_reg.append(
            {
                "ano": str(ano),
                nivel_geo: geo,
                "total_participantes": total_part,
                "nota_media": media_ponderada(df_g, "nota_media_selecionada", weight_col)
            }
        )

        renda_reg.append(
            {
                "ano": str(ano),
                nivel_geo: geo,
                "total_participantes": total_part,
                "renda_media": media_ponderada(df_g, "renda_media", weight_col)
            }
        )

    df_notas = pd.DataFrame(notas_reg)
    df_renda = pd.DataFrame(renda_reg)

    if df_notas.empty or df_renda.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados suficientes para construir o gráfico",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, df_notas, df_renda

    df_notas = adicionar_colunas_hover_br(
        df_notas,
        {
            "nota_fmt": ("nota_media", 1, "decimal"),
            "participantes_fmt": ("total_participantes", 0, "numero")
        }
    )

    df_renda = adicionar_colunas_hover_br(
        df_renda,
        {
            "renda_fmt": ("renda_media", 2, "decimal"),
            "participantes_fmt": ("total_participantes", 0, "numero")
        }
    )

    ordem_geo = sorted(df_notas[nivel_geo].astype(str).unique())

    # ---------------------------------------------------------
    # 6) Título
    # ---------------------------------------------------------
    if titulo is None:
        titulo = f"Evolução Comparada: Notas e Renda por {rotulo_geo} - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)

        if escolas_selecionadas:
            titulo += f"<br><sub>Escolas: {', '.join(escolas_selecionadas)}</sub>"

        if materias_validas:
            materias_txt = ", ".join(materias_validas[:3])
            if len(materias_validas) > 3:
                materias_txt += "..."
            titulo += f"<br><sub>Matérias: {materias_txt}</sub>"

    # ---------------------------------------------------------
    # 7) Figura
    # ---------------------------------------------------------
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.5, 0.5],
        vertical_spacing=0.08,
        shared_xaxes=True,
        subplot_titles=("Notas Médias", "Renda Média")
    )

    anos = sorted(df_notas["ano"].astype(str).unique())

    for i, ano in enumerate(anos):
        df_ano = df_notas[df_notas["ano"].astype(str) == str(ano)].copy()
        df_ano[nivel_geo] = pd.Categorical(df_ano[nivel_geo], categories=ordem_geo, ordered=True)
        df_ano = df_ano.sort_values(nivel_geo)

        fig.add_trace(
            go.Scatter(
                x=df_ano[nivel_geo],
                y=df_ano["nota_media"],
                name=f"{ano} Nota",
                mode="lines+markers",
                line=dict(width=3, color=SEQUENCIA_CORES[(i + 1) % len(SEQUENCIA_CORES)]),
                marker=dict(size=10, symbol="circle"),
                legendgroup=f"ano_{ano}",
                showlegend=True,
                customdata=df_ano[["participantes_fmt", "nota_fmt"]].values,
                hovertemplate=(
                    f"<b>{rotulo_geo}:</b> %{{x}}<br>"
                    "<b>Série:</b> %{fullData.name}<br>"
                    "<b>Nota Média:</b> %{customdata[1]}<br>"
                    "<b>Participantes:</b> %{customdata[0]}<br>"
                    "<extra></extra>"
                )
            ),
            row=1, col=1
        )

    for i, ano in enumerate(anos):
        df_ano = df_renda[df_renda["ano"].astype(str) == str(ano)].copy()
        df_ano[nivel_geo] = pd.Categorical(df_ano[nivel_geo], categories=ordem_geo, ordered=True)
        df_ano = df_ano.sort_values(nivel_geo)

        fig.add_trace(
            go.Scatter(
                x=df_ano[nivel_geo],
                y=df_ano["renda_media"],
                name=f"{ano} Renda",
                mode="lines+markers",
                line=dict(width=3, color=SEQUENCIA_CORES[(i + 1) % len(SEQUENCIA_CORES)], dash="dash"),
                marker=dict(size=10, symbol="diamond"),
                legendgroup=f"ano_{ano}",
                showlegend=True,
                customdata=df_ano[["participantes_fmt", "renda_fmt"]].values,
                hovertemplate=(
                    f"<b>{rotulo_geo}:</b> %{{x}}<br>"
                    "<b>Série:</b> %{fullData.name}<br>"
                    "<b>Renda Média:</b> %{customdata[1]} salários mínimos<br>"
                    "<b>Participantes:</b> %{customdata[0]}<br>"
                    "<extra></extra>"
                )
            ),
            row=2, col=1
        )

    fig.update_layout(
        height=550,
        title=dict(
            text=titulo,
            x=0.5,
            y=0.97,
            xanchor="center",
            font=dict(size=18)
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.35,
            xanchor="center",
            x=1.03,
            traceorder="normal",
            itemwidth=30
        ),
        #plot_bgcolor="white",
        #template="plotly_white",
        separators=".,"
    )

    fig.update_xaxes(
        title_text=rotulo_geo,
        row=2, col=1,
        tickangle=45,
        showgrid=True,
        gridcolor="lightgray"
    )

    fig.update_xaxes(
        showticklabels=False,
        row=1, col=1,
        showgrid=True,
        gridcolor="lightgray"
    )

    fig.update_yaxes(
        title_text="Nota Média",
        row=1, col=1,
        showgrid=True,
        gridcolor="lightgray"
    )

    fig.update_yaxes(
        title_text="Renda Média (salários mínimos)",
        row=2, col=1,
        showgrid=True,
        gridcolor="lightgray"
    )

    return fig, df_notas, df_renda
#=============================================================================
# FUNÇÕES DE GRÁFICOS - TREEMAPS
# ===============================================================================

def treemap_escola_renda(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Treemap mostrando participantes por nível geográfico e tipo de escola,
    colorido pela renda média ponderada.
    """
    df_filtrado = aplicar_filtros_dashboard(
        df,
        escopo=escopo,
        ano_selecionado=ano_selecionado
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    colunas_necessarias = {"escola", "renda_media", weight_col}
    if not colunas_necessarias.issubset(df_filtrado.columns):
        fig = go.Figure()
        fig.add_annotation(
            text="Colunas necessárias ausentes para o treemap",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="crimson")
        )
        return fig, pd.DataFrame()

    nivel_geo = obter_nivel_geografico_treemap(df_filtrado, escopo)

    df_aux = df_filtrado.copy()
    df_aux["escola"] = df_aux["escola"].astype(str)
    df_aux["renda_media"] = pd.to_numeric(df_aux["renda_media"], errors="coerce")
    df_aux[weight_col] = pd.to_numeric(df_aux[weight_col], errors="coerce")

    df_aux = df_aux.dropna(subset=["renda_media", weight_col, nivel_geo, "escola"])
    df_aux = df_aux[df_aux[weight_col] > 0]

    df_aux["renda_x_peso"] = df_aux["renda_media"] * df_aux[weight_col]

    df_agrupado = (
        df_aux
        .groupby([nivel_geo, "escola"], observed=True, as_index=False)
        .agg(
            participantes=(weight_col, "sum"),
            soma_renda=("renda_x_peso", "sum")
        )
    )

    df_agrupado = df_agrupado[df_agrupado["participantes"] > 0].copy()

    if df_agrupado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum resultado encontrado",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    df_agrupado["renda_media_ponderada"] = (
        df_agrupado["soma_renda"] / df_agrupado["participantes"]
    ).round(2)

    df_agrupado = adicionar_colunas_hover_br(
        df_agrupado,
        {
            "participantes_fmt": ("participantes", 0, "numero"),
            "renda_fmt": ("renda_media_ponderada", 2, "decimal")
        }
    )

    if titulo is None:
        titulo = f"Participantes do ENEM <br>por Escola e Renda Média Familiar - {obter_nome_escopo(escopo)}"
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"

    fig = px.treemap(
        df_agrupado,
        path=[nivel_geo, "escola"],
        values="participantes",
        color="renda_media_ponderada",
        color_continuous_scale="RdYlGn",
        title=titulo,
        labels={
            "renda_media_ponderada": "Renda Média <br>(sal. mínimos)",
            "escola": "Tipo de Escola",
            nivel_geo: obter_rotulo_geo(escopo)
        },
        custom_data=["renda_fmt", "participantes_fmt", "escola"]
    )

    fig.update_traces(
        texttemplate="<br>Escola: %{customdata[2]}<br>Participantes: %{customdata[1]}<br>Renda: %{customdata[0]}",
        hovertemplate=(
            "<b>Escola:</b> %{customdata[2]}<br>"
            "<b>Participantes:</b> %{customdata[1]}<br>"
            "<b>Renda Média Familiar (salários mínimos):</b> %{customdata[0]}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(
            x=0.5, 
            y=0.95, 
            xanchor="center",
            font=dict(size=18)
        ),
        margin=dict(t=80),
        separators=".,",
        height=600,
    )

    return fig, df_agrupado
    
def treemap_nota_escola(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    materia: str = "Matemática",
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Treemap mostrando participantes por nível geográfico e tipo de escola,
    colorido pela nota agregada ponderada da matéria selecionada.
    """
    mapa_materias = {
        "Média Geral": "nota_media",
        "Matemática": "nota_mt",
        "Ciências da Natureza": "nota_cn",
        "Ciências Humanas": "nota_ch",
        "Linguagens e Códigos": "nota_lc",
        "Redação": "nota_redacao"
    }

    if materia not in mapa_materias:
        raise ValueError(f"Matéria '{materia}' inválida. Escolha entre: {list(mapa_materias.keys())}")

    df_filtrado = aplicar_filtros_dashboard(
        df,
        escopo=escopo,
        ano_selecionado=ano_selecionado
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    coluna_nota = mapa_materias[materia]
    nivel_geo = obter_nivel_geografico_treemap(df_filtrado, escopo)

    colunas_necessarias = {coluna_nota, weight_col, "escola", nivel_geo}
    if not colunas_necessarias.issubset(df_filtrado.columns):
        fig = go.Figure()
        fig.add_annotation(
            text="Colunas necessárias ausentes para o treemap",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="crimson")
        )
        return fig, pd.DataFrame()

    df_aux = df_filtrado.copy()
    df_aux["escola"] = df_aux["escola"].astype(str)
    df_aux[coluna_nota] = pd.to_numeric(df_aux[coluna_nota], errors="coerce")
    df_aux[weight_col] = pd.to_numeric(df_aux[weight_col], errors="coerce")

    df_aux = df_aux.dropna(subset=[coluna_nota, weight_col, nivel_geo, "escola"])
    df_aux = df_aux[df_aux[weight_col] > 0]

    titulo_metrico = "Nota Média"
    df_aux["nota_x_peso"] = df_aux[coluna_nota] * df_aux[weight_col]

    df_agg = (
        df_aux
        .groupby([nivel_geo, "escola"], observed=True, as_index=False)
        .agg(
            participantes=(weight_col, "sum"),
            soma_nota=("nota_x_peso", "sum")
        )
    )

    df_agg = df_agg[df_agg["participantes"] > 0].copy()

    if df_agg.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum resultado encontrado",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    df_agg["nota_agregada"] = (df_agg["soma_nota"] / df_agg["participantes"]).round(2)

    df_agg = adicionar_colunas_hover_br(
        df_agg,
        {
            "participantes_fmt": ("participantes", 0, "numero"),
            "nota_fmt": ("nota_agregada", 2, "decimal")
        }
    )

    if titulo is None:
        titulo = f"{titulo_metrico} de {materia} por {obter_rotulo_geo(escopo)} e Escola - {obter_nome_escopo(escopo)}"
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"

    fig = px.treemap(
        df_agg,
        path=[nivel_geo, "escola"],
        values="participantes",
        color="nota_agregada",
        color_continuous_scale="RdYlGn",
        title=titulo,
        labels={
            "nota_agregada": titulo_metrico,
            "escola": "Tipo de Escola",
            nivel_geo: obter_rotulo_geo(escopo)
        },
        custom_data=["nota_fmt", "participantes_fmt", "escola"]
    )

    fig.update_traces(
        texttemplate="<br>Escola: %{customdata[2]}<br>Participantes: %{customdata[1]}<br>Nota: %{customdata[0]}",
        hovertemplate=(
            "<b>Escola:</b> %{customdata[2]}<br>"
            "<b>Participantes:</b> %{customdata[1]}<br>"
            f"<b>{titulo_metrico}:</b> %{{customdata[0]}}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=dict(
            x=0.5, 
            y=0.95, 
            xanchor="center",
            font=dict(size=18)),
        margin=dict(t=80),
        separators=".,",
        height=600,
    )

    return fig, df_agg

# =============================================================================
# FUNÇÕES DE GRÁFICOS - NOTAS MÉDIAS
# =============================================================================

def grafico_notas_por_regiao(
    df: pd.DataFrame,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    escola_selecionada: Optional[str] = None,
    materia_selecionada: str = "nota_media",
    tipo_agregacao: str = "media",
    titulo: Optional[str] = None,
    weight_col: str = "participantes",
    metodo: str = "ponderado",
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico horizontal de notas por região/UF, com suporte a:
    - filtro por ano
    - filtro geográfico
    - filtro por escola
    - seleção de matéria
    - agregação por média ou máximo

    Parameters
    ----------
    df : pd.DataFrame
        Base de dados.
    escopo : {'br', 'mg', 'caxambu'}, default='mg'
        Escopo geográfico do gráfico.
    ano_selecionado : str, optional
        Ano a filtrar.
    filtro_geo : str, optional
        Filtro geográfico adicional:
        - UF, se escopo='br'
        - Região, se escopo='mg'
        - Município, se escopo='caxambu'
    escola_selecionada : str, optional
        Tipo de escola a filtrar.
    materia_selecionada : str, default='nota_media'
        Pode ser:
        - 'nota_media'
        - 'nota_cn'
        - 'nota_ch'
        - 'nota_lc'
        - 'nota_mt'
        - 'nota_redacao'
    tipo_agregacao : {'media', 'maxima'}, default='media'
        Define se usa colunas médias ou máximas.
    titulo : str, optional
        Título customizado.
    weight_col : str, default='participantes'
        Coluna de peso para média ponderada.
    metodo : {'ponderado', 'simples'}, default='ponderado'
        Método de agregação para tipo_agregacao='media'.

    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Figura Plotly e DataFrame utilizado no gráfico.
    """

    # ---------------------------------------------------------
    # 1) Filtros padronizados
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if (
        escola_selecionada is not None
        and escola_selecionada != "Todas"
        and "escola" in df_filtrado.columns
    ):
        df_filtrado = df_filtrado[df_filtrado["escola"] == escola_selecionada].copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 2) Nível geográfico
    # ---------------------------------------------------------
    if escopo == "br" and "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    elif escopo == "mg" and "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif escopo == "caxambu":
        if "municipio" in df_filtrado.columns:
            nivel_geo = "municipio"
        elif "cidade" in df_filtrado.columns:
            nivel_geo = "cidade"
        else:
            raise ValueError("Nenhuma coluna geográfica compatível encontrada para escopo='caxambu'.")
    elif "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    else:
        raise ValueError("Nenhuma coluna geográfica compatível encontrada no DataFrame.")

    rotulo_geo = obter_rotulo_geo(escopo)

    # ---------------------------------------------------------
    # 3) Mapeamento da coluna escolhida
    # ---------------------------------------------------------
    colunas_media = {
        "nota_media": "nota_media",
        "nota_cn": "nota_cn",
        "nota_ch": "nota_ch",
        "nota_lc": "nota_lc",
        "nota_mt": "nota_mt",
        "nota_redacao": "nota_redacao",
    }

    colunas_maxima = {
        "nota_cn": "nota_cn_max",
        "nota_ch": "nota_ch_max",
        "nota_lc": "nota_lc_max",
        "nota_mt": "nota_mt_max",
        "nota_redacao": "nota_redacao_max",
    }

    nomes_materias = {
        "nota_media": "Nota Média",
        "nota_cn": "Ciências da Natureza",
        "nota_ch": "Ciências Humanas",
        "nota_lc": "Linguagens e Códigos",
        "nota_mt": "Matemática",
        "nota_redacao": "Redação",
    }

    if tipo_agregacao == "media":
        if materia_selecionada not in colunas_media:
            raise ValueError(
                "Para tipo_agregacao='media', materia_selecionada deve ser uma de: "
                f"{list(colunas_media.keys())}"
            )
        coluna_valor = colunas_media[materia_selecionada]
        titulo_metrico = "Média"

    elif tipo_agregacao == "maxima":
        if materia_selecionada == "nota_media":
            raise ValueError(
                "Não existe 'nota_media_max'. Para tipo_agregacao='maxima', "
                "selecione uma área específica."
            )
        if materia_selecionada not in colunas_maxima:
            raise ValueError(
                "Para tipo_agregacao='maxima', materia_selecionada deve ser uma de: "
                f"{list(colunas_maxima.keys())}"
            )
        coluna_valor = colunas_maxima[materia_selecionada]
        titulo_metrico = "Máxima"

    else:
        raise ValueError("tipo_agregacao deve ser 'media' ou 'maxima'")

    if coluna_valor not in df_filtrado.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Coluna '{coluna_valor}' não disponível na base",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
        )
        return fig, pd.DataFrame()

    nome_materia = nomes_materias[materia_selecionada]

    # ---------------------------------------------------------
    # 4) Agregação
    # ---------------------------------------------------------
    if tipo_agregacao == "media":
        if metodo == "ponderado" and weight_col in df_filtrado.columns:
            registros = []

            for geo, grupo in df_filtrado.groupby(nivel_geo, observed=True):
                valor_agregado = media_ponderada(grupo, coluna_valor, weight_col)
                registros.append(
                    {
                        nivel_geo: geo,
                        "valor_agregado": valor_agregado
                    }
                )

            df_plot = pd.DataFrame(registros)

        else:
            df_plot = (
                df_filtrado
                .groupby(nivel_geo, observed=True)[coluna_valor]
                .mean()
                .reset_index(name="valor_agregado")
            )
    else:
        # Para máximos, faz mais sentido usar o máximo real do grupo
        df_plot = (
            df_filtrado
            .groupby(nivel_geo, observed=True)[coluna_valor]
            .max()
            .reset_index(name="valor_agregado")
        )

    df_plot = df_plot.dropna(subset=["valor_agregado"]).copy()

    if df_plot.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem valores válidos para os filtros selecionados",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray"),
        )
        return fig, pd.DataFrame()

    df_plot = df_plot.sort_values("valor_agregado", ascending=True).reset_index(drop=True)

    # formatação BR para texto/hover
    df_plot = adicionar_colunas_hover_br(
        df_plot,
        {
            "valor_fmt": ("valor_agregado", 1, "decimal")
        }
    )

    # ---------------------------------------------------------
    # 5) Título
    # ---------------------------------------------------------
    if titulo is None:
        escopo_nome = obter_nome_escopo(escopo)
        titulo = f"{titulo_metrico} de {nome_materia} por {rotulo_geo} - {escopo_nome}"

        if filtro_geo:
            titulo += montar_complemento_filtro_geo(escopo, filtro_geo)

        if ano_selecionado is not None:
            titulo += f" ({ano_selecionado})"

        if escola_selecionada and escola_selecionada != "Todas":
            titulo += f" - Escola {escola_selecionada}"
    

    # ---------------------------------------------------------
    # 6) Gráfico
    # ---------------------------------------------------------

    def definir_cor_texto(valor, vmin, vmax):
        # normaliza entre 0 e 1
        norm = (valor - vmin) / (vmax - vmin) if vmax > vmin else 0.5
        # threshold empírico (ajuste fino depois)
        return "black" if norm < 0.55 else "white"


    vmin = df_plot["valor_agregado"].min()
    vmax = df_plot["valor_agregado"].max()

    df_plot["cor_texto"] = df_plot["valor_agregado"].apply(
        lambda v: definir_cor_texto(v, vmin, vmax)
    )
    fig = px.bar(
        df_plot,
        y=nivel_geo,
        x="valor_agregado",
        orientation="h",
        title=titulo,
        color="valor_agregado",
        color_continuous_scale=[
            "#d9f0ef",
            "#a6d8d4",
            "#6fc2bb",
            "#3aa9a1",
            "#178f87",
            "#0b6e69",
        ],
        labels={
            nivel_geo: rotulo_geo,
            "valor_agregado": f"{titulo_metrico} da Nota",
        },
        text="valor_fmt",
    )

    limite_superior = max(750, float(df_plot["valor_agregado"].max()) * 1.05)

    fig.update_layout(
        height=750,
        width=900,
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(size=18)
        ),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=100, l=80, r=40, b=40),
        coloraxis_showscale=False,
        xaxis=dict(
            title="",
            range=[0, limite_superior]
        ),
        yaxis=dict(
            title=""
        ),
        separators=".,"
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(
            size=12,
            family="Arial Bold, Arial, sans-serif"
        ),
        textfont_color=df_plot["cor_texto"],  # 🔥 aqui está o ajuste
        hovertemplate=(
            f"<b>{rotulo_geo}:</b> %{{y}}"
            f"<br><b>{nome_materia}:</b> %{{customdata[0]}}"
            "<extra></extra>"
        ),
        customdata=np.stack([df_plot["valor_fmt"]], axis=-1)
    )

    return fig, df_plot


def grafico_notas_violino(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg"
) -> go.Figure:
    """
    Gráfico de violino para distribuição de notas por escola,
    com possibilidade de filtro geográfico.
    """
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig

    notas_cols = ["nota_cn", "nota_ch", "nota_lc", "nota_mt", "nota_redacao"]
    notas_cols_existentes = [col for col in notas_cols if col in df_filtrado.columns]

    if not notas_cols_existentes or "escola" not in df_filtrado.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Colunas de notas ou escola não disponíveis",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="crimson")
        )
        return fig

    df_long = df_filtrado[["escola"] + notas_cols_existentes].melt(
        id_vars="escola",
        var_name="materia",
        value_name="nota"
    )

    df_long["materia"] = df_long["materia"].map(MATERIAS)
    df_long["nota"] = pd.to_numeric(df_long["nota"], errors="coerce")
    df_long = df_long.dropna(subset=["escola", "materia", "nota"]).copy()

    if df_long.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem notas válidas para exibir",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig

    if ORDEM_ESCOLA:
        df_long["escola"] = pd.Categorical(
            df_long["escola"],
            categories=ORDEM_ESCOLA,
            ordered=True
        )
        df_long = df_long.sort_values("escola")

    if titulo is None:
        titulo = f"Distribuição de Notas por Escola <br> {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"

    fig = go.Figure()

    escolas_plot = (
        ORDEM_ESCOLA
        if ORDEM_ESCOLA
        else list(df_long["escola"].dropna().unique())
    )

    for escola in escolas_plot:
        df_e = df_long[df_long["escola"] == escola]
        if df_e.empty:
            continue

        cor = MAPA_CORES_ESCOLA.get(escola, "gray")

        fig.add_trace(
            go.Violin(
                x=df_e["materia"],
                y=df_e["nota"],
                name=str(escola),
                line_color=cor,
                fillcolor=cor,
                opacity=0.6,
                box_visible=True,
                meanline_visible=True,
                points=False,
                hovertemplate=(
                    "<b>Matéria:</b> %{x}<br>"
                    "<b>Nota:</b> %{y:.1f}<br>"
                    f"<b>Escola:</b> {escola}<br>"
                    "<extra></extra>"
                )
            )
        )

    y_max = float(df_long["nota"].max()) * 1.05 if not df_long.empty else 1000

    fig.update_layout(
        title=dict(
            text=titulo, 
            x=0.5, 
            y=0.94,
            xanchor="center",
            font=dict(size=18)),
        xaxis=dict(title="Matérias", tickangle=45),
        yaxis=dict(
            title="Nota",
            range=[0, y_max]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="center",
            y=1.02,
            x=0.5
        ),
        #template="plotly_white",
        separators=",.",
        height=500,
        width=600,
        margin=dict(t=100, b=20, l=20, r=20),
    )

    return fig

def grafico_notas_linhas_max(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes",
    metodo: str = "ponderado",
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gráfico com barras das médias por matéria e escola, e linha dos máximos.

    Parameters
    ----------
    df : pd.DataFrame
        Base com colunas de notas médias e, preferencialmente, colunas nota_*_max.
    ano_selecionado : str, optional
        Ano para filtro.
    filtro_geo : str, optional
        UF (escopo='br') ou Região (escopo='mg') ou Município (escopo='caxambu').
    titulo : str, optional
        Título personalizado.
    escopo : str, default='mg'
        'br', 'mg' ou 'caxambu'.
    weight_col : str, default='participantes'
        Coluna de peso usada na média ponderada.
    metodo : str, default='ponderado'
        'ponderado' ou 'simples'.

    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Figura Plotly e DataFrame consolidado.
    """

    # ---------------------------------------------------------
    # 1) Filtros
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    if "escola" not in df_filtrado.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Coluna 'escola' não disponível na base",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 2) Mapas e ordens
    # ---------------------------------------------------------
    ordem_escola = [e for e in ORDEM_ESCOLA if e in df_filtrado["escola"].astype(str).unique()]
    ordem_materias = [
        "Ciências Humanas",
        "Ciências da Natureza",
        "Linguagens e Códigos",
        "Matemática",
        "Redação"
    ]

    mapa_media = {
        "nota_ch": "Ciências Humanas",
        "nota_cn": "Ciências da Natureza",
        "nota_lc": "Linguagens e Códigos",
        "nota_mt": "Matemática",
        "nota_redacao": "Redação"
    }

    mapa_max = {
        "nota_ch_max": "Ciências Humanas",
        "nota_cn_max": "Ciências da Natureza",
        "nota_lc_max": "Linguagens e Códigos",
        "nota_mt_max": "Matemática",
        "nota_redacao_max": "Redação"
    }

    colunas_media = [c for c in mapa_media.keys() if c in df_filtrado.columns]
    colunas_max = [c for c in mapa_max.keys() if c in df_filtrado.columns]

    if not colunas_media:
        fig = go.Figure()
        fig.add_annotation(
            text="Colunas de notas médias não disponíveis",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 3) Consolidação estatística
    # ---------------------------------------------------------
    registros = []

    escolas_validas = [e for e in ordem_escola if e in df_filtrado["escola"].astype(str).unique()]

    for escola in escolas_validas:
        df_escola = df_filtrado[df_filtrado["escola"].astype(str) == str(escola)].copy()

        if df_escola.empty:
            continue

        for col_media, nome_materia in mapa_media.items():
            if col_media not in df_escola.columns:
                continue

            # média
            if metodo == "ponderado" and weight_col in df_escola.columns:
                nota_media = media_ponderada(df_escola, col_media, weight_col)
            else:
                nota_media = pd.to_numeric(df_escola[col_media], errors="coerce").mean()

            # máximo
            col_max = col_media + "_max"
            if col_max in df_escola.columns:
                # se a base já traz máximos agregados, usa o máximo real deles
                nota_max = pd.to_numeric(df_escola[col_max], errors="coerce").max()
            else:
                # fallback: máximo observado da própria coluna média por matéria
                nota_max = pd.to_numeric(df_escola[col_media], errors="coerce").max()

            registros.append({
                "escola": escola,
                "materia": nome_materia,
                "nota_media": nota_media,
                "nota_max": nota_max
            })

    stats_df = pd.DataFrame(registros)

    if stats_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados válidos para construção do gráfico",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 4) Ordenação e formatação
    # ---------------------------------------------------------
    stats_df["escola"] = pd.Categorical(
        stats_df["escola"],
        categories=ordem_escola,
        ordered=True
    )
    stats_df["materia"] = pd.Categorical(
        stats_df["materia"],
        categories=ordem_materias,
        ordered=True
    )

    stats_df = stats_df.sort_values(["escola", "materia"]).reset_index(drop=True)

    stats_df["categoria_x"] = (
        stats_df["materia"].astype(str) + "<br>" + stats_df["escola"].astype(str)
    )

    stats_df = adicionar_colunas_hover_br(
        stats_df,
        {
            "media_fmt": ("nota_media", 1, "decimal"),
            "max_fmt": ("nota_max", 1, "decimal"),
        }
    )

    # ---------------------------------------------------------
    # 5) Título
    # ---------------------------------------------------------
    if titulo is None:
        titulo = f"Médias e Máximos das Notas por Matéria e Escola - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"

    # ---------------------------------------------------------
    # 6) Figura
    # ---------------------------------------------------------
    fig = go.Figure()
    # eixo x mostrando apenas a matéria (sem quebrar agrupamento)
    categorias = stats_df["categoria_x"].tolist()
    
    ticktext = []
    ultima_materia = None
        
    for cat in categorias:
        materia = cat.split("<br>")[0]
        # mostra apenas na primeira ocorrência do grupo
        if materia != ultima_materia:
            ticktext.append(materia)
            ultima_materia = materia
        else:
            ticktext.append("")

    fig.update_xaxes(
        tickmode="array",
        tickvals=categorias,
        ticktext=ticktext
    )

    for escola in ordem_escola:
        df_escola = stats_df[stats_df["escola"] == escola].copy()

        if df_escola.empty:
            continue

        fig.add_trace(
            go.Bar(
                x=df_escola["categoria_x"],
                y=df_escola["nota_media"],
                name=str(escola),
                marker_color=MAPA_CORES_ESCOLA.get(str(escola), "gray"),
                text=df_escola["media_fmt"],
                customdata=np.stack(
                    [
                        df_escola["materia"].astype(str),
                        df_escola["media_fmt"],
                        df_escola["max_fmt"],
                    ],
                    axis=-1
                ),
                hovertemplate=(
                    "<b>Escola:</b> " + str(escola) +
                    "<br><b>Matéria:</b> %{customdata[0]}"
                    "<br><b>Média:</b> %{customdata[1]}"
                    "<br><b>Máximo:</b> %{customdata[2]}"
                    "<extra></extra>"
                )
            )
        )

    fig.add_trace(
        go.Scatter(
            x=stats_df["categoria_x"],
            y=stats_df["nota_max"],
            mode="lines+markers+text",
            line=dict(color="darkgreen", width=2.5),
            marker=dict(size=8, symbol="triangle-up", color="darkgreen"),
            text=stats_df["max_fmt"],
            textposition="top center",
            textfont=dict(
                family="Arial Bold, Arial, sans-serif",
                size=11,
                color="darkgreen"
            ),
            name="Máximo",
            hovertemplate=(
                "<b>Matéria:</b> %{x}"
                "<br><b>Máximo:</b> %{text}"
                "<extra></extra>"
            )
        )
    )

    y_max = float(stats_df[["nota_media", "nota_max"]].max().max())
    range_superior = y_max * 1.12 if y_max > 0 else 1

    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            y=0.95,
            xanchor="center",
            font=dict(size=18)
        ),
        barmode="group",
        bargap=0.15,
        bargroupgap=0.08,
        height=520,
        width=950,
        template="plotly_white",
        margin=dict(t=80, b=80, l=30, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            title="",
            tickangle=35
        ),
        yaxis=dict(
            title="",
            visible=False,
            range=[0, range_superior]
        ),
        separators=".,"
    )

    for trace in fig.data:
        if trace.type == "bar":
            trace.textposition = "inside"
            trace.textangle = -90
            trace.textfont = dict(
                family="Arial Bold, Arial, sans-serif",
                size=11,
            )
        elif trace.type == "scatter":
            trace.textposition = "top center"
            trace.textfont = dict(
                family="Arial Bold, Arial, sans-serif",
                size=11,
            )

    return fig, stats_df
# =============================================================================
# FUNÇÕES DE GRÁFICOS - EVOLUÇÃO TEMPORAL
# =============================================================================

def evolucao_renda_grupos_demograficos(
    df: pd.DataFrame,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    variavel_demografica: str = 'cor_raca',
    titulo: Optional[str] = None,
    weight_col: str = 'participantes'
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Analisa a evolução temporal da renda por grupos demográficos.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com os dados
    escopo : str
        'br', 'mg' ou 'caxambu'
    ano_selecionado : str, optional
        Ano específico (se None, mostra todos os anos)
    filtro_geo : str, optional
        UF (para br) ou região (para mg)
    variavel_demografica : str
        Variável para agrupar (cor_raca, sexo, escola, etc.)
    titulo : str, optional
        Título personalizado
    weight_col : str
        Coluna de pesos
    
    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Gráfico e DataFrame com os dados
    """
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    )
    
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    # Verificar se colunas necessárias existem
    colunas_necessarias = {'ano', variavel_demografica, 'renda_media', weight_col}
    if not colunas_necessarias.issubset(df_filtrado.columns):
        fig = go.Figure()
        fig.add_annotation(
            text="Colunas necessárias não disponíveis",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    # Agrupar por ano e variável demográfica
    evolucao = (
        df_filtrado.groupby(['ano', variavel_demografica], observed=True)
        .apply(lambda x: pd.Series({
            'renda_media': media_ponderada(x, 'renda_media', weight_col),
            'participantes': x[weight_col].sum()
        }))
        .reset_index()
        .round(2)
    )
    
    # Ordenar por ordem padrão se existir
    ordem = obter_ordem_padrao(variavel_demografica)
    
    # Criar colunas formatadas para hover
    evolucao['renda_fmt'] = evolucao['renda_media'].apply(lambda x: formatar_decimal_br(x, 2))
    evolucao['participantes_fmt'] = evolucao['participantes'].apply(lambda x: formatar_numero_br(x, 0))
    
    # Nome amigável para legenda
    nome_variavel = NOMES_AMIGAVEIS.get(variavel_demografica, variavel_demografica.replace('_', ' ').title())
    
    # Título
    if titulo is None:
        titulo = f"Evolução da Renda por {nome_variavel} - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" - {ano_selecionado}"
    
    # Criar gráfico
    fig = px.line(
        evolucao,
        x='ano',
        y='renda_media',
        color=variavel_demografica,
        title=titulo,
        markers=True,
        color_discrete_sequence=SEQUENCIA_CORES,
        category_orders={variavel_demografica: ordem} if ordem else None,
        custom_data=['renda_fmt', 'participantes_fmt']
    )
    
    # Atualizar layout
    fig.update_layout(
        height=400,
        xaxis_title="Ano",
        yaxis_title="Renda Média (salários mínimos)",
        legend_title=nome_variavel,
        title=dict(x=0.5, y=0.95, font=dict(size=18)),
        hovermode="x unified",
        separators=",."
    )
    
    # Atualizar traces com formatação
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate=(
            "<b>Ano:</b> %{x}<br>"
            f"<b>{nome_variavel}:</b> %{{fullData.name}}<br>"
            "<b>Renda Média:</b> %{customdata[0]} salários mínimos<br>"
            "<b>Participantes:</b> %{customdata[1]}<br>"
            "<extra></extra>"
        )
    )
    
    return fig, evolucao


def grafico_evolucao_temporal_acurado(
    df: pd.DataFrame,
    escopo: str = "mg",
    filtro_geo: Optional[str] = None,
    materias_selecionadas: Optional[List[str]] = None,
    weight_col: str = "participantes",
    titulo: Optional[str] = None
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Gera gráfico de evolução temporal com:
    - barras para nota média
    - linha para renda média
    - linha tracejada para participantes (escala normalizada)

    Usa média ponderada por participantes na agregação anual.
    """

    materias_disponiveis = {
        "Ciências da Natureza": "nota_cn",
        "Ciências Humanas": "nota_ch",
        "Linguagens e Códigos": "nota_lc",
        "Matemática": "nota_mt",
        "Redação": "nota_redacao"
    }

    if materias_selecionadas is None:
        materias_selecionadas = list(materias_disponiveis.keys())

    colunas_notas = [
        materias_disponiveis[m]
        for m in materias_selecionadas
        if m in materias_disponiveis and materias_disponiveis[m] in df.columns
    ]

    if not colunas_notas:
        raise ValueError("Nenhuma matéria válida foi selecionada.")

    colunas_necessarias = {"ano", "renda_media", weight_col, *colunas_notas}
    colunas_faltantes = colunas_necessarias - set(df.columns)
    if colunas_faltantes:
        raise KeyError(f"Colunas ausentes no DataFrame: {sorted(colunas_faltantes)}")

    # ---------------------------------------------------------
    # 1) Filtros
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=None,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Sem dados para os filtros selecionados",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 2) Preparação
    # ---------------------------------------------------------
    df_filtrado["ano"] = df_filtrado["ano"].astype(str)

    for col in colunas_notas + ["renda_media", weight_col]:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors="coerce")

    df_filtrado["nota_media_selecionada"] = df_filtrado[colunas_notas].mean(axis=1)

    # ---------------------------------------------------------
    # 3) Agregação ponderada por ano
    # ---------------------------------------------------------
    registros = []

    for ano in sorted(df_filtrado["ano"].dropna().unique()):
        df_ano = df_filtrado[df_filtrado["ano"] == ano].copy()

        participantes = pd.to_numeric(df_ano[weight_col], errors="coerce").sum()

        nota_media = media_ponderada(df_ano, "nota_media_selecionada", weight_col)
        renda_media = media_ponderada(df_ano, "renda_media", weight_col)

        registros.append(
            {
                "ano": ano,
                "nota_media": nota_media,
                "renda_media": renda_media,
                weight_col: participantes
            }
        )

    df_agrupado = pd.DataFrame(registros).sort_values("ano").reset_index(drop=True)

    if df_agrupado.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Sem dados após agregação",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        return fig, df_agrupado

    # ---------------------------------------------------------
    # 4) Participantes normalizados
    # ---------------------------------------------------------
    part_max = float(df_agrupado[weight_col].max()) if not df_agrupado.empty else 0.0

    if part_max > 0:
        df_agrupado["participantes_normalizado"] = (
            df_agrupado[weight_col] / part_max
        ) * 500
    else:
        df_agrupado["participantes_normalizado"] = 0.0

    # ---------------------------------------------------------
    # 5) Formatação BR
    # ---------------------------------------------------------
    df_agrupado = adicionar_colunas_hover_br(
        df_agrupado,
        {
            "nota_media_fmt": ("nota_media", 1, "decimal"),
            "renda_media_fmt": ("renda_media", 2, "decimal"),
            "participantes_fmt": (weight_col, 0, "numero")
        }
    )

    # ---------------------------------------------------------
    # 6) Cores / título
    # ---------------------------------------------------------
    FONTE_COR = "#262626"

    cor_barra = SEQUENCIA_CORES[0]
    cor_renda = SEQUENCIA_CORES[1]
    cor_participantes = SEQUENCIA_CORES[2]

    nome_escopo = obter_nome_escopo(escopo)
    complemento_filtro = montar_complemento_filtro_geo(escopo, filtro_geo)
    titulo_materias = ", ".join(materias_selecionadas)

    if titulo is None:
        titulo_final = (
            f"Evolução Temporal - {nome_escopo}{complemento_filtro}"
            f"<br><sub>Matérias: {titulo_materias}</sub>"
        )
    else:
        titulo_final = titulo

    # ---------------------------------------------------------
    # 7) Figura
    # ---------------------------------------------------------
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    customdata = np.stack(
        [
            df_agrupado["renda_media_fmt"],
            df_agrupado["nota_media_fmt"],
            df_agrupado["participantes_fmt"]
        ],
        axis=-1
    )

    fig.add_trace(
        go.Bar(
            x=df_agrupado["ano"],
            y=df_agrupado["nota_media"],
            name="Nota Média",
            marker_color=cor_barra,
            width=0.6,
            text=df_agrupado["nota_media_fmt"],
            textposition="outside",
            textfont=dict(
                size=11,
                family="Arial Bold, Arial, sans-serif",
                color=FONTE_COR
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>Ano %{x}</b><br>"
                "<b>Nota Média:</b> %{customdata[1]}<br>"
                "<b>Renda Média:</b> %{customdata[0]} salários mínimos<br>"
                "<b>Participantes:</b> %{customdata[2]}"
                "<extra></extra>"
            )
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_agrupado["ano"],
            y=df_agrupado["renda_media"],
            name="Renda Média Familiar Mensal",
            mode="lines+markers+text",
            line=dict(color=cor_renda, width=4),
            marker=dict(size=11, color=cor_renda),
            text=df_agrupado["renda_media_fmt"],
            textposition="bottom center",
            textfont=dict(
                size=11,
                family="Arial Bold, Arial, sans-serif",
                color=FONTE_COR
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>Ano %{x}</b><br>"
                "<b>Renda Média Familiar Mensal:</b> %{customdata[0]} salários mínimos<br>"
                "<b>Nota Média:</b> %{customdata[1]}<br>"
                "<b>Participantes:</b> %{customdata[2]}"
                "<extra></extra>"
            ),
        ),
        secondary_y=True
    )

    fig.add_trace(
        go.Scatter(
            x=df_agrupado["ano"],
            y=df_agrupado["participantes_normalizado"],
            name="Participantes",
            mode="lines+markers+text",
            line=dict(color=cor_participantes, width=4, dash="dash"),
            marker=dict(size=11, color=cor_participantes, symbol="diamond"),
            text=df_agrupado["participantes_fmt"],
            textposition="top center",
            textfont=dict(
                size=11,
                family="Arial Bold, Arial, sans-serif",
                color=FONTE_COR
            ),
            customdata=customdata,
            hovertemplate=(
                "<b>Ano %{x}</b><br>"
                "<b>Participantes:</b> %{customdata[2]}<br>"
                "<b>Nota Média:</b> %{customdata[1]}<br>"
                "<b>Renda Média:</b> %{customdata[0]} salários mínimos"
                "<extra></extra>"
            ),
        ),
        secondary_y=False
    )

    fig.update_layout(
        title=dict(
            text=titulo_final,
            x=0.5,
            y=0.92,
            xanchor="center",
            font=dict(size=16, family="Arial", color=FONTE_COR)
        ),
        height=700,
        width=700,
        #plot_bgcolor="white",
        #paper_bgcolor="white",
        hovermode="x unified",
        separators=".,",
        xaxis=dict(
            showgrid=False,
            tickmode="array",
            tickvals=df_agrupado["ano"],
            ticktext=df_agrupado["ano"],
            tickfont=dict(size=12, color=FONTE_COR),
            title=None
        ),
        yaxis=dict(
            range=[0, 650],
            visible=False,
            showgrid=False
        ),
        yaxis2=dict(
            range=[0, 10],
            visible=False,
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.30,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=FONTE_COR),
            #bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(l=50, r=50, t=120, b=150),
        hoverlabel=dict(
            #bgcolor="white",
            font_size=12,
            font_family="Arial",
            #font_color="dimgrey"  # ← Cor dimgrey adicionada aqui
        )
    )

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.60,
        text=(
            "<b>Escalas:</b> "
            "Notas: 0–650 | "
            "Renda: 0–10 salários mínimos | "
            "Participantes: escala normalizada de 0 ao valor máximo<br>"
            "<br>(valores reais nos rótulos)"
        ),
        showarrow=False,
        font=dict(size=10, color=FONTE_COR),
        align="center",
        bgcolor="rgba(255,255,255,0.7)"
    )

    return fig, df_agrupado

def analise_mobilidade_ranking(
    df: pd.DataFrame,
    ano_selecionado=None,
    escopo: str = "mg",
    filtro_geo: Optional[str] = None,
    materia_selecionada: str = "nota_media",
    titulo: Optional[str] = None,
    weight_col: str = "participantes",
    metodo: str = "ponderado",
    top_n: Optional[int] = None,
    escola_selecionada: Optional[List[str]] = None,  
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Analisa a mobilidade do ranking de notas ao longo dos anos.

    Parameters
    ----------
    df : pd.DataFrame
        Base agregada com coluna 'ano' e variáveis de nota.
    escopo : str, default='mg'
        'br', 'mg' ou 'caxambu'.
    filtro_geo : str, optional
        Filtro geográfico adicional.
    materia_selecionada : str, default='nota_media'
        Variável de nota usada no ranking.
    titulo : str, optional
        Título personalizado.
    weight_col : str, default='participantes'
        Coluna de peso.
    metodo : str, default='ponderado'
        'ponderado' ou 'simples'.
    top_n : int, optional
        Se informado, exibe apenas os top N do último ano disponível.

    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Figura Plotly e DataFrame final com rankings.
    """

    # ---------------------------------------------------------
    # 1) Filtros base
    # ---------------------------------------------------------

    if escola_selecionada is not None and "escola" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado["escola"].astype(str).isin(escola_selecionada)
            ].copy()
    
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=None,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    if "ano" not in df_filtrado.columns:
        raise ValueError("A base precisa conter a coluna 'ano'.")

    # ---------------------------------------------------------
    # 2) Nível geográfico
    # ---------------------------------------------------------
    if escopo == "br" and "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    elif escopo == "mg" and "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif escopo == "caxambu":
        if "municipio" in df_filtrado.columns:
            nivel_geo = "municipio"
        elif "cidade" in df_filtrado.columns:
            nivel_geo = "cidade"
        else:
            raise ValueError("Nenhuma coluna geográfica compatível encontrada para escopo='caxambu'.")
    elif "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    else:
        raise ValueError("Nenhuma coluna geográfica compatível encontrada no DataFrame.")

    rotulo_geo = obter_rotulo_geo(escopo)

    # ---------------------------------------------------------
    # 3) Validação da matéria
    # ---------------------------------------------------------
    nomes_materias = {
        "nota_media": "Nota Média",
        "nota_cn": "Ciências da Natureza",
        "nota_ch": "Ciências Humanas",
        "nota_lc": "Linguagens e Códigos",
        "nota_mt": "Matemática",
        "nota_redacao": "Redação",
    }

    if materia_selecionada not in nomes_materias:
        raise ValueError(
            f"materia_selecionada deve ser uma das seguintes: {list(nomes_materias.keys())}"
        )

    if materia_selecionada not in df_filtrado.columns:
        raise ValueError(f"Coluna '{materia_selecionada}' não encontrada no DataFrame.")

    nome_materia = nomes_materias[materia_selecionada]

    # ---------------------------------------------------------
    # 4) Agregação por ano e geografia
    # ---------------------------------------------------------
    df_filtrado["ano"] = df_filtrado["ano"].astype(str)
    anos = sorted(df_filtrado["ano"].dropna().unique())

    lista_resultados = []

    for ano in anos:
        df_ano = df_filtrado[df_filtrado["ano"] == ano].copy()

        if df_ano.empty:
            continue

        registros = []
        for geo, grupo in df_ano.groupby(nivel_geo, observed=True):
            if metodo == "ponderado" and weight_col in grupo.columns:
                nota = media_ponderada(grupo, materia_selecionada, weight_col)
            else:
                nota = pd.to_numeric(grupo[materia_selecionada], errors="coerce").mean()

            registros.append({
                nivel_geo: geo,
                "nota": nota,
                "ano": ano
            })

        df_ag = pd.DataFrame(registros)
        lista_resultados.append(df_ag)

    if not lista_resultados:
        fig = go.Figure()
        fig.add_annotation(
            text="Não foi possível calcular os rankings",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    df_ranking = pd.concat(lista_resultados, ignore_index=True)
    df_ranking = df_ranking.dropna(subset=["nota"]).copy()

    if df_ranking.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem valores válidos para cálculo do ranking",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    # ranking: 1 = melhor nota
    df_ranking["ranking"] = (
        df_ranking.groupby("ano", observed=True)["nota"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # ---------------------------------------------------------
    # 5) Mobilidade entre primeiro e último ano
    # ---------------------------------------------------------
    ano_inicial = anos[0]
    ano_final = anos[-1]

    df_inicio = (
        df_ranking[df_ranking["ano"] == ano_inicial][[nivel_geo, "ranking", "nota"]]
        .rename(columns={"ranking": "ranking_inicial", "nota": "nota_inicial"})
    )

    df_fim = (
        df_ranking[df_ranking["ano"] == ano_final][[nivel_geo, "ranking", "nota"]]
        .rename(columns={"ranking": "ranking_final", "nota": "nota_final"})
    )

    df_mobilidade = df_inicio.merge(df_fim, on=nivel_geo, how="outer")
    df_mobilidade["variacao_ranking"] = (
        df_mobilidade["ranking_inicial"] - df_mobilidade["ranking_final"]
    )

    df_ranking = df_ranking.merge(df_mobilidade, on=nivel_geo, how="left")

    # opcional: limitar aos top N do último ano
    if top_n is not None:
        locais_top = (
            df_mobilidade.sort_values("ranking_final", ascending=True)[nivel_geo]
            .head(top_n)
            .tolist()
        )
        df_ranking = df_ranking[df_ranking[nivel_geo].isin(locais_top)].copy()
        df_mobilidade = df_mobilidade[df_mobilidade[nivel_geo].isin(locais_top)].copy()

    # ---------------------------------------------------------
    # 6) Formatação
    # ---------------------------------------------------------
    df_ranking = adicionar_colunas_hover_br(
        df_ranking,
        {
            "nota_fmt": ("nota", 1, "decimal"),
        }
    )

    if "nota_inicial" in df_ranking.columns:
        df_ranking = adicionar_colunas_hover_br(
            df_ranking,
            {
                "nota_inicial_fmt": ("nota_inicial", 1, "decimal"),
                "nota_final_fmt": ("nota_final", 1, "decimal"),
            }
        )

    # ordem das linhas pelo ranking final
    ordem_localidades = (
        df_mobilidade.sort_values("ranking_final", ascending=True)[nivel_geo]
        .dropna()
        .astype(str)
        .tolist()
    )

    df_ranking[nivel_geo] = pd.Categorical(
        df_ranking[nivel_geo].astype(str),
        categories=ordem_localidades,
        ordered=True
    )

    df_ranking = df_ranking.sort_values([nivel_geo, "ano"]).reset_index(drop=True)

    # ---------------------------------------------------------
    # 7) Título
    # ---------------------------------------------------------
    if titulo is None:
        titulo = f"Evolução do Ranking de {nome_materia} <br> por {rotulo_geo} - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if escola_selecionada:
            escolas_txt = ", ".join(escola_selecionada)
            titulo += f" | Escola: {escolas_txt}"

    # ---------------------------------------------------------
    # 8) Figura
    # ---------------------------------------------------------
    # Cria lista de cores baseada no número de categorias
    categorias_unicas = df_ranking[nivel_geo].nunique()
    cores = SEQUENCIA_CORES * (categorias_unicas // len(SEQUENCIA_CORES) + 1)
    cores = cores[:categorias_unicas]
    fig = px.line(
        df_ranking,
        x="ano",
        y="ranking",
        color=nivel_geo,
        markers=True,
        text="nota_fmt",
        custom_data=[
            nivel_geo,
            "ranking",
            "nota_fmt",
            "ranking_inicial",
            "ranking_final",
            "variacao_ranking",
        ],
        title=titulo,
        color_discrete_sequence=cores 
    )
     

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=9),
        hovertemplate=(
            f"<b>{rotulo_geo}:</b> %{{customdata[0]}}"
            "<br><b>Ano:</b> %{x}"
            "<br><b>Ranking:</b> %{customdata[1]}"
            "<br><b>Nota:</b> %{customdata[2]}"
            "<br><b>Ranking inicial:</b> %{customdata[3]}"
            "<br><b>Ranking final:</b> %{customdata[4]}"
            "<br><b>Variação no ranking:</b> %{customdata[5]}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=600,
        width=980,
        template='plotly_white',
        title=dict(
            text=titulo,
            x=0.5,
            y=0.95,
            xanchor="center",
            font=dict(size=18)
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title=rotulo_geo
        ),
        margin=dict(t=90, b=50, l=50, r=180),
        separators=".,"
    )

    # ranking melhor no topo
    ranking_max = int(df_ranking["ranking"].max()) if not df_ranking.empty else 1
    fig.update_yaxes(
        title="Ranking",
        autorange="reversed",
        range=[ranking_max + 0.5, 0.5],
        dtick=1
    )

    fig.update_xaxes(title="Ano")

    fig = aplicar_texto_negrito_linhas(
        fig,
        textfont_size=10,
        textposition="top center"
    )

    return fig, df_ranking
# =============================================================================
# FUNÇÕES DE GRÁFICOS - COMPARATIVO NOTA X RENDA
# =============================================================================

def grafico_comparativo_nota_renda(df: pd.DataFrame, ano_selecionado: Optional[str] = None,
                                     materias_selecionadas: Optional[List[str]] = None,
                                     escolas_selecionadas: Optional[List[str]] = None,
                                     titulo: Optional[str] = None,
                                     escopo: str = 'mg') -> go.Figure:
    """
    Gráfico comparativo de nota média e renda média por região
    """
    # Filtrar por escopo
    df_filtrado = filtrar_por_escopo(df, escopo)
    
    # Filtrar por ano
    if ano_selecionado is not None and 'ano' in df_filtrado.columns:
        df_filtrado['ano'] = df_filtrado['ano'].astype(str)
        df_filtrado = df_filtrado[df_filtrado['ano'] == str(ano_selecionado)]
    
    # Filtrar por escola
    if escolas_selecionadas and 'escola' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['escola'].isin(escolas_selecionadas)]
    
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig
    
    # Definir matérias
    if materias_selecionadas is None:
        materias_selecionadas = list(MATERIAS.values())
    
    materias_dict = {v: k for k, v in MATERIAS.items()}
    colunas_notas = [materias_dict[mat] for mat in materias_selecionadas if mat in materias_dict]
    
    if not colunas_notas:
        colunas_notas = ['nota_cn', 'nota_ch', 'nota_lc', 'nota_mt', 'nota_redacao']
    
    # Calcular nota média
    df_filtrado['nota_media'] = df_filtrado[colunas_notas].mean(axis=1)
    
    nivel_geo = 'regiao' if 'regiao' in df_filtrado.columns else 'uf'
    
    # Agrupar por região
    df_agrupado = df_filtrado.groupby(nivel_geo, as_index=False).agg({
        'nota_media': 'mean',
        'renda_media': 'mean'
    }).round(2)
    
    df_agrupado = df_agrupado.sort_values(nivel_geo)
    
    # Título
    if titulo is None:
        escopo_nome = {
            'br': 'Brasil',
            'mg': 'Minas Gerais',
            'caxambu': 'Caxambu'
        }.get(escopo, escopo.upper())
        
        titulo = f"Comparação: Nota Média vs Renda Média - {escopo_nome}"
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"
    
    # Criar figura com eixo secundário
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Barras para notas
    fig.add_trace(
        go.Bar(
            x=df_agrupado[nivel_geo],
            y=df_agrupado['nota_media'],
            name="Nota Média",
            marker_color=SEQUENCIA_CORES[0],
            opacity=0.7,
            text=df_agrupado['nota_media'].round(1),
            textposition='outside',
            textfont=dict(size=11),
            hovertemplate='<b>%{x}</b><br>Nota Média: %{y:.1f}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Linha para renda
    fig.add_trace(
        go.Scatter(
            x=df_agrupado[nivel_geo],
            y=df_agrupado['renda_media'],
            name="Renda Média",
            line=dict(color=SEQUENCIA_CORES[1], width=3),
            marker=dict(size=8, color=SEQUENCIA_CORES[1]),
            mode='lines+markers',
            text=df_agrupado['renda_media'].round(1),
            textposition='top center',
            textfont=dict(size=11),
            hovertemplate='<b>%{x}</b><br>Renda Média: %{y:.1f} SM<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        height=550,
        title=dict(
            text=titulo, 
            x=0.5, 
            xanchor="center",
            font=dict(size=16)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        template='plotly_white',
        bargap=0.15
    )
    
    fig.update_xaxes(title_text=nivel_geo.title())
    fig.update_yaxes(title_text="Nota Média", secondary_y=False)
    fig.update_yaxes(title_text="Renda Média (SM)", secondary_y=True)
    
    return fig


    
# =============================================================================
# FUNÇÕES DE GRÁFICOS - BOXPLOT
# =============================================================================

def boxplot_notas_por_regiao(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    materia_selecionada: str = "Matemática",
    titulo: Optional[str] = None,
    escopo: str = 'mg',
    weight_col: str = 'participantes'
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Boxplot das notas por região/UF.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com os dados
    ano_selecionado : str, optional
        Ano para filtrar
    filtro_geo : str, optional
        UF (para br) ou região (para mg)
    materia_selecionada : str
        Matéria para análise
    titulo : str, optional
        Título personalizado
    escopo : str
        'br', 'mg' ou 'caxambu'
    weight_col : str
        Coluna de pesos (não usada diretamente no boxplot, mas para consistência)
    
    Returns
    -------
    Tuple[go.Figure, pd.DataFrame]
        Boxplot e DataFrame com estatísticas
    """
    
    # Aplicar filtros do dashboard
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    )
    
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    # Mapear matéria para coluna
    materias_map = {v: k for k, v in MATERIAS.items()}
    coluna_nota = materias_map.get(materia_selecionada, 'nota_mt')
    
    # Verificar se a coluna existe
    if coluna_nota not in df_filtrado.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Coluna {coluna_nota} não disponível",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    # Determinar nível geográfico
    if escopo == "br" and "uf" in df_filtrado.columns:
        nivel_geo = "uf"
        rotulo_geo = "UF"
    elif "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
        rotulo_geo = "Região"
    elif "uf" in df_filtrado.columns:
        nivel_geo = "uf"
        rotulo_geo = "UF"
    else:
        nivel_geo = "escola"
        rotulo_geo = "Escola"
    
    # Ordem das categorias
    ordem_geo = obter_ordem_padrao(nivel_geo)

    
    
    # Criar boxplot
    fig = px.box(
        df_filtrado,
        x=nivel_geo,
        y=coluna_nota,
        color=nivel_geo,
        title="",  # Título será definido no layout
        labels={
            nivel_geo: rotulo_geo, 
            coluna_nota: f"Nota de {materia_selecionada}"
        },
        color_discrete_sequence=SEQUENCIA_CORES,
        category_orders={nivel_geo: ordem_geo} if ordem_geo else None,
        points="outliers"  # Mostrar apenas outliers como pontos
    )
    
    # Calcular estatísticas com observed=True para evitar warning
    estatisticas = df_filtrado.groupby(nivel_geo, observed=True)[coluna_nota].agg([
        ('min', 'min'),
        ('q1', lambda x: x.quantile(0.25)),
        ('median', 'median'),
        ('q3', lambda x: x.quantile(0.75)),
        ('max', 'max'),
        ('mean', 'mean'),
        ('std', 'std'),
        ('count', 'count')
    ]).round(2).reset_index()
    
    # Renomear colunas
    estatisticas.columns = [
        rotulo_geo, 'Mínimo', 'Q1', 'Mediana', 'Q3', 'Máximo', 
        'Média', 'Desvio Padrão', 'Nº Participantes'
    ]
    
    # Formatar colunas numéricas para exibição
    estatisticas['Média_fmt'] = estatisticas['Média'].apply(lambda x: formatar_decimal_br(x, 1))
    estatisticas['Mediana_fmt'] = estatisticas['Mediana'].apply(lambda x: formatar_decimal_br(x, 1))
    estatisticas['Participantes_fmt'] = estatisticas['Nº Participantes'].apply(lambda x: formatar_numero_br(x, 0))
    
    # Título
    if titulo is None:
        titulo = f"Distribuição das Notas de {materia_selecionada} - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"
    
    # Atualizar layout
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            xanchor="center",
            font=dict(size=18, family="Arial Bold, Arial, sans-serif")
        ),
        showlegend=False,
        template='plotly_white',
        height=500,
        width=900,
        xaxis=dict(
            title=rotulo_geo,
            tickangle=45,
            tickfont=dict(family="Arial, sans-serif", size=11)
        ),
        yaxis=dict(
            title=f"Nota de {materia_selecionada}",
            tickfont=dict(family="Arial, sans-serif", size=11),
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        boxgap=0.3,
        boxgroupgap=0.3,
        hovermode="x unified",
        separators=",."
    )
    
    # Atualizar traces com formatação melhorada
    fig.update_traces(
        marker=dict(
            size=4,
            opacity=0.6,
            line=dict(width=1, color='black')
        ),
        line=dict(width=2),
        hovertemplate=(
            f"<b>{rotulo_geo}:</b> %{{x}}<br>"
            f"<b>{materia_selecionada}:</b> %{{y:.1f}}<br>"
            "<extra></extra>"
        )
    )
    
    # Adicionar anotações com os valores dos quartis (opcional)
    
    """
    
    for geo in df_filtrado[nivel_geo].unique():
        if ordem_geo and geo not in ordem_geo:
            continue
            
        dados = df_filtrado[df_filtrado[nivel_geo] == geo][coluna_nota]
        if len(dados) > 0:
            q1, mediana, q3 = np.percentile(dados, [25, 50, 75])
            minimo, maximo = dados.min(), dados.max()
            
            for valor, offset in [(minimo, -15), (q1, -10), (mediana, 10), (q3, 15), (maximo, 20)]:
                fig.add_annotation(
                    x=geo,
                    y=valor,
                    text=formatar_decimal_br(valor, 1),
                    showarrow=False,
                    font=dict(size=9, color="black", family="Arial, sans-serif"),
                    yshift=offset,
                    bgcolor="rgba(255,255,255,0.7)",
                    bordercolor="lightgray",
                    borderwidth=1,
                    borderpad=2
                )
    """
    
    return fig, estatisticas


# Versão alternativa com estatísticas em tabela separada
def boxplot_notas_por_regiao_com_tabela(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    materia_selecionada: str = "Matemática",
    escopo: str = 'mg'
) -> Tuple[go.Figure, pd.DataFrame, go.Figure]:
    """
    Versão que retorna boxplot + tabela de estatísticas.
    """
    
    # Obter boxplot e estatísticas
    fig_box, estatisticas = boxplot_notas_por_regiao(
        df=df,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo,
        materia_selecionada=materia_selecionada,
        escopo=escopo
    )
    
    if estatisticas.empty:
        return fig_box, estatisticas, go.Figure()
    
    # Criar tabela com estatísticas formatadas
    colunas_exibir = [estatisticas.columns[0], 'Média', 'Mediana', 'Mínimo', 'Máximo', 'Desvio Padrão', 'Nº Participantes']
    colunas_exibir = [col for col in colunas_exibir if col in estatisticas.columns]
    
    df_tabela = estatisticas[colunas_exibir].copy()
    
    # Formatar números para a tabela
    for col in df_tabela.columns:
        if col != estatisticas.columns[0]:
            if col == 'Nº Participantes':
                df_tabela[col] = df_tabela[col].apply(lambda x: formatar_numero_br(x, 0))
            else:
                df_tabela[col] = df_tabela[col].apply(lambda x: formatar_decimal_br(x, 1))
    
    # Criar figura da tabela
    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=[f"<b>{col}</b>" for col in df_tabela.columns],
            fill_color="#2C3E50",
            font=dict(color="white", size=12, family="Arial, sans-serif"),
            align="center",
            height=40
        ),
        cells=dict(
            values=[df_tabela[col].tolist() for col in df_tabela.columns],
            fill_color="white",
            font=dict(color="black", size=11, family="Arial, sans-serif"),
            align="center",
            height=30,
            line=dict(width=1, color="lightgray")
        )
    )])
    
    fig_table.update_layout(
        height=200 + 25 * len(df_tabela),
        width=800,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig_box, estatisticas, fig_table




    # Exibir estatísticas
    print("\n=== Estatísticas por Região/UF ===")
    display(estatisticas[['UF' if 'UF' in estatisticas.columns else estatisticas.columns[0], 
                          'Média', 'Mediana', 'Mínimo', 'Máximo', 'Nº Participantes']])


# =============================================================================
# FUNÇÕES DE GRÁFICOS - ANÁLISE DE TECNOLOGIA
# =============================================================================

def analise_acesso_tecnologia(
    df: pd.DataFrame,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None,
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Analisa acesso à tecnologia por região/UF, comparando:
    - média de celulares
    - média de computadores
    - nota média

    Usa média ponderada por participantes.
    """

    # ---------------------------------------------------------
    # 1) Filtros
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 2) Nível geográfico
    # ---------------------------------------------------------
    if escopo == "br" and "uf" in df_filtrado.columns:
        nivel_geo = "uf"
        rotulo_geo = "UF"
    elif escopo == "mg" and "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
        rotulo_geo = "Região"
    elif escopo == "caxambu":
        if "municipio" in df_filtrado.columns:
            nivel_geo = "municipio"
        elif "cidade" in df_filtrado.columns:
            nivel_geo = "cidade"
        else:
            nivel_geo = "escola"
        rotulo_geo = obter_rotulo_geo(escopo)
    elif "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
        rotulo_geo = "Região"
    elif "uf" in df_filtrado.columns:
        nivel_geo = "uf"
        rotulo_geo = "UF"
    else:
        nivel_geo = "escola"
        rotulo_geo = "Escola"

    # ---------------------------------------------------------
    # 3) Verificações
    # ---------------------------------------------------------
    colunas_necessarias = [nivel_geo, "cel", "comptdr", "nota_media", weight_col]
    if not all(col in df_filtrado.columns for col in colunas_necessarias):
        fig = go.Figure()
        fig.add_annotation(
            text="Colunas necessárias não disponíveis",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    # ---------------------------------------------------------
    # 4) Agregação ponderada
    # ---------------------------------------------------------
    registros = []
    for geo in df_filtrado[nivel_geo].dropna().unique():
        df_geo = df_filtrado[df_filtrado[nivel_geo] == geo].copy()

        registros.append(
            {
                nivel_geo: geo,
                "cel": media_ponderada(df_geo, "cel", weight_col),
                "comptdr": media_ponderada(df_geo, "comptdr", weight_col),
                "nota_media": media_ponderada(df_geo, "nota_media", weight_col),
                "participantes": pd.to_numeric(df_geo[weight_col], errors="coerce").sum(),
            }
        )

    df_final = pd.DataFrame(registros)

    if df_final.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Não foi possível agregar os dados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()

    df_final[nivel_geo] = df_final[nivel_geo].astype(str)
    df_final = df_final.sort_values(nivel_geo, kind="stable").reset_index(drop=True)

    ordem_categorias = df_final[nivel_geo].tolist()

    df_final = adicionar_colunas_hover_br(
        df_final,
        {
            "cel_fmt": ("cel", 2, "decimal"),
            "comptdr_fmt": ("comptdr", 2, "decimal"),
            "nota_fmt": ("nota_media", 1, "decimal"),
            "participantes_fmt": ("participantes", 0, "numero"),
        }
    )

    # ---------------------------------------------------------
    # 5) Título
    # ---------------------------------------------------------
    if titulo is None:
        titulo = f"Acesso à Tecnologia por {rotulo_geo} x Nota Média - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"

    # ---------------------------------------------------------
    # 6) Figura
    # ---------------------------------------------------------
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df_final[nivel_geo],
            y=df_final["cel"],
            name="Celulares",
            marker_color=SEQUENCIA_CORES[0],
            text=df_final["cel_fmt"],
            customdata=np.stack([df_final["participantes_fmt"]], axis=-1),
            hovertemplate=(
                f"<b>{rotulo_geo}:</b> %{{x}}<br>"
                "<b>Celulares:</b> %{text}<br>"
                "<b>Participantes:</b> %{customdata[0]}"
                "<extra></extra>"
            )
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Bar(
            x=df_final[nivel_geo],
            y=df_final["comptdr"],
            name="Computadores",
            marker_color=SEQUENCIA_CORES[1],
            text=df_final["comptdr_fmt"],
            customdata=np.stack([df_final["participantes_fmt"]], axis=-1),
            hovertemplate=(
                f"<b>{rotulo_geo}:</b> %{{x}}<br>"
                "<b>Computadores:</b> %{text}<br>"
                "<b>Participantes:</b> %{customdata[0]}"
                "<extra></extra>"
            )
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_final[nivel_geo],
            y=df_final["nota_media"],
            name="Nota média",
            mode="lines+markers+text",
            text=df_final["nota_fmt"],
            textposition="top center",
            textfont=dict(
                family="Arial Black",
                size=11,
                color=SEQUENCIA_CORES[2]
            ),
            line=dict(color=SEQUENCIA_CORES[2], width=2.5),
            marker=dict(size=7, color=SEQUENCIA_CORES[2]),
            customdata=np.stack([df_final["participantes_fmt"]], axis=-1),
            hovertemplate=(
                f"<b>{rotulo_geo}:</b> %{{x}}<br>"
                "<b>Nota média:</b> %{text}<br>"
                "<b>Participantes:</b> %{customdata[0]}"
                "<extra></extra>"
            )
        ),
        secondary_y=True
    )

    # ---------------------------------------------------------
    # 7) Ranges
    # ---------------------------------------------------------
    max_barras = float(df_final[["cel", "comptdr"]].max().max())
    y1_superior = max_barras * 1.50 if max_barras > 0 else 1

    nota_min = float(df_final["nota_media"].min())
    nota_max = float(df_final["nota_media"].max())
    amplitude = nota_max - nota_min

    margem_inferior = max(amplitude * 0.50, 220)
    margem_superior = max(amplitude * 0.10, 40)

    y2_inferior = max(0, nota_min - margem_inferior)
    y2_superior = nota_max + margem_superior

    # ---------------------------------------------------------
    # 8) Layout
    # ---------------------------------------------------------
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            xanchor="center",
            y=0.95,
            font=dict(size=18)
        ),
        barmode="overlay",
        template="plotly_white",
        height=520,
        width=920,
        margin=dict(t=100, b=80, l=30, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            title="",
            tickangle=35
        ),
        separators=".,"
    )

    fig.update_xaxes(
        categoryorder="array",
        categoryarray=ordem_categorias
    )

    fig.update_yaxes(
        visible=False,
        title_text="",
        range=[0, y1_superior],
        secondary_y=False
    )

    fig.update_yaxes(
        visible=False,
        title_text="",
        range=[y2_inferior, y2_superior],
        secondary_y=True
    )

    for trace in fig.data:
        if trace.type == "bar":
            trace.textposition = "inside"
            trace.textangle = -90
            trace.textfont = dict(
                family="Arial Bold, Arial, sans-serif",
                size=11,
            )
        elif trace.type == "scatter":
            trace.textposition = "top center"
            trace.textfont = dict(
                family="Arial Bold, Arial, sans-serif",
                size=10,
            )

    return fig, df_final

# =============================================================================
# FUNÇÕES DE GRÁFICOS - TABELAS
# =============================================================================

def tabela_notas_maximas(df: pd.DataFrame, ano_selecionado: Optional[str] = None,
                          titulo: Optional[str] = None,
                          escopo: str = 'mg') -> Tuple[go.Figure, pd.DataFrame]:
    """
    Tabela com as notas máximas por matéria
    """
    # Filtrar por escopo
    df_filtrado = filtrar_por_escopo(df, escopo)
    
    # Filtrar por ano
    if ano_selecionado is not None and 'ano' in df_filtrado.columns:
        df_filtrado['ano'] = df_filtrado['ano'].astype(str)
        df_filtrado = df_filtrado[df_filtrado['ano'] == str(ano_selecionado)]
    
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    registros = []
    nivel_geo = 'regiao' if 'regiao' in df_filtrado.columns else 'uf'
    
    for col, nome in MATERIAS.items():
        col_max = f"{col}_max" if f"{col}_max" in df_filtrado.columns else col
        
        if col_max in df_filtrado.columns:
            nota_max = df_filtrado[col_max].max()
            df_top = df_filtrado[df_filtrado[col_max] == nota_max]
            
            regioes = df_top[nivel_geo].unique()
            escolas = df_top['escola'].unique() if 'escola' in df_top.columns else []
            
            registros.append({
                "Matéria": nome,
                "Nota máxima": f"{nota_max:.1f}",
                "Regiões": ", ".join(map(str, regioes)),
                "Tipo de escola": ", ".join(map(str, escolas)) if len(escolas) > 0 else "Não informado"
            })
    
    if not registros:
        fig = go.Figure()
        fig.add_annotation(
            text="Nenhum dado disponível",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame()
    
    df_tabela = pd.DataFrame(registros)
    
    # Título
    if titulo is None:
        escopo_nome = {
            'br': 'Brasil',
            'mg': 'Minas Gerais',
            'caxambu': 'Caxambu'
        }.get(escopo, escopo.upper())
        
        titulo = f"Notas Máximas - {escopo_nome}"
        if ano_selecionado:
            titulo += f" ({ano_selecionado})"
    
    # Criar tabela
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_tabela.columns),
            fill_color='#1f2937',
            font=dict(color='white', size=12),
            align='left',
            height=40
        ),
        cells=dict(
            values=[df_tabela[col] for col in df_tabela.columns],
            fill_color=[['#f9fafb', '#eef2f7'] * len(df_tabela)],
            align='left',
            font=dict(size=11),
            height=30
        )
    )])
    
    fig.update_layout(
        title=dict(
            text=titulo, 
            x=0.5, 
            xanchor="center",
            font=dict(size=16)
        ),
        height=400 + 40 * len(df_tabela),
        margin=dict(l=20, r=20, t=60, b=50)
    )
    
    return fig, df_tabela


# =============================================================================
# FUNÇÕES DE GRÁFICOS - CORRELAÇÃO
# =============================================================================

def corr_heat_ponderada(
    df: pd.DataFrame,
    colunas_corr: List[str],
    weight_col: str = 'participantes',
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    titulo: Optional[str] = None
) -> go.Figure:
    """
    Gera matriz de correlação ponderada pelo número de participantes.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame agregado
    colunas_corr : List[str]
        Lista de colunas para correlação
    weight_col : str
        Coluna com os pesos (participantes)
    escopo, ano_selecionado, filtro_geo : filtros padrão
    titulo : str, optional
    
    Returns
    -------
    go.Figure
        Heatmap de correlação ponderada
    """
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    )
    
    if df_filtrado.empty or len(df_filtrado) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes para correlação",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Filtrar colunas existentes
    colunas_validas = [col for col in colunas_corr if col in df_filtrado.columns]
    df_corr = df_filtrado[colunas_validas + [weight_col]].copy()
    
    # Remover linhas com NaN
    df_corr = df_corr.dropna()
    
    if len(df_corr) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Dados insuficientes após remover NaN",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Calcular correlação ponderada
    pesos = df_corr[weight_col].values
    n_cols = len(colunas_validas)
    matriz_corr = np.zeros((n_cols, n_cols))
    
    for i, col1 in enumerate(colunas_validas):
        for j, col2 in enumerate(colunas_validas):
            if i == j:
                matriz_corr[i, j] = 1.0
            elif i < j:  # Calcular apenas uma vez
                # Extrair valores
                x = df_corr[col1].values
                y = df_corr[col2].values
                
                # Calcular médias ponderadas
                media_x = np.average(x, weights=pesos)
                media_y = np.average(y, weights=pesos)
                
                # Calcular covariância ponderada
                cov = np.average((x - media_x) * (y - media_y), weights=pesos)
                
                # Calcular desvios padrão ponderados
                std_x = np.sqrt(np.average((x - media_x)**2, weights=pesos))
                std_y = np.sqrt(np.average((y - media_y)**2, weights=pesos))
                
                # Correlação
                if std_x > 0 and std_y > 0:
                    corr = cov / (std_x * std_y)
                else:
                    corr = 0
                
                matriz_corr[i, j] = corr
                matriz_corr[j, i] = corr  # Simétrica
    
    # Nomes amigáveis
    nomes = [NOMES_AMIGAVEIS.get(col, col.replace('_', ' ').title()) for col in colunas_validas]
    
    # Criar máscara triangular superior
    mask = np.triu(np.ones_like(matriz_corr), k=1).astype(bool)
    matriz_masked = np.where(mask, np.nan, matriz_corr)
    
    # Título
    if titulo is None:
        titulo = f"Matriz de Correlação Ponderada - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" - {ano_selecionado}"
    
    # Criar heatmap
    fig = px.imshow(
        matriz_masked,
        x=nomes,
        y=nomes,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        labels=dict(color="Correlação"),
        title=titulo,
        text_auto='.2f'
    )
    
    # Layout
    fig.update_layout(
        title=dict(
            x=0.5, 
            xanchor="center",
            font=dict(size=18, family="Arial, sans-serif")),
        width=900,
        height=800,
        xaxis=dict(tickangle=45, tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11)),
        coloraxis_colorbar=dict(
            title="Correlação",
            tickformat=".2f",
            tickfont=dict(family="Arial, sans-serif")
        ),
        separators=",."
    )
    
    return fig

# =============================================================================
# FUNÇÕES DE GRÁFICOS - DASHBOARD MÉTRICAS
# =============================================================================
def criar_painel_indicadores_gerais(
    df_notas_filtrado: pd.DataFrame,
    df_demografico_filtrado: pd.DataFrame,
    escopo: str = "mg",
    titulo_base: Optional[str] = None,
    label_ano: str = "",
    ano_selecionado: Optional[str] = None, 
) -> Tuple[go.Figure, Dict]:
    """
    Cria painel com indicadores gerais do dashboard.

    Parameters
    ----------
    df_notas_filtrado : pd.DataFrame
        Base agregada com notas e participação.
    df_demografico_filtrado : pd.DataFrame
        Base demográfica agregada.
    escopo : str, default="mg"
        'br', 'mg' ou 'caxambu'.
    titulo_base : str, optional
        Título base do painel.
    label_ano : str, default=""
        Texto complementar para o título.

    Returns
    -------
    Tuple[go.Figure, Dict]
        Figura e dicionário de métricas.
        
    """
    escopo_nome = obter_nome_escopo(escopo)
    rotulo_geo = obter_rotulo_geo(escopo)

    if ano_selecionado is not None:
        if "ano" in df_notas_filtrado.columns:
            df_notas_filtrado = df_notas_filtrado[
                df_notas_filtrado["ano"].astype(str) == str(ano_selecionado)
                ].copy()
        
        if "ano" in df_demografico_filtrado.columns:
            df_demografico_filtrado = df_demografico_filtrado[
                df_demografico_filtrado["ano"].astype(str) == str(ano_selecionado)
                ].copy()

    if df_notas_filtrado is None or df_notas_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados de notas para construir o painel",
            x=0.5, 
            xanchor="center",
            y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, {}

    if df_demografico_filtrado is None:
        df_demografico_filtrado = pd.DataFrame()

    # ---------------------------------------------------------
    # totais
    # ---------------------------------------------------------
    total_participantes_notas = (
        int(pd.to_numeric(df_notas_filtrado.get("participantes"), errors="coerce").sum())
        if "participantes" in df_notas_filtrado.columns else 0
    )

    total_participantes_demo = (
        int(pd.to_numeric(df_demografico_filtrado.get("participantes"), errors="coerce").sum())
        if "participantes" in df_demografico_filtrado.columns else 0
    )

    # ---------------------------------------------------------
    # métricas centrais ponderadas
    # ---------------------------------------------------------
    nota_media_geral = media_ponderada(df_notas_filtrado, "nota_media", "participantes")

    renda_media = (
        media_ponderada(df_demografico_filtrado, "renda_media", "participantes")
        if {"renda_media", "participantes"}.issubset(df_demografico_filtrado.columns)
        else 0.0
    )

    indice_consumo_medio = (
        media_ponderada(df_demografico_filtrado, "indice_consumo", "participantes")
        if {"indice_consumo", "participantes"}.issubset(df_demografico_filtrado.columns)
        else 0.0
    )

    celulares_media = (
        media_ponderada(df_demografico_filtrado, "cel", "participantes")
        if {"cel", "participantes"}.issubset(df_demografico_filtrado.columns)
        else 0.0
    )

    computadores_media = (
        media_ponderada(df_demografico_filtrado, "comptdr", "participantes")
        if {"comptdr", "participantes"}.issubset(df_demografico_filtrado.columns)
        else 0.0
    )

    taxa_presenca_dia1 = (
        media_ponderada(df_notas_filtrado, "taxa_presenca_dia1", "participantes") * 100
        if "taxa_presenca_dia1" in df_notas_filtrado.columns else 0.0
    )

    taxa_presenca_dia2 = (
        media_ponderada(df_notas_filtrado, "taxa_presenca_dia2", "participantes") * 100
        if "taxa_presenca_dia2" in df_notas_filtrado.columns else 0.0
    )

    taxa_presenca_media = (taxa_presenca_dia1 + taxa_presenca_dia2) / 2

    materias_cols = {
        "Ciências da Natureza": "nota_cn",
        "Ciências Humanas": "nota_ch",
        "Linguagens e Códigos": "nota_lc",
        "Matemática": "nota_mt",
        "Redação": "nota_redacao",
    }
    materias_cols = {k: v for k, v in materias_cols.items() if v in df_notas_filtrado.columns}

    notas_por_materia = (
        calcular_notas_por_materia(
            df_notas_filtrado,
            materias_cols,
            coluna_peso="participantes"
        ) if materias_cols else {}
    )

    # ---------------------------------------------------------
    # melhor / pior geografia
    # ---------------------------------------------------------
    if escopo == "br" and "uf" in df_notas_filtrado.columns:
        coluna_geo = "uf"
    elif escopo == "mg" and "regiao" in df_notas_filtrado.columns:
        coluna_geo = "regiao"
    elif escopo == "caxambu" and "municipio" in df_notas_filtrado.columns:
        coluna_geo = "municipio"
    elif escopo == "caxambu" and "cidade" in df_notas_filtrado.columns:
        coluna_geo = "cidade"
    else:
        coluna_geo = None

    if coluna_geo is not None and df_notas_filtrado[coluna_geo].nunique(dropna=True) > 1:
        melhor_geo, melhor_nota_geo, pior_geo, pior_nota_geo = melhor_pior_categoria(
            df_notas_filtrado,
            coluna_categoria=coluna_geo,
            coluna_valor="nota_media",
            coluna_peso="participantes"
        )
    else:
        melhor_geo = escopo_nome
        pior_geo = escopo_nome
        melhor_nota_geo = nota_media_geral
        pior_nota_geo = nota_media_geral

    melhor_escola, melhor_nota, pior_escola, pior_nota = melhor_pior_categoria(
        df_notas_filtrado,
        coluna_categoria="escola",
        coluna_valor="nota_media",
        coluna_peso="participantes"
    )

    # ---------------------------------------------------------
    # métricas
    # ---------------------------------------------------------
    metricas = {
        "total_participantes": total_participantes_notas,
        "total_participantes_demo": total_participantes_demo,
        "nota_media": round(nota_media_geral, 2),
        "renda_media": round(renda_media, 2),
        "indice_consumo_medio": round(indice_consumo_medio, 3),
        "celulares_media": round(celulares_media, 2),
        "computadores_media": round(computadores_media, 2),
        "taxa_presenca_dia1": round(taxa_presenca_dia1, 1),
        "taxa_presenca_dia2": round(taxa_presenca_dia2, 1),
        "taxa_presenca_media": round(taxa_presenca_media, 1),
        "melhor_geo": melhor_geo,
        "melhor_nota_geo": round(melhor_nota_geo, 2),
        "pior_geo": pior_geo,
        "pior_nota_geo": round(pior_nota_geo, 2),
        "melhor_escola": melhor_escola,
        "melhor_nota": round(melhor_nota, 2),
        "pior_escola": pior_escola,
        "pior_nota": round(pior_nota, 2),
        "notas_por_materia": notas_por_materia,
        "escopo": escopo_nome,
        "rotulo_geo": rotulo_geo,
    }

    # ---------------------------------------------------------
    # título
    # ---------------------------------------------------------
    if titulo_base is None:
        titulo_base = f"📊 Indicadores Gerais - {escopo_nome}"

    if ano_selecionado:
        label_ano = f"({ano_selecionado})"

    titulo_completo = f"{titulo_base} {label_ano}".strip()

    # ---------------------------------------------------------
    # figura
    # ---------------------------------------------------------
    fig = make_subplots(
        rows=4, cols=3,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "bar", "colspan": 3}, None, None]
        ],
        subplot_titles=(
            "Total de Participantes",
            "Nota Média Geral",
            "Renda Média Familiar<br>(salários mínimos)",
            "Índice de Consumo Médio",
            "Média de Computadores",
            "Taxa de Presença Média",
            "Melhor Nota Média (UF/ região)",
            "Melhor Nota Média",
            "Pior Nota Média",
            "Média das Notas por Área"
        ),
       
        vertical_spacing=0.05,
        horizontal_spacing=0.2,
        row_heights=[0.14, 0.14, 0.19, 0.53],
    )

    cor_numero = SEQUENCIA_CORES[1]

    # ---------------------------------------------------------
    # linha 1
    # ---------------------------------------------------------
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br><br>"
                    f"<span style='font-size:22px; color:{cor_numero}'><b>"
                    f"{formatar_numero_br(metricas['total_participantes'], 0)}"
                    "</b></span>"
                ),
                "font": {"size": 14}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br><br>"
                    f"<span style='font-size:22px; color:{cor_numero}'><b>"
                    f"{formatar_decimal_br(metricas['nota_media'], 1)} pts"
                    "</b></span>"
                ),
                "font": {"size": 14}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br>"
                    f"<span style='font-size:22px; color:{cor_numero}'><b>"
                    f"{formatar_decimal_br(metricas['renda_media'], 2)}"
                    "</b></span>"
                ),
                "font": {"size": 14}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=1, col=3
    )

    # ---------------------------------------------------------
    # linha 2
    # ---------------------------------------------------------
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br><br>"
                    f"<span style='font-size:22px; color:{cor_numero}'><b>"
                    f"{formatar_decimal_br(metricas['indice_consumo_medio'], 3)}"
                    "</b></span>"
                ),
                "font": {"size": 14}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br><br>"
                    f"<span style='font-size:22px; color:{cor_numero}'><b>"
                    f"{formatar_decimal_br(metricas['computadores_media'], 2)}"
                    "</b></span>"
                ),
                "font": {"size": 14}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=2, col=2
    )

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br><br>"
                    f"<span style='font-size:22px; color:{cor_numero}'><b>"
                    f"{formatar_decimal_br(metricas['taxa_presenca_media'], 1)}%"
                    "</b></span>"
                ),
                "font": {"size": 14}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=2, col=3
    )

    # ---------------------------------------------------------
    # linha 3
    # ---------------------------------------------------------
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=0,
            title={
                "text": (
                    "<br>"
                    f"<b>{quebrar_nome_meio(str(metricas['melhor_geo']))}</b>"
                    "<br>"
                    f"<span style='font-size:18px; color:{cor_numero}'>"
                    f"<b>{formatar_decimal_br(metricas['melhor_nota_geo'], 1)}</b>"
                    "</span>"
                ),
                "font": {"size": 13}
            },
            number={"font": {"size": 1, "color": "rgba(0,0,0,0)"}}
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        montar_indicador_escola(
            valor=metricas["melhor_nota"],
            nome_escola=metricas["melhor_escola"],
            cor=cor_numero,
            incluir_delta=False,
            referencia_delta=0.0,
            espacamento_extra_titulo=False
        ),
        row=3, col=2
    )

    fig.add_trace(
        montar_indicador_escola(
            valor=metricas["pior_nota"],
            nome_escola=metricas["pior_escola"],
            cor=cor_numero,
            incluir_delta=False,
            referencia_delta=0.0,
            espacamento_extra_titulo=False
        ),
        row=3, col=3
    )

    # ---------------------------------------------------------
    # linha 4
    # ---------------------------------------------------------
    notas_ord = []
    if metricas["notas_por_materia"]:
        materias = list(metricas["notas_por_materia"].keys())
        notas = list(metricas["notas_por_materia"].values())

        dados_ordenados = sorted(zip(materias, notas), key=lambda x: x[1], reverse=True)
        materias_ord = [x[0] for x in dados_ordenados]
        notas_ord = [x[1] for x in dados_ordenados]
        textos_formatados = [formatar_decimal_br(v, 1) for v in notas_ord]

        fig.add_trace(
            go.Bar(
                x=materias_ord,
                y=notas_ord,
                text=textos_formatados,
                textposition="outside",
                textfont={"size": 12},
                marker_color=SEQUENCIA_CORES[:len(materias_ord)],
                name="Notas por Matéria",
                hovertemplate="<b>%{x}</b><br>Nota Média: %{y:,.1f}<extra></extra>"
            ),
            row=4, col=1
        )

    # ---------------------------------------------------------
    # layout
    # ---------------------------------------------------------
    fig.update_layout(
        height=850,
        title=dict(
            text=titulo_completo,
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="#2C3E50")
        ),
        showlegend=False,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Arial", size=12, color="#2C3E50"),
        margin=dict(t=130, b=100, l=60, r=60),
        separators=".,"
    )

    if notas_ord:
        fig.update_yaxes(
            title_text="Nota Média",
            visible=False,
            row=4, col=1,
            showgrid=False,
            range=[0, max(notas_ord) * 1.2]
        )

    fig.update_xaxes(
        title_text="Área de Conhecimento",
        row=4, col=1,
        tickangle=45,
        tickfont={"size": 11}
    )

    # ---------------------------------------------------------
    # ajuste fino dos subtítulos
    # ---------------------------------------------------------
    for i, annotation in enumerate(fig.layout.annotations):
        annotation.font.size = 13
    
        if i == 2:   # renda média familiar
            annotation.y += 0.010
        
        # terceira linha - ajuste mais fino
        elif i == 6:   # melhor região
            annotation.y += 0.025  # Reduzido de 0.050 para 0.025
        elif i == 7:   # melhor nota média (escola)
            annotation.y += 0.025  # Reduzido para aproximar do conteúdo
        elif i == 8:   # pior nota média (escola)
            annotation.y += 0.025  # Reduzido para aproximar do conteúdo

    return fig, metricas

   
# =============================================================================
# FUNÇÕES DE GRÁFICOS - BUBBLE CHART
# =============================================================================
def bubble_chart_4d(
    df: pd.DataFrame,
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    usar_presenca_media: bool = True,
    titulo: Optional[str] = None,
    escopo: str = "mg",
    weight_col: str = "participantes"
) -> Tuple[go.Figure, pd.DataFrame, float]:
    """
    Gráfico de bolhas com 4 dimensões:
    - x: renda média
    - y: nota média
    - cor: presença
    - tamanho: participantes

    A base já deve estar agregada no nível analítico apropriado.
    A correção principal aqui é ponderar a tendência e o R² por participantes.
    """

    # ---------------------------------------------------------
    # 1) Filtros
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    colunas_minimas = ["nota_media", "renda_media", weight_col, "escola"]
    colunas_ausentes = [col for col in colunas_minimas if col not in df_filtrado.columns]

    if colunas_ausentes:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Colunas ausentes: {', '.join(colunas_ausentes)}",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="crimson")
        )
        return fig, pd.DataFrame(), 0.0

    df_filtrado = df_filtrado.dropna(subset=["nota_media", "renda_media", weight_col, "escola"])

    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados disponíveis para os filtros selecionados",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame(), 0.0

    # ---------------------------------------------------------
    # 2) Colunas auxiliares
    # ---------------------------------------------------------
    if "taxa_presenca_dia1" not in df_filtrado.columns:
        df_filtrado["taxa_presenca_dia1"] = 0.85

    if "taxa_presenca_dia2" not in df_filtrado.columns:
        df_filtrado["taxa_presenca_dia2"] = 0.85

    if usar_presenca_media:
        df_filtrado["presenca"] = (
            pd.to_numeric(df_filtrado["taxa_presenca_dia1"], errors="coerce") +
            pd.to_numeric(df_filtrado["taxa_presenca_dia2"], errors="coerce")
        ) / 2
    else:
        df_filtrado["presenca"] = pd.to_numeric(df_filtrado["taxa_presenca_dia1"], errors="coerce")

    df_filtrado[weight_col] = pd.to_numeric(df_filtrado[weight_col], errors="coerce")
    df_filtrado["tamanho_bolha"] = np.log1p(df_filtrado[weight_col].clip(lower=0)) * 15

    # ---------------------------------------------------------
    # 3) Nível geográfico
    # ---------------------------------------------------------
    if escopo == "br" and "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    elif escopo == "mg" and "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif escopo == "caxambu":
        df_filtrado["geo_label"] = "Caxambu"
        nivel_geo = "geo_label"
    elif "regiao" in df_filtrado.columns:
        nivel_geo = "regiao"
    elif "uf" in df_filtrado.columns:
        nivel_geo = "uf"
    else:
        df_filtrado["geo_label"] = obter_nome_escopo(escopo)
        nivel_geo = "geo_label"

    rotulo_geo = obter_rotulo_geo(escopo)

    # ---------------------------------------------------------
    # 4) DataFrame final
    # ---------------------------------------------------------
    df_bolha = df_filtrado[
        [nivel_geo, "escola", "nota_media", "renda_media", "presenca", weight_col, "tamanho_bolha"]
    ].copy()

    for col in ["nota_media", "renda_media", "presenca", weight_col]:
        df_bolha[col] = pd.to_numeric(df_bolha[col], errors="coerce")

    df_bolha = df_bolha.dropna(subset=["nota_media", "renda_media", "presenca", weight_col])

    if df_bolha.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados válidos após preparação",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig, pd.DataFrame(), 0.0

    df_bolha["nota_media"] = df_bolha["nota_media"].round(2)
    df_bolha["renda_media"] = df_bolha["renda_media"].round(2)
    df_bolha["presenca"] = df_bolha["presenca"].round(3)

    df_bolha = adicionar_colunas_hover_br(
        df_bolha,
        {
            "nota_fmt": ("nota_media", 1, "decimal"),
            "renda_fmt": ("renda_media", 2, "decimal"),
            "presenca_fmt": ("presenca", 1, "percentual"),
            "participantes_fmt": (weight_col, 0, "numero")
        }
    )

    # ---------------------------------------------------------
    # 5) Título
    # ---------------------------------------------------------
    if titulo is None:
        titulo = f"Relação Renda Média Familiar vs Nota Média - {obter_nome_escopo(escopo)}"
        titulo += montar_complemento_filtro_geo(escopo, filtro_geo)
        if ano_selecionado:
            titulo += f" - {ano_selecionado}"

    # ---------------------------------------------------------
    # 6) Gráfico
    # ---------------------------------------------------------
    fig = px.scatter(
        df_bolha,
        x="renda_media",
        y="nota_media",
        size="tamanho_bolha",
        color="presenca",
        color_continuous_scale="RdYlGn",
        hover_name=nivel_geo,
        custom_data=["escola", "participantes_fmt", "renda_fmt", "nota_fmt", "presenca_fmt"],
        title=titulo,
        labels={
            "renda_media": "Renda Média (salários mínimos)",
            "nota_media": "Nota Média",
            "presenca": "Presença",
            "escola": "Tipo de Escola",
            nivel_geo: rotulo_geo
        },
        size_max=20,
        opacity=0.7
    )

    fig.update_traces(
        hovertemplate=(
            f"<b>{rotulo_geo}:</b> %{{hovertext}}<br>"
            "<b>Escola:</b> %{customdata[0]}<br>"
            "<b>Participantes:</b> %{customdata[1]}<br>"
            "<b>Renda Média:</b> %{customdata[2]}<br>"
            "<b>Nota Média:</b> %{customdata[3]}<br>"
            "<b>Presença:</b> %{customdata[4]}<br>"
            "<extra></extra>"
        )
    )

    # ---------------------------------------------------------
    # 7) Tendência ponderada e R² ponderado
    # ---------------------------------------------------------
    r_quadrado = 0.0

    x = df_bolha["renda_media"].to_numpy(dtype=float)
    y = df_bolha["nota_media"].to_numpy(dtype=float)
    w = df_bolha[weight_col].to_numpy(dtype=float)

    mascara = np.isfinite(x) & np.isfinite(y) & np.isfinite(w) & (w > 0)

    if mascara.sum() > 1 and np.unique(x[mascara]).size > 1:
        xw = x[mascara]
        yw = y[mascara]
        ww = w[mascara]

        coef = np.polyfit(xw, yw, 1, w=ww)
        p = np.poly1d(coef)

        x_line = np.linspace(xw.min(), xw.max(), 100)
        y_line = p(x_line)

        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name="Tendência ponderada",
                line=dict(color="red", width=2, dash="dash"),
                hovertemplate=f"Tendência ponderada: y = {coef[0]:.2f}x + {coef[1]:.2f}<extra></extra>"
            )
        )

        media_x = np.average(xw, weights=ww)
        media_y = np.average(yw, weights=ww)
        cov_xy = np.average((xw - media_x) * (yw - media_y), weights=ww)
        var_x = np.average((xw - media_x) ** 2, weights=ww)
        var_y = np.average((yw - media_y) ** 2, weights=ww)

        if var_x > 0 and var_y > 0:
            corr_w = cov_xy / np.sqrt(var_x * var_y)
            r_quadrado = float(corr_w ** 2)

    # ---------------------------------------------------------
    # 8) Linhas de referência
    # ---------------------------------------------------------
    renda_mediana = df_bolha["renda_media"].median()
    nota_mediana = df_bolha["nota_media"].median()

    fig.add_hline(
        y=nota_mediana,
        line_dash="dot",
        line_color="gray",
        opacity=0.5,
        annotation_text=f"Mediana Nota: {formatar_decimal_br(nota_mediana, 1)}",
        annotation_position="top right"
    )

    fig.add_vline(
        x=renda_mediana,
        line_dash="dot",
        line_color="gray",
        opacity=0.5,
        annotation_text=f"Mediana Renda: {formatar_decimal_br(renda_mediana, 1)}",
        annotation_position="top right"
    )

    # ---------------------------------------------------------
    # 9) Layout
    # ---------------------------------------------------------
    y_max = df_bolha["nota_media"].max() * 1.1 if not df_bolha.empty else 700

    fig.update_layout(
        height=400,
        width=700,
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(size=18, family="Arial")
        ),
        #template="plotly_white",
        hovermode="closest",
        yaxis=dict(
            range=[0, y_max],
            title="Nota Média"
        ),
        legend=dict(
            x=0.9,
            y=0.6,
            xanchor="right",
            yanchor="top",
            bordercolor="lightgray",
            #bgcolor="rgba(255,255,255,0.95)",
            borderwidth=1
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="Taxa de Presença<br>dias de Enem<br><br>",
                font=dict(size=11, family="Arial Bold, Arial, sans-serif", color="#2C3E50"),
                side="top"
            ),
            tickformat=".0%",
            x=1.02,
            y=0.5,
            len=0.8,
            thickness=20
        ),
        margin=dict(l=80, r=80, t=80, b=60)
    )

    fig.update_coloraxes(cmin=0.5, cmax=1.0)


    texto_nota = (
        f" <b>R² = {formatar_decimal_br(r_quadrado * 100, 1)}%</b><br><br>"
        f"• Indica a variância das notas associada à renda familiar,<br>"
        f" * trata-se de associação, não causalidade;<br>"
        f" * os dados são agregados por perfil;<br>"
        f" * outros fatores não incluídos podem influenciar o desempenho;<br>"
    )

    fig.add_annotation(
        x=0.5, y=0.08,
        xanchor="center",        
        xref="paper", yref="paper",
        text=texto_nota,
        showarrow=False,
        font=dict(size=12 ),
        align="left",
        bordercolor="dimgrey",
        borderwidth=1,
        borderpad=8,
        bgcolor="rgba(255,255,255,0.30)",
        width=400,
    )

    return fig, df_bolha, r_quadrado
    

def grafico_nota_media_por_categoria_escola_ano(
    df: pd.DataFrame,
    categoria: str,
    escopo: str = "mg",
    ano_selecionado: Optional[str] = None,
    filtro_geo: Optional[str] = None,
    weight_col: str = "participantes",
    titulo: Optional[str] = None
) -> Tuple[Optional[go.Figure], pd.DataFrame]:
    """
    Gera gráfico de barras agrupadas com facet por ano para mostrar
    a nota média ponderada por:
    - categoria
    - tipo de escola
    - ano
    """

    # ---------------------------------------------------------
    # validação
    # ---------------------------------------------------------
    colunas_notas = ["nota_cn", "nota_ch", "nota_lc", "nota_mt", "nota_redacao"]
    colunas_notas_existentes = [c for c in colunas_notas if c in df.columns]

    colunas_necessarias = {"ano", "escola", categoria, weight_col}
    faltantes = colunas_necessarias - set(df.columns)

    if faltantes:
        raise KeyError(f"Colunas ausentes no DataFrame: {sorted(faltantes)}")

    if "nota_media" not in df.columns and not colunas_notas_existentes:
        raise KeyError("Nem 'nota_media' nem colunas de nota por área foram encontradas no DataFrame.")

    # ---------------------------------------------------------
    # filtros
    # ---------------------------------------------------------
    df_filtrado = aplicar_filtros_dashboard(
        df=df,
        escopo=escopo,
        ano_selecionado=ano_selecionado,
        filtro_geo=filtro_geo
    ).copy()

    if df_filtrado.empty:
        return None, pd.DataFrame()

    # ---------------------------------------------------------
    # limpeza
    # ---------------------------------------------------------
    df_filtrado["ano"] = df_filtrado["ano"].astype(str)
    df_filtrado["escola"] = df_filtrado["escola"].astype(str).str.strip()
    df_filtrado[categoria] = df_filtrado[categoria].astype(str).str.strip()
    df_filtrado[weight_col] = pd.to_numeric(df_filtrado[weight_col], errors="coerce")

    df_filtrado = df_filtrado[
        ~df_filtrado["escola"].str.lower().isin(["não respondeu", "não informada"])
    ].copy()

    df_filtrado = df_filtrado.dropna(subset=["ano", "escola", categoria, weight_col])
    df_filtrado = df_filtrado[df_filtrado[weight_col] > 0]

    if df_filtrado.empty:
        return None, pd.DataFrame()

    # ---------------------------------------------------------
    # nota da linha: usa nota_media pronta quando existir
    # ---------------------------------------------------------
    if "nota_media" in df_filtrado.columns:
        df_filtrado["nota_media_base"] = pd.to_numeric(df_filtrado["nota_media"], errors="coerce")
    else:
        for col in colunas_notas_existentes:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors="coerce")
        df_filtrado["nota_media_base"] = df_filtrado[colunas_notas_existentes].mean(axis=1)

    df_filtrado = df_filtrado.dropna(subset=["nota_media_base", weight_col])

    if df_filtrado.empty:
        return None, pd.DataFrame()

    # ---------------------------------------------------------
    # agregação ponderada
    # ---------------------------------------------------------
    df_filtrado["nota_x_peso"] = df_filtrado["nota_media_base"] * df_filtrado[weight_col]

    df_plot = (
        df_filtrado
        .groupby(["ano", categoria, "escola"], observed=True, as_index=False)
        .agg(
            soma_nota_ponderada=("nota_x_peso", "sum"),
            participantes=(weight_col, "sum")
        )
    )

    df_plot = df_plot[df_plot["participantes"] > 0].copy()
    df_plot["nota_media_ponderada"] = (
        df_plot["soma_nota_ponderada"] / df_plot["participantes"]
    ).round(2)

    df_plot = df_plot.drop(columns=["soma_nota_ponderada"])

    if df_plot.empty:
        return None, df_plot

    # ---------------------------------------------------------
    # ordenação
    # ---------------------------------------------------------
    ordem_categoria = obter_ordem_padrao(categoria)
    if ordem_categoria is None:
        ordem_categoria = sorted(df_plot[categoria].dropna().astype(str).unique())

    df_plot[categoria] = pd.Categorical(
        df_plot[categoria],
        categories=ordem_categoria,
        ordered=True
    )

    df_plot["escola"] = pd.Categorical(
        df_plot["escola"],
        categories=ORDEM_ESCOLA,
        ordered=True
    )

    ordem_anos = [a for a in ORDEM_ANOS if a in df_plot["ano"].astype(str).unique()] if "ORDEM_ANOS" in globals() else sorted(df_plot["ano"].astype(str).unique())
    df_plot["ano"] = pd.Categorical(df_plot["ano"], categories=ordem_anos, ordered=True)

    df_plot = df_plot.sort_values(["ano", categoria, "escola"]).reset_index(drop=True)

    # ---------------------------------------------------------
    # formatação
    # ---------------------------------------------------------
    df_plot = adicionar_colunas_hover_br(
        df_plot,
        {
            "nota_media_ponderada_fmt": ("nota_media_ponderada", 1, "decimal"),
            "participantes_fmt": ("participantes", 0, "numero")
        }
    )

    nome_categoria = NOMES_AMIGAVEIS.get(categoria, categoria.replace("_", " ").title())
    nome_escopo = obter_nome_escopo(escopo)
    complemento_filtro = montar_complemento_filtro_geo(escopo, filtro_geo)

    if titulo is None:
        titulo_final = (
            f"Nota Média Ponderada por {nome_categoria}, "
            f"Escola e Ano - {nome_escopo}{complemento_filtro}"
        )
    else:
        titulo_final = titulo

    # ---------------------------------------------------------
    # gráfico
    # ---------------------------------------------------------
    fig = px.bar(
        df_plot,
        x=categoria,
        y="nota_media_ponderada",
        color="escola",
        barmode="group",
        facet_col="ano",
        title=titulo_final,
        labels={
            categoria: nome_categoria,
            "nota_media_ponderada": "Nota Média Ponderada",
            "escola": "Tipo de Escola"
        },
        color_discrete_map=MAPA_CORES_ESCOLA,
        custom_data=["participantes_fmt", "nota_media_ponderada_fmt"],
        category_orders={
            categoria: ordem_categoria,
            "escola": ORDEM_ESCOLA,
            "ano": ordem_anos
        }
    )

    y_min = max(0, float(df_plot["nota_media_ponderada"].min()) - 20)
    y_max = float(df_plot["nota_media_ponderada"].max()) + 20

    fig.update_layout(
        width=980,
        height=500,
        title=dict(
            x=0.5,
            y=0.95,
            xanchor="center",
            font=dict(size=18, color="#4a4a4a")
        ),
        legend_title="Tipo de Escola",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            font=dict(color="#4a4a4a")
        ),
        separators=".,"
    )

    fig.update_traces(
        hovertemplate=(
            f"<b>{nome_categoria}:</b> %{{x}}<br>"
            "<b>Escola:</b> %{fullData.name}<br>"
            "<b>Nota Média Ponderada:</b> %{customdata[1]}<br>"
            "<b>Participantes:</b> %{customdata[0]}<extra></extra>"
        )
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_xaxes(
        tickangle=-45,
        title=None,
        showgrid=False,
        tickfont=dict(color="#4a4a4a")
    )

    fig.update_yaxes(
        title=None,
        showgrid=True,
        gridcolor="lightgray",
        tickfont=dict(color="#4a4a4a"),
        range=[y_min, y_max]
    )

    return fig, df_plot


def _normalizar_tamanho_bolha(
    valores: pd.Series,
    tamanho_min: int = 12,
    tamanho_max: int = 30
) -> pd.Series:
    vmin = valores.min()
    vmax = valores.max()

    if pd.isna(vmin) or pd.isna(vmax):
        return pd.Series([tamanho_min] * len(valores), index=valores.index)

    if vmax == vmin:
        return pd.Series(
            [((tamanho_min + tamanho_max) / 2)] * len(valores),
            index=valores.index
        )

    return ((valores - vmin) / (vmax - vmin)) * (tamanho_max - tamanho_min) + tamanho_min


def _texto_bolha_br(mapa: pd.DataFrame, coluna_valor: str, nome_legivel: str) -> pd.Series:
    return (
        mapa["label_geo"].astype(str)
        + "<br>"
        + nome_legivel
        + ": "
        + mapa[coluna_valor].apply(lambda x: formatar_decimal_br(x, 1))
    )


def _padronizar_nome_regiao_mg(serie: pd.Series) -> pd.Series:
    """
    Padroniza nomes da coluna 'regiao' para casar com o shape do geobr.
    Ajuste este dicionário se algum nome do seu shape vier diferente.
    """
    mapa_nomes = {
        "Metrop. de Belo Horizonte": "Metropolitana de Belo Horizonte",
        "Triâng. Min. e Alto Paran.": "Triângulo Mineiro e Alto Paranaíba",
        "Sul de Minas": "Sul/Sudoeste de Minas",
        "Sudoeste de Minas": "Sul/Sudoeste de Minas",
        "Centro de Minas": "Central Mineira",
        "Vale do Rio Doce": "Vale do Rio Doce",
        "Vale do Jequitinhonha": "Jequitinhonha",
        "Vale do Mucuri": "Vale do Mucuri",
        "Campo das Vertentes": "Campo das Vertentes",
        "Noroeste de Minas": "Noroeste de Minas",
        "Norte de Minas": "Norte de Minas",
        "Oeste de Minas": "Oeste de Minas",
        "Zona da Mata": "Zona da Mata",
    }
    return serie.replace(mapa_nomes)

def _agregar_notas_geograficas(
    df: pd.DataFrame,
    coluna_geo: str,
    weight_col: str = "participantes"
) -> pd.DataFrame:
    """
    Reagrega as notas no nível geográfico desejado usando média ponderada.

    Parameters
    ----------
    df : pd.DataFrame
        Base agregada.
    coluna_geo : str
        Coluna geográfica para reagregação.
    weight_col : str, default='participantes'
        Coluna de peso.

    Returns
    -------
    pd.DataFrame
        DataFrame com notas reagregadas por geografia.
    """
    colunas_notas = [
        "nota_media",
        "nota_cn",
        "nota_ch",
        "nota_lc",
        "nota_mt",
        "nota_redacao",
    ]

    colunas_existentes = [c for c in colunas_notas if c in df.columns]

    if not colunas_existentes:
        raise ValueError("O DataFrame não possui colunas de notas para agregação.")

    if coluna_geo not in df.columns:
        raise ValueError(f"A coluna geográfica '{coluna_geo}' não existe no DataFrame.")

    if weight_col not in df.columns:
        raise ValueError(f"A coluna de peso '{weight_col}' não existe no DataFrame.")

    registros = []

    for geo in df[coluna_geo].dropna().unique():
        df_geo = df[df[coluna_geo] == geo].copy()

        registro = {"chave_geo": geo}

        for col in colunas_existentes:
            registro[col] = media_ponderada(df_geo, col, weight_col)

        registro[weight_col] = pd.to_numeric(df_geo[weight_col], errors="coerce").sum()
        registros.append(registro)

    return pd.DataFrame(registros)


def df_mapa_nota_enem(
    df_notas: pd.DataFrame,
    nivel_geografico: str = "uf",
    weight_col: str = "participantes"
) -> gpd.GeoDataFrame:
    """
    Prepara GeoDataFrame com médias ponderadas das notas e centróides para plotagem.

    Parâmetros
    ----------
    df_notas : pd.DataFrame
        Base agregada de notas.
    nivel_geografico : str
        'uf'        -> Brasil por UF
        'mg'        -> Minas Gerais como um único polígono
        'regiao_mg' -> regiões de Minas Gerais
    weight_col : str, default='participantes'
        Coluna de peso usada para reagregação.
    """
    
    df_aux = df_notas.copy()

    if nivel_geografico == "uf":
        if "uf" not in df_aux.columns:
            raise ValueError("A base precisa ter a coluna 'uf' para nivel_geografico='uf'.")

        medias_geo = _agregar_notas_geograficas(df_aux, "uf", weight_col=weight_col)

        mapa = geobr.read_state(year=2020)
        mapa = mapa.merge(
            medias_geo,
            left_on="abbrev_state",
            right_on="chave_geo",
            how="inner"
        )

        mapa["label_geo"] = mapa["abbrev_state"]
        mapa["titulo_geo"] = "UF"

    elif nivel_geografico == "mg":
        if "uf" not in df_aux.columns:
            raise ValueError("A base precisa ter a coluna 'uf' para nivel_geografico='mg'.")

        df_mg = df_aux[df_aux["uf"].astype(str) == "MG"].copy()

        if df_mg.empty:
            raise ValueError("Não há registros de MG na base.")

        colunas_notas = [
            "nota_media",
            "nota_cn",
            "nota_ch",
            "nota_lc",
            "nota_mt",
            "nota_redacao",
        ]

        colunas_existentes = [col for col in colunas_notas if col in df_mg.columns]

        medias_mg = {
            col: [media_ponderada(df_mg, col, weight_col)]
            for col in colunas_existentes
        }
        medias_mg[weight_col] = [pd.to_numeric(df_mg[weight_col], errors="coerce").sum()]

        medias_mg = pd.DataFrame(medias_mg)

        mapa = geobr.read_state(code_state="MG", year=2020)
        mapa = pd.concat([mapa.reset_index(drop=True), medias_mg], axis=1)

        mapa["label_geo"] = "MG"
        mapa["titulo_geo"] = "Minas Gerais"

    elif nivel_geografico == "regiao_mg":
        if "uf" not in df_aux.columns or "regiao" not in df_aux.columns:
            raise ValueError(
                "A base precisa ter as colunas 'uf' e 'regiao' para nivel_geografico='regiao_mg'."
            )

        df_mg = df_aux[df_aux["uf"].astype(str) == "MG"].copy()

        if df_mg.empty:
            raise ValueError("Não há registros de MG na base.")

        medias_geo = _agregar_notas_geograficas(df_mg, "regiao", weight_col=weight_col)
        medias_geo = medias_geo.rename(columns={"chave_geo": "regiao_original"})
        medias_geo["chave_geo"] = medias_geo["regiao_original"]

        mapa = geobr.read_meso_region(code_meso="MG", year=2020)

        colunas_candidatas = ["name_meso_region", "name_meso", "name", "name_region"]
        col_shape = next((c for c in colunas_candidatas if c in mapa.columns), None)

        if col_shape is None:
            raise ValueError(
                f"Não encontrei a coluna de nome da região no shape. Colunas disponíveis: {list(mapa.columns)}"
            )

        medias_geo["chave_norm"] = medias_geo["chave_geo"].astype(str).apply(_normalizar_texto_regiao)
        mapa["chave_norm"] = mapa[col_shape].astype(str).apply(_normalizar_texto_regiao)

        mapa = mapa.merge(
            medias_geo,
            on="chave_norm",
            how="inner"
        )

        mapa["label_geo"] = mapa[col_shape]
        mapa["titulo_geo"] = "Regiões de Minas Gerais"

    else:
        raise ValueError("Use 'uf', 'mg' ou 'regiao_mg'.")

    # ---------------------------------------------------------
    # centróides
    # ---------------------------------------------------------
    mapa = mapa.to_crs(5880)
    centroids = mapa.geometry.centroid
    centroids_4326 = centroids.to_crs(4326)

    mapa["lon"] = centroids_4326.x
    mapa["lat"] = centroids_4326.y
    mapa = mapa.to_crs(4326)

    return mapa

def gerar_mapa_enem(
    df_notas: pd.DataFrame,
    nivel_geografico: str = "uf",
    weight_col: str = "participantes",
    ano_selecionado: Optional[str] = None
) -> go.Figure:
    """
    Gera mapa interativo com médias ponderadas do ENEM
    e menu suspenso para trocar a disciplina.
    """
    # ---------------------------------------------------------
    # filtro por ano
    # ---------------------------------------------------------
    if ano_selecionado is not None and "ano" in df_notas.columns:
        df_notas = df_notas[
            df_notas["ano"].astype(str) == str(ano_selecionado)
            ].copy()
        
    mapa = df_mapa_nota_enem(
        df_notas,
        nivel_geografico=nivel_geografico,
        weight_col=weight_col
    )

    materias_dict = {
        "nota_media": "Nota Média",
        "nota_mt": "Matemática",
        "nota_lc": "Linguagens",
        "nota_ch": "Ciências Humanas",
        "nota_cn": "Ciências da Natureza",
        "nota_redacao": "Redação",
    }

    titulo_geo = mapa["titulo_geo"].iloc[0]

    fig = go.Figure()

    # fronteiras
    for _, row in mapa.iterrows():
        geom = row.geometry

        if geom.geom_type == "Polygon":
            x, y = geom.exterior.xy
            fig.add_trace(
                go.Scattergeo(
                    lon=list(x),
                    lat=list(y),
                    mode="lines",
                    line=dict(width=0.7, color="gray"),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

        elif geom.geom_type == "MultiPolygon":
            for polygon in geom.geoms:
                x, y = polygon.exterior.xy
                fig.add_trace(
                    go.Scattergeo(
                        lon=list(x),
                        lat=list(y),
                        mode="lines",
                        line=dict(width=0.7, color="gray"),
                        hoverinfo="none",
                        showlegend=False,
                    )
                )

    # camada inicial de bolhas
    materia_inicial = "nota_media"
    nome_inicial = materias_dict[materia_inicial]
    valores = mapa[materia_inicial]
    sizes = _normalizar_tamanho_bolha(valores)
    texto_inicial = _texto_bolha_br(mapa, materia_inicial, nome_inicial)

    fig.add_trace(
        go.Scattergeo(
            lon=mapa["lon"],
            lat=mapa["lat"],
            mode="markers",
            text=texto_inicial,
            marker=dict(
                size=sizes,
                color=valores,
                colorscale="RdYlGn",
                cmin=valores.min(),
                cmax=valores.max(),
                colorbar=dict(title="Nota"),
                line=dict(width=0.5, color="black"),
                opacity=0.88,
            ),
            hovertemplate="<b>%{text}</b><extra></extra>",
            showlegend=False,
            name=nome_inicial,
        )
    )

    idx_bolha = len(fig.data) - 1

    buttons = []
    for materia, nome_legivel in materias_dict.items():
        valores = mapa[materia]
        sizes = _normalizar_tamanho_bolha(valores)
        texto = _texto_bolha_br(mapa, materia, nome_legivel)

        buttons.append(
            dict(
                method="restyle",
                label=nome_legivel,
                args=[
                    {
                        "marker.color": [valores],
                        "marker.size": [sizes],
                        "marker.cmin": [valores.min()],
                        "marker.cmax": [valores.max()],
                        "text": [texto],
                        "name": [nome_legivel],
                    },
                    [idx_bolha],
                ],
            )
        )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
    )
    
    label_ano = f" ({ano_selecionado})" if ano_selecionado else ""
    
    fig.update_layout(
        title=dict( 
            text=f"{nome_inicial} por {titulo_geo} (ENEM){label_ano}",
            font=dict(
                size=18,
                family="Arial Bold, Arial, sans-serif",
                color="#2C3E50"
            ),
            x=0.5,
            xanchor="center",
        ),
        height=650,
        width=900,
        margin=dict(l=20, r=20, t=60, b=20),
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                x=0.05,
                y=0.92,
                showactive=True,
                #bgcolor="white",
                bordercolor="gray",
                font=dict(size=13),
            )
        ],
        geo=dict(
            showcountries=False,
            showcoastlines=True,
            coastlinecolor="LightGray",
        ),
    )

    return fig