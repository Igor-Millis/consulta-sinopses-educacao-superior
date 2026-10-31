"""Detalha as falhas do T3 da P3 (geografia) e procura notas sobre EaD 'somente a nível Brasil' (somente leitura)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import DIAG, NUCLEO, ler_catalogo

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 70)
n = ler_catalogo(DIAG / "02_catalogo_abas.xlsx", sheet_name="notas_rodape")
n = n[(n.ano == 2024) & (n.conjunto == "Sinopse por município")]
x = n[n.texto.str.contains("nível Brasil|total Brasil|somente a nível|não são coletad|não são computad", case=False, regex=True)]
for nota, g in x.groupby(x.texto.str.strip().str.replace(r"^(Notas:)?\s*\d+\s*-\s*", "", regex=True)):
    print(f"[{', '.join(sorted({t.replace('Tab ', '') for t in g.chave_tabela}))}] {nota[:300]}")

con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
D = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo", "cor_raca",
     "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento", "reserva_vagas"]
for ano, tab, nivel in ((2024, "3.1", "reg"), (2024, "4.1", "reg"), (2024, "7.3", "reg"), (2024, "1.1", "mun"),
                        (2024, "3.2", "mun"), (2024, "5.15", "mun"), (2018, "6.8", "reg")):
    if nivel == "reg":
        q = f"""WITH f AS (SELECT * FROM fato_sinopse WHERE ano={ano} AND tabela='{tab}')
          SELECT b.indicador, r.modalidade, r.org_academica, b.nivel_academico, b.valor AS brasil, sum(x.valor) AS soma_reg
          FROM f b JOIN f x ON x.nivel_geo IN ('Região','Exterior') AND x.indicador=b.indicador AND x.id_recorte=b.id_recorte
               AND x.nivel_academico=b.nivel_academico
          JOIN dim_recorte_sinopse r ON r.id_recorte=b.id_recorte
          WHERE b.id_geo='BR' GROUP BY ALL HAVING sum(x.valor) IS DISTINCT FROM b.valor LIMIT 8"""
    else:
        q = f"""WITH f AS (SELECT fs.*, g.co_uf FROM fato_sinopse fs LEFT JOIN dim_geografia g USING (id_geo) WHERE ano={ano} AND tabela='{tab}')
          SELECT u.id_geo, u.indicador, u.nivel_academico, u.id_recorte, u.valor AS uf, sum(m.valor) AS soma_mun, count(m.valor) n_mun
          FROM f u JOIN f m ON m.nivel_geo='Município' AND m.co_uf=substr(u.id_geo,4) AND m.indicador=u.indicador
               AND m.id_recorte=u.id_recorte AND m.nivel_academico=u.nivel_academico
          WHERE u.nivel_geo='UF' GROUP BY ALL HAVING sum(m.valor) IS DISTINCT FROM u.valor LIMIT 8"""
    print(f"\n== {ano} {tab} ({nivel})"); print(con.execute(q).df().to_string(index=False))
