"""6.6 (concluintes por org., dependência, cor/raça e sexo): onde Total ≠ Feminino + Masculino no Brasil? (somente leitura)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 60)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
for ano in (2023, 2022):
    df = con.execute(f"""
      WITH f AS (SELECT f.coluna, f.valor, f.nivel_academico, r.* FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
                 WHERE f.ano = {ano} AND f.tabela = '6.6' AND f.id_geo = 'BR' AND f.nivel_academico = 'Graduação')
      SELECT t.org_academica, t.dependencia, t.categoria_privada, t.cor_raca, t.coluna AS col_total, t.valor AS total,
             fe.coluna AS col_fem, fe.valor AS fem, ma.coluna AS col_mas, ma.valor AS mas, t.valor - fe.valor - ma.valor AS dif
      FROM f t JOIN f fe ON fe.sexo = 'Feminino' AND fe.org_academica = t.org_academica AND fe.dependencia = t.dependencia
           AND fe.categoria_privada = t.categoria_privada AND fe.cor_raca = t.cor_raca
      JOIN f ma ON ma.sexo = 'Masculino' AND ma.org_academica = t.org_academica AND ma.dependencia = t.dependencia
           AND ma.categoria_privada = t.categoria_privada AND ma.cor_raca = t.cor_raca
      WHERE t.sexo = 'Total' ORDER BY abs(t.valor - fe.valor - ma.valor) DESC, t.coluna""").df()
    print(f"\n== {ano}: {len(df)} trios Total/Fem/Masc; com diferença: {(df.dif != 0).sum()}")
    print(df[df.dif != 0].head(15).to_string(index=False))
