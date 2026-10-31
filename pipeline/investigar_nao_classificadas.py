"""Mostra as linhas da Sinopse que não foram classificadas, com as colunas identificadoras cruas (somente leitura)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO, PROJETO, STAGING

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 100); pd.set_option("display.max_colwidth", 40)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
nc = con.execute("SELECT * FROM linhas_nao_classificadas_sinopse ORDER BY ano, tabela, linha").df()
print("por ano/tabela:", nc.groupby(["ano", "tabela"]).size().to_dict())
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
for (ano, tab), g in list(nc.groupby(["ano", "tabela"]))[:6]:
    s = cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & cat.parquet.str.contains(f"\\\\{tab.replace('.', '.')}[._ ]", regex=True)]
    s = s if len(s) else cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba.str.split(" ").str[0] == tab)]
    pq = str(PROJETO / s.parquet.iloc[0]).replace("\\", "/")
    ls = ",".join(str(x) for x in g.linha)
    lin = g.linha.tolist()
    viz = sorted({l + d for l in lin for d in (-1, 0, 1)})
    print(f"\n== {ano} {tab} ({s.aba.iloc[0]!r}) — linhas {lin} e vizinhas")
    print(con.execute(f"""SELECT linha, "A", "B", "C", "D", "E", "F", "G" FROM read_parquet('{pq}')
                          WHERE linha IN ({','.join(map(str, viz))}) ORDER BY linha""").df().to_string(index=False))
