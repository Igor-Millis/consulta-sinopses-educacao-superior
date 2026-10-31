"""Mostra o estado do núcleo (somente leitura): tabelas e contagens dos fatos."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
t = [r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()]
print("tabelas:", len(t))
print("fato_sinopse existe:", "fato_sinopse" in t)
if "fato_sinopse" in t:
    print("  por ano:", con.execute("SELECT ano, count(*) FROM fato_sinopse GROUP BY 1 ORDER BY 1").fetchall())
    print("  tabelas×anos:", con.execute("SELECT count(DISTINCT ano || tabela) FROM fato_sinopse").fetchone()[0], "(esperado 526)")
print("fato_anexo_curso:", con.execute("SELECT anexo, count(*) FROM fato_anexo_curso GROUP BY 1").fetchall())
print("últimas cargas:", con.execute("SELECT * FROM carga_log ORDER BY quando DESC LIMIT 4").fetchall())
