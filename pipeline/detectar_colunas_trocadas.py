"""Q09 — Detecta pares de colunas da Sinopse com VALORES TROCADOS na publicação (somente leitura do núcleo).

Critério (na linha Total Brasil de cada tabela/ano/nível acadêmico): dois recortes P e Q da mesma tabela tais que
  valor(P) ≠ Σ filhos(P),  valor(P) = Σ filhos(Q)  e  valor(Q) = Σ filhos(P)
ou seja, os números de P e Q estão nas colunas um do outro (o cabeçalho é o mesmo dos anos corretos).
Filhos = categorias exclusivas de uma dimensão (mesma regra do teste T2 da P3).
Grava config/q09_colunas_trocadas.csv (ano, tabela, coluna_p, coluna_q, evidências). Nenhum valor é alterado.

Uso: python -I detectar_colunas_trocadas.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import CONFIG, NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit = '3GB'")
DIMS = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
        "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
        "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
r = con.execute("SELECT * FROM dim_recorte_sinopse").df().set_index("id_recorte")
norm = r.copy()
norm["categoria_privada"] = norm.categoria_privada.replace("Não se aplica", "Total")
GRUPOS = {("dependencia", "Total"): {"Federal", "Estadual", "Municipal", "Privada"},
          ("dependencia", "Pública"): {"Federal", "Estadual", "Municipal"}}
ex = con.execute("""SELECT f.ano, f.tabela, f.nivel_academico, f.indicador, f.id_recorte, f.valor, f.coluna
  FROM fato_sinopse f WHERE f.id_geo = 'BR' AND f.valor IS NOT NULL
    -- só as tabelas com falha no T2 da P3 (dados/qualidade/p3_t2_por_tabela.csv); as demais fecham
    AND f.tabela IN ('3.1', '4.1', '5.14', '6.3', '6.6', '6.14')
    AND f.indicador IN (SELECT indicador FROM dim_indicador WHERE aditivo)""").df()
achados = []
for (ano, tab, niv, ind), g in ex.groupby(["ano", "tabela", "nivel_academico", "indicador"]):
    val = dict(zip(g.id_recorte, g.valor)); col = dict(zip(g.id_recorte, g.coluna))
    ids = list(val)
    sub = norm.loc[ids]
    soma = {}
    for p in ids:
        for d in DIMS:
            pv = sub.at[p, d]
            if pv not in ("Total", "Pública"):
                continue
            outros = [x for x in DIMS if x != d]
            mask = (sub[outros] == sub.loc[p, outros]).all(axis=1) & ~sub[d].isin(["Total", "Pública", "Não se aplica"])
            if (d, pv) in GRUPOS:
                mask &= sub[d].isin(GRUPOS[(d, pv)])
            elif d == "dependencia":
                continue
            fil = sub.index[mask]
            if len(fil) >= 2:
                soma.setdefault(p, []).append((d, sum(val[f] for f in fil)))
    for p, lst in soma.items():
        for d, s in lst:
            if s == val[p]:
                continue
            for q, lq in soma.items():
                if q == p:
                    continue
                if val[p] in {sq for _, sq in lq} and val[q] == s:
                    a, b = sorted([col[p], col[q]])
                    achados.append({"ano": ano, "tabela": tab, "nivel_academico": niv, "indicador": ind, "coluna_a": a,
                                    "coluna_b": b, "valor_publicado_a": val[p] if col[p] == a else val[q],
                                    "valor_publicado_b": val[q] if col[p] == a else val[p], "dimensao": d})
A = pd.DataFrame(achados).drop_duplicates(["ano", "tabela", "coluna_a", "coluna_b"])
A.to_csv(CONFIG / "q09_colunas_trocadas.csv", index=False, encoding="utf-8-sig")
print(f"pares de colunas trocadas: {len(A)}")
if len(A):
    print(A.groupby(["tabela", "ano"]).size().to_string())
    print(A.head(20).to_string(index=False))
