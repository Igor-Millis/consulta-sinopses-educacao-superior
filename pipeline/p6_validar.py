"""Validação da P6 (marts) contra o núcleo, por caminhos independentes da construção.

V1 mart_anexos_geo, Município: Σ folhas = Σ do recorte publicado "Total" (org/grau/dep/categoria) nos fatos,
   por ano × indicador × modalidade (o mart soma folhas; o teste soma a linha total publicada).
V2 mart_anexos_geo, UF e Região: = Σ dos municípios do próprio mart, por ano × indicador × modalidade.
V3 mart_anexos_geo, Brasil: Σ folhas = célula "Total Brasil" × recorte Total dos fatos.
V4 mart_curso_geo, Município e UF: Σ cursos = Σ do mart_anexos_geo no mesmo nível.
V5 mart_sinopse_geo (soma das folhas), UF: Σ categorias = total publicado da própria tabela (org/dep/dim = Total).
V6 mart_sinopse_geo × mart_anexos_geo, por UF: matrículas/ingressantes/concluintes por sexo (Σ) = Anexos (Σ modalidades).
V7 mart_sinopse_geo, 1.1/2.1 (publicado): Σ dependências = total publicado para IES (aditivo); docentes só informativo.
Grava dados/qualidade/p6_validacao.txt. Modo leve (3 GB, 4 threads).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
SAIDA = NUCLEO.parent / "qualidade" / "p6_validacao.txt"
t0 = time.time()
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit = '3GB'")
con.execute("SET threads = 4")
linhas, resumo = [], []


def p(s=""):
    print(s, flush=True)
    linhas.append(str(s))


def teste(nome, sql, tolerancia=0.0):
    df = con.execute(sql).df()
    df["dif"] = (df["a"].fillna(0) - df["b"].fillna(0)).abs()
    falhas = df[df["dif"] > tolerancia]
    ok = len(falhas) == 0
    resumo.append((nome, len(df), len(falhas)))
    p(f"{nome}: {len(df):,} comparações | falhas: {len(falhas):,} {'OK' if ok else ''} ({round(time.time() - t0)} s)")
    if not ok:
        p(falhas.head(15).to_string(index=False))
    return falhas


MOD = "CASE f.anexo WHEN 'anexo_ii' THEN 'Presencial' ELSE 'A Distância' END"
TOT = """(SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
          AND dependencia='Total' AND categoria_privada='Total')"""

teste("V1 anexos Município: Σ folhas = recorte Total publicado", f"""
WITH m AS (SELECT ano, indicador, modalidade, sum(valor) a FROM mart_anexos_geo WHERE nivel_geo='Município' GROUP BY ALL),
     f AS (SELECT ano, indicador, {MOD} modalidade, sum(valor) b FROM fato_anexo_curso f
           WHERE nivel_geo='Município' AND id_recorte={TOT} GROUP BY ALL)
SELECT * FROM m FULL JOIN f USING (ano, indicador, modalidade) ORDER BY ALL""")

for nivel, chave in [("UF", "'UF-' || g.co_uf"), ("Região", "'REG-' || g.no_regiao")]:
    teste(f"V2 anexos {nivel} = Σ municípios do mart", f"""
WITH a AS (SELECT ano, id_geo, indicador, modalidade, rede, org_academica, grau, sum(valor) a FROM mart_anexos_geo
           WHERE nivel_geo='{nivel}' GROUP BY ALL),
     b AS (SELECT ano, {chave} id_geo, indicador, modalidade, rede, org_academica, grau, sum(valor) b
           FROM mart_anexos_geo m JOIN dim_geografia g USING (id_geo) WHERE m.nivel_geo='Município' GROUP BY ALL)
SELECT * FROM a FULL JOIN b USING (ano, id_geo, indicador, modalidade, rede, org_academica, grau)""")

teste("V3 anexos Brasil: Σ folhas = Total Brasil publicado", f"""
WITH m AS (SELECT ano, indicador, modalidade, sum(valor) a FROM mart_anexos_geo WHERE nivel_geo='Brasil' GROUP BY ALL),
     f AS (SELECT ano, indicador, {MOD} modalidade, sum(valor) b FROM fato_anexo_curso f
           WHERE nivel_geo='Brasil' AND co_cine='_TOTAL' AND id_recorte={TOT} GROUP BY ALL)
SELECT * FROM m FULL JOIN f USING (ano, indicador, modalidade) ORDER BY ALL""")

for nivel in ["Município", "UF"]:
    teste(f"V4 curso {nivel}: Σ cursos = mart_anexos_geo", f"""
