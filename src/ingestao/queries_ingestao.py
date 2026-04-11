from __future__ import annotations


def escapar_caminho_duckdb(caminho: str) -> str:
    """
    Normaliza o caminho para uso em SQL DuckDB.
    """
    return caminho.replace("\\", "/")


def montar_select_ingestao(
    caminho_csv: str,
    colunas_origem: list[str],
    rename_map: dict[str, str],
    sep: str = ";",
    header: bool = True,
    all_varchar: bool = True,
    ignore_errors: bool = False,
    encoding: str = "latin-1",
) -> str:
    """
    Monta uma query SQL DuckDB para:
    - ler um CSV bruto;
    - selecionar apenas as colunas desejadas;
    - renomear colunas para o padrão do projeto.
    """
    if not colunas_origem:
        raise ValueError("A lista 'colunas_origem' não pode ser vazia.")

    caminho_csv = escapar_caminho_duckdb(caminho_csv)

    colunas_sql: list[str] = []
    for col in colunas_origem:
        nome_final = rename_map.get(col, col)

        if nome_final != col:
            colunas_sql.append(f'"{col}" AS "{nome_final}"')
        else:
            colunas_sql.append(f'"{col}"')

    select_cols = ",\n        ".join(colunas_sql)

    sql = f"""
SELECT
        {select_cols}
FROM read_csv_auto(
        '{caminho_csv}',
        delim='{sep}',
        header={str(header).lower()},
        sample_size=-1,
        all_varchar={str(all_varchar).lower()},
        ignore_errors={str(ignore_errors).lower()},
        encoding='{encoding}'
)
"""
    return sql.strip()