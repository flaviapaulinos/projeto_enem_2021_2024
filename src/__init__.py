"""
src
===

Pacote principal do projeto ENEM — estrutura social.
"""


# Em vez disso, faça assim:
from . import config

__all__ = ["config"]


import os
import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent  # Corrigido: sobe um nível
sys.path.append(str(ROOT_PATH))