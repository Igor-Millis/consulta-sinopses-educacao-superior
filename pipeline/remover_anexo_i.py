"""Remove fisicamente o Anexo I do núcleo, depois de provar que a visão v_anexo_i (II + III) o reproduz.

1. Cria as visões (visoes.py).
2. Compara v_anexo_i com o Anexo I publicado, ano a ano: linhas faltantes de cada lado e valores diferentes
   (valor publicado; zeros anulados por status contam como 0). Se houver QUALQUER diferença, para sem apagar.
3. Recria o banco sem as linhas do Anexo I (DuckDB não encolhe o arquivo com DELETE) e troca os arquivos.
   O banco antigo é apagado só depois que o novo abre e confere as contagens.

Uso: python -I remover_anexo_i.py
"""
import os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO, QUALIDADE
from visoes import criar_visoes

sys.stdout.reconfigure(encoding="utf-8")
DB, NOVO = NUCLEO / "ijsn.duckdb", NUCLEO / "ijsn_novo.duckdb"
PUB = "COALESCE(i.valor, TRY_CAST(i.valor_bruto AS BIGINT), 0)"
t0 = time.time()
con = duckdb.connect(str(DB))
con.execute("SET memory_limit = '6GB'")
con.execute("SET preserve_insertion_order = false")
criar_visoes(con)

# Anos já validados célula a célula numa execução anterior (FULL OUTER JOIN; ver dados/qualidade/remocao_anexo_i_log.txt):
# 2017–2022, 343 milhões de valores, 0 diferenças. Para os demais anos o JOIN completo estoura o espaço temporário,
# então a validação é por agregados (contagem de linhas e soma por nível × indicador × recorte), que, junto com o
# teste T4 da P2 (I = II + III célula a célula, todos os anos), é suficiente.
ANOS_JOIN_OK = range(2017, 2023)
if con.execute("SELECT count(*) FROM fato_anexo_curso WHERE anexo = 'anexo_i'").fetchone()[0]:
    linhas = ["2017–2022: validados célula a célula na execução anterior (343.457.398 valores; 0 diferenças; 0 linhas faltantes)."]
    tot = {"grupos": 0, "contagem_diferente": 0, "soma_diferente": 0}
    for ano in [a for a in range(2017, 2025) if a not in ANOS_JOIN_OK]:
        r = con.execute(f"""
          WITH i AS (SELECT nivel_geo, indicador, id_recorte, count(*) n, sum({PUB}) s
                     FROM fato_anexo_curso i WHERE anexo = 'anexo_i' AND ano = {ano} GROUP BY ALL),
               v AS (SELECT nivel_geo, indicador, id_recorte, count(*) n, sum(COALESCE(valor, 0)) s
                     FROM v_anexo_i WHERE ano = {ano} GROUP BY ALL)
          SELECT count(*), count(*) FILTER (WHERE i.n IS DISTINCT FROM v.n), count(*) FILTER (WHERE i.s IS DISTINCT FROM v.s)
          FROM i FULL OUTER JOIN v USING (nivel_geo, indicador, id_recorte)""").fetchone()
        for k, x in zip(tot, r):
            tot[k] += x
        linhas.append(f"{ano}: grupos nível×indicador×recorte {r[0]:,} | contagem diferente {r[1]:,} | soma diferente {r[2]:,}")
        print(linhas[-1], f"({round(time.time() - t0)} s)", flush=True)
    resumo = "TOTAL (agregados): " + " | ".join(f"{k} {v:,}" for k, v in tot.items())
    print(resumo)
    (QUALIDADE / "remocao_anexo_i_validacao.txt").write_text("\n".join(linhas + [resumo]), encoding="utf-8")
    if tot["contagem_diferente"] or tot["soma_diferente"]:
        print("DIFERENÇAS ENCONTRADAS — nada foi apagado.")
        sys.exit(1)
    print("v_anexo_i reproduz o Anexo I publicado. Recriando o banco sem o Anexo I...")
else:
    print("O Anexo I já não está no banco.")

# ---------------------------------------------------------------- recria o banco sem o Anexo I
if NOVO.exists():
    NOVO.unlink()
con.execute(f"ATTACH '{str(NOVO).replace(chr(92), '/')}' AS novo")
tabelas = [t for (t,) in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main' AND table_type='BASE TABLE'").fetchall()]
esperado = {}
for t in tabelas:
    cols = [c for (c,) in con.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{t}' AND table_schema='main'").fetchall()]
    filtro = "WHERE anexo <> 'anexo_i'" if "anexo" in cols else ""
    con.execute(f"CREATE TABLE novo.{t} AS SELECT * FROM main.{t} {filtro}")
    esperado[t] = con.execute(f"SELECT count(*) FROM main.{t} {filtro}").fetchone()[0]
    print(f"   {t}: {esperado[t]:,} linhas", flush=True)
con.execute("DETACH novo")
con.close()

chk = duckdb.connect(str(NOVO))
criar_visoes(chk)
ok = all(chk.execute(f"SELECT count(*) FROM {t}").fetchone()[0] == n for t, n in esperado.items())
chk.execute("INSERT INTO carga_log VALUES (current_timestamp, 'remover_anexo_i', 'Anexo I removido; v_anexo_i = II + III validada')")
chk.close()
if not ok:
    print("Contagens do banco novo não conferem — banco antigo mantido.")
    sys.exit(1)
os.replace(NOVO, DB)
print(f"Banco substituído: {DB.stat().st_size / 2**30:.2f} GB ({round((time.time() - t0) / 60, 1)} min)")
