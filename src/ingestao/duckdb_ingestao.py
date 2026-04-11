from __future__ import annotations

from pathlib import Path
import duckdb

from src.ingestao.queries_ingestao import montar_select_ingestao


def exportar_consulta_para_parquet(
    sql: str,
    destino_parquet: Path,
    db_path: Path | None = None,
    overwrite: bool = True,
) -> None:
    """
    Executa uma consulta DuckDB e exporta o resultado diretamente para Parquet.
    """
    destino_parquet.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path)) if db_path else duckdb.connect()

    destino = str(destino_parquet).replace("\\", "/")

    if overwrite and destino_parquet.exists():
        destino_parquet.unlink()

    con.execute(
        f"""
        COPY (
            {sql}
        )
        TO '{destino}'
        (FORMAT PARQUET);
        """
    )

    con.close()


def ingerir_csv_para_parquet(
    caminho_csv: Path,
    destino_parquet: Path,
    colunas_origem: list[str],
    rename_map: dict[str, str],
    db_path: Path | None = None,
    sep: str = ";",
    header: bool = True,
    all_varchar: bool = True,
    ignore_errors: bool = False,
    overwrite: bool = True,
    encoding: str = "latin-1",
) -> None:
    """
    Lê um CSV bruto com DuckDB e exporta um Parquet enxuto,
    com seleção e renomeação de colunas.
    """
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

    sql = montar_select_ingestao(
        caminho_csv=str(caminho_csv),
        colunas_origem=colunas_origem,
        rename_map=rename_map,
        sep=sep,
        header=header,
        all_varchar=all_varchar,
        ignore_errors=ignore_errors,
        encoding=encoding,
    )

    exportar_consulta_para_parquet(
        sql=sql,
        destino_parquet=destino_parquet,
        db_path=db_path,
        overwrite=overwrite,
    )


def validar_colunas_csv(
    caminho_csv: Path,
    colunas_esperadas: list[str],
    db_path: Path | None = None,
    sep: str = ";",
    header: bool = True,
    encoding: str = "latin-1",
) -> tuple[list[str], list[str]]:
    """
    Valida se as colunas esperadas existem no CSV.
    """
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

    con = duckdb.connect(str(db_path)) if db_path else duckdb.connect()

    caminho = str(caminho_csv).replace("\\", "/")

    schema_df = con.execute(
        f"""
        DESCRIBE
        SELECT *
        FROM read_csv_auto(
            '{caminho}',
            delim='{sep}',
            header={str(header).lower()},
            sample_size=20000,
            all_varchar=true,
            encoding='{encoding}'
        )
        """
    ).fetchdf()

    con.close()

    colunas_encontradas = schema_df["column_name"].tolist()
    colunas_presentes = [c for c in colunas_esperadas if c in colunas_encontradas]
    colunas_ausentes = [c for c in colunas_esperadas if c not in colunas_encontradas]

    return colunas_presentes, colunas_ausentes