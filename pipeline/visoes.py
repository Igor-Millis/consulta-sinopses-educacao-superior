"""Visões do núcleo que não dependem de tabelas físicas extras.

v_fato_anexo_curso: fato com a origem reconstruída ("aba!célula").
v_anexo_i: Anexo I (presencial + EaD) DERIVADO dos Anexos II e III. Foi validado contra o Anexo I
publicado antes da remoção física (557 milhões de comparações, ver pipeline/remover_anexo_i.py):
  - Brasil: II + III
  - Município, ingressantes/matrículas/concluintes: II + III
  - Município, cursos/vagas/inscritos: só II (presencial; o EaD não é distribuído por município)
  - Distância e Exterior: III
A coluna origem lista as células somadas (por exemplo, "anexo_ii:8.2!CA20 + anexo_iii:8.3!CA20").
"""
OFERTA = "('cursos', 'vagas', 'inscritos')"

SQL_VISOES = f"""
CREATE OR REPLACE VIEW v_fato_anexo_curso AS
  SELECT *, aba || '!' || coluna || linha AS origem FROM fato_anexo_curso;

CREATE OR REPLACE VIEW v_anexo_i AS
  SELECT ano, 'anexo_i_derivado' AS anexo, id_geo, nivel_geo, co_cine, indicador, id_recorte,
         bool_or(eh_agregado) AS eh_agregado,
         CASE WHEN nivel_geo = 'Distância' AND indicador NOT IN {OFERTA} THEN NULL
              WHEN nivel_geo = 'Exterior' AND indicador IN {OFERTA} THEN NULL
              WHEN nivel_geo = 'Município' AND indicador IN {OFERTA}
                   THEN COALESCE(sum(valor) FILTER (WHERE anexo = 'anexo_ii'), 0)
              ELSE sum(valor) END AS valor,
         CASE WHEN nivel_geo = 'Distância' AND indicador NOT IN {OFERTA} THEN 'nao_aplicavel'
              WHEN nivel_geo = 'Exterior' AND indicador IN {OFERTA} THEN 'nao_desagregado'
              WHEN bool_or(status_valor = 'suspeito') THEN 'suspeito'
              WHEN nivel_geo = 'Município' AND indicador IN {OFERTA} THEN 'somente_presencial'
              ELSE 'informado' END AS status_valor,
         string_agg(DISTINCT id_ocorrencia, ';') AS id_ocorrencia,
         string_agg(anexo || ':' || aba || '!' || coluna || linha, ' + ' ORDER BY anexo) AS origem
  FROM fato_anexo_curso
  WHERE anexo IN ('anexo_ii', 'anexo_iii')
  GROUP BY ano, id_geo, nivel_geo, co_cine, indicador, id_recorte;
"""


def criar_visoes(con):
    con.execute(SQL_VISOES)
    if con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'fato_sinopse'").fetchone()[0]:
        con.execute("""CREATE OR REPLACE VIEW v_fato_sinopse AS
          SELECT *, aba || '!' || coluna || linha AS origem FROM fato_sinopse""")


def criar_dim_indicador(con):
    """Todos os indicadores do núcleo (Anexos e Sinopse). aditivo = pode ser somado entre geografias/categorias."""
    con.execute("""CREATE OR REPLACE TABLE dim_indicador AS SELECT * FROM (VALUES
      ('cursos', 'Número de Cursos', 'contagem', true, NULL),
      ('vagas', 'Vagas Oferecidas', 'contagem', true, NULL),
      ('inscritos', 'Candidatos Inscritos', 'contagem', true, NULL),
      ('ingressantes', 'Ingressantes', 'contagem', true, NULL),
      ('matriculas', 'Matrículas', 'contagem', true, NULL),
      ('concluintes', 'Concluintes', 'contagem', true, NULL),
      ('matriculas_trancadas', 'Matrículas Trancadas', 'contagem', true, NULL),
      ('matriculas_desvinculadas', 'Matrículas Desvinculadas', 'contagem', true, NULL),
      ('alunos_transferidos', 'Alunos Transferidos para outros cursos na mesma IES', 'contagem', true, NULL),
      ('alunos_falecidos', 'Alunos Falecidos', 'contagem', true, NULL),
      ('ies', 'Número de Instituições de Ensino Superior', 'contagem', true, 'Contadas pelo município da sede administrativa'),
      ('docentes_exercicio', 'Número de Docentes em Exercício', 'contagem', false,
       'Cada docente é contado uma vez em cada nível de agregação (notas 3–7 das tabelas 2.x): totais NÃO são somas'),
      ('docentes_ies', 'Número de Docentes das IES Comunitárias e/ou Confessionais', 'contagem', false,
       'Tabela 2.10 (2023–2024); definição diferente de docentes_exercicio; totais não são somas'),
      ('polos', 'Número de Polos (EaD)', 'contagem', NULL, 'Aditividade não verificada: um polo pode atender mais de uma IES'))
      t(indicador, nome, unidade, aditivo, observacao)""")


def construir_dim_geografia(con):
    """Brasil, regiões, UFs, municípios (dos Anexos e da Sinopse) e pseudo-regiões Distância/Exterior."""
    tem_sin = con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'stg_linhas_sinopse'").fetchone()[0]
    sin = """UNION ALL SELECT co_municipio, no_municipio, substr(co_municipio, 1, 2), ano
             FROM stg_linhas_sinopse WHERE nivel_geo = 'Município'""" if tem_sin else ""
    con.execute(f"""CREATE OR REPLACE TABLE dim_geografia AS
      WITH m0 AS (SELECT co_municipio, no_municipio, co_uf, ano FROM stg_linhas_anexo WHERE nivel_geo = 'Município' {sin}),
      mun AS (SELECT co_municipio, arg_max(no_municipio, ano) AS no_municipio, arg_max(co_uf, ano) AS co_uf FROM m0 GROUP BY 1)
      SELECT * FROM (VALUES
        ('BR', 'Brasil', NULL, 'Brasil', NULL, NULL, NULL, NULL, false),
        ('DIST', 'Distância', NULL, 'Distância (EaD não distribuído por município)', NULL, NULL, NULL, NULL, true),
        ('EXT', 'Exterior', NULL, 'Exterior (cursos de IES brasileiras fora do país)', NULL, NULL, NULL, NULL, true))
        t(id_geo, nivel_geo, co_municipio, no_municipio, co_uf, sg_uf, no_uf, no_regiao, eh_pseudo)
      UNION ALL
      SELECT DISTINCT 'REG-' || no_regiao, 'Região', NULL, no_regiao, NULL, NULL, NULL, no_regiao, false FROM dim_uf
      UNION ALL
      SELECT 'UF-' || co_uf, 'UF', NULL, no_uf, co_uf, sg_uf, no_uf, no_regiao, false FROM dim_uf
      UNION ALL
      SELECT m.co_municipio, 'Município', m.co_municipio, m.no_municipio, m.co_uf, u.sg_uf, u.no_uf, u.no_regiao, false
      FROM mun m LEFT JOIN dim_uf u ON u.co_uf = m.co_uf""")
