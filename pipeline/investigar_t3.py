"""Investiga as falhas do T3 da P2 (Brasil por curso ≠ Σ Município + Distância + Exterior). Somente leitura."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO, QUALIDADE

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90)
d = pd.read_csv(QUALIDADE / "p2_divergencias.csv", encoding="utf-8-sig")
x = d[d.teste == "T3"]
print("falhas por ano:", x.groupby("ano").size().to_dict())
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
PUB = "COALESCE(valor, TRY_CAST(valor_bruto AS BIGINT))"
idt = con.execute("""SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
                     AND dependencia='Total' AND categoria_privada='Total'""").fetchone()[0]
for anexo in ("anexo_iii", "anexo_i"):
    xa = x[x.detalhe.str.startswith(anexo)]
    ano = int(xa.ano.iloc[0])
    lin = int(xa.detalhe.iloc[0].split("!")[1].split(" ")[0].lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    cine = con.execute(f"SELECT co_cine FROM fato_anexo_curso WHERE anexo='{anexo}' AND ano={ano} AND linha={lin} LIMIT 1").fetchone()[0]
    nome = con.execute(f"SELECT no_cine FROM dim_curso_cine WHERE ano={ano} AND co_cine='{cine}'").fetchone()
    print(f"\n== {anexo} {ano} linha {lin}: curso {cine} {nome}")
    print(con.execute(f"""SELECT nivel_geo, indicador, count(*) AS linhas, sum({PUB}) AS total, min(linha) AS primeira_linha
        FROM fato_anexo_curso WHERE anexo='{anexo}' AND ano={ano} AND co_cine='{cine}' AND id_recorte={idt}
        GROUP BY 1, 2 ORDER BY 2, 1""").df().to_string(index=False))
    # existe linha Distância com outro código para o mesmo nome de curso?
    print(con.execute(f"""SELECT s.nivel_geo, s.co_cine_original, s.no_cine, s.linha FROM stg_linhas_anexo s
        WHERE s.anexo='{anexo}' AND s.ano={ano} AND s.nivel_geo IN ('Distância', 'Brasil')
          AND (s.no_cine = (SELECT no_cine FROM dim_curso_cine WHERE ano={ano} AND co_cine='{cine}') OR replace(s.co_cine_original, '"', '') = '{cine}')
        ORDER BY s.linha""").df().to_string(index=False))
