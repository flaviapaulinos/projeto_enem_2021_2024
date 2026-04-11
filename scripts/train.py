# =====================================
# train.py — Pipeline FINAL (Analítico + Produto)
# =====================================

import pandas as pd
import numpy as np
import json
import joblib
import logging
from pathlib import Path

import mlflow

from sklearn.linear_model import Ridge
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder

# Projeto
from src.config import (
    DADOS_AGG_MG_ML,
    PASTA_RESULTADOS,
    TARGET
)

from src.modelos.treino import (
    avaliar_estabilidade,
    grid_search_estratificado,
    validacao_cruzada_estratificada,
)

from src.modelos.interpretacao import (
    dataframe_coeficientes,
    impacto_por_dimensao,
    decompor_ide,
    elasticidade_padronizada,
    elasticidade_por_dimensao,
    indice_desigualdade_estrutural,
    score_estrutural
)

# ---------------------------------
# Setup
# ---------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# ---------------------------------
# Configurações base
# ---------------------------------

coluna_categorica_ordenada = ["SalMin"]

ordem_renda = [
    'até 1', '1 a 3', '3 a 5',
    '5 a 10', '10 a 15', '15 a 20', 'acima de 20'
]

colunas_numericas = [
    "OcupPaisMedia",
    "EscolaridadePaisMedia",
    "Cel",
    "Comptdr",
    "PessoasResd"
]

# ---------------------------------
# Funções auxiliares
# ---------------------------------

def carregar_dados():
    df = pd.read_parquet(DADOS_AGG_MG_ML)
    logger.info(f"Dados carregados: {df.shape}")
    return df


def selecionar_features(incluir_ano: bool):
    base = [
        "SalMin",
        "Escola",
        "OcupPaisMedia",
        "EscolaridadePaisMedia",
        "Cel",
        "Comptdr",
        "PessoasResd",
    ]
    
    if incluir_ano:
        return ["Ano"] + base
    return base


def criar_preprocessador(colunas_categoricas):
    pre = ColumnTransformer(
        transformers=[
            ("one_hot", OneHotEncoder(drop="first", sparse_output=False), colunas_categoricas),
            ("ordinal", OrdinalEncoder(categories=[ordem_renda]), coluna_categorica_ordenada),
            ("num", StandardScaler(), colunas_numericas),
        ]
    )
    pre.set_output(transform="pandas")
    return pre


def separar_variaveis(df, features):
    X = df[features]
    y = df[TARGET]
    sample_weight = np.sqrt(df["Participantes"])
    return X, y, sample_weight


def criar_faixas(y):
    return pd.qcut(y, q=5, labels=False, duplicates="drop")


# ---------------------------------
# Treino genérico
# ---------------------------------

def treinar_modelo(df, incluir_ano: bool):

    nome_modelo = "analitico" if incluir_ano else "produto"
    logger.info(f"\n🔹 Treinando modelo: {nome_modelo}")

    # Definir features
    features = selecionar_features(incluir_ano)
    
    colunas_categoricas = ["Escola"]
    if incluir_ano:
        colunas_categoricas = ["Ano", "Escola"]

    # Separar dados
    X, y, sample_weight = separar_variaveis(df, features)

    # Preprocessador
    preprocessador = criar_preprocessador(colunas_categoricas)

    # Estratificação
    y_faixas = criar_faixas(y)

    # Grid
    param_grid = {
        "reg__alpha": [1, 10, 30, 50, 60, 80, 100]
    }

    grid = grid_search_estratificado(
        X=X,
        y=y,
        regressor=Ridge(),
        preprocessor=preprocessador,
        param_grid=param_grid,
        sample_weight=sample_weight,
        y_faixas=y_faixas,
        n_splits=5
    )

    modelo = grid.best_estimator_
    alpha = grid.best_params_["reg__alpha"]

    # Validação
    resultados = validacao_cruzada_estratificada(
        modelo=modelo,
        X=X,
        y=y,
        y_faixas=y_faixas,
        sample_weight=sample_weight
    )

    rmse = resultados["resumo"]["rmse_medio"]
    r2 = resultados["resumo"]["r2_medio"]
    cv = resultados["resumo"]["rmse_cv"]
    estabilidade = avaliar_estabilidade(cv)

    logger.info(f"RMSE: {rmse:.2f} | CV: {cv:.1f}% | {estabilidade}")

    # MLflow
    with mlflow.start_run(run_name=f"modelo_{nome_modelo}"):

        mlflow.log_param("modelo", nome_modelo)
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("inclui_ano", incluir_ano)

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("cv", cv)

        mlflow.sklearn.log_model(modelo, "model")

        # Interpretação
        coefs = dataframe_coeficientes(
            modelo.named_steps["reg"].coef_,
            modelo.named_steps["preprocessor"].get_feature_names_out()
        )

        impactos = decompor_ide(impacto_por_dimensao(coefs))
        elastic = elasticidade_por_dimensao(
            elasticidade_padronizada(modelo, X)
        )

        ide, ide_norm = indice_desigualdade_estrutural(impactos)
        mlflow.log_metric("ide", ide_norm)

    # ---------------------------------
    # Salvar artefatos
    # ---------------------------------
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    caminho_modelo = PASTA_RESULTADOS / f"modelo_{nome_modelo}.joblib"
    joblib.dump(modelo, caminho_modelo)

    coefs.to_parquet(PASTA_RESULTADOS / f"coef_{nome_modelo}.parquet")

    df_out = df.copy()
    df_out["IDE"] = score_estrutural(modelo, X)
    df_out.to_parquet(PASTA_RESULTADOS / f"dados_ide_{nome_modelo}.parquet")

    metricas = {
        "alpha": alpha,
        "rmse": float(rmse),
        "r2": float(r2),
        "cv": float(cv),
        "estabilidade": estabilidade,
        "ide": float(ide_norm)
    }

    with open(PASTA_RESULTADOS / f"metricas_{nome_modelo}.json", "w") as f:
        json.dump(metricas, f, indent=4)

    logger.info(f"✅ Modelo {nome_modelo} salvo em: {caminho_modelo}")


# ---------------------------------
# MAIN
# ---------------------------------

def main():

    mlflow.set_experiment("enem_mg_modelos_final")

    df = carregar_dados()

    # 🔬 Modelo analítico
    treinar_modelo(df, incluir_ano=True)

    # 🚀 Modelo produto
    treinar_modelo(df, incluir_ano=False)

    logger.info("\n🏁 Pipeline completo finalizado!")


if __name__ == "__main__":
    main()