"""P6 — Camada de consulta (marts): tabelas analíticas compactas derivadas do núcleo, para o motor de perguntas.

Princípios: não duplicar os fatos (os marts agregam e descartam zeros de FOLHA, que não alteram somas);
toda linha guarda quantas células do núcleo a compõem e um exemplo de origem; regras de agregação explícitas.

mart_anexos_geo — Anexos II (presencial) e III (EaD), recortes-FOLHA (org. acadêmica × grau × dependência ×
  categoria privada), somados sobre os cursos Cine:
    Município: Σ linhas Município × Cine do núcleo
    UF, Região: Σ dos municípios (indicadores aditivos; EaD de cursos/vagas/inscritos não existe abaixo do Brasil)
    Brasil: linha publicada "Total Brasil" (todos os cursos) — inclui Distância/Exterior
  Qualquer marginal (rede pública/privada, dependência, organização, grau, total) = soma das folhas.
mart_curso_geo — mesmo desenho, recorte Total, por curso Cine (com co_cine_ref da P4).
mart_sinopse_geo — Sinopse, totais publicados para dimensões que os Anexos não têm (sexo, cor/raça, faixa etária,
  docentes, IES), recorte em que só UMA dimensão de interesse é aberta e as demais = Total.

Uso: python -I p6_marts.py [mart_anexos_geo] [mart_curso_geo] [mart_sinopse_geo]  (sem argumentos: todos)
"""
import sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
t0 = time.time()
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"))
con.execute("SET memory_limit = '3GB'")
con.execute("SET preserve_insertion_order = false")
con.execute("SET threads = 4")
TODOS = ["mart_anexos_geo", "mart_curso_geo", "mart_sinopse_geo"]
ALVOS = sys.argv[1:] or TODOS
assert set(ALVOS) <= set(TODOS), f"marts válidos: {TODOS}"

FOLHA = """r.org_academica <> 'Total' AND r.grau <> 'Total' AND r.dependencia <> 'Total' AND r.categoria_privada <> 'Total'"""

# ---------------------------------------------------------------- mart_anexos_geo
if "mart_anexos_geo" in ALVOS:
    con.execute(f"""CREATE OR REPLACE TABLE mart_anexos_geo AS
    WITH mun AS (
      SELECT f.ano, 'Município' AS nivel_geo, f.id_geo, f.indicador,
             CASE f.anexo WHEN 'anexo_ii' THEN 'Presencial' ELSE 'A Distância' END AS modalidade,
             r.org_academica, r.grau, r.dependencia, r.categoria_privada,
             sum(f.valor) AS valor, count(f.valor) AS n_celulas,
             bool_or(f.status_valor = 'suspeito') AS tem_suspeito, string_agg(DISTINCT f.id_ocorrencia, ';') AS ocorrencias,
             min(f.aba || '!' || f.coluna || f.linha) AS origem_exemplo
      FROM fato_anexo_curso f JOIN dim_recorte r USING (id_recorte)
      WHERE f.nivel_geo = 'Município' AND {FOLHA} AND f.valor IS NOT NULL
      GROUP BY ALL HAVING sum(f.valor) <> 0),
    br AS (
      SELECT f.ano, 'Brasil' AS nivel_geo, 'BR' AS id_geo, f.indicador,
             CASE f.anexo WHEN 'anexo_ii' THEN 'Presencial' ELSE 'A Distância' END AS modalidade,
             r.org_academica, r.grau, r.dependencia, r.categoria_privada,
             sum(f.valor) AS valor, count(f.valor) AS n_celulas,
             bool_or(f.status_valor = 'suspeito') AS tem_suspeito, string_agg(DISTINCT f.id_ocorrencia, ';') AS ocorrencias,
             min(f.aba || '!' || f.coluna || f.linha) AS origem_exemplo
      FROM fato_anexo_curso f JOIN dim_recorte r USING (id_recorte)
      WHERE f.nivel_geo = 'Brasil' AND f.co_cine = '_TOTAL' AND {FOLHA} AND f.valor IS NOT NULL
      GROUP BY ALL HAVING sum(f.valor) <> 0),
    uf AS (
      SELECT m.ano, 'UF' AS nivel_geo, 'UF-' || g.co_uf AS id_geo, m.indicador, m.modalidade, m.org_academica, m.grau,
             m.dependencia, m.categoria_privada, sum(m.valor), sum(m.n_celulas), bool_or(m.tem_suspeito),
             string_agg(DISTINCT m.ocorrencias, ';'), 'Σ municípios' AS origem_exemplo
      FROM mun m JOIN dim_geografia g USING (id_geo) GROUP BY ALL),
    reg AS (
      SELECT m.ano, 'Região', 'REG-' || g.no_regiao, m.indicador, m.modalidade, m.org_academica, m.grau,
             m.dependencia, m.categoria_privada, sum(m.valor), sum(m.n_celulas), bool_or(m.tem_suspeito),
             string_agg(DISTINCT m.ocorrencias, ';'), 'Σ municípios'
      FROM mun m JOIN dim_geografia g USING (id_geo) GROUP BY ALL)
    SELECT * FROM mun UNION ALL SELECT * FROM uf UNION ALL SELECT * FROM reg UNION ALL SELECT * FROM br""")
    con.execute("""ALTER TABLE mart_anexos_geo ADD COLUMN rede VARCHAR""")
    con.execute("""UPDATE mart_anexos_geo SET rede = CASE WHEN dependencia = 'Privada' THEN 'Privada' ELSE 'Pública' END""")
    n = con.execute("SELECT count(*) FROM mart_anexos_geo").fetchall()[0][0]
    print(f"mart_anexos_geo: {n:,} linhas ({round(time.time() - t0)} s)", flush=True)

