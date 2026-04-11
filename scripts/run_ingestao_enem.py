import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.append(str(ROOT_PATH))

from src.config import (
    ARQUIVO_DUCKDB,
    DADOS_2021,
    DADOS_2022,
    DADOS_2023,
    DADOS_2024,
    RESULTADOS_2024,
    BASE_BRUTA_2021,
    BASE_BRUTA_2022,
    BASE_BRUTA_2023,
    BASE_BRUTA_2024,
    BASE_RESULTADOS_2024,
)

from src.dados.enem_schema import (
    USECOLS_ENEM_2021_2023,
    RENAME_MAP_ENEM_2021_2023,
    USECOLS_ENEM_2024_DADOS,
    RENAME_MAP_ENEM_2024_DADOS,
    USECOLS_RESULTADOS_ENEM_2024,
    RENAME_MAP_RESULTADOS_ENEM_2024,
)

from src.ingestao.duckdb_ingestao import (
    ingerir_csv_para_parquet,
    validar_colunas_csv,
)


def executar_ingestao(
    origem: Path,
    destino: Path,
    usecols: list[str],
    rename_map: dict[str, str],
    descricao: str,
    encoding: str = "latin-1",
) -> None:
    print(f"\n📥 {descricao}")
    print(f"   Origem : {origem.name}")
    print(f"   Destino: {destino.name}")

    presentes, ausentes = validar_colunas_csv(
        caminho_csv=origem,
        colunas_esperadas=usecols,
        db_path=ARQUIVO_DUCKDB,
        sep=";",
        header=True,
        encoding=encoding,
    )

    if ausentes:
        print(f"   ⚠️ Colunas ausentes ({len(ausentes)}): {ausentes}")

    if not presentes:
        raise ValueError(f"Nenhuma coluna esperada foi encontrada no arquivo: {origem}")

    usecols_validas = [c for c in usecols if c in presentes]

    ingerir_csv_para_parquet(
        caminho_csv=origem,
        destino_parquet=destino,
        colunas_origem=usecols_validas,
        rename_map=rename_map,
        db_path=ARQUIVO_DUCKDB,
        sep=";",
        header=True,
        all_varchar=True,
        ignore_errors=False,
        overwrite=True,
        encoding=encoding,
    )

    print("   ✅ Ingestão concluída.")


def main() -> None:
    print("🚀 Iniciando ingestão com DuckDB...")

    tarefas_2021_2023 = [
        (DADOS_2021, BASE_BRUTA_2021, "ENEM 2021 — base bruta"),
        (DADOS_2022, BASE_BRUTA_2022, "ENEM 2022 — base bruta"),
        (DADOS_2023, BASE_BRUTA_2023, "ENEM 2023 — base bruta"),
    ]

    for origem, destino, descricao in tarefas_2021_2023:
        executar_ingestao(
            origem=origem,
            destino=destino,
            usecols=USECOLS_ENEM_2021_2023,
            rename_map=RENAME_MAP_ENEM_2021_2023,
            descricao=descricao,
            encoding="latin-1",
        )

    executar_ingestao(
        origem=DADOS_2024,
        destino=BASE_BRUTA_2024,
        usecols=USECOLS_ENEM_2024_DADOS,
        rename_map=RENAME_MAP_ENEM_2024_DADOS,
        descricao="ENEM 2024 — participantes",
        encoding="utf-8",
    )

    executar_ingestao(
        origem=RESULTADOS_2024,
        destino=BASE_RESULTADOS_2024,
        usecols=USECOLS_RESULTADOS_ENEM_2024,
        rename_map=RENAME_MAP_RESULTADOS_ENEM_2024,
        descricao="ENEM 2024 — resultados",
        encoding="latin-1",
    )

    print("\n✅ Todas as ingestões foram concluídas com sucesso.")


if __name__ == "__main__":
    main()