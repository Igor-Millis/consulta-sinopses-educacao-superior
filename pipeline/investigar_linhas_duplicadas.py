"""Linhas da Sinopse com a mesma geografia repetida na mesma tabela (somente leitura)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO, PROJETO, STAGING

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 40)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
d = con.execute("""SELECT ano, tabela, id_geo, nivel_geo, nivel_academico, list(linha ORDER BY linha) AS linhas
  FROM stg_linhas_sinopse GROUP BY ALL HAVING count(*) > 1 ORDER BY ano, tabela""").df()
print("geografias repetidas por ano/tabela:", d.groupby(["ano", "tabela"]).size().to_dict())
print("nível das repetidas:", d.nivel_geo.value_counts().to_dict())
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
for (ano, tab), g in d.groupby(["ano", "tabela"]):
    aba = con.execute(f"SELECT aba FROM dim_tabela_sinopse WHERE ano={ano} AND tabela='{tab}'").fetchone()[0]
    pq = str(PROJETO / cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba == aba)].parquet.iloc[0]).replace("\\", "/")
    r = g.iloc[0]
    ls = list(r.linhas)
    print(f"\n== {ano} {tab}: {len(g)} geografias repetidas; exemplo {r.id_geo} ({r.nivel_geo}) nas linhas {ls}")
    igual = con.execute(f"""SELECT count(DISTINCT md5(CAST(columns(* EXCLUDE (linha, _num_como_texto, _extra)) AS VARCHAR)))
                            FROM read_parquet('{pq}') WHERE linha IN ({','.join(map(str, ls))})""").fetchall()
    print(con.execute(f"""SELECT linha, "A", "B", "C", "D", "E", "F", "G", "H" FROM read_parquet('{pq}')
                          WHERE linha IN ({','.join(str(x) for l in ls for x in (l - 1, l, l + 1))}) ORDER BY linha""").df().to_string(index=False))
    todas = [l for ls_ in g.linhas for l in ls_]
    # as linhas repetidas têm valores idênticos?
    df = con.execute(f"SELECT * EXCLUDE (_num_como_texto, _extra) FROM read_parquet('{pq}') WHERE linha IN ({','.join(map(str, todas))})").df()
    df = df.set_index("linha")
    ident = sum(df.loc[list(x)].drop_duplicates().shape[0] == 1 for x in g.linhas)
    print(f"   repetições com conteúdo idêntico em todas as colunas: {ident} de {len(g)}")