# ---------------------------------------------------------------- mart_curso_geo
if "mart_curso_geo" in ALVOS:
    TOT = """(SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
              AND dependencia='Total' AND categoria_privada='Total')"""
    con.execute(f"""CREATE OR REPLACE TABLE mart_curso_geo AS
    WITH mun AS (
      SELECT f.ano, 'Município' AS nivel_geo, f.id_geo, f.co_cine, f.indicador,
             CASE f.anexo WHEN 'anexo_ii' THEN 'Presencial' ELSE 'A Distância' END AS modalidade,
             f.valor, f.status_valor = 'suspeito' AS tem_suspeito, f.aba || '!' || f.coluna || f.linha AS origem
      FROM fato_anexo_curso f WHERE f.nivel_geo = 'Município' AND f.id_recorte = {TOT} AND f.valor IS NOT NULL AND f.valor <> 0),
    br AS (
      SELECT f.ano, 'Brasil', 'BR', f.co_cine, f.indicador,
             CASE f.anexo WHEN 'anexo_ii' THEN 'Presencial' ELSE 'A Distância' END,
             f.valor, f.status_valor = 'suspeito', f.aba || '!' || f.coluna || f.linha
      FROM fato_anexo_curso f WHERE f.nivel_geo = 'Brasil' AND f.co_cine <> '_TOTAL' AND f.id_recorte = {TOT}
        AND f.valor IS NOT NULL AND f.valor <> 0),
    uf AS (
      SELECT m.ano, 'UF', 'UF-' || g.co_uf, m.co_cine, m.indicador, m.modalidade, sum(m.valor), bool_or(m.tem_suspeito), 'Σ municípios'
      FROM mun m JOIN dim_geografia g USING (id_geo) GROUP BY ALL)
    SELECT x.*, c.no_cine, xc.co_cine_ref, xc.tipo AS tipo_cine
    FROM (SELECT * FROM mun UNION ALL SELECT * FROM uf UNION ALL SELECT * FROM br) x
    LEFT JOIN dim_curso_cine c ON c.ano = x.ano AND c.co_cine = x.co_cine
    LEFT JOIN xw_cine xc ON xc.co_cine = x.co_cine""")
    n = con.execute("SELECT count(*) FROM mart_curso_geo").fetchall()[0][0]
    print(f"mart_curso_geo: {n:,} linhas ({round(time.time() - t0)} s)", flush=True)

