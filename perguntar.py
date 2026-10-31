"""Atalho: python -I perguntar.py "Quantas matrículas havia em Vila Velha em 2024?"  (sem argumento: modo interativo)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motor.api import main  # noqa: E402

main()
