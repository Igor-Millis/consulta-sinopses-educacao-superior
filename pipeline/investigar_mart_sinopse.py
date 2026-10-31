"""Por que as tabelas 4.6–4.8, 5.5–5.7, 6.5–6.7 não entram em mart_sinopse_geo?

Achado (30/10/2026): nessas tabelas sexo/cor/faixa só são abertos nas FOLHAS org. acadêmica × dependência ×
categoria privada; não há linha "Total org./dep." aberta por sexo. Este script testa a soma das folhas contra o
total conhecido (ES 2024: matrículas = 182.335 = Σ municípios dos Anexos).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit='2GB'")
print(con.execute("""SELECT tabela, nivel_academico, count(*) n FROM fato_sinopse
    WHERE tabela IN ('4.6','4.7','4.8','5.5','5.6','5.7','6.5','6.6','6.7') AND ano = 2024 GROUP BY ALL ORDER BY 1, 2""").df().to_string())
print(con.execute("""SELECT DISTINCT r.org_academica, r.dependencia, r.categoria_privada FROM fato_sinopse f
    JOIN dim_recorte_sinopse r USING (id_recorte) WHERE f.tabela = '5.5' AND f.ano = 2024 ORDER BY ALL""").df().to_string())
LEAF = """r.org_academica <> 'Total' AND r.dependencia <> 'Total' AND r.categoria_privada <> 'Total'"""
for tab, dim in [("5.5", "sexo"), ("5.6", "cor_raca"), ("5.7", "faixa_etaria")]:
    outros = "sexo = 'Total' AND " if dim != "sexo" else ""
    print(tab, con.execute(f"""SELECT f.nivel_academico, sum(f.valor) soma, count(*) n FROM fato_sinopse f
        JOIN dim_recorte_sinopse r USING (id_recorte)
        WHERE f.tabela = '{tab}' AND f.ano = 2024 AND f.id_geo = 'UF-32' AND {LEAF} AND {outros} r.{dim} <> 'Total'
        GROUP BY ALL""").df().to_string())
    print("  total publicado (todas as linhas Total):", con.execute(f"""SELECT f.nivel_academico, f.valor FROM fato_sinopse f
        JOIN dim_recorte_sinopse r USING (id_recorte) WHERE f.tabela = '{tab}' AND f.ano = 2024 AND f.id_geo = 'UF-32'
        AND r.org_academica = 'Total' AND r.dependencia = 'Total' AND r.sexo = 'Total' AND r.{dim} = 'Total'""").fetchall())
