# scripts/setup.py
from pathlib import Path

# Raiz do projeto
ROOT = Path(__file__).resolve().parents[1]

# Pastas para criar
pastas = [
    "resultados/metricas",
    "resultados/configuracoes", 
    "resultados/tabelas",
    "modelos",
    "relatorios/imagens",
    "logs"
]

for pasta in pastas:
    (ROOT / pasta).mkdir(parents=True, exist_ok=True)
    print(f"✅ Criada: {pasta}")

print("\n📁 Estrutura criada com sucesso!")