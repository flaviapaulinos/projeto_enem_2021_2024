"""
src/processamento/agregacoes.py
===============================

Funções de transformação e recodificação (nível microdados).
"""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd

from .categorias import (
    MAP_BENS_ABCDE,
    MAP_BENS_ABCD,
    MAP_BENS_AB,
    MAP_COR_RACA,
    MAP_EMP_DOMST,
    MAP_ESCOLA,
    MAP_DADOS_ESCOLA_2024,
    MAP_RESULTADOS_ESCOLA_2024,
    MAP_ESCOLARIDADE,
    MAP_ESTADO_CIVIL,
    MAP_FAIXA_ETARIA,
    MAP_LINGUA,
    MAP_OCUP,
    MAP_SAL_MIN_POR_LETRA,
    MAP_SEXO,
    MAP_ESCOLARIDADE_REV,
    MAP_OCUP_REV,
    
)


def agregar_perfil_socioeconomico(
    df: pd.DataFrame,
    cols_agg: list[str],
    incluir_ordinal_media: bool = False,
    incluir_escola_num_pais_media: bool = False,
) -> pd.DataFrame:
    """
    Agrega o perfil socioeconômico por grupos definidos em `cols_agg`.

    Parameters
    ----------
    df : pd.DataFrame
        Base de dados socioeconômica.
    cols_agg : list[str]
        Colunas utilizadas para agrupamento.
    incluir_ordinal_media : bool, default=False
        Se True, inclui médias arredondadas das variáveis ordinais
        `escolaridade_pai`, `escolaridade_mae`, `ocup_pai` e `ocup_mae`.
        Útil para a versão numérica da base merged.

    Returns
    -------
    pd.DataFrame
        DataFrame agregado com estatísticas socioeconômicas.
    """
    base = df.copy()

    for col in cols_agg:
        if col in base.columns and base[col].dtype.name == "category":
            base[col] = base[col].cat.remove_unused_categories()

    agregacoes = {
        "participantes": ("uf", "count"),
        "cel": ("cel", "mean"),
        "comptdr": ("comptdr", "mean"),
        "n_pessoas_resd": ("n_pessoas_resd", "mean"),
        "renda_media": ("renda_media", "mean"),
        "indice_consumo": ("indice_consumo", "mean"),
    }

    if incluir_ordinal_media:
        agregacoes.update(
            {
                "escolaridade_pai": ("escolaridade_pai", lambda x: round(x.mean())),
                "escolaridade_mae": ("escolaridade_mae", lambda x: round(x.mean())),
                "ocup_pai": ("ocup_pai", lambda x: round(x.mean())),
                "ocup_mae": ("ocup_mae", lambda x: round(x.mean())),
            }
        )

    if incluir_escola_num_pais_media:
        agregacoes.update(
            {
                "escola_num": ("escola_num", "mean"),
                "escolaridade_pais_media": ("escolaridade_mae", "mean"),
                "ocup_pais_media": ("ocup_pai", "mean"),
               
            }
        )

    df_agg = (
        base.groupby(cols_agg, observed=True, dropna=False)
        .agg(**agregacoes)
        .reset_index()
    )

    df_agg = df_agg[df_agg["participantes"] > 0]
    return df_agg

