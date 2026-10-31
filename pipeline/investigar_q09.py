"""Q09: compara a mesma tabela num ano que falha no T2 e num que passa (somente leitura).

Para o Brasil (nível Total/Graduação), mostra os valores por recorte e os cabeçalhos crus das colunas envolvidas.
Uso: python -I investigar_q09.py <tabela> <ano_falha> <ano_ok>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 120)
tab, a1, a2 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
D = ["org_academica", "dependencia", "categoria_privada", "modalidade", "sexo", "cor_raca"]
q = f"""SELECT f.ano, f.coluna, {', '.join('r.' + d for d in D)}, f.valor
  FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
  WHERE f.tabela = '{tab}' AND f.id_geo = 'BR' AND f.ano IN ({a1}, {a2})
    AND f.nivel_academico = (SELECT min(nivel_academico) FROM fato_sinopse WHERE tabela='{tab}' AND id_geo='BR' AND ano={a1})"""
df = con.execute(q).df()
w = df.pivot_table(index=D, columns="ano", values=["coluna", "valor"], aggfunc="first")
print(w.head(80).to_string())
xw = pd.read_csv(Path(__file__).resolve().parent.parent / "config" / "xw_colunas_sinopse.csv", encoding="utf-8-sig",
                 dtype=str, keep_default_na=False)
for a in (a1, a2):
    x = xw[(xw.tabela == tab) & (xw.ano == str(a))]
    print(f"\n== {tab} {a}: {len(x)} colunas; primeiras 30 rótulos")
    print(x[["coluna", "rotulo_completo"]].head(30).to_string(index=False))
