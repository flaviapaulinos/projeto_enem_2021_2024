"""
graficos.py
===========

Funções de visualização utilizadas no projeto de modelagem da desigualdade
educacional (ENEM).

Este módulo centraliza gráficos de:
- interpretação de modelos (coeficientes e elasticidades)
- comparação de desempenho
- diagnóstico de resíduos
- análise estrutural da desigualdade

Autor: Flavia Paulinos
Projeto: Projeto ENEM 2021–2023
"""
import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.ticker import EngFormatter
from matplotlib.figure import Figure
from sklearn.metrics import PredictionErrorDisplay
from typing import Dict, Optional

from src.modelos.treino import RANDOM_STATE, avaliar_estabilidade

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # <-- ADICIONAR ESTA LINHA

# ---------------------------------------------------------------------
# Configurações globais de estilo
# ---------------------------------------------------------------------

sns.set_theme(palette="viridis")

PALETTE = "coolwarm"
SCATTER_ALPHA = 0.2

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # <-- ADICIONAR ESTA LINHA

# =====================================================================
# GRÁFICOS DE INTERPRETAÇÃO DO MODELO
# =====================================================================

def plot_coeficientes(df_coefs, titulo="Coeficientes", top_n=20, *, show=False) -> Figure:
    """
    Plota os coeficientes mais relevantes do modelo linear.

    Apenas as variáveis com maior magnitude absoluta são exibidas,
    facilitando a interpretação dos principais fatores associados
    à variação da nota média.

    Parameters
    ----------
    df_coefs : pd.DataFrame
        DataFrame contendo coluna 'coeficiente' e índice com nomes das variáveis.

    titulo : str, default="Coeficientes"
        Título do gráfico.

    top_n : int, default=20
        Número de coeficientes exibidos (maior magnitude).
    """

    # Seleciona coeficientes mais relevantes
    df_plot = (
        df_coefs
        .assign(abs_coef=lambda d: d["coeficiente"].abs())
        .sort_values("abs_coef", ascending=True)
        .tail(top_n)
        .drop(columns="abs_coef")
    )

    fig, ax = plt.subplots(figsize=(8, 10))

    colors = df_plot["coeficiente"].apply(
        lambda x: "tab:red" if x < 0 else "tab:blue"
    )

    ax.barh(df_plot.index, df_plot["coeficiente"], color=colors)

    ax.axvline(0, color="black", linewidth=1)

    ax.set_title(titulo)
    ax.set_xlabel("Impacto na nota média (coeficiente padronizado)")
    ax.set_ylabel("Variáveis")

    #fig.tight_layout()

    if show:
        plt.show()

    return fig


# =====================================================================
# COMPARAÇÃO DE MODELOS
# =====================================================================

def plot_comparar_metricas_modelos(df_resultados, *, show=False) -> Figure:
    """
    Compara o desempenho dos modelos via boxplots de validação cruzada.

    Exibe simultaneamente:
    - tempo de execução
    - R²
    - MAE
    - RMSE

    Parameters
    ----------
    df_resultados : pd.DataFrame
        Resultado consolidado do cross_validate().
    """

    fig, axs = plt.subplots(2, 2, figsize=(8, 8), sharex=True)

    comparar_metricas = [
        "time_seconds",
        "test_r2",
        "test_neg_mean_absolute_error",
        "test_neg_root_mean_squared_error",
    ]

    nomes_metricas = ["Tempo (s)", "R²", "MAE", "RMSE"]

    for ax, metrica, nome in zip(axs.flatten(), comparar_metricas, nomes_metricas):
        sns.boxplot(
            x="model",
            y=metrica,
            data=df_resultados,
            ax=ax,
            showmeans=True,
        )

        ax.set_title(nome)
        ax.set_ylabel(nome)
        ax.tick_params(axis="x", rotation=90)

    #fig.tight_layout()

    if show:
        plt.show()

    return fig