def agrupar_notas(df: pd.DataFrame, grupo_cols: list[str] = ["ano", "uf", "escola"], 
                  incluir_regiao: bool = False, incluir_municipio:bool=False) -> pd.DataFrame:
    """
    Agrega notas e métricas de presença por grupos.

    Parameters
    ----------
    df : pd.DataFrame
        Base de resultados tratada.
    grupo_cols : list[str], default=["uf", "escola"]
        Colunas base para agregação.
    incluir_regiao : bool, default=False
        Se True, tenta incluir 'regiao' no agrupamento se a coluna existir.

    Returns
    -------
    pd.DataFrame
        DataFrame agregado com estatísticas de notas, inscritos,
        faltosos e taxas de presença.
    """
    # Define as colunas de agrupamento
    cols_agrupamento = grupo_cols.copy()
    
    # Se solicitado, tenta incluir região
    if incluir_regiao and 'regiao' in df.columns:
        if 'regiao' not in cols_agrupamento:
            cols_agrupamento.append('regiao')

    # Se solicitado, tenta incluir ano na análise de município
    if incluir_municipio and 'municipio' in df.columns:
        if 'municipio' not in cols_agrupamento:
            cols_agrupamento.append('municipio')
    
    # Verifica se todas as colunas de grupo existem no DataFrame
    missing_cols = [col for col in cols_agrupamento if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas não encontradas no DataFrame: {missing_cols}")
    
    # Resto da função permanece igual, usando cols_agrupamento
    df_ag = (
        df.groupby(cols_agrupamento, observed=True)
        .agg(
            nota_media=("nota_media", "mean"),
            nota_cn=("nota_cn", "mean"),
            nota_cn_max=("nota_cn", "max"),
            nota_ch=("nota_ch", "mean"),
            nota_ch_max=("nota_ch", "max"),
            nota_lc=("nota_lc", "mean"),
            nota_lc_max=("nota_lc", "max"),
            nota_mt=("nota_mt", "mean"),
            nota_mt_max=("nota_mt", "max"),
            nota_redacao=("nota_redacao", "mean"),
            nota_redacao_max=("nota_redacao", "max"),
            desvio_padrao=("nota_media", "std"),
            participantes=("uf", "count"),
        )
        .round(2)
        .reset_index()
    )

    faltas = (
        df.groupby(cols_agrupamento, observed=True)
        .agg(
            inscritos=("nota_lc", "size"),
            faltosos_dia1=("nota_lc", lambda x: x.isna().sum()),
            faltosos_dia2=("nota_mt", lambda x: x.isna().sum()),
        )
        .reset_index()
    )

    faltas["presentes_dia1"] = faltas["inscritos"] - faltas["faltosos_dia1"]
    faltas["presentes_dia2"] = faltas["inscritos"] - faltas["faltosos_dia2"]
    
    faltas["taxa_presenca_dia1"] = (faltas["presentes_dia1"] / faltas["inscritos"]).round(4)
    faltas["taxa_presenca_dia2"] = (faltas["presentes_dia2"] / faltas["inscritos"]).round(4)
    
    faltas[["taxa_presenca_dia1", "taxa_presenca_dia2"]] = faltas[
        ["taxa_presenca_dia1", "taxa_presenca_dia2"]
    ].fillna(0)

    final = df_ag.merge(faltas, on=cols_agrupamento, how="left")
    
    return final



def amostrar_por_percentil_original(
    df: pd.DataFrame,
    coluna_nota: str = "nota_media",
    escopo: str = "mg",
    n_por_percentil: int = 150,
    q: int = 20,
    random_state: int = 42,
    manter_coluna_percentil: bool = False
) -> pd.DataFrame:
    """
    Gera uma amostra estratificada preservando distribuição de notas
    e estrutura geográfica do conjunto de dados, retornando todas as
    colunas originais do DataFrame.

    A amostragem ocorre em duas etapas:
    1. Estratificação geográfica e institucional.
    2. Estratificação por percentis da variável de nota dentro de cada grupo.

    Estratos utilizados:
    - escopo='br' -> ano × uf × escola
    - escopo='mg' -> ano × regiao × escola
    - demais casos -> ano × escola

    Dentro de cada estrato são criadas faixas de percentil da nota
    (`q` quantis) e uma amostra de tamanho máximo `n_por_percentil`
    é extraída de cada faixa.

    Essa abordagem preserva simultaneamente:
    - distribuição das notas
    - diferenças regionais
    - diferenças entre escola pública e privada
    - evolução temporal

    Parameters
    ----------
    df : pd.DataFrame
        Base de dados original contendo as notas do ENEM.
        Espera-se que contenha pelo menos:
        - 'ano'
        - coluna_nota
        - 'escola'
        além de:
        - 'uf' (para escopo='br')
        - 'regiao' (para escopo='mg')

        Todas as colunas originais são preservadas no resultado final.

    coluna_nota : str, default="nota_media"
        Coluna utilizada para calcular os percentis de estratificação.

    escopo : str, default="mg"
        Define o nível geográfico da amostragem.
        - 'br' -> estratificação por ano × uf × escola
        - 'mg' -> estratificação por ano × regiao × escola
        - demais casos -> estratificação por ano × escola

    n_por_percentil : int, default=150
        Número máximo de observações amostradas dentro de cada faixa
        de percentil para cada estrato geográfico.

    q : int, default=20
        Número de faixas de percentil (quantis) criadas dentro de cada
        estrato geográfico.

    random_state : int, default=42
        Semente para reprodutibilidade da amostragem.

    manter_coluna_percentil : bool, default=False
        Se True, mantém a coluna auxiliar 'percentil' no resultado final.

    Returns
    -------
    pd.DataFrame
        DataFrame contendo a amostra estratificada com todas as colunas
        originais do DataFrame de entrada.
    """
    if coluna_nota not in df.columns:
        raise ValueError(f"A coluna '{coluna_nota}' não existe no DataFrame.")

    # Definir estratos geográficos
    if escopo == "mg" and "regiao" in df.columns:
        colunas_estrato = ["ano", "regiao", "escola"]
    elif escopo == "br" and "uf" in df.columns:
        colunas_estrato = ["ano", "uf", "escola"]
    else:
        colunas_estrato = ["ano", "escola"]

    # Usar apenas colunas mínimas para selecionar a amostra,
    # mas guardando o índice original para recuperar o dataframe completo depois
    colunas_necessarias = list(dict.fromkeys(colunas_estrato + [coluna_nota]))
    df_base = df.loc[:, colunas_necessarias].copy()
    df_base["_idx_original"] = df.index
    df_base = df_base.dropna(subset=[coluna_nota])

    if df_base.empty:
        return pd.DataFrame(columns=df.columns)

    amostras_idx = []

    for _, grupo in df_base.groupby(colunas_estrato, observed=True, sort=False):
        tamanho_grupo = len(grupo)

        # Grupo muito pequeno: leva tudo
        if tamanho_grupo <= n_por_percentil:
            bloco = grupo[["_idx_original"]].copy()
            if manter_coluna_percentil:
                bloco["percentil"] = pd.NA
            amostras_idx.append(bloco)
            continue

        nunique_nota = grupo[coluna_nota].nunique(dropna=True)

        # Se quase não há variação, amostra simples do grupo
        if nunique_nota <= 1:
            bloco = grupo.sample(
                n=min(n_por_percentil, tamanho_grupo),
                random_state=random_state
            )[["_idx_original"]].copy()

            if manter_coluna_percentil:
                bloco["percentil"] = pd.NA

            amostras_idx.append(bloco)
            continue

        q_efetivo = min(q, nunique_nota, tamanho_grupo)

        grupo_tmp = grupo.copy()
        try:
            grupo_tmp["percentil"] = pd.qcut(
                grupo_tmp[coluna_nota],
                q=q_efetivo,
                labels=False,
                duplicates="drop"
            )
        except ValueError:
            bloco = grupo.sample(
                n=min(n_por_percentil, tamanho_grupo),
                random_state=random_state
            )[["_idx_original"]].copy()

            if manter_coluna_percentil:
                bloco["percentil"] = pd.NA

            amostras_idx.append(bloco)
            continue

        for perc, subgrupo in grupo_tmp.groupby("percentil", observed=True, sort=False):
            if subgrupo.empty:
                continue

            n_amostra = min(n_por_percentil, len(subgrupo))
            amostra = subgrupo.sample(n=n_amostra, random_state=random_state)[["_idx_original"]].copy()

            if manter_coluna_percentil:
                amostra["percentil"] = perc

            amostras_idx.append(amostra)

    if not amostras_idx:
        return pd.DataFrame(columns=df.columns)

    df_indices = pd.concat(amostras_idx, ignore_index=True)

    # Recuperar linhas completas do dataframe original
    resultado = df.loc[df_indices["_idx_original"]].copy()

    if manter_coluna_percentil:
        resultado = resultado.reset_index().rename(columns={"index": "_idx_original"})
        resultado = resultado.merge(df_indices, on="_idx_original", how="left")
        resultado = resultado.drop(columns="_idx_original")
    else:
        resultado = resultado.reset_index(drop=True)

    return resultado

def categoria_ordenada_para_numero(serie: pd.Series) -> pd.Series:
    """
    Converte uma categoria ordenada em códigos numéricos.

    Parameters
    ----------
    serie : pd.Series
        Série categórica ordenada.

    Returns
    -------
    pd.Series
        Série numérica com códigos da categoria. Valores ausentes
        permanecem como NA.
    """
    codigos = serie.cat.codes.replace(-1, pd.NA)
    return codigos.astype("Int16")
    
    
def recodificar_microdados_enem(
    df: pd.DataFrame,
    *,
    schema_escola: Literal["auto", "enem_2021_2023", "dados_2024", "resultados_2024"] = "auto",
    col_bens_ab: Optional[Iterable[str]] = None,
    col_bens_abcd: Optional[Iterable[str]] = None,
    col_bens_abcde: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Recodifica microdados ENEM (já renomeados) em categorias interpretáveis
    e variáveis numéricas padronizadas.

    Observação importante:
    - A coluna `escola` muda de codificação em 2024 dependendo do arquivo:
      - dados_2024 (participantes): letras A..F
      - resultados_2024: inteiros 1..4 (dependência administrativa)
      - 2021–2023: inteiros 1..3 (TP_ESCOLA)
    """

    df = df.copy()

    # ----------------------------
    # Helpers
    # ----------------------------
    def _map_para_texto(col: str, mapa: dict, default: str) -> None:
        """Mapeia coluna numérica -> texto (string) com coerção segura."""
        if col not in df.columns:
            return
        s = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("Int16")
        df[col] = s.map(mapa).fillna(default).astype("string")

    def _map_letra_para_texto(col: str, mapa: dict, default: str) -> None:
        """Mapeia coluna letra -> texto (string)."""
        if col not in df.columns:
            return
        s = df[col].astype("string")
        df[col] = s.map(mapa).fillna(default).astype("string")

    def _map_letra_para_int(col: str, mapa: dict) -> None:
        """Mapeia letra -> inteiro (Int16), mantendo <NA> quando não mapear."""
        if col not in df.columns:
            return
        s = df[col].astype("string")
        out = s.map(mapa)
        df[col] = pd.to_numeric(out, errors="coerce").astype("Int16")

    # ----------------------------
    # Categóricas gerais
    # ----------------------------
    _map_letra_para_texto("sexo", MAP_SEXO, default="não informado")
    _map_para_texto("cor_raca", MAP_COR_RACA, default="não informada")
    _map_para_texto("estado_civil", MAP_ESTADO_CIVIL, default="não informado")
    _map_para_texto("lingua", MAP_LINGUA, default="inglês")

    if "faixa_etaria" in df.columns:
        s = pd.to_numeric(df["faixa_etaria"], errors="coerce").fillna(0).astype("Int16")
        df["faixa_etaria"] = s.map(MAP_FAIXA_ETARIA).fillna("não informado").astype("string")

    # ----------------------------
    # Escola (tratamento por contexto)
    # ----------------------------
    if "escola" in df.columns:
        escola_raw = df["escola"].astype("string").str.strip()

        # modo AUTO: inferir pelo “alfabeto”/faixa de valores
        if schema_escola == "auto":
            # Se tiver letras A..F, é dados_2024
            tem_letra = escola_raw.str.fullmatch(r"[A-Za-z]").fillna(False).any()
            if tem_letra:
                schema_escola_eff = "dados_2024"
            else:
                # tenta numérico
                escola_num = pd.to_numeric(escola_raw, errors="coerce")
                maxv = escola_num.max(skipna=True)
                minv = escola_num.min(skipna=True)

                if pd.notna(maxv) and pd.notna(minv):
                    # resultados_2024: 1..4
                    if minv >= 1 and maxv <= 4:
                        schema_escola_eff = "resultados_2024"
                    # 2021–2023: 1..3
                    elif minv >= 1 and maxv <= 3:
                        schema_escola_eff = "enem_2021_2023"
                    else:
                        schema_escola_eff = "enem_2021_2023"  # fallback conservador
                else:
                    schema_escola_eff = "enem_2021_2023"
        else:
            schema_escola_eff = schema_escola

        if schema_escola_eff == "dados_2024":
            df["escola"] = escola_raw.map(MAP_DADOS_ESCOLA_2024).fillna("não informada").astype("string")

        elif schema_escola_eff == "resultados_2024":
            # aqui é numérico 1..4
            _map_para_texto("escola", MAP_RESULTADOS_ESCOLA_2024, default="não informada")

        else:  # "enem_2021_2023"
            _map_para_texto("escola", MAP_ESCOLA, default="não informada")

    # ----------------------------
    # Escolaridade / Ocupação
    # ----------------------------
    for col in ("escolaridade_pai", "escolaridade_mae"):
        _map_letra_para_texto(col, MAP_ESCOLARIDADE, default="desconhecido")

    for col in ("ocup_pai", "ocup_mae"):
        _map_letra_para_texto(col, MAP_OCUP, default="desconhecido")

    # ----------------------------
    # Salário mínimo (se existir como letra A..Q)
    # ----------------------------
    # IMPORTANTE: isso só faz sentido se `sal_min` estiver como A..Q (ou `renda_mens` nos anos antigos).
    # Se em 2024 você já renomeou Q007 para sal_min e ele é letra, funciona.
    if "sal_min" in df.columns:
        s = df["sal_min"].astype("string").str.strip()
        df["sal_min"] = s.map(MAP_SAL_MIN_POR_LETRA).fillna("não informado").astype("string")

    # ----------------------------
    # Numéricos (emp_domst + bens)
    # ----------------------------
    _map_letra_para_int("emp_domst", MAP_EMP_DOMST)

    if col_bens_abcde is not None:
        for col in col_bens_abcde:
            _map_letra_para_int(col, MAP_BENS_ABCDE)

    if col_bens_abcd is not None:
        for col in col_bens_abcd:
            _map_letra_para_int(col, MAP_BENS_ABCD)

    if col_bens_ab is not None:
        for col in col_bens_ab:
            _map_letra_para_int(col, MAP_BENS_AB)

    return df

def numero_para_categoria(
    serie: pd.Series,
    mapa_rev: dict,
    categorias_ordem: list
) -> pd.Series:
    """
    Reconstrói uma série categórica ordenada a partir de códigos numéricos.
    """
    serie_cat = serie.map(mapa_rev)

    return pd.Categorical(
        serie_cat,
        categories=categorias_ordem,
        ordered=True
    )