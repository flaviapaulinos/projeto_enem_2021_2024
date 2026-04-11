"""
pipeline.py
===========

Construção e manipulação de pipelines de regressão.
"""

from sklearn.compose import TransformedTargetRegressor
from sklearn.pipeline import Pipeline


def construir_pipeline_modelo_regressao(
    regressor,
    preprocessor=None,
    target_transformer=None,
):
    """
    Constrói pipeline padronizado de regressão.
    """

    if preprocessor is not None:
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("reg", regressor),
        ])
    else:
        pipeline = Pipeline([("reg", regressor)])

    if target_transformer is not None:
        return TransformedTargetRegressor(
            regressor=pipeline,
            transformer=target_transformer,
        )

    return pipeline


def extrair_pipeline(model):
    """
    Retorna o pipeline interno independentemente
    do uso de TransformedTargetRegressor.
    """
    if hasattr(model, "regressor_"):
        return model.regressor_
    return model