from pathlib import Path
import mlflow

from ..config import (
    PASTA_FIGURAS,
    PASTA_CSV,
)

# -----------------------------------------------------
# garantir pastas
# -----------------------------------------------------
def criar_pastas():
    PASTA_FIGURAS.mkdir(parents=True, exist_ok=True)
    PASTA_CSV.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------
# salvar figura
# -----------------------------------------------------
def salvar_figura(fig, nome, log_mlflow=True):
    criar_pastas()

    caminho = PASTA_FIGURAS / f"{nome}.png"

    fig.savefig(
        caminho,
        dpi=300,
        bbox_inches="tight"
    )

    if log_mlflow:
        mlflow.log_artifact(str(caminho), artifact_path="figuras")

    return caminho


# -----------------------------------------------------
# salvar tabela
# -----------------------------------------------------
def salvar_csv(df, nome, log_mlflow=True):
    criar_pastas()

    caminho = PASTA_CSV / f"{nome}.csv"

    df.to_csv(caminho, index=False)

    if log_mlflow:
        mlflow.log_artifact(str(caminho), artifact_path="tabelas")

    return caminho