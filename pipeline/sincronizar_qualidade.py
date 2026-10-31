"""Copia config/qualidade_ocorrencias.csv para a tabela qualidade_ocorrencias do banco (só essa tabela).

Uso: python -I pipeline/sincronizar_qualidade.py
Não altera nenhuma outra tabela. Registra a contagem antes/depois.
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import CONFIG, NUCLEO  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
df = pd.read_csv(CONFIG / "qualidade_ocorrencias.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"))
antes = con.execute("SELECT count(*) FROM qualidade_ocorrencias").fetchall()[0][0]
con.register("v_q", df)
con.execute("CREATE OR REPLACE TABLE qualidade_ocorrencias AS SELECT * FROM v_q")
depois = con.execute("SELECT string_agg(id, ', ' ORDER BY id) FROM qualidade_ocorrencias").fetchall()[0][0]
print(f"qualidade_ocorrencias: {antes} → {len(df)} linhas ({depois})")
con.close()
