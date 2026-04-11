from pathlib import Path

# ======================
# RAIZ DO PROJETO
# ======================
PASTA_PROJETO = Path(__file__).resolve().parents[1]

# ======================
# DADOS
# ======================
PASTA_DADOS = PASTA_PROJETO / "dados"
PASTA_DADOS_BRUTOS = PASTA_DADOS / "brutos"
PASTA_DADOS_INTERMEDIARIOS = PASTA_DADOS / "intermediarios"
PASTA_DADOS_ANALITICOS = PASTA_DADOS / "analiticos"
PASTA_DUCKDB = PASTA_DADOS / "duckdb"

for pasta in [
    PASTA_DADOS,
    PASTA_DADOS_BRUTOS,
    PASTA_DADOS_INTERMEDIARIOS,
    PASTA_DADOS_ANALITICOS,
    PASTA_DUCKDB,
]:
    pasta.mkdir(parents=True, exist_ok=True)

ARQUIVO_DUCKDB = PASTA_DUCKDB / "enem.duckdb"

# ======================
# ARQUIVOS CSV BRUTOS
# ======================
DADOS_2020 = PASTA_DADOS_BRUTOS / "MICRODADOS_ENEM_2020.csv"
DADOS_2021 = PASTA_DADOS_BRUTOS / "MICRODADOS_ENEM_2021.csv"
DADOS_2022 = PASTA_DADOS_BRUTOS / "MICRODADOS_ENEM_2022.csv"
DADOS_2023 = PASTA_DADOS_BRUTOS / "MICRODADOS_ENEM_2023.csv"
DADOS_2024 = PASTA_DADOS_BRUTOS / "PARTICIPANTES_2024.csv"
RESULTADOS_2024 = PASTA_DADOS_BRUTOS / "RESULTADOS_2024.csv"

# ======================
# INGESTÃO BASE (CSV -> PARQUET)
# ======================
BASE_BRUTA_2021 = PASTA_DADOS_INTERMEDIARIOS / "base_bruta_2021.parquet"
BASE_BRUTA_2022 = PASTA_DADOS_INTERMEDIARIOS / "base_bruta_2022.parquet"
BASE_BRUTA_2023 = PASTA_DADOS_INTERMEDIARIOS / "base_bruta_2023.parquet"
BASE_BRUTA_2024 = PASTA_DADOS_INTERMEDIARIOS / "base_bruta_2024.parquet"
BASE_RESULTADOS_2024 = PASTA_DADOS_INTERMEDIARIOS / "base_resultados_2024.parquet"

# ======================
# INTERMEDIÁRIOS
# ======================
# 2021
DADOS_TRATADOS_2021 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2021.parquet"
DADOS_TRATADOS_MEDIAS_2021 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2021_medias.parquet"
DADOS_TRAT_MG_2021 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_MG_21.parquet"
DADOS_TRAT_CAX_2021 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_CAX_21.parquet"

# 2022
DADOS_TRATADOS_2022 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2022.parquet"
DADOS_TRATADOS_MEDIAS_2022 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2022_medias.parquet"
DADOS_TRAT_MG_2022 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_MG_22.parquet"
DADOS_NUM_MG_2022 = PASTA_DADOS_INTERMEDIARIOS / "dados_num_MG_22.parquet"
DADOS_TRAT_CAX_2022 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_CAX_22.parquet"

# 2023
DADOS_TRATADOS_2023 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2023.parquet"
DADOS_TRATADOS_MEDIAS_2023 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2023_medias.parquet"
DADOS_TRAT_MG_2023 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_MG_23.parquet"
DADOS_TRAT_CAX_2023 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_CAX_23.parquet"

# 2024
DADOS_TRATADOS_2024 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_24.parquet"
DADOS_TRATADOS_MEDIAS_2024 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_2024_medias.parquet"
RESULTADOS_TRATADOS_2024 = PASTA_DADOS_INTERMEDIARIOS / "resultados_tratados_24.parquet"
RESULTADOS_TRATADOS_MEDIAS_2024 = PASTA_DADOS_INTERMEDIARIOS / "resultados_tratados_2024_medias.parquet"

DADOS_TRAT_MG_2024 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_MG_24.parquet"
RESULTADOS_TRAT_MG_2024 = PASTA_DADOS_INTERMEDIARIOS / "resultados_tratados_MG_24.parquet"

DADOS_TRAT_CAX_2024 = PASTA_DADOS_INTERMEDIARIOS / "dados_tratados_CAX_24.parquet"
RESULTADOS_TRAT_CAX_2024 = PASTA_DADOS_INTERMEDIARIOS / "resultados_tratados_CAX_24.parquet"

# ======================
# ANALÍTICOS / CONSOLIDAÇÃO
# ======================
# Gerais / EDA
DADOS_MG_21_23 = PASTA_DADOS_ANALITICOS / "mg_21_23.parquet"
DADOS_MG_21_23_NUM = PASTA_DADOS_ANALITICOS / "mg_21_23_num.parquet"
DADOS_AGG_MG_ML = PASTA_DADOS_ANALITICOS / "dados_consolidados_mg_ml.parquet"

