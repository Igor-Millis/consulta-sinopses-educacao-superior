"""Investiga as 178 falhas da T3 (p3_validar): Σ regiões + Exterior ≠ Brasil e Σ municípios ≠ UF.

Combinações com falha (revalidação de 30/10/2026): 2018 6.8; 2023 4.1 e 7.4; 2024 5.14, 5.8, 6.14 e 7.4.
Para cada falha: recorte, soma das partes, valor publicado, diferença, células de origem e se existe linha de outra
geografia (Distância, não informado) que explique a diferença.
Grava dados/qualidade/t3_falhas_detalhe.csv.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit='2GB'")
COMBOS = [(2018, "6.8"), (2023, "4.1"), (2023, "7.4"), (2024, "5.14"), (2024, "5.8"), (2024, "6.14"), (2024, "7.4")]
partes = []
for ano, tab in COMBOS:
    df = con.execute(f"""
      WITH f AS (SELECT fs.*, g.co_uf FROM fato_sinopse fs LEFT JOIN dim_geografia g USING (id_geo)
                 WHERE fs.ano = {ano} AND fs.tabela = '{tab}'
                   AND fs.indicador IN (SELECT indicador FROM dim_indicador WHERE aditivo)),
      reg AS (SELECT nivel_academico, indicador, id_recorte, 'BR' alvo, sum(valor) soma,
                     string_agg(id_geo || '=' || valor, ' ' ORDER BY id_geo) partes
              FROM f WHERE nivel_geo IN ('Região', 'Exterior') AND status_valor <> 'somente_presencial' GROUP BY ALL),
      mun AS (SELECT nivel_academico, indicador, id_recorte, 'UF-' || co_uf alvo, sum(valor) soma, count(*) || ' municípios' partes
              FROM f WHERE nivel_geo = 'Município' GROUP BY ALL),
      x AS (SELECT * FROM reg UNION ALL SELECT * FROM mun)
      SELECT {ano} ano, '{tab}' tabela, x.alvo, x.nivel_academico, x.indicador, x.id_recorte, x.soma, f.valor publicado,
             f.valor - x.soma dif, f.aba || '!' || f.coluna || f.linha celula, f.status_valor, x.partes
      FROM x JOIN f ON f.id_geo = x.alvo AND f.nivel_academico = x.nivel_academico AND f.indicador = x.indicador
                   AND f.id_recorte = x.id_recorte
      WHERE x.soma IS NOT NULL AND f.valor IS NOT NULL AND x.soma <> f.valor""").df()
    partes.append(df)
import pandas as pd  # noqa: E402

d = pd.concat(partes)
rec = con.execute("SELECT * FROM dim_recorte_sinopse").df().set_index("id_recorte")
d["recorte"] = d["id_recorte"].map(lambda i: "; ".join(f"{k}={v}" for k, v in rec.loc[i].items()
                                                         if v not in ("Total", "Não se aplica") and k != "eh_agregado"))
print(f"{len(d)} falhas")
print(d.groupby(["ano", "tabela", "alvo"]).agg(n=("dif", "size"), dif_min=("dif", "min"), dif_max=("dif", "max")).to_string())
print("\npadrão das diferenças (|dif|):", d["dif"].abs().value_counts().head(10).to_dict())
print("\nexemplos:")
print(d[["ano", "tabela", "alvo", "indicador", "recorte", "soma", "publicado", "dif", "celula", "partes"]].head(25).to_string(index=False))
# linhas de geografias que não entram na soma (ex.: 'Distância') nessas tabelas
print("\nníveis geográficos presentes nessas tabelas:")
print(con.execute(f"""SELECT ano, tabela, nivel_geo, count(*) FROM fato_sinopse
    WHERE (ano, tabela) IN ({', '.join(f"({a}, '{t}')" for a, t in COMBOS)}) GROUP BY ALL ORDER BY ALL""").df().to_string(index=False))
d.to_csv(NUCLEO.parent / "qualidade" / "t3_falhas_detalhe.csv", sep=";", index=False, encoding="utf-8-sig")
