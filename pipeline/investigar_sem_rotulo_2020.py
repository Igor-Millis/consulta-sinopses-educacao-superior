"""Colunas sem rótulo com dados (Sinopse 2020: 3.2 FM–HK; 4.4 HE–JY): são cópias de colunas rotuladas? (somente leitura)

Para cada coluna sem rótulo, procura uma coluna rotulada da mesma aba com valores idênticos em todas as linhas de dados.
Compara também com a mesma tabela de 2019 e 2021 (por posição), caso seja uma cópia de outro ano.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import PROJETO, STAGING, col2n, n2col

sys.stdout.reconfigure(encoding="utf-8")
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")


def ler(ano, aba, ini):
    pq = str(PROJETO / cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba == aba)].parquet.iloc[0]).replace("\\", "/")
    return duckdb.sql(f"SELECT * FROM read_parquet('{pq}') WHERE linha >= {ini}").df()


for aba, rot_fim, sem_ini, sem_fim, ini in (("3.2", "BW", "FM", "HK", 12), ("4.4", "HD", "HE", "JY", 12)):
    df = ler(2020, aba, ini)
    rot = [n2col(i) for i in range(col2n("E"), col2n(rot_fim) + 1)]
    sem = [n2col(i) for i in range(col2n(sem_ini), col2n(sem_fim) + 1)]
    iguais = {}
    for s in sem:
        for r in rot:
            if df[s].equals(df[r]):
                iguais[s] = r
                break
    print(f"== 2020 {aba}: {len(sem)} colunas sem rótulo ({sem_ini}–{sem_fim}); idênticas a uma coluna rotulada: {len(iguais)}")
    print("   exemplos:", dict(list(iguais.items())[:8]))
    # soma das sem rótulo × colunas de total
    tot = pd.to_numeric(df["E"], errors="coerce")
    print("   1ª linha (Total Brasil): E =", df["E"].iloc[0], "| sem rótulo:", df[sem[:12]].iloc[0].tolist())
    print("   cabeçalho rotulado (1ª linha):", df[rot[:12]].iloc[0].tolist())
