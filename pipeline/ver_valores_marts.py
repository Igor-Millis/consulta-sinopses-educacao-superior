"""Lista os valores distintos das dimensões dos marts (referência para o catálogo semântico do motor)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
for col in ["nivel_geo", "indicador", "modalidade", "org_academica", "grau", "dependencia", "categoria_privada", "rede"]:
    print("mart_anexos_geo", col, [r[0] for r in con.execute(f"SELECT DISTINCT {col} FROM mart_anexos_geo ORDER BY 1").fetchall()])
print("anexos: indicador × modalidade × nível:", con.execute("""SELECT indicador, modalidade, string_agg(DISTINCT nivel_geo, ',')
    FROM mart_anexos_geo GROUP BY ALL ORDER BY ALL""").fetchall())
for col in ["nivel_geo", "indicador", "modalidade", "tipo_cine"]:
    print("mart_curso_geo", col, [r[0] for r in con.execute(f"SELECT DISTINCT {col} FROM mart_curso_geo ORDER BY 1").fetchall()])
print(con.execute("DESCRIBE xw_cine").df()[["column_name", "column_type"]].to_string())
print(con.execute("SELECT * FROM xw_cine WHERE co_cine_ref IS NOT NULL AND co_cine <> co_cine_ref LIMIT 5").df().to_string())
print(con.execute("SELECT tipo, count(*) FROM xw_cine GROUP BY 1").fetchall())
for col in ["nivel_geo", "nivel_academico", "dimensao"]:
    print("mart_sinopse_geo", col, [r[0] for r in con.execute(f"SELECT DISTINCT {col} FROM mart_sinopse_geo ORDER BY 1").fetchall()])
print(con.execute("SELECT dimensao, string_agg(DISTINCT categoria, ' | ') FROM mart_sinopse_geo GROUP BY 1").fetchall())
print(con.execute("SELECT DISTINCT tabela, indicador, nivel_academico FROM mart_sinopse_geo ORDER BY 1").fetchall())
print(con.execute("SELECT nivel_geo, min(id_geo), max(id_geo), count(*) FROM dim_geografia GROUP BY 1").fetchall())
print(con.execute("DESCRIBE dim_geografia").df()[["column_name", "column_type"]].to_string())
