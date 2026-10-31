"""Mostra as linhas de cabeçalho cruas de uma aba no staging, para colunas escolhidas (somente leitura).

Uso: python -I ver_cabecalho.py <ano> <aba> <col_ini> <col_fim> [linha_ini linha_fim]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import PROJETO, STAGING, col2n, n2col

sys.stdout.reconfigure(encoding="utf-8")
ano, aba, c1, c2 = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
l1, l2 = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (6, 12)
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
pq = str(PROJETO / cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba == aba)].parquet.iloc[0]).replace("\\", "/")
cols = [n2col(i) for i in range(col2n(c1), col2n(c2) + 1)]
df = duckdb.sql(f"SELECT linha, {', '.join(chr(34) + c + chr(34) for c in cols)} FROM read_parquet('{pq}') WHERE linha BETWEEN {l1} AND {l2}").df()
for _, r in df.iterrows():
    cel = [f"{c}={str(r[c]).strip()[:28]!r}" for c in cols if pd.notna(r[c]) and str(r[c]).strip()]
    print(int(r.linha), " | ".join(cel))
