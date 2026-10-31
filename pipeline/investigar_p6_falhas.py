"""Investiga as falhas V5 (Σ categorias ≠ total em 6.6) e V7 (Σ dependências de IES ≠ total) da p6_validar."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit='2GB'")
print("V5 — falhas por tabela × ano (UF):")
print(con.execute("""
WITH s AS (SELECT ano, tabela, id_geo, sum(valor) a FROM mart_sinopse_geo WHERE modo='soma das folhas' AND nivel_geo='UF' GROUP BY ALL),
     t AS (SELECT f.ano, f.tabela, f.id_geo, f.valor b FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
           WHERE f.nivel_geo='UF' AND f.nivel_academico='Graduação' AND r.org_academica='Total' AND r.dependencia='Total'
             AND r.sexo='Total' AND r.cor_raca='Total' AND r.faixa_etaria='Total')
SELECT tabela, ano, count(*) ufs_com_falha, sum(b - a) dif_total, sum(b) total FROM s JOIN t USING (ano, tabela, id_geo)
WHERE a <> b GROUP BY ALL ORDER BY ALL""").df().to_string(index=False))
print("\n6.6 — status das células das folhas (UF), por ano:")
print(con.execute("""SELECT f.ano, f.status_valor, count(*) n, sum(f.valor) soma FROM fato_sinopse f
    JOIN dim_recorte_sinopse r USING (id_recorte) WHERE f.tabela='6.6' AND f.nivel_geo='UF' AND f.nivel_academico='Graduação'
    AND r.org_academica<>'Total' AND r.dependencia<>'Total' AND r.categoria_privada<>'Total' AND r.sexo='Total' AND r.cor_raca<>'Total'
    GROUP BY ALL ORDER BY ALL""").df().to_string(index=False))
print("\nV7 — categorias de dependência em 1.1 por ano (Brasil):")
print(con.execute("""SELECT ano, categoria, valor FROM mart_sinopse_geo WHERE tabela='1.1' AND id_geo='BR'
    AND dimensao IN ('dependencia','total') ORDER BY ano, categoria""").df().to_string(index=False))
print(con.execute("""SELECT DISTINCT f.ano, r.dependencia, r.categoria_privada, r.tipo_privada, r.org_academica
    FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte) WHERE f.tabela='1.1' AND f.id_geo='BR' AND f.ano IN (2018, 2019)
    ORDER BY ALL""").df().to_string(index=False))
