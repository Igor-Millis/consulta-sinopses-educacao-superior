"""P5 — Visões analíticas do Espírito Santo (Brasil × UFs × municípios do ES) e exportações em CSV.

Visões (só leem o núcleo; nada é somado entre totais publicados e detalhes):
  v_es_municipio_curso      ES, município × curso Cine × indicador: presencial (Anexo II) e EaD por polo (Anexo III), recorte Total
  v_es_municipio_indicador  ES, município × indicador: presencial, EaD (polos) e total (só onde ambos existem)
  v_comparativo_uf          Sinopse, recorte Total: Brasil, regiões e UFs (com o ES marcado) — IES, docentes, cursos,
                            ingressantes, matrículas e concluintes (Graduação quando a tabela tem nível acadêmico)
Status e ocorrências são preservados: valores 'suspeito' aparecem com o id da ocorrência; 'nao_desagregado' fica nulo.

Uso: python -I p5_visoes_es.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO, PROJETO

sys.stdout.reconfigure(encoding="utf-8")
OUT = PROJETO / "dados" / "analitico"
OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"))
con.execute("SET memory_limit = '3GB'")
TOT_A = """(SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
            AND dependencia='Total' AND categoria_privada='Total')"""
DIMS_S = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
          "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
          "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
TOT_S = " AND ".join(f"{d} IN ('Total', 'Não se aplica')" for d in DIMS_S)

con.execute(f"""CREATE OR REPLACE VIEW v_es_municipio_curso AS
  SELECT f.ano, g.co_municipio, g.no_municipio, f.co_cine, c.no_cine, f.indicador,
         CASE f.anexo WHEN 'anexo_ii' THEN 'Presencial' ELSE 'A Distância (polo)' END AS modalidade,
         f.valor, f.status_valor, f.id_ocorrencia, f.aba || '!' || f.coluna || f.linha AS origem
  FROM fato_anexo_curso f
  JOIN dim_geografia g ON g.id_geo = f.id_geo
  LEFT JOIN dim_curso_cine c ON c.ano = f.ano AND c.co_cine = f.co_cine
  WHERE g.co_uf = '32' AND f.id_recorte = {TOT_A}""")

con.execute(f"""CREATE OR REPLACE VIEW v_es_municipio_indicador AS
  WITH b AS (
    SELECT f.ano, g.co_municipio, g.no_municipio, f.indicador, f.anexo, sum(f.valor) AS valor,
           bool_or(f.status_valor = 'suspeito') AS tem_suspeito, count(f.valor) AS n_valores
    FROM fato_anexo_curso f JOIN dim_geografia g ON g.id_geo = f.id_geo
    WHERE g.co_uf = '32' AND f.id_recorte = {TOT_A}
    GROUP BY ALL)
  SELECT ano, co_municipio, no_municipio, indicador,
         max(valor) FILTER (WHERE anexo = 'anexo_ii') AS presencial,
         max(valor) FILTER (WHERE anexo = 'anexo_iii' AND n_valores > 0) AS ead_polo,
         CASE WHEN indicador IN ('cursos', 'vagas', 'inscritos') THEN NULL
              ELSE COALESCE(max(valor) FILTER (WHERE anexo = 'anexo_ii'), 0)
                 + COALESCE(max(valor) FILTER (WHERE anexo = 'anexo_iii' AND n_valores > 0), 0) END AS total,
         bool_or(tem_suspeito) AS tem_suspeito,
         CASE WHEN indicador IN ('cursos', 'vagas', 'inscritos')
              THEN 'EaD não distribuído por município (só no total Brasil); total municipal = presencial' END AS observacao
  FROM b GROUP BY ano, co_municipio, no_municipio, indicador""")

con.execute(f"""CREATE OR REPLACE VIEW v_comparativo_uf AS
  WITH tabs AS (SELECT * FROM (VALUES ('1.1', 'ies'), ('2.1', 'docentes_exercicio'), ('3.1', 'cursos'),
                                       ('4.2', 'ingressantes'), ('5.1', 'matriculas'), ('6.1', 'concluintes')) t(tabela, indicador)),
       niv AS (SELECT ano, tabela, CASE WHEN bool_or(nivel_academico = 'Graduação') THEN 'Graduação' ELSE 'Total' END AS nivel
               FROM fato_sinopse WHERE tabela IN (SELECT tabela FROM tabs) GROUP BY ALL)
  SELECT f.ano, f.tabela, f.indicador, f.id_geo, g.nivel_geo, g.no_municipio AS nome, g.sg_uf,
         (f.id_geo = 'UF-32') AS eh_es, f.nivel_academico, f.valor, f.status_valor, f.id_ocorrencia,
         i.aditivo, f.aba || '!' || f.coluna || f.linha AS origem
  FROM fato_sinopse f
  JOIN tabs t ON t.tabela = f.tabela AND t.indicador = f.indicador
  JOIN niv n ON n.ano = f.ano AND n.tabela = f.tabela AND n.nivel = f.nivel_academico
  JOIN dim_geografia g ON g.id_geo = f.id_geo
  JOIN dim_indicador i ON i.indicador = f.indicador
  WHERE f.nivel_geo IN ('Brasil', 'Região', 'UF')
    AND f.id_recorte IN (SELECT id_recorte FROM dim_recorte_sinopse WHERE {TOT_S})""")

for v in ("v_es_municipio_curso", "v_es_municipio_indicador", "v_comparativo_uf"):
    dest = str(OUT / f"{v}.csv").replace("\\", "/")
    con.execute(f"COPY (SELECT * FROM {v} ORDER BY ALL) TO '{dest}' (HEADER, DELIMITER ';')")  # UTF-8 é o padrão do DuckDB
    n = con.execute(f"SELECT count(*) FROM {v}").fetchone()[0]
    print(f"{v}: {n:,} linhas → {dest}")

print("\nES × Brasil — matrículas de graduação (Sinopse 5.1):")
print(con.execute("""SELECT ano, max(valor) FILTER (WHERE id_geo='UF-32') AS es, max(valor) FILTER (WHERE id_geo='BR') AS brasil,
       round(100.0 * max(valor) FILTER (WHERE id_geo='UF-32') / max(valor) FILTER (WHERE id_geo='BR'), 2) AS pct_es
  FROM v_comparativo_uf WHERE indicador = 'matriculas' GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
print("\nES — municípios com matrícula (presencial ou EaD) por ano:")
print(con.execute("""SELECT ano, count(DISTINCT co_municipio) FILTER (WHERE presencial > 0) AS com_presencial,
       count(DISTINCT co_municipio) FILTER (WHERE ead_polo > 0) AS com_ead, sum(presencial) AS matr_presencial, sum(ead_polo) AS matr_ead
  FROM v_es_municipio_indicador WHERE indicador = 'matriculas' GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
con.execute("INSERT INTO carga_log VALUES (current_timestamp, 'p5_visoes_es', 'concluída')")
con.close()
