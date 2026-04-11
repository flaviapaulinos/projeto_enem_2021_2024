"""
categorias.py
=============

Constantes e mapeamentos para padronização de categorias do ENEM.

- Ordens (categorias ordenadas) usadas em análises e modelagem.
- Mapas de recodificação (questionário socioeconômico).
- Mapas específicos por ano (renda em R$).
- Padronização semântica das variáveis socioeconômicas
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
# ---------------------------------------------------------------------
# Ordens categóricas
# ---------------------------------------------------------------------

# -----------------------------
# Ordens (categorias ordenadas)
# -----------------------------

"""
Transformação da variável escola para análise de correlação

A variável escola é originalmente categórica nominal, representando o tipo de instituição de ensino médio frequentada pelos participantes:

* pública
* privada
* não informada

Para viabilizar sua inclusão em análises de correlação, foi adotada uma codificação ordinal controlada, baseada na relação empírica observada entre tipo de escola e desempenho médio.

Observou-se que:

* candidatos de escolas públicas apresentam, em média, menores notas;
* candidatos que não informaram o tipo de escola apresentam desempenho intermediário;
* candidatos de escolas privadas apresentam, em média, maiores notas.

Com base nesse padrão, definiu-se a seguinte ordenação:

* pública → 0
* não informada → 1
* privada → 2

Essa transformação não implica que a variável seja quantitativa, mas permite sua utilização como uma aproximação ordinal em análises exploratórias, especialmente em matrizes de correlação.

Interpretação

A codificação deve ser interpretada como um gradiente aproximado de condições educacionais associadas ao tipo de escola, e não como uma medida contínua.

Limitação metodológica

Essa abordagem pressupõe uma relação monotônica entre as categorias, o que pode não capturar completamente a heterogeneidade interna de cada grupo.

Por esse motivo, na etapa de modelagem, a variável escola é tratada como categórica, sendo transformada por meio de one-hot encoding, evitando a imposição de uma estrutura ordinal artificial no modelo.
"""

ORDEM_ANOS: List[str]=['2021', '2022', '2023', '2024']
ORDEM_ESCOLA: List[str]=['pública','não informada', 'privada', ]
ORDEM_FAIXA_ETARIA: List[str] = ["até 19", "20-25", "26-35", "36-45", "46-60", "acima de 61"]
ORDEM_SAL_MIN: List[str] = ["até 1", "1 a 3", "3 a 5", "5 a 10", "10 a 15", "15 a 20", "acima de 20"]
ORDEM_PAIS_ESCOLARIDADE: List[str] = ["desconhecida", "não estudou", "até fund", "médio", "superior", "pós-grad"]
ORDEM_OCUPACAO: List[str] = [ 'desconhecida','rural','básico', 'manual/tec', 'médio/tec', 'superior']
ORDEM_RACA:List[str]=['não informada','negra', 'branca', 'amarela', 'indígena']
ORDEM_SEXO: List[str]=['feminino', 'masculino']
ORDEM_ESTADO_CIVIL:List[str]=["não informado","solteiro","casado/mora com companheiro", "divorciado/separado", "viúvo"]
ORDEM_LINGUA:List[str]=["inglês", "espanhol"]


# -----------------------------
# Mapas "estáveis" (A–Q etc.)
# -----------------------------

MAP_FAIXA_ETARIA = {
    1: "até 19", 2: "até 19", 3: "até 19", 4: "até 19",
    5: "20-25", 6: "20-25", 7: "20-25", 8: "20-25", 9: "20-25", 10: "20-25",
    11: "26-35", 12: "26-35",
    13: "36-45", 14: "36-45",
    15: "46-60", 16: "46-60", 17: "46-60",
    18: "acima de 61", 19: "acima de 61", 20: "acima de 61",
}

MAP_ESCOLARIDADE = {
    "A": "não estudou",
    "B": "até fund", "C": "até fund", "D": "até fund",
    "E": "médio",
    "F": "superior",
    "G": "pós-grad",
    "H": "desconhecida",
}

MAP_OCUP = {
    "A": "rural",
    "B": "básico",
    "C": "manual/tec",
    "D": "médio/tec",
    "E": "superior",
    "F": "desconhecida",
}
MAP_COR_RACA = {
    0: "não informada",
    1: "branca",
    2: "negra",  # preta
    3: "negra",  # parda
    4: "amarela",
    5: "indígena",
    6: "não informada",
}

MAP_ESTADO_CIVIL = {
    0: "não informado",
    1: "solteiro",
    2: "casado/mora com companheiro",
    3: "divorciado/separado",
    4: "viúvo",
}

MAP_ESCOLA = {1: "não informada", 2: "pública", 3: "privada"}

MAP_LINGUA = {0: "inglês", 1: "espanhol"}

MAP_BENS_ABCDE = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4} #4+
MAP_BENS_ABCD = {"A": 0, "B": 1, "C": 2, "D": 3}#3+
MAP_BENS_AB = {"A": 0, "B": 1}

MAP_EMP_DOMST = {"A": 0, "B": 1, "C": 3, "D": 5}

MAP_SEXO = {"F": "feminino", "M": "masculino"}

# -----------------------------
# Renda em salários mínimos
# -----------------------------

MAP_SAL_MIN_POR_LETRA = {
    "A": "até 1",
    "B": "1 a 3", "C": "1 a 3", "D": "1 a 3", "E": "1 a 3", "F": "1 a 3",
    "G": "3 a 5", "H": "3 a 5",
    "I": "5 a 10", "J": "5 a 10", "K": "5 a 10", "L": "5 a 10", "M": "5 a 10",
    "N": "10 a 15", "O": "10 a 15",
    "P": "15 a 20",
    "Q": "acima de 20",
}

MAP_DADOS_ESCOLA_2024= {
    "A": "pública",
    "B": "pública",
    "C": "pública",
    "D": "privada",
    "E": "privada",
    "F": "não informada",
}


MAP_RESULTADOS_ESCOLA_2024= {
    1: "pública",
    2: "pública",
    3: "pública",
    4: "privada",
  
}

MAP_SAL_MIN_RENDA_MEDIA={
    'até 1': 0.5,   
    '1 a 3':2,
    '3 a 5': 4,    
    '5 a 10': 7.5,    
    '10 a 15': 12.5,   
    '15 a 20': 17.5,    
    'acima de 20': 22,   
             
   }
    
MAP_SAL_MIN_SEG={	
    'até 1':'até 1',
    '1 a 3': '1 a 3',
    '3 a 5': '3 a 5',
    '5 a 10': '5 a 10',
    '10 a 15': '10 a 15',
    '15 a 20':'acima de 15',
    'acima de 20': 'acima de 15' ,        
        
}

MAP_FAIXA_ETARIA_SEG={
    'até 19': 'até 25',
    '20-25': 'até 25',
    '26-35': '26-45',
    '36-45': '26-45',
    '46-60': 'acima de 46',
    'acima de 61': 'acima de 46',
}

# -----------------------------
# MAPEAMENTO REVERSO
# -----------------------------


MAP_ESCOLARIDADE_REV = dict(enumerate(ORDEM_PAIS_ESCOLARIDADE))
MAP_OCUP_REV = dict(enumerate(ORDEM_OCUPACAO))