"""Mostra os grupos de colunas da Sinopse que caem no mesmo recorte (somente leitura).
Reaproveita a lógica de p3_mapear_sinopse.py sem gravar nada."""
import runpy, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import PROJETO, STAGING

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 140); pd.set_option("display.max_rows", 200)
# executa o mapeamento até antes da checagem de duplicidade
src = Path(__file__).with_name("p3_mapear_sinopse.py").read_text(encoding="utf-8")
src = src.split("dup = X.duplicated")[0]
ns = {"__file__": str(Path(__file__).with_name("p3_mapear_sinopse.py"))}
exec(compile(src, "p3_mapear_sinopse.py", "exec"), ns)
X, DIMS = ns["X"], ns["DIMS"]
k = ["ano", "tabela", "indicador"] + DIMS
g = X[X.duplicated(k, keep=False)].sort_values(k + ["coluna"])
print("tabelas×anos com duplicidade:", g.groupby(["ano", "tabela"]).size().to_dict())
for key, gg in list(g[g.ano == 2017].groupby(k))[:6]:
    print("\n--", {d: v for d, v in zip(k, key) if v not in ("Total", "Não se aplica")})
    print(gg[["coluna", "rotulo_completo"]].to_string(index=False))
# conteúdo da coluna oculta BI da 6.5 de 2017 × coluna F
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
pq = str(PROJETO / cat[(cat.ano == 2017) & (cat.aba.str.startswith("6.5"))].parquet.iloc[0]).replace("\\", "/")
print("\n6.5/2017 coluna oculta BI × F:", duckdb.sql(f"""SELECT count(*) linhas, count("BI") bi_preenchidas,
      count(*) FILTER (WHERE "BI" IS NOT NULL AND "BI" <> "F") bi_diferente_de_f FROM read_parquet('{pq}') WHERE linha >= 11""").fetchall())
print(duckdb.sql(f"""SELECT linha, "A", "F", "BI" FROM read_parquet('{pq}') WHERE linha BETWEEN 5 AND 16""").df().to_string(index=False))
