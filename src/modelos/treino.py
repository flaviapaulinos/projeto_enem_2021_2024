"""
treino.py
=========

Rotinas de treinamento, validação cruzada
e busca de hiperparâmetros.
"""
import logging
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.pipeline import Pipeline 
from sklearn.model_selection import (
    cross_validate,
    GridSearchCV,
    KFold,   
    StratifiedKFold,
)

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, List, Tuple, Optional, Union
from .pipeline import construir_pipeline_modelo_regressao

RANDOM_STATE = 42

# Configurações padrão para validação cruzada
CV_CONFIG = {
    'n_splits': 5,
    'random_state': 42,
    'scoring': 'neg_root_mean_squared_error',
    'nome_regressor': 'reg'  # Nome padrão do regressor
}

# Thresholds para estabilidade
ESTABILIDADE_THRESHOLDS = {
    'extremamente_estavel': 5,
    'estavel': 10,
    'moderado': 15
}

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def avaliar_estabilidade(cv_percentual: float) -> str:
    """Avalia qualitativamente a estabilidade baseada no CV"""
    if cv_percentual < 5:
        return "❄️ Extremamente estável"
    elif cv_percentual < 10:
        return "✅ Estável"
    elif cv_percentual < 15:
        return "⚠️ Moderadamente estável"
    else:
        return "🔴 Instável"

def calcular_estatisticas_validacao(resultados: Dict) -> Dict:
    """
    Calcula estatísticas resumidas dos resultados da validação cruzada.
    """
    resumo = {}
    
    for metrica in ['rmse', 'r2', 'mae']:
        valores = resultados[metrica]
        resumo.update({
            f'{metrica}_medio': valores.mean(),
            f'{metrica}_std': valores.std(),
            f'{metrica}_min': valores.min(),
            f'{metrica}_max': valores.max(),
            f'{metrica}_mediana': np.median(valores),
            f'{metrica}_cv': (valores.std() / valores.mean() * 100)  # Coeficiente de variação
        })
    
    # Intervalo de confiança (95%)
    resumo['rmse_ic_inferior'] = resumo['rmse_medio'] - 1.96 * resumo['rmse_std']
    resumo['rmse_ic_superior'] = resumo['rmse_medio'] + 1.96 * resumo['rmse_std']
    
    return resumo

def comparar_modelos_cv(
    modelos: Dict[str, Pipeline],
    X: pd.DataFrame,
    y: pd.Series,
    sample_weight: Optional[np.ndarray] = None,
    n_splits: int = 5
) -> pd.DataFrame:
    """
    Compara múltiplos modelos usando validação cruzada.
    
    Parameters
    ----------
    modelos : Dict[str, Pipeline]
        Dicionário com nome: modelo
    X, y : dados
    sample_weight : pesos opcionais
    n_splits : número de folds
    
    Returns
    -------
    pd.DataFrame
        DataFrame comparativo
    """
    resultados = {}
    
    for nome, modelo in modelos.items():
        logger.info(f"Validando modelo: {nome}")
        
        # Identificar nome do regressor
        nome_regressor = list(modelo.named_steps.keys())[-1]
        
        res = validacao_cruzada_modelo(
            modelo, X, y,
            sample_weight=sample_weight,
            n_splits=n_splits,
            nome_regressor=nome_regressor
        )
        
        resultados[nome] = {
            'RMSE': f"{res['resumo']['rmse_medio']:.2f} ± {res['resumo']['rmse_std']:.2f}",
            'R²': f"{res['resumo']['r2_medio']:.3f} ± {res['resumo']['r2_std']:.3f}",
            'MAE': f"{res['resumo']['mae_medio']:.2f} ± {res['resumo']['mae_std']:.2f}",
            'CV(%)': f"{res['resumo']['rmse_cv']:.1f}%",
            'estabilidade': avaliar_estabilidade(res['resumo']['rmse_cv'])
        }
    
    return pd.DataFrame(resultados).T

#Grid Search