# ---------------------------------------------------------------- mart_sinopse_geo
if "mart_sinopse_geo" in ALVOS:
    # Uma dimensão aberta por vez. Dois modos:
    #   publicado — a tabela tem a linha com as demais dimensões = Total (1.1, 2.1, 2.5): valor publicado, sem soma
    #               (obrigatório para docentes, que não são aditivos);
    #   folhas    — 4.6–4.8, 5.5–5.7, 6.5–6.7 só abrem sexo/cor/faixa nas folhas org. acadêmica × dependência ×
    #               categoria privada: soma das folhas, nível Graduação. Validado: ES 2024, Σ folhas de 5.5, 5.6 e 5.7
    #               = 182.335 = total publicado (pipeline/investigar_mart_sinopse.py).
    FONTES = [  # (tabela, indicador, dimensão aberta ou None, modo)
        ("1.1", "ies", "dependencia", "publicado"), ("1.1", "ies", "org_academica", "publicado"), ("1.1", "ies", None, "publicado"),
        ("2.1", "docentes_exercicio", "dependencia", "publicado"), ("2.1", "docentes_exercicio", "org_academica", "publicado"),
        ("2.1", "docentes_exercicio", None, "publicado"), ("2.5", "docentes_exercicio", "sexo", "publicado"),
        ("5.5", "matriculas", "sexo", "folhas"), ("5.6", "matriculas", "cor_raca", "folhas"), ("5.7", "matriculas", "faixa_etaria", "folhas"),
        ("4.6", "ingressantes", "sexo", "folhas"), ("4.7", "ingressantes", "cor_raca", "folhas"), ("4.8", "ingressantes", "faixa_etaria", "folhas"),
        ("6.5", "concluintes", "sexo", "folhas"), ("6.6", "concluintes", "cor_raca", "folhas"), ("6.7", "concluintes", "faixa_etaria", "folhas"),
    ]
    DIMS = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
            "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
            "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
    FOLHA_ORG = ("org_academica", "dependencia", "categoria_privada")
    partes = []
    for tab, ind, dim, modo in FONTES:
        abre = f"r.{dim} NOT IN ('Total', 'Não se aplica')" if dim else "TRUE"
        if modo == "publicado":
            cond = " AND ".join(f"r.{d} IN ('Total', 'Não se aplica')" for d in DIMS if d != dim)
            partes.append(f"""SELECT f.ano, f.tabela, f.nivel_geo, f.id_geo, f.nivel_academico, f.indicador,
                '{dim or 'total'}' AS dimensao, {('r.' + dim) if dim else "'Total'"} AS categoria,
                f.valor, 1 AS n_celulas, f.status_valor = 'suspeito' AS tem_suspeito, f.id_ocorrencia AS ocorrencias,
                f.aba || '!' || f.coluna || f.linha AS origem, 'publicado' AS modo
              FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
              WHERE f.tabela = '{tab}' AND f.indicador = '{ind}' AND {cond} AND {abre}""")
        else:
            cond = " AND ".join([f"r.{d} <> 'Total'" for d in FOLHA_ORG]
                                + [f"r.{d} IN ('Total', 'Não se aplica')" for d in DIMS if d != dim and d not in FOLHA_ORG])
            partes.append(f"""SELECT f.ano, f.tabela, f.nivel_geo, f.id_geo, f.nivel_academico, f.indicador,
                '{dim}' AS dimensao, r.{dim} AS categoria,
                sum(f.valor) AS valor, count(f.valor) AS n_celulas, bool_or(f.status_valor = 'suspeito') AS tem_suspeito,
                string_agg(DISTINCT f.id_ocorrencia, ';') AS ocorrencias, min(f.aba || '!' || f.coluna || f.linha) AS origem,
                'soma das folhas' AS modo
              FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
              WHERE f.tabela = '{tab}' AND f.indicador = '{ind}' AND f.nivel_academico = 'Graduação' AND {cond} AND {abre}
              GROUP BY ALL""")
    con.execute("CREATE OR REPLACE TABLE mart_sinopse_geo AS " + " UNION ALL ".join(partes))
    n = con.execute("SELECT count(*) FROM mart_sinopse_geo").fetchall()[0][0]
    print(f"mart_sinopse_geo: {n:,} linhas ({round(time.time() - t0)} s)", flush=True)
    print(con.execute("""SELECT 'mart_sinopse_geo' t, tabela, dimensao, count(*) n FROM mart_sinopse_geo GROUP BY ALL ORDER BY 2, 3""").df().to_string(index=False))
con.execute("CREATE TABLE IF NOT EXISTS carga_log (quando TIMESTAMP, etapa VARCHAR, situacao VARCHAR)")
con.execute("INSERT INTO carga_log VALUES (current_timestamp, 'p6_marts:' || ?, 'concluída')", [",".join(ALVOS)])
con.close()
print(f"P6 concluída em {round((time.time() - t0) / 60, 1)} min; tamanho do banco: {(NUCLEO / 'ijsn.duckdb').stat().st_size / 2**30:.2f} GB")
