"""P1/P2 — Carga dos Anexos I, II e III (2017–2024) no núcleo: dados/nucleo/ijsn.duckdb.

Regras (documento de arquitetura, §4): R1 (códigos da linha 12), R4 (nível da linha e eh_agregado),
R5 (pseudo-regiões Distância e Exterior), R6 (zeros estruturais do EaD), R7 (célula vazia ≠ zero),
R8 (marcador "."), R9 (Cine sem aspas, original preservado), R10 (strip), R13 (suspeitos Q02/Q03).

Semântica verificada no staging (2017 e 2024): Brasil = Σ Município + Σ Distância + Σ Exterior.
  - Anexo III, linhas Município/Exterior: cursos, vagas e inscritos não são distribuídos (0 publicado)
    → status nao_desagregado, valor nulo.
  - Anexo I, linhas Município: cursos, vagas e inscritos contêm só a parte presencial
    → status somente_presencial, valor mantido. Linhas Exterior: 0 publicado → nao_desagregado.
  - Linhas Distância (I e III): ingressantes, matrículas e concluintes ficam nos polos (0 publicado)
    → status nao_aplicavel, valor nulo.
O valor publicado continua em valor_bruto. Nenhuma linha é descartada: as que não se classificam
vão para linhas_nao_classificadas.

Idempotente por conjunto. Uso: python -I carregar_anexos.py [anexo_i anexo_ii anexo_iii]
"""
import sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import ler_catalogo, CONFIG, DIAG, NUCLEO, PROJETO, STAGING
from visoes import construir_dim_geografia, criar_dim_indicador, criar_visoes

sys.stdout.reconfigure(encoding="utf-8")
# Anexo I não é carregado por padrão: é idêntico a II + III (validado) e está disponível na visão v_anexo_i.
CONJS = sys.argv[1:] or ["anexo_ii", "anexo_iii"]
IDS = ["NO_REGIAO", "NO_UF", "CO_UF", "NO_MUNICIPIO", "CO_MUNICIPIO", "NO_CINE_ROTULO", "CO_CINE_ROTULO"]
NULO = "('celula_vazia', 'marcador_ponto', 'texto_nao_numerico', 'nao_desagregado', 'nao_aplicavel')"
BLOCO = 20000  # linhas por bloco de UNPIVOT (limita a memória no Anexo I)
t0 = time.time()

cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
c02 = ler_catalogo(DIAG / "02_catalogo_abas.xlsx", sheet_name="abas")
xw = pd.read_csv(CONFIG / "xw_colunas_anexos.csv", encoding="utf-8-sig", keep_default_na=False, na_values=[""])
assert not xw.coluna.isna().any(), "coluna sem letra no mapeamento"
man = pd.read_csv(CONFIG / "manifesto_fontes.csv", encoding="utf-8-sig")
NUCLEO.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"))

# ---------------------------------------------------------------- dimensões estáticas
con.register("v_ufs", pd.read_csv(CONFIG / "ufs.csv", dtype=str))
con.register("v_man", man)
con.register("v_xw", xw)
con.register("v_q", pd.read_csv(CONFIG / "qualidade_ocorrencias.csv", encoding="utf-8-sig", dtype=str))
con.execute("CREATE OR REPLACE TABLE dim_uf AS SELECT * FROM v_ufs")
con.execute("CREATE OR REPLACE TABLE dim_fonte AS SELECT * FROM v_man")
con.execute("CREATE OR REPLACE TABLE qualidade_ocorrencias AS SELECT * FROM v_q")
criar_dim_indicador(con)
# recortes de todos os Anexos (ids estáveis enquanto o mapeamento não mudar)
con.execute("""CREATE OR REPLACE TABLE dim_recorte AS
  SELECT row_number() OVER (ORDER BY org_academica, grau, dependencia, categoria_privada) AS id_recorte, *,
         (org_academica='Total' OR grau='Total' OR dependencia='Total' OR categoria_privada='Total') AS eh_agregado
  FROM (SELECT DISTINCT org_academica, grau, dependencia, categoria_privada FROM v_xw)""")
con.execute("""CREATE OR REPLACE TABLE dim_status_valor AS SELECT * FROM (VALUES
  ('informado', true, 'Número publicado'),
  ('suspeito', true, 'Número publicado com inconsistência documentada (ver qualidade_ocorrencias)'),
  ('somente_presencial', true, 'Anexo I, linha municipal: cursos/vagas/inscritos só da parte presencial (EaD não é distribuído por município)'),
  ('nao_desagregado', false, 'O INEP não distribui o indicador neste nível (EaD por município/exterior); 0 publicado em valor_bruto'),
  ('nao_aplicavel', false, 'Linha Distância: ingressantes/matrículas/concluintes ficam nos polos; 0 publicado em valor_bruto'),
  ('celula_vazia', false, 'Célula vazia ou inexistente na planilha'),
  ('marcador_ponto', false, 'Célula com "."'),
  ('texto_nao_numerico', false, 'Texto não numérico em coluna de medida'))
  t(status_valor, tem_valor, descricao)""")