# 2024
AMOSTRAG_RESULTADOS_2024 = PASTA_DADOS_ANALITICOS / "amostrag_24.parquet"
DADOS_AGG_2024 = PASTA_DADOS_ANALITICOS / "dados_agg_24.parquet"
RESULTADOS_AGG_2024 = PASTA_DADOS_ANALITICOS / "resultado_agg_24.parquet"
MERGED_2024 = PASTA_DADOS_ANALITICOS / "merged_24.parquet"

# MG
DADOS_AGG_MG_21_23 = PASTA_DADOS_ANALITICOS / "dados_tratados_mg_agg.parquet"
MERGED_MG_NUM = PASTA_DADOS_ANALITICOS / "merged_mg_num.parquet"
MERGED_MG = PASTA_DADOS_ANALITICOS / "merged_mg.parquet"
DADOS_AGG_MG = PASTA_DADOS_ANALITICOS / "dados_agg_mg.parquet"
RESULTADOS_AGG_MG = PASTA_DADOS_ANALITICOS / "resultados_agg_mg.parquet"
DADOS_UNI_MG = PASTA_DADOS_ANALITICOS / "dados_uni_mg.parquet"
RESULTADOS_UNI_MG = PASTA_DADOS_ANALITICOS / "resultados_uni_mg.parquet"
AMOSTRAG_RESULTADOS_MG = PASTA_DADOS_ANALITICOS / "resultados_amostrag_mg.parquet"

# Caxambu
DADOS_CAX_21_23 = PASTA_DADOS_ANALITICOS / "dados_21_23_cax.parquet"
DADOS_AGG_CAX_21_23 = PASTA_DADOS_ANALITICOS / "dados_21_23_agg_cax.parquet"
MERGED_CAX = PASTA_DADOS_ANALITICOS / "merged_cax.parquet"
MERGED_CAX_NUM = PASTA_DADOS_ANALITICOS / "merged_num_cax.parquet"
RESULTADOS_AGG_CAX = PASTA_DADOS_ANALITICOS / "resultados_agg_cax.parquet"
DADOS_AGG_CAX = PASTA_DADOS_ANALITICOS / "dados_agg_cax.parquet"
DADOS_UNI_CAX = PASTA_DADOS_ANALITICOS / "dados_uni_cax.parquet"
RESULTADOS_UNI_CAX = PASTA_DADOS_ANALITICOS / "resultados_uni_cax.parquet"

# ======================
# MODELOS
# ======================
PASTA_MODELOS = PASTA_PROJETO / "modelos"
PASTA_MODELOS.mkdir(parents=True, exist_ok=True)

MODELO_FINAL = PASTA_MODELOS / "modelo.joblib"

# ======================
# RELATÓRIOS
# ======================
PASTA_RELATORIOS = PASTA_PROJETO / "relatorios"
PASTA_IMAGENS = PASTA_RELATORIOS / "imagens"

for pasta in [PASTA_RELATORIOS, PASTA_IMAGENS]:
    pasta.mkdir(parents=True, exist_ok=True)

RELATORIO = PASTA_RELATORIOS / "relatorio-eda.html"

# ======================
# RESULTADOS / MLFLOW
# ======================
PASTA_RESULTADOS = PASTA_PROJETO / "resultados"
PASTA_METRICAS = PASTA_RESULTADOS / "metricas"
PASTA_CONFIGURACOES = PASTA_RESULTADOS / "configuracoes"
PASTA_TABELAS = PASTA_RESULTADOS / "tabelas"

for pasta in [PASTA_RESULTADOS, PASTA_METRICAS, PASTA_CONFIGURACOES, PASTA_TABELAS]:
    pasta.mkdir(parents=True, exist_ok=True)

CONFIG_MODELO_NOTEBOOK = PASTA_CONFIGURACOES / "config_modelo_notebook.json"
METRICAS_NOTEBOOK = PASTA_METRICAS / "metricas_notebook.json"
METRICAS_PRODUCAO = PASTA_METRICAS / "metricas_producao.json"
COEFICIENTES_PATH = PASTA_TABELAS / "coeficientes.parquet"
IDE_PATH = PASTA_TABELAS / "dados_com_ide.parquet"
MODELO_FINAL = PASTA_MODELOS / "modelo_final.joblib"


# ======================
# TARGET
# ======================
TARGET = "NotaMedia"

# ======================
# MAPEAMENTOS GERAIS
# ======================
MAPA_MATERIA_LABEL_PARA_COLUNA = {
    "Média Geral": "nota_media",
    "Matemática": "nota_mt",
    "Ciências da Natureza": "nota_cn",
    "Ciências Humanas": "nota_ch",
    "Linguagens e Códigos": "nota_lc",
    "Redação": "nota_redacao",
}

MATERIAS_DASHBOARD = [
    "Média Geral",
    "Matemática",
    "Ciências da Natureza",
    "Ciências Humanas",
    "Linguagens e Códigos",
    "Redação",
]

MATERIAS_SEM_MEDIA_GERAL = [
    "Matemática",
    "Ciências da Natureza",
    "Ciências Humanas",
    "Linguagens e Códigos",
    "Redação",
]