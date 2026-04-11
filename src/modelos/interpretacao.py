"""
interpretacao.py
================

Ferramentas de interpretação estrutural
de modelos lineares aplicados à desigualdade educacional.
"""

import pandas as pd
import numpy as np

from typing import Iterable
from .pipeline import extrair_pipeline

def dataframe_coeficientes(
    coefs: Iterable,
    colunas: Iterable
) -> pd.DataFrame:
    """
    Constrói DataFrame organizado dos coeficientes estimados
    pelo modelo linear.

    A função associa cada coeficiente à feature gerada pelo
    ColumnTransformer, permitindo análise interpretativa
    direta da magnitude e do sentido dos efeitos estruturais.

    Parameters
    ----------
    coefs : array-like
        Vetor de coeficientes do estimador linear treinado
        (ex: pipeline["reg"].coef_).

    colunas : array-like
        Nomes das features transformadas retornadas por
        preprocessor.get_feature_names_out().

    Returns
    -------
    pd.DataFrame
        DataFrame indexado pelas features contendo:

        - coeficiente : valor estimado do parâmetro

    Notes
    -----
    O ordenamento é feito pelo valor do coeficiente,
    facilitando inspeção de efeitos negativos e positivos.
    """
    
    df = pd.DataFrame(
        data=coefs,
        index=colunas,
        columns=["coeficiente"],
    )
    
    return df.sort_values(by="coeficiente")

#Decompor IDE

def decompor_ide(impactos):
    """
    Decompõe o IDE mostrando a contribuição estrutural
    de cada dimensão.

    A participação estrutural é definida como:

        |impacto_dimensão| / soma(|impactos|)

    O IDE equivale à soma dos quadrados dessas participações.

    Parameters
    ----------
    impactos : pd.DataFrame
        Saída de impacto_por_dimensao()

    Returns
    -------
    pd.DataFrame
        DataFrame com participação e contribuição no IDE.
    """

    df = impactos.copy()

    total = df["impacto_total"].abs().sum()

    # participação relativa
    df["participacao"] = df["impacto_total"].abs() / total

    # contribuição ao índice (forma Herfindahl)
    df["contrib_ide"] = df["participacao"] ** 2

    ide_total = df["contrib_ide"].sum()

    df["contrib_ide_%"] = df["contrib_ide"] / ide_total * 100

    return df.sort_values("contrib_ide", ascending=False)


#Elasticidade

def elasticidade_padronizada(estimator, X):
    """
    Calcula elasticidade padronizada das features.

    Elasticidade ≈ coeficiente × desvio padrão da feature.

    Isso permite comparar impactos entre variáveis
    em diferentes escalas.

    Returns
    -------
    pd.DataFrame
        coeficiente, std_feature e elasticidade.
    """

    pipeline = extrair_pipeline(estimator)

    preprocessor = pipeline["preprocessor"]
    reg = pipeline["reg"]

    # Features já transformadas
    X_transf = preprocessor.transform(X)

    if not isinstance(X_transf, pd.DataFrame):
        X_transf = pd.DataFrame(
            X_transf,
            columns=preprocessor.get_feature_names_out()
        )

    std_features = X_transf.std()

    coef = pd.Series(
        reg.coef_,
        index=X_transf.columns,
        name="coeficiente"
    )

    elasticidade = coef * std_features

    df = pd.DataFrame({
        "coeficiente": coef,
        "std_feature": std_features,
        "elasticidade": elasticidade
    })

    return df.sort_values("elasticidade", key=np.abs, ascending=False)

def elasticidade_por_dimensao(df_elasticidades):
    """
    Agrega elasticidades por dimensão estrutural.

    Exemplo:
        one_hot__Escola_privada → Escola
    """

    df = df_elasticidades.copy()

    df["variavel_base"] = (
        df.index
        .str.split("__").str[1]
        .str.split("_").str[0]
    )

    resultado = (
        df.groupby("variavel_base")
        .agg(
            elasticidade_total=("elasticidade", lambda x: np.abs(x).sum()),
            elasticidade_media=("elasticidade", "mean"),
            n_variaveis=("elasticidade", "count")
        )
        .sort_values("elasticidade_total", ascending=False)
    )

    return resultado

#Índicie de Desigualdade Estrtural

def indice_desigualdade_estrutural(impactos: pd.DataFrame) -> tuple[float, float]:
    """
    Calcula o Índice de Desigualdade Estrutural (IDE).

    O IDE mede o grau de concentração estrutural dos impactos
    socioeconômicos estimados pelo modelo, sendo definido como:

        IDE = Σ p_i²

    onde:

        p_i = participação estrutural da dimensão i

    O índice assume valores maiores quando poucas dimensões
    concentram grande parte do impacto estrutural
    (forma equivalente ao índice de Herfindahl).

    Parameters
    ----------
    impactos : pd.DataFrame
        DataFrame produzido por `impacto_por_dimensao`,
        contendo a coluna:

        - impacto_total

    Returns
    -------
    ide : float
        Índice bruto de desigualdade estrutural.

    ide_norm : float
        IDE normalizado no intervalo [0, 1],
        ajustado pelo número de dimensões.

    Notes
    -----
    A normalização segue:

        IDE_norm = (IDE − 1/k) / (1 − 1/k)

    onde k é o número de dimensões estruturais.
    """

    p = impactos["impacto_total"]

    # participação relativa
    p = p / p.sum()

    # índice tipo Herfindahl
    ide = (p ** 2).sum()

    # normalização
    k = len(p)
    ide_norm = (ide - 1 / k) / (1 - 1 / k)

    return ide, ide_norm

# Impacto estrutural


def impacto_por_dimensao(df_coefs):
    """
    Agrega coeficientes por dimensão socioeconômica
    a partir dos nomes do ColumnTransformer.
    """

    df = df_coefs.copy().reset_index(names="feature")

    df["variavel_base"] = (
        df["feature"]
        .str.replace("one_hot__", "", regex=False)
        .str.replace("ordinal__", "", regex=False)
        .str.replace("num__", "", regex=False)
        .str.split("_")
        .str[0]
    )

    resumo = (
        df.groupby("variavel_base")
        .agg(
            impacto_total=("coeficiente", lambda x: x.abs().sum()),
            impacto_medio=("coeficiente", "mean"),
            n_variaveis=("coeficiente", "count"),
        )
        .sort_values("impacto_total", ascending=False)
    )

    return resumo




#Score Estrtural

def score_estrutural(model, X: pd.DataFrame) -> np.ndarray:
    """
    Calcula o score estrutural (contribuição linear) de cada observação
    a partir dos coeficientes do modelo treinado.

    O score é obtido pelo produto matricial entre as variáveis já
    transformadas pelo pipeline e os coeficientes do estimador linear.

    Parameters
    ----------
    model : sklearn Pipeline
        Pipeline treinado contendo as etapas 'preprocessor' e 'reg'.
    X : pd.DataFrame
        Dados de entrada no formato original (antes do preprocessing).

    Returns
    -------
    np.ndarray
        Vetor com o score estrutural para cada linha de X.
    """

    # Extrai pipeline padronizado
    pipeline = extrair_pipeline(model)

    # Aplica transformações do pré-processamento
    X_transformado = pipeline["preprocessor"].transform(X)

    # Coeficientes do modelo linear
    coeficientes = pipeline["reg"].coef_

    # Score estrutural (contribuição linear)
    score = X_transformado @ coeficientes

    return score
    