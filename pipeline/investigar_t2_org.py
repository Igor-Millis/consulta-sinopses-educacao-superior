"""Caso concreto do T2 (org_academica, soma menor) na 4.2 de 2024, Brasil, Graduação (somente leitura)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 100)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
for tab in ("4.2", "5.1", "1.1"):
    print(f"\n== {tab} 2024, Brasil — recortes com forma_ingresso/demais = Total")
    print(con.execute(f"""
      SELECT r.org_academica, r.dependencia, r.categoria_privada, r.forma_ingresso, f.valor, f.aba || '!' || f.coluna || f.linha AS origem
      FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
      WHERE f.ano = 2024 AND f.tabela = '{tab}' AND f.id_geo = 'BR' AND f.nivel_academico IN ('Total', 'Graduação')
        AND r.forma_ingresso IN ('Total') AND r.grau = 'Total' AND r.modalidade = 'Total'
        AND f.nivel_academico = (SELECT max(nivel_academico) FROM fato_sinopse WHERE ano = 2024 AND tabela = '{tab}' AND id_geo = 'BR')
      ORDER BY r.org_academica, r.dependencia, r.categoria_privada""").df().to_string(index=False))