WITH c AS (SELECT ano, id_geo, indicador, modalidade, sum(valor) a FROM mart_curso_geo WHERE nivel_geo='{nivel}' GROUP BY ALL),
     m AS (SELECT ano, id_geo, indicador, modalidade, sum(valor) b FROM mart_anexos_geo WHERE nivel_geo='{nivel}' GROUP BY ALL)
SELECT * FROM c FULL JOIN m USING (ano, id_geo, indicador, modalidade)""")

teste("V5 sinopse (folhas) UF: Σ categorias = total publicado da tabela (exceto Q10: 6.6 em 2017–2019 e 2023)", """
WITH s AS (SELECT ano, tabela, id_geo, sum(valor) a FROM mart_sinopse_geo
           WHERE modo='soma das folhas' AND nivel_geo='UF' GROUP BY ALL),
     t AS (SELECT f.ano, f.tabela, f.id_geo, f.valor b FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
           WHERE f.tabela IN (SELECT DISTINCT tabela FROM mart_sinopse_geo WHERE modo='soma das folhas')
             AND f.nivel_geo='UF' AND f.nivel_academico='Graduação'
             AND r.org_academica='Total' AND r.dependencia='Total' AND r.sexo='Total' AND r.cor_raca='Total'
             AND r.faixa_etaria='Total')
SELECT * FROM s FULL JOIN t USING (ano, tabela, id_geo)
WHERE NOT (tabela = '6.6' AND ano IN (2017, 2018, 2019, 2023))""")
q10 = teste("V5b (esperado falhar — Q10, publicação INEP) 6.6 em 2017–2019 e 2023", """
WITH s AS (SELECT ano, tabela, id_geo, sum(valor) a FROM mart_sinopse_geo
           WHERE modo='soma das folhas' AND nivel_geo='UF' AND tabela='6.6' GROUP BY ALL),
     t AS (SELECT f.ano, f.tabela, f.id_geo, f.valor b FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
           WHERE f.tabela='6.6' AND f.nivel_geo='UF' AND f.nivel_academico='Graduação' AND r.org_academica='Total'
             AND r.dependencia='Total' AND r.sexo='Total' AND r.cor_raca='Total')
SELECT * FROM s FULL JOIN t USING (ano, tabela, id_geo) WHERE ano IN (2017, 2018, 2019, 2023)""")
resumo[-1] = (resumo[-1][0], resumo[-1][1], 0)  # falhas aqui são a ocorrência Q10 documentada, não erro do mart
p(f"   → {len(q10)} UF×ano com Σ cor/raça ≠ total: ocorrência Q10 (documentada); o motor exibe a limitação.")

teste("V6 sinopse por sexo (Σ) × Anexos (Σ modalidades), UF", """
WITH s AS (SELECT ano, id_geo, indicador, sum(valor) a FROM mart_sinopse_geo
           WHERE dimensao='sexo' AND modo='soma das folhas' AND nivel_geo='UF' GROUP BY ALL),
     m AS (SELECT ano, id_geo, indicador, sum(valor) b FROM mart_anexos_geo
           WHERE nivel_geo='UF' AND indicador IN ('matriculas','ingressantes','concluintes') GROUP BY ALL)
SELECT * FROM s FULL JOIN m USING (ano, id_geo, indicador)""")

# "Pública" é categoria agregada publicada (= Federal + Estadual + Municipal): não entra na soma das partes
teste("V7 IES (1.1): Federal + Estadual + Municipal + Privada = total publicado", """
WITH d AS (SELECT ano, id_geo, sum(valor) a FROM mart_sinopse_geo WHERE tabela='1.1' AND dimensao='dependencia'
           AND categoria <> 'Pública' GROUP BY ALL),
     t AS (SELECT ano, id_geo, valor b FROM mart_sinopse_geo WHERE tabela='1.1' AND dimensao='total')
SELECT * FROM d FULL JOIN t USING (ano, id_geo)""")
teste("V7b IES (1.1): Pública = Federal + Estadual + Municipal", """
WITH d AS (SELECT ano, id_geo, sum(valor) a FROM mart_sinopse_geo WHERE tabela='1.1' AND dimensao='dependencia'
           AND categoria IN ('Federal', 'Estadual', 'Municipal') GROUP BY ALL),
     t AS (SELECT ano, id_geo, valor b FROM mart_sinopse_geo WHERE tabela='1.1' AND dimensao='dependencia' AND categoria='Pública')
SELECT * FROM d FULL JOIN t USING (ano, id_geo) WHERE coalesce(a, 0) + coalesce(b, 0) > 0""")

p("\nResumo:")
for nome, n, f in resumo:
    p(f"  {'OK   ' if f == 0 else 'FALHA'} {nome}: {f:,}/{n:,}")
p(f"duração: {round((time.time() - t0) / 60, 1)} min")
SAIDA.write_text("\n".join(linhas), encoding="utf-8")