# origem guardada em campos compactos (aba, linha, coluna); a visão reconstrói "aba!célula".
# valor_bruto só é guardado quando o status deixa o valor nulo (nos demais casos valor = número publicado).
con.execute("""CREATE TABLE IF NOT EXISTS fato_anexo_curso (
  ano SMALLINT, anexo VARCHAR, id_geo VARCHAR, nivel_geo VARCHAR, co_cine VARCHAR, indicador VARCHAR,
  id_recorte SMALLINT, valor BIGINT, status_valor VARCHAR, id_ocorrencia VARCHAR, eh_agregado BOOLEAN,
  valor_bruto VARCHAR, aba VARCHAR, linha INTEGER, coluna VARCHAR, md5_zip VARCHAR)""")
criar_visoes(con)
con.execute("""CREATE TABLE IF NOT EXISTS stg_linhas_anexo (
  ano SMALLINT, anexo VARCHAR, linha INTEGER, nivel_geo VARCHAR, no_regiao VARCHAR, no_uf VARCHAR, co_uf VARCHAR,
  no_municipio VARCHAR, co_municipio VARCHAR, no_cine VARCHAR, co_cine_original VARCHAR)""")
con.execute("CREATE TABLE IF NOT EXISTS linhas_nao_classificadas (ano SMALLINT, anexo VARCHAR, linha INTEGER, conteudo VARCHAR)")
con.execute("CREATE TABLE IF NOT EXISTS carga_log (quando TIMESTAMP, etapa VARCHAR, situacao VARCHAR)")

