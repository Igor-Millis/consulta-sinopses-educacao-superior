"""Auditoria do núcleo DuckDB (somente leitura): tabelas, visões, colunas, contagens e status.

Uso: python -I auditar_banco.py   → imprime e grava dados/qualidade/auditoria_banco.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO, QUALIDADE

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit = '3GB'")
out = []


def p(s=""):
    print(s, flush=True)
    out.append(str(s))


objs = con.execute("""SELECT table_name, table_type FROM information_schema.tables
                      WHERE table_schema = 'main' ORDER BY table_type, table_name""").fetchall()
p(f"# Auditoria do banco {NUCLEO / 'ijsn.duckdb'} ({(NUCLEO / 'ijsn.duckdb').stat().st_size / 2**30:.2f} GB)")
for nome, tipo in objs:
    cols = con.execute(f"""SELECT column_name || ':' || data_type FROM information_schema.columns
                           WHERE table_name = '{nome}' ORDER BY ordinal_position""").fetchall()
    try:
        n = con.execute(f"SELECT count(*) FROM {nome}").fetchone()[0] if tipo == "BASE TABLE" else "—"
    except Exception as e:  # visão quebrada
        n = f"ERRO: {e}"
    if tipo == "VIEW":
        try:
            con.execute(f"EXPLAIN SELECT * FROM {nome}").fetchall()  # valida sem executar (v_anexo_i agrega 610 mi)
            ok = "ok (compila)"
        except Exception as e:
            ok = f"ERRO: {str(e)[:120]}"
        n = ok
    p(f"- [{tipo}] {nome}: {n if isinstance(n, str) else f'{n:,}'} | " + ", ".join(c for (c,) in cols))
p()
p("## Fatos por conjunto/ano e status")
p(con.execute("SELECT anexo, status_valor, count(*) n FROM fato_anexo_curso GROUP BY ALL ORDER BY 1, 3 DESC").df().to_string(index=False))
p(con.execute("SELECT status_valor, id_ocorrencia, count(*) n FROM fato_sinopse GROUP BY ALL ORDER BY 3 DESC").df().to_string(index=False))
p(con.execute("SELECT ano, count(*) AS sinopse, count(DISTINCT tabela) AS tabelas FROM fato_sinopse GROUP BY 1 ORDER BY 1").df().to_string(index=False))
p()
p("## Ocorrências de qualidade")
p(con.execute("SELECT id, anos, tabela, situacao FROM qualidade_ocorrencias ORDER BY id").df().to_string(index=False))
p()
p("## Carga")
p(con.execute("SELECT * FROM carga_log ORDER BY quando").df().to_string(index=False))
(QUALIDADE / "auditoria_banco.txt").write_text("\n".join(out), encoding="utf-8")
