"""Mostra um pickle intermediario. Uso: python -I inspect_pkl.py <arquivo.pkl> <consulta|-> <colunas|-> [n]"""
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 120)
pd.set_option("display.max_rows", 1000); pd.set_option("display.max_columns", 50)
df = pd.read_pickle(sys.argv[1])
if len(sys.argv) > 2 and sys.argv[2] != "-":
    df = df.query(sys.argv[2])
if len(sys.argv) > 3 and sys.argv[3] != "-":
    df = df[sys.argv[3].split(",")]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 200
print(df.head(n).to_string())
print(f"[{len(df)} linhas]")