def grid_search_estratificado(
    X, 
    y, 
    regressor, 
    preprocessor, 
    param_grid, 
    sample_weight, 
    y_faixas,  # Usaremos para criar o CV
    n_splits=5
):
    """
    Grid search com validação estratificada para manter distribuição das notas
    """
    
    # Construir pipeline
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('reg', regressor)
    ])
    
    # CRIAR O CV ESTRATIFICADO COM AS FAIXAS
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    # IMPORTANTE: Criar uma lista de splits manualmente
    # Isso força o uso das faixas em vez do y contínuo
    splits = list(cv.split(X, y_faixas))  # <-- Usando y_faixas aqui!
    
    # Configurar GridSearch com o CV personalizado
    grid_search = GridSearchCV(
        model,
        cv=splits,  # <-- Passar os splits prontos
        param_grid=param_grid,
        scoring=["r2", "neg_mean_absolute_error", "neg_root_mean_squared_error"],
        refit="neg_root_mean_squared_error",
        n_jobs=-1,
        verbose=1,
    )
    
    # Preparar fit_kwargs com sample_weight
    fit_kwargs = {}
    if sample_weight is not None:
        fit_kwargs["reg__sample_weight"] = sample_weight
    
    # Treinar
    grid_search.fit(X, y, **fit_kwargs)
    
    return grid_search


#Cross-validation

def treinar_e_validar_modelo_regressao(
    X,
    y,
    regressor,
    preprocessor=None,
    target_transformer=None,
    sample_weight=None,
    n_splits=5,
    random_state=RANDOM_STATE,
):
    """
    Executa validação cruzada padronizada.
    """

    model = construir_pipeline_modelo_regressao(
        regressor,
        preprocessor,
        target_transformer,
    )

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    params = {}

    if sample_weight is not None:
        chave = (
            "regressor__reg__sample_weight"
            if target_transformer
            else "reg__sample_weight"
        )
        params[chave] = sample_weight

    scores = cross_validate(
        model,
        X,
        y,
        cv=kf,
        scoring=[
            "r2",
            "neg_mean_absolute_error",
            "neg_root_mean_squared_error",
        ],
        params=params if params else None,
    )

    return scores

#Organização de resultados


def organiza_resultados(resultados):
    """
    Converte saída de múltiplos cross_validate
    em DataFrame longo.
    """

    for chave in resultados:
        resultados[chave]["time_seconds"] = (
            resultados[chave]["fit_time"]
            + resultados[chave]["score_time"]
        )

    df = (
        pd.DataFrame(resultados)
        .T.reset_index()
        .rename(columns={"index": "model"})
    )

    df_expandido = df.explode(df.columns[1:].to_list()).reset_index(drop=True)

    try:
        df_expandido = df_expandido.apply(pd.to_numeric)
    except ValueError:
        pass

    return df_expandido

def validacao_cruzada_estratificada(
    modelo,
    X: pd.DataFrame,
    y: pd.Series,
    y_faixas: pd.Series,
    sample_weight: Optional[np.ndarray] = None,
    n_splits: int = 5,
    nome_regressor: str = 'reg'
) -> Dict:
    """
    Validação cruzada com estratificação para manter distribuição das notas
    """
    from sklearn.model_selection import StratifiedKFold
    from sklearn.base import clone
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    
    logger = logging.getLogger(__name__)
    
    # IMPORTANTE: StratifiedKFold usa as faixas (y_faixas) para estratificação
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    resultados = {
        'folds': [],
        'rmse': [],
        'r2': [],
        'mae': [],
        'modelos': []
    }
    
    logger.info(f"Iniciando validação cruzada ESTRATIFICADA com {n_splits} folds...")
    
    # Passar y_faixas para o split, não o y original
    for fold, (train_idx, val_idx) in enumerate(cv.split(X, y_faixas), 1):
        # Split dos dados (usando índices)
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        w_train = sample_weight[train_idx] if sample_weight is not None else None
        
        # Clonar e treinar modelo
        modelo_fold = clone(modelo)
        
        if w_train is not None:
            modelo_fold.fit(X_train, y_train, **{f'{nome_regressor}__sample_weight': w_train})
        else:
            modelo_fold.fit(X_train, y_train)
        
        # Predições e métricas
        y_pred = modelo_fold.predict(X_val)
        
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)
        mae = mean_absolute_error(y_val, y_pred)
        
        resultados['folds'].append(fold)
        resultados['rmse'].append(rmse)
        resultados['r2'].append(r2)
        resultados['mae'].append(mae)
        resultados['modelos'].append(modelo_fold)
        
        logger.info(f"Fold {fold}: RMSE={rmse:.2f}, R²={r2:.3f}, MAE={mae:.2f}")
    
    # Converter para arrays numpy
    for metrica in ['rmse', 'r2', 'mae']:
        resultados[metrica] = np.array(resultados[metrica])
    
    # Adicionar estatísticas resumidas
    resultados['resumo'] = calcular_estatisticas_validacao(resultados)
    
    logger.info(f"Validação cruzada concluída. RMSE médio: {resultados['resumo']['rmse_medio']:.2f} ± {resultados['resumo']['rmse_std']:.2f}")
    
    return resultados

