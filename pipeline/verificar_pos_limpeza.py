"""Verificação pós-limpeza (somente leitura): itens apagados ausentes, banco atual íntegro, ZIPs intactos, disco.

Uso: python -I pipeline/verificar_pos_limpeza.py   → imprime e grava dados/qualidade/verificacao_pos_limpeza.txt
ZIPs: MD5 recalculado × config/manifesto_fontes.csv (registrado na P0). Banco: aberto só para leitura; tabelas,
visões (compilam), contagens e uma consulta simples; mais uma pergunta pelo motor.
"""
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import duckdb
import pandas as pd
from comum import CONFIG, NUCLEO, PROJETO, md5

sys.stdout.reconfigure(encoding="utf-8")
linhas, falhas = [], 0


def p(ok, msg):
    global falhas
    falhas += not ok
    linhas.append(f"{'OK   ' if ok else 'FALHA'} {msg}")
    print(linhas[-1], flush=True)


antigo = NUCLEO / "ijsn_pre_compactacao_20261031_011217.duckdb"
p(not antigo.exists(), f"banco antigo ausente: {antigo}")
xlsx = Path(os.environ.get("TEMP", "")) / "ijsn_pipeline"
p(not xlsx.exists(), f"pasta de cópias XLSX ausente: {xlsx}")
banco = NUCLEO / "ijsn.duckdb"
p(banco.exists(), f"banco atual existe: {banco} ({banco.stat().st_size / 2**30:.2f} GB, {banco.stat().st_size:,} bytes)")

man = pd.read_csv(CONFIG / "manifesto_fontes.csv", encoding="utf-8-sig")
col_md5 = "md5"
for _, r in man.sort_values("ano").iterrows():
    z = PROJETO / r.arquivo_zip
    ok = z.exists() and z.stat().st_size == int(r.bytes) and md5(z).upper() == str(r[col_md5]).upper()
    p(ok, f"ZIP {int(r.ano)}: {z.name} {z.stat().st_size:,} bytes, MD5 {r[col_md5]} "
          f"{'igual ao manifesto' if ok else 'DIFERENTE/ausente'}")
p(len(man) == 8, f"manifesto com {len(man)} ZIPs (esperado 8)")

con = duckdb.connect(str(banco), read_only=True)
con.execute("SET memory_limit = '2GB'")
tabs = [r[0] for r in con.execute("SELECT table_name FROM duckdb_tables() ORDER BY 1").fetchall()]
p(len(tabs) == 25, f"{len(tabs)} tabelas (esperado 25)")
vis = [r[0] for r in con.execute("SELECT view_name FROM duckdb_views() WHERE NOT internal").fetchall()]
erros_v = []
for v in vis:
    try:
        con.execute(f"SELECT * FROM {v} LIMIT 0").fetchall()
    except Exception as e:
        erros_v.append(f"{v}: {e}")
p(len(vis) == 8 and not erros_v, f"{len(vis)} visões, {len(vis) - len(erros_v)} compilam {erros_v or ''}")
esperado = {"fato_sinopse": 126_758_202, "fato_anexo_curso": 609_970_482, "mart_anexos_geo": 662_772,
            "mart_curso_geo": 3_182_105, "mart_sinopse_geo": 2_741_684}
for t, n in esperado.items():
    c = con.execute(f"SELECT count(*) FROM {t}").fetchall()[0][0]
    p(c == n, f"{t}: {c:,} linhas (esperado {n:,})")
st = dict(con.execute("SELECT status_valor, count(*) FROM fato_sinopse GROUP BY 1").fetchall())
p(st.get("suspeito") == 80_369 and st.get("somente_presencial") == 178_644,
  f"marcações de qualidade preservadas: suspeito {st.get('suspeito'):,}, somente_presencial {st.get('somente_presencial'):,}")
v = con.execute("""SELECT sum(valor) FROM mart_anexos_geo WHERE ano = 2024 AND id_geo = 'UF-32'
                   AND indicador = 'matriculas'""").fetchall()[0][0]
p(v == 182_335, f"consulta simples de leitura: matrículas ES 2024 = {v:,} (esperado 182.335, = Sinopse 5.1)")
con.close()

from motor.api import perguntar  # noqa: E402
r = perguntar("Quantas matrículas havia em Vila Velha em 2024?")
p(r.tabela is not None and r.tabela["valor"].iloc[0] == 27_743, "motor: Vila Velha 2024 = 27.743 matrículas")

livre = shutil.disk_usage("C:\\").free
linhas.append(f"disco C: {livre / 2**30:.1f} GB livres")
print(linhas[-1])
resumo = f"{'TUDO OK' if falhas == 0 else f'{falhas} FALHA(S)'} — verificado em {datetime.now():%d/%m/%Y %H:%M:%S}"
linhas.append(resumo)
print(resumo)
(PROJETO / "dados" / "qualidade" / "verificacao_pos_limpeza.txt").write_text("\n".join(linhas), encoding="utf-8")
sys.exit(0 if falhas == 0 else 1)