def plot_comparacao_modelos(df_comparacao: pd.DataFrame, salvar: bool = False) -> plt.Figure:
    """
    Gera gráfico comparativo entre modelos.
    """
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    
    # Extrair médias e desvios
    modelos = df_comparacao.index
    rmse_vals = df_comparacao['RMSE'].str.split(' ± ').apply(lambda x: float(x[0]))
    rmse_std = df_comparacao['RMSE'].str.split(' ± ').apply(lambda x: float(x[1]))
    
    # Gráfico de barras comparativo
    cores = plt.cm.Set3(np.linspace(0, 1, len(modelos)))
    bars = ax[0].barh(modelos, rmse_vals, xerr=rmse_std, color=cores, 
                      edgecolor='black', linewidth=1, capsize=5)
    ax[0].set_xlabel('RMSE', fontsize=12)
    ax[0].set_title('Comparação de Modelos - RMSE', fontsize=13, fontweight='bold')
    ax[0].grid(True, alpha=0.3, axis='x')
    
    # Tabela de estabilidade
    ax[1].axis('off')
    dados_tabela = [['Modelo', 'RMSE', 'R²', 'Estabilidade']]
    for modelo in modelos:
        dados_tabela.append([
            modelo,
            df_comparacao.loc[modelo, 'RMSE'],
            df_comparacao.loc[modelo, 'R²'],
            df_comparacao.loc[modelo, 'estabilidade']
        ])
    
    tabela = ax[1].table(cellText=dados_tabela, loc='center', cellLoc='center')
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1, 2)
    
    plt.suptitle('Comparação de Modelos - Validação Cruzada', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    return fig

# =====================================================================
# ANÁLISE ESTRUTURAL
# =====================================================================

def plot_elasticidade_dimensao(df, *, show=False) -> Figure:
    """
    Plota elasticidade estrutural agregada por dimensão social.

    A elasticidade representa o impacto esperado na nota média
    para um aumento de 1 desvio padrão na variável.
    """

    fig, ax = plt.subplots(figsize=(8, 6))

    df["elasticidade_total"].plot.barh(ax=ax)

    ax.axvline(0, color=".5")
    ax.set_title("Elasticidade estrutural por dimensão")
    ax.set_xlabel("Impacto (1 desvio padrão)")

    fig.tight_layout()

    if show:
        plt.show()

    return fig

def plot_impacto_dimensoes(
    df_impactos,
    titulo="Impacto estrutural por dimensão",
    show=False,
):
    """
    Exibe o impacto estrutural agregado por dimensão social.

    Barras azuis indicam impacto médio positivo,
    barras vermelhas indicam impacto médio negativo.
    """
    
    fig, ax = plt.subplots(figsize=(8, 6))

    cores = df_impactos["impacto_medio"].apply(
        lambda x: "tab:red" if x < 0 else "tab:blue"
    )

    ax.barh(
        df_impactos.index,
        df_impactos["impacto_total"],
        color=cores,
    )

    ax.set_xlabel("Impacto estrutural total (|coeficientes|)")
    ax.set_title(titulo)
    ax.invert_yaxis()

    fig.tight_layout()

    if show:
        plt.show()

    return fig


def plot_mapa_estrutural(
    impactos,
    elastic_dim,
    titulo="Mapa Estrutural da Desigualdade",
    show=False,
):
    """
    Cria o mapa estrutural da desigualdade.

    O gráfico combina:
    - Impacto estrutural (eixo X)
    - Elasticidade estrutural (eixo Y)
    - Participação no IDE (tamanho do ponto)

    Interpretação:
    --------------
    Quadrantes indicam tipos distintos de desigualdade estrutural.

    Parameters
    ----------
    impactos : DataFrame
        Saída de decompor_ide() (deve conter 'participacao').

    elastic_dim : DataFrame
        Saída de elasticidade_por_dimensao().
    """

    # Merge seguro
    df = impactos.join(
        elastic_dim[["elasticidade_total"]],
        how="inner"
    )

    x = df["impacto_total"]
    y = df["elasticidade_total"]

    x_med = x.mean()
    y_med = y.mean()

    tamanho = df["participacao"] * 4000

    cores = np.where(
        df["impacto_medio"] >= 0,
        "tab:blue",
        "tab:red",
    )

    fig, ax = plt.subplots(figsize=(9, 7))

    # ---------------------------
    # Classificação estrutural
    # ---------------------------
    def classificar(row, xm, ym):
        if row["impacto_total"] >= xm and row["elasticidade_total"] >= ym:
            return "Prioridade estrutural"
        elif row["impacto_total"] < xm and row["elasticidade_total"] >= ym:
            return "Alavanca rápida"
        elif row["impacto_total"] >= xm and row["elasticidade_total"] < ym:
            return "Estrutura rígida"
        else:
            return "Baixa prioridade"

    df["quadrante"] = df.apply(
        classificar,
        axis=1,
        xm=x_med,
        ym=y_med,
    )

    # ---------------------------
    # Scatter
    # ---------------------------
    ax.scatter(
        x,
        y,
        s=tamanho,
        alpha=0.7,
        c=cores,
        edgecolor="black",
        linewidth=0.7,
    )

    # linhas médias
    ax.axvline(x_med, linestyle="--")
    ax.axhline(y_med, linestyle="--")

    # rótulos
    for nome, xi, yi in zip(df.index, x, y):
        ax.text(xi, yi, f" {nome}", fontsize=10, va="center")

    ax.set_xlabel("Impacto estrutural total")
    ax.set_ylabel("Elasticidade estrutural")
    ax.set_title(titulo)

    ax.grid(alpha=0.2)

    fig.tight_layout()

    if show:
        plt.show()

    return fig


# =====================================================================
# DIAGNÓSTICO DO MODELO
# =====================================================================

def plot_residuos(y_true, y_pred):
    """
    Visualiza diagnóstico básico de resíduos.

    Inclui:
    - distribuição dos resíduos
    - resíduos vs predição
    - valores reais vs preditos
    """

    residuos = y_true - y_pred

    fig, axs = plt.subplots(1, 3, figsize=(12, 6))

    sns.histplot(residuos, kde=True, ax=axs[0])

    PredictionErrorDisplay.from_predictions(
        y_true=y_true,
        y_pred=y_pred,
        kind="residual_vs_predicted",
        ax=axs[1],
    )

    PredictionErrorDisplay.from_predictions(
        y_true=y_true,
        y_pred=y_pred,
        kind="actual_vs_predicted",
        ax=axs[2],
    )

    plt.tight_layout()
    return fig


def plot_residuos_estimador(
    estimator,
    X,
    y,
    eng_formatter=False,
    fracao_amostra=0.25,
    show=False,
):
    """
    Diagnóstico completo de resíduos a partir de um estimador treinado.

    Utiliza subsampling para melhorar legibilidade em grandes bases.

    Parameters
    ----------
    estimator : sklearn estimator
        Modelo treinado.

    X : array-like
        Features.

    y : array-like
        Target.

    eng_formatter : bool, default=False
        Aplica formatação científica nos eixos.

    fracao_amostra : float, default=0.25
        Fração dos pontos exibidos nos gráficos.
    """

    fig, axs = plt.subplots(1, 3, figsize=(12, 6))

    error_display = PredictionErrorDisplay.from_estimator(
        estimator,
        X,
        y,
        kind="residual_vs_predicted",
        ax=axs[1],
        random_state=RANDOM_STATE,
        scatter_kwargs={"alpha": SCATTER_ALPHA},
        subsample=fracao_amostra,
    )

    PredictionErrorDisplay.from_estimator(
        estimator,
        X,
        y,
        kind="actual_vs_predicted",
        ax=axs[2],
        random_state=RANDOM_STATE,
        scatter_kwargs={"alpha": SCATTER_ALPHA},
        subsample=fracao_amostra,
    )

    residuos = error_display.y_true - error_display.y_pred

    sns.histplot(residuos, kde=True, ax=axs[0])

    if eng_formatter:
        for ax in axs:
            ax.xaxis.set_major_formatter(EngFormatter())
            ax.yaxis.set_major_formatter(EngFormatter())

    fig.tight_layout()

    if show:
        plt.show()

    return fig



def plot_residuos_vs_estrutura(df_res, show=False):
    """
    Plota resíduos do modelo em função do score estrutural.

    Este gráfico permite avaliar se existe viés estrutural
    sistemático no modelo. Idealmente, os resíduos devem
    oscilar aleatoriamente ao redor de zero, sem tendência
    linear em relação ao score estrutural.

    Parameters
    ----------
    df_res : pd.DataFrame
        DataFrame contendo, no mínimo, as colunas:

        - 'score_estrutural' : contribuição linear prevista
        - 'residuo' : erro do modelo (real − previsto)
    """

    # --------------------------------------------------
    # 1. Preparar dados
    # --------------------------------------------------
    x = df_res["score_estrutural"]
    y = df_res["residuo"]

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(
        x,
        y,
        alpha=SCATTER_ALPHA,
    )

    # linha de tendência
    coef = np.polyfit(x, y, 1)
    tendencia = np.poly1d(coef)

    xs = np.linspace(x.min(), x.max(), 100)

    ax.plot(xs, tendencia(xs), linewidth=2)

    ax.axhline(0, linestyle="--", linewidth=1)

    ax.set_xlabel("Score estrutural previsto")
    ax.set_ylabel("Resíduo (real − previsto)")
    ax.set_title("Resíduos vs Estrutura Social")

    ax.grid(alpha=0.2)

    #fig.tight_layout()

    if show:
        plt.show()

    return fig


def plot_validacao_cruzada(
    resultados: Dict,
    nome_modelo: str = "Ridge Regression",
    salvar: bool = False,
    caminho_salvar: Optional[str] = None
) -> plt.Figure:
    """
    Gera visualizações completas da validação cruzada.
    
    Parameters
    ----------
    resultados : Dict
        Dicionário retornado por validacao_cruzada_modelo()
    nome_modelo : str
        Nome do modelo para o título
    salvar : bool
        Se True, salva a figura
    caminho_salvar : str
        Caminho para salvar a figura
    
    Returns
    -------
    plt.Figure
        Figura matplotlib
    """
    
    # Extrair dados
    folds = resultados['folds']
    rmse = resultados['rmse']
    r2 = resultados['r2']
    mae = resultados['mae']
    resumo = resultados['resumo']
    
    # Configurar estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    cores = ['#2E86AB', '#E63946', '#2A9D8F']
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # 1. RMSE por fold (barras)
    ax1 = axes[0, 0]
    bars = ax1.bar(folds, rmse, color=cores[0], edgecolor='#1D3557', linewidth=2, alpha=0.8)
    ax1.axhline(y=resumo['rmse_medio'], color=cores[1], linestyle='--', linewidth=2,
                label=f'Média: {resumo["rmse_medio"]:.2f}')
    ax1.fill_between(folds, 
                     resumo['rmse_medio'] - resumo['rmse_std'], 
                     resumo['rmse_medio'] + resumo['rmse_std'], 
                     alpha=0.2, color=cores[1],
                     label=f'±1σ: {resumo["rmse_std"]:.2f}')
    ax1.set_xlabel('Fold', fontsize=11)
    ax1.set_ylabel('RMSE', fontsize=11)
    ax1.set_title(f'RMSE por Fold - {nome_modelo}', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    ax1.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, val in zip(bars, rmse):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 2. Boxplot RMSE
    ax2 = axes[0, 1]
    box = ax2.boxplot(rmse, patch_artist=True, widths=0.6)
    box['boxes'][0].set_facecolor(cores[0])
    box['boxes'][0].set_alpha(0.7)
    box['medians'][0].set_color(cores[1])
    box['medians'][0].set_linewidth(2)
    ax2.set_ylabel('RMSE', fontsize=11)
    ax2.set_title('Distribuição do RMSE', fontsize=12, fontweight='bold')
    ax2.set_xticklabels([nome_modelo])
    ax2.grid(True, alpha=0.3)
    
    # 3. R² por fold
    ax3 = axes[0, 2]
    ax3.plot(folds, r2, 'o-', color=cores[2], linewidth=2, markersize=10,
             markerfacecolor='white', markeredgecolor=cores[2], markeredgewidth=2)
    ax3.axhline(y=resumo['r2_medio'], color=cores[1], linestyle='--', linewidth=2,
                label=f'Média: {resumo["r2_medio"]:.3f}')
    ax3.fill_between(folds, 
                     resumo['r2_medio'] - resumo['r2_std'], 
                     resumo['r2_medio'] + resumo['r2_std'], 
                     alpha=0.2, color=cores[1])
    ax3.set_xlabel('Fold', fontsize=11)
    ax3.set_ylabel('R²', fontsize=11)
    ax3.set_title('R² por Fold', fontsize=12, fontweight='bold')
    ax3.legend(loc='lower right')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0.9, 1.0)
    
    # 4. MAE por fold
    ax4 = axes[1, 0]
    ax4.plot(folds, mae, 's-', color=cores[2], linewidth=2, markersize=10,
             markerfacecolor='white', markeredgecolor=cores[2], markeredgewidth=2)
    ax4.axhline(y=resumo['mae_medio'], color=cores[1], linestyle='--', linewidth=2,
                label=f'Média: {resumo["mae_medio"]:.2f}')
    ax4.fill_between(folds, 
                     resumo['mae_medio'] - resumo['mae_std'], 
                     resumo['mae_medio'] + resumo['mae_std'], 
                     alpha=0.2, color=cores[1])
    ax4.set_xlabel('Fold', fontsize=11)
    ax4.set_ylabel('MAE', fontsize=11)
    ax4.set_title('MAE por Fold', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    # 5. Histograma RMSE
    ax5 = axes[1, 1]
    ax5.hist(rmse, bins=5, edgecolor='black', alpha=0.7, color=cores[0])
    ax5.axvline(x=resumo['rmse_medio'], color=cores[1], linestyle='--', linewidth=2,
                label=f'Média: {resumo["rmse_medio"]:.2f}')
    ax5.axvline(x=resumo['rmse_medio'] + resumo['rmse_std'], color=cores[1], linestyle=':', linewidth=1.5)
    ax5.axvline(x=resumo['rmse_medio'] - resumo['rmse_std'], color=cores[1], linestyle=':', linewidth=1.5)
    ax5.set_xlabel('RMSE', fontsize=11)
    ax5.set_ylabel('Frequência', fontsize=11)
    ax5.set_title('Distribuição de Frequência do RMSE', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Tabela de estatísticas
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Criar tabela com estatísticas
    dados_tabela = [
        ['Métrica', 'Valor'],
        ['RMSE médio', f"{resumo['rmse_medio']:.2f} ± {resumo['rmse_std']:.2f}"],
        ['R² médio', f"{resumo['r2_medio']:.3f} ± {resumo['r2_std']:.3f}"],
        ['MAE médio', f"{resumo['mae_medio']:.2f} ± {resumo['mae_std']:.2f}"],
        ['CV (%)', f"{resumo['rmse_cv']:.1f}%"],
        ['IC 95%', f"[{resumo['rmse_ic_inferior']:.2f}, {resumo['rmse_ic_superior']:.2f}]"],
        ['Estabilidade', avaliar_estabilidade(resumo['rmse_cv']).replace('✅', '').replace('⚠️', '').replace('🔴', '').replace('❄️', '').strip()],
    ]
    
    tabela = ax6.table(cellText=dados_tabela, loc='center', cellLoc='left', colWidths=[0.3, 0.5])
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.scale(1, 1.5)
    
    # Colorir cabeçalho
    for (i, j), cell in tabela.get_celld().items():
        if i == 0:
            cell.set_facecolor('#2E86AB')
            cell.set_text_props(color='white', fontweight='bold')
        cell.set_edgecolor('#dddddd')
    
    ax6.set_title('Resumo Estatístico', fontsize=12, fontweight='bold')
    
    plt.suptitle(f'Validação Cruzada - {nome_modelo}', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if salvar and caminho_salvar:
        plt.savefig(caminho_salvar, bbox_inches='tight', dpi=300)
        logger.info(f"Figura salva em: {caminho_salvar}")
    
    return fig