# ---------------------------------------------------------------- carga
for CONJ in CONJS:
    for t in ("fato_anexo_curso", "stg_linhas_anexo", "linhas_nao_classificadas"):
        con.execute(f"DELETE FROM {t} WHERE anexo = ?", [CONJ])
    for ano in sorted(cat[cat.conjunto == CONJ].ano.unique()):
        s = cat[(cat.conjunto == CONJ) & (cat.ano == ano)].iloc[0]
        meta = c02[(c02.ano == ano) & (c02.arquivo == s.arquivo) & (c02.aba == s.aba)].iloc[0]
        pq = str(PROJETO / s.parquet).replace("\\", "/")
        md5 = man[man.ano == ano].md5.iloc[0]
        ini, fim, lcod = int(meta.linha_inicio_dados), int(meta.ultima_linha_com_numero), int(meta.linha_codigos_variaveis)
        # R1: identificadores pelo código da linha 12
        cod = con.execute(f"SELECT * FROM read_parquet('{pq}') WHERE linha = {lcod}").df().iloc[0]
        letra = {str(v).strip(): k for k, v in cod.items() if k not in ("linha", "_num_como_texto", "_extra") and pd.notna(v)}
        L = {c: letra[c] for c in IDS}
        m = xw[(xw.ano == ano) & (xw.conjunto == CONJ)]
        cols = ", ".join(f'"{c}"' for c in m.coluna)
        con.execute(f"""CREATE OR REPLACE TEMP TABLE src AS
          SELECT *, CASE WHEN trim("A") = 'Total Brasil' THEN 'Brasil'
                         WHEN regexp_full_match(trim("{L['CO_MUNICIPIO']}"), '\\d{{7}}') THEN 'Município'
                         WHEN trim("A") = 'Distância' THEN 'Distância'
                         WHEN trim("A") = 'Exterior' THEN 'Exterior'
                         ELSE 'não classificada' END AS nivel_geo
          FROM read_parquet('{pq}') WHERE linha BETWEEN {ini} AND {fim}""")
        con.execute(f"""INSERT INTO linhas_nao_classificadas
          SELECT {ano}, '{CONJ}', linha, concat_ws(' | ', "A", "B", "C", "D", "E", "F", "G") FROM src WHERE nivel_geo = 'não classificada'""")
        con.execute(f"""INSERT INTO stg_linhas_anexo SELECT {ano}, '{CONJ}', linha, nivel_geo,
          trim("{L['NO_REGIAO']}"), trim("{L['NO_UF']}"), trim("{L['CO_UF']}"), trim("{L['NO_MUNICIPIO']}"),
          trim("{L['CO_MUNICIPIO']}"), trim("{L['NO_CINE_ROTULO']}"), "{L['CO_CINE_ROTULO']}" FROM src WHERE nivel_geo <> 'não classificada'""")
        con.register("v_m", m[["coluna", "indicador", "org_academica", "grau", "dependencia", "categoria_privada", "eh_agregado"]])
        for lo in range(ini, fim + 1, BLOCO):
          con.execute(f"""CREATE OR REPLACE TEMP VIEW src_med AS
            SELECT linha, nivel_geo, "{L['CO_UF']}" AS _uf, "{L['CO_MUNICIPIO']}" AS _mun,
                   "{L['CO_CINE_ROTULO']}" AS _cine, {cols} FROM src
            WHERE nivel_geo <> 'não classificada' AND linha BETWEEN {lo} AND {lo + BLOCO - 1}""")
          con.execute(f"CREATE OR REPLACE TEMP TABLE u AS SELECT * FROM src_med UNPIVOT INCLUDE NULLS (bruto FOR coluna IN ({cols}))")
          con.execute(f"""INSERT INTO fato_anexo_curso
          WITH b AS (
            SELECT u.*, m.indicador, m.org_academica, m.eh_agregado, r.id_recorte,
                   TRY_CAST(trim(u.bruto) AS DOUBLE) AS num,
                   (m.indicador IN ('cursos', 'vagas', 'inscritos')) AS ind_oferta,
                   ('{CONJ}' <> 'anexo_iii' AND trim(u._uf) = '51' AND m.org_academica = 'IF/Cefet'
                    AND ((m.indicador = 'inscritos' AND {ano} BETWEEN 2018 AND 2023)
                      OR (m.indicador = 'ingressantes' AND {ano} BETWEEN 2021 AND 2022))) AS susp
            FROM u JOIN v_m m USING (coluna)
            JOIN dim_recorte r ON r.org_academica = m.org_academica AND r.grau = m.grau
                               AND r.dependencia = m.dependencia AND r.categoria_privada = m.categoria_privada),
          s AS (
            SELECT *, CASE
              WHEN bruto IS NULL OR trim(bruto) = '' THEN 'celula_vazia'
              WHEN trim(bruto) = '.' THEN 'marcador_ponto'
              WHEN num IS NULL THEN 'texto_nao_numerico'
              WHEN '{CONJ}' = 'anexo_iii' AND nivel_geo IN ('Município', 'Exterior') AND ind_oferta AND num = 0 THEN 'nao_desagregado'
              WHEN '{CONJ}' = 'anexo_i' AND nivel_geo = 'Exterior' AND ind_oferta AND num = 0 THEN 'nao_desagregado'
              WHEN '{CONJ}' = 'anexo_i' AND nivel_geo = 'Município' AND ind_oferta THEN 'somente_presencial'
              WHEN nivel_geo = 'Distância' AND NOT ind_oferta AND num = 0 THEN 'nao_aplicavel'
              WHEN susp THEN 'suspeito'
              ELSE 'informado' END AS st
            FROM b)
          SELECT {ano}, '{CONJ}',
                 CASE nivel_geo WHEN 'Brasil' THEN 'BR' WHEN 'Distância' THEN 'DIST' WHEN 'Exterior' THEN 'EXT' ELSE trim(_mun) END,
                 nivel_geo, COALESCE(NULLIF(replace(trim(_cine), '"', ''), ''), '_TOTAL'), indicador, id_recorte,
                 CASE WHEN st IN {NULO} THEN NULL ELSE CAST(num AS BIGINT) END, st,
                 CASE WHEN st = 'suspeito' THEN (CASE WHEN indicador = 'inscritos' THEN 'Q02' ELSE 'Q03' END) END,
                 eh_agregado, CASE WHEN st IN {NULO} OR CAST(num AS BIGINT) <> num THEN bruto END,
                 '{s.aba}', linha, coluna, '{md5}'
          FROM s""")
        n = con.execute(f"SELECT count(*) FROM fato_anexo_curso WHERE anexo='{CONJ}' AND ano={ano}").fetchone()[0]
        print(f"{CONJ} {ano}: {n:,} valores ({round(time.time() - t0)} s)", flush=True)
    con.execute("INSERT INTO carga_log VALUES (current_timestamp, ?, 'concluída')", [f"carregar_anexos:{CONJ}"])

# ---------------------------------------------------------------- dimensões derivadas dos dados
construir_dim_geografia(con)
con.execute("""CREATE OR REPLACE TABLE dim_geografia_nomes AS
  SELECT DISTINCT ano, co_municipio, no_municipio, no_uf AS no_uf_planilha, no_regiao AS no_regiao_planilha
  FROM stg_linhas_anexo WHERE nivel_geo = 'Município'""")
con.execute("""CREATE OR REPLACE TABLE dim_curso_cine AS
  SELECT DISTINCT ano, COALESCE(NULLIF(replace(trim(co_cine_original), '"', ''), ''), '_TOTAL') AS co_cine,
         COALESCE(NULLIF(no_cine, ''), '(todos os cursos)') AS no_cine, co_cine_original
  FROM stg_linhas_anexo""")
print(con.execute("""SELECT anexo, status_valor, count(*) n FROM fato_anexo_curso GROUP BY ALL ORDER BY 1, 3 DESC""").df().to_string(index=False))
print("linhas não classificadas:", con.execute("SELECT anexo, count(*) FROM linhas_nao_classificadas GROUP BY 1").fetchall())
print("geografias:", con.execute("SELECT nivel_geo, count(*) FROM dim_geografia GROUP BY 1 ORDER BY 1").fetchall(),
      "| cursos Cine (ano×código):", con.execute("SELECT count(*) FROM dim_curso_cine").fetchone()[0])
con.close()
print(f"carga concluída em {round((time.time() - t0) / 60, 1)} min")
