"""P3 — Carga da Sinopse por município (tabelas 1.x a 7.x, 2017–2024) no núcleo: dados/nucleo/ijsn.duckdb.

Entrada: staging (P0), config/xw_colunas_sinopse.csv (p3_mapear_sinopse.py), catálogo 02 (linhas de dados e
colunas identificadoras). Regras (documento de arquitetura, §4):
  - linhas: Total Brasil → BR; "Total <Região>" → REG-<região>; "Total <UF>" (coluna da UF) → UF-<código>;
    código IBGE de 7 dígitos → município; "Exterior" → EXT. Demais linhas → linhas_nao_classificadas_sinopse;
  - nível acadêmico (Graduação/Sequencial) quando a tabela tem essa coluna; senão "Total";
  - célula vazia ≠ zero (celula_vazia, valor nulo); "." → marcador_ponto; texto → texto_nao_numerico;
  - suspeitos: Q01 (4.1/2023, IF, vagas/inscritos, MT e agregados Centro-Oeste/Brasil),
    Q02 (inscritos do IF em MT 2018–2023, presencial), Q03 (ingressantes do IF em MT 2021–2022, presencial),
    Q09 (colunas trocadas, config/q09_colunas_trocadas.csv), Q10 (células 'suspeita' de config/q10_celulas_suspeitas.csv,
    geradas por q10_detectar.py);
  - somente_presencial: cursos/vagas/inscritos abaixo do Brasil em 3.1/4.1 (modalidade Total) e 7.4 (Q13).
Idempotente. Uso: python -I carregar_sinopse.py
  Teste controlado (não toca o banco principal): python -I carregar_sinopse.py --banco OUTRO.duckdb --tabelas 6.3,6.6,7.4
"""
import re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import ler_catalogo, CONFIG, DIAG, NUCLEO, PROJETO, STAGING
from visoes import construir_dim_geografia, criar_dim_indicador, criar_visoes

sys.stdout.reconfigure(encoding="utf-8")
DIMS = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
        "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
        "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
NULO = "('celula_vazia', 'marcador_ponto', 'texto_nao_numerico', 'nao_desagregado')"
t0 = time.time()

cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
c02 = ler_catalogo(DIAG / "02_catalogo_abas.xlsx", sheet_name="abas")
xw = pd.read_csv(CONFIG / "xw_colunas_sinopse.csv", encoding="utf-8-sig", keep_default_na=False, na_values=[""], dtype=str)
xw["ano"] = xw.ano.astype(int)
xw["eh_agregado"] = xw.eh_agregado == "True"
man = pd.read_csv(CONFIG / "manifesto_fontes.csv", encoding="utf-8-sig")
ARGS = dict(zip(sys.argv[1::2], sys.argv[2::2]))
BANCO_DESTINO = Path(ARGS.get("--banco", NUCLEO / "ijsn.duckdb"))
SO_TABELAS = set(ARGS["--tabelas"].split(",")) if "--tabelas" in ARGS else None
if SO_TABELAS is not None and BANCO_DESTINO.resolve() == (NUCLEO / "ijsn.duckdb").resolve():
    raise SystemExit("--tabelas só é permitido com --banco diferente do banco principal (carga parcial apagaria o resto)")
con = duckdb.connect(str(BANCO_DESTINO))
con.execute("SET memory_limit = '6GB'" if SO_TABELAS is None else "SET memory_limit = '3GB'")

con.register("v_ufs", pd.read_csv(CONFIG / "ufs.csv", dtype=str))
con.execute("CREATE OR REPLACE TABLE dim_uf AS SELECT * FROM v_ufs")
con.register("v_q", pd.read_csv(CONFIG / "qualidade_ocorrencias.csv", encoding="utf-8-sig", dtype=str))
con.execute("CREATE OR REPLACE TABLE qualidade_ocorrencias AS SELECT * FROM v_q")
criar_dim_indicador(con)
con.register("v_xw", xw)
_q9 = CONFIG / "q09_colunas_trocadas.csv"
q9 = pd.read_csv(_q9, encoding="utf-8-sig", dtype={"tabela": str}, keep_default_na=False) if _q9.exists() else pd.DataFrame(
    columns=["ano", "tabela", "coluna_a", "coluna_b"])
con.register("v_q09", pd.concat([q9[["ano", "tabela", "coluna_a"]].rename(columns={"coluna_a": "coluna"}),
                                 q9[["ano", "tabela", "coluna_b"]].rename(columns={"coluna_b": "coluna"})]).drop_duplicates()
             if len(q9) else pd.DataFrame({"ano": pd.Series(dtype=int), "tabela": pd.Series(dtype=str), "coluna": pd.Series(dtype=str)}))
_q10 = CONFIG / "q10_celulas_suspeitas.csv"
q10 = (pd.read_csv(_q10, encoding="utf-8-sig", dtype={"tabela": str, "coluna": str})
       .query("papel == 'suspeita'")[["ano", "tabela", "linha", "coluna"]] if _q10.exists() else
       pd.DataFrame({"ano": pd.Series(dtype=int), "tabela": pd.Series(dtype=str), "linha": pd.Series(dtype=int),
                     "coluna": pd.Series(dtype=str)}))
con.register("v_q10", q10)
con.execute(f"""CREATE OR REPLACE TABLE dim_recorte_sinopse AS
  SELECT row_number() OVER (ORDER BY {', '.join(DIMS)}) AS id_recorte, *,
         ({' OR '.join(f"{d} IN ('Total', 'Pública')" for d in DIMS)}) AS eh_agregado
  FROM (SELECT DISTINCT {', '.join(DIMS)} FROM v_xw)""")
c02s = c02[c02.conjunto == "Sinopse por município"].copy()
c02s["tabela"] = c02s.chave_tabela.str.replace("Tab ", "", regex=False)
con.register("v_tab", c02s[c02s.tipo_aba == "tabela_dados"][["ano", "tabela", "aba", "titulo_tabela", "subtitulo_universo", "tema_secao"]])
con.execute("""CREATE OR REPLACE TABLE dim_tabela_sinopse AS
  SELECT *, CASE WHEN split_part(tabela, '.', 1) IN ('1', '2') THEN 'sede' ELSE 'oferta' END AS ref_geografica FROM v_tab""")

con.execute("DROP TABLE IF EXISTS fato_sinopse")
con.execute("""CREATE TABLE fato_sinopse (
  ano SMALLINT, tabela VARCHAR, id_geo VARCHAR, nivel_geo VARCHAR, nivel_academico VARCHAR, indicador VARCHAR,
  id_recorte INTEGER, valor BIGINT, status_valor VARCHAR, id_ocorrencia VARCHAR, eh_agregado BOOLEAN,
  valor_bruto VARCHAR, aba VARCHAR, linha INTEGER, coluna VARCHAR, md5_zip VARCHAR)""")
con.execute("""CREATE OR REPLACE TABLE stg_linhas_sinopse (
  ano SMALLINT, tabela VARCHAR, linha INTEGER, nivel_geo VARCHAR, id_geo VARCHAR, no_regiao VARCHAR, no_uf VARCHAR,
  no_municipio VARCHAR, co_municipio VARCHAR, nivel_academico VARCHAR)""")
con.execute("CREATE OR REPLACE TABLE linhas_nao_classificadas_sinopse (ano SMALLINT, tabela VARCHAR, linha INTEGER, conteudo VARCHAR)")
con.execute("""CREATE OR REPLACE TABLE correcoes_geografia_sinopse (ano SMALLINT, tabela VARCHAR, linha INTEGER,
  rotulo_planilha VARCHAR, co_uf_pelo_rotulo VARCHAR, co_uf_atribuido VARCHAR, motivo VARCHAR)""")
REG = "lower(strip_accents(trim({})))"

for (ano, tabela), m in xw.groupby(["ano", "tabela"]):
    if SO_TABELAS is not None and tabela not in SO_TABELAS:
        continue
    meta = c02s[(c02s.ano == ano) & (c02s.tabela == tabela)].iloc[0]
    s = cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba == meta.aba)].iloc[0]
    pq = str(PROJETO / s.parquet).replace("\\", "/")
    md5 = man[man.ano == ano].md5.iloc[0]
    ids = dict(re.findall(r"([A-Z]+)=([^,]+?)(?=, [A-Z]+=|$)", meta.colunas_identificadoras))
    def col(pred):
        return next((k for k, v in ids.items() if pred(v.strip())), None)
    c_uf = col(lambda v: v.startswith("Unidade da Federa"))
    c_mn = col(lambda v: v == "Município")
    c_cod = col(lambda v: v.startswith("Código do Município"))
    c_niv = col(lambda v: v.startswith("Nível Acadêmico"))
    niv = f'COALESCE(NULLIF(trim("{c_niv}"), \'\'), \'Total\')' if c_niv else "'Total'"
    con.execute(f"""CREATE OR REPLACE TEMP TABLE src AS
      WITH x AS (SELECT *, COALESCE(trim("{c_uf}"), '') AS _ufr, COALESCE(trim("{c_mn}"), '') AS _mnr,
                        COALESCE(trim("{c_cod}"), '') AS _cod
                 FROM read_parquet('{pq}') WHERE linha BETWEEN {int(meta.linha_inicio_dados)} AND {int(meta.ultima_linha_com_numero)})
      SELECT *, CASE
          WHEN trim("A") = 'Total Brasil' THEN 'Brasil'
          WHEN regexp_full_match(_cod, '\\d{{7}}') THEN 'Município'
          WHEN trim("A") LIKE 'Total %' THEN 'Região'
          WHEN trim("A") = 'Exterior' THEN 'Exterior'
          -- subtotal de UF: nome da UF sem código de município. Aceita "Total " repetido ou ausente e o nome quebrado
          -- em duas colunas ("Total" | "Rondônia") — 2024 6.x/7.x, 2.6 e 2022 2.4 (Q07/Q08)
          WHEN _cod = '' AND _ufr <> '' AND (_mnr = '' OR regexp_full_match(_ufr, 'Total')) THEN 'UF'
          ELSE 'não classificada' END AS _nivel,
        regexp_replace(CASE WHEN regexp_full_match(_ufr, 'Total') THEN 'Total ' || _mnr ELSE _ufr END, '^(Total\\s+)+', '') AS _ufnome,
        {niv} AS _nivac
      FROM x""")
    # UF pelo rótulo; se o mesmo rótulo de UF se repete no mesmo nível acadêmico, confirma pelo código IBGE dos
    # municípios logo abaixo (2024: segundo "Total Rondônia" é o subtotal do Acre — Q08). Toda troca é registrada.
    con.execute(f"""CREATE OR REPLACE TEMP TABLE geo AS
      WITH ufs AS (
        SELECT s.linha, s._ufnome, u.co_uf AS uf_rotulo,
               (SELECT substr(s2._cod, 1, 2) FROM src s2 WHERE s2._nivel = 'Município' AND s2.linha > s.linha
                ORDER BY s2.linha LIMIT 1) AS uf_seguinte,
               count(*) OVER (PARTITION BY u.co_uf, s._nivac) AS repeticoes
        FROM src s LEFT JOIN dim_uf u ON {REG.format('u.no_uf')} = {REG.format('s._ufnome')}
        WHERE s._nivel = 'UF'),
      ufs2 AS (
        SELECT *, CASE WHEN uf_rotulo IS NULL THEN uf_seguinte
                       WHEN repeticoes > 1 AND uf_seguinte IS NOT NULL AND uf_seguinte <> uf_rotulo THEN uf_seguinte
                       ELSE uf_rotulo END AS uf_final FROM ufs)
      SELECT s.linha, s._nivel, s._nivac,
        CASE s._nivel WHEN 'Brasil' THEN 'BR' WHEN 'Exterior' THEN 'EXT'
             WHEN 'Município' THEN s._cod
             WHEN 'UF' THEN 'UF-' || x.uf_final
             WHEN 'Região' THEN 'REG-' || r.no_regiao END AS id_geo,
        trim(s."A") AS no_regiao, s._ufr AS no_uf, s._mnr AS no_municipio, s._cod AS co_municipio,
        x.uf_rotulo, x.uf_final, x._ufnome
      FROM src s
      LEFT JOIN ufs2 x USING (linha)
      LEFT JOIN (SELECT DISTINCT no_regiao FROM dim_uf) r ON s._nivel = 'Região'
           AND {REG.format('r.no_regiao')} = {REG.format('substr(trim(s."A"), 7)')}""")
    con.execute(f"""INSERT INTO correcoes_geografia_sinopse
      SELECT {ano}, '{tabela}', linha, _ufnome, uf_rotulo, uf_final,
             CASE WHEN uf_rotulo IS NULL THEN 'rótulo de UF não reconhecido' ELSE 'rótulo de UF repetido' END
      FROM geo WHERE _nivel = 'UF' AND uf_final IS DISTINCT FROM uf_rotulo""")
    # linhas que não se classificam (ou UF/Região sem correspondência) não entram no fato, mas ficam registradas
    con.execute(f"""INSERT INTO linhas_nao_classificadas_sinopse
      SELECT {ano}, '{tabela}', s.linha, concat_ws(' | ', s."A", s."B", s."C", s."D", s."E")
      FROM src s JOIN geo g USING (linha) WHERE g._nivel = 'não classificada' OR g.id_geo IS NULL""")
    con.execute(f"""INSERT INTO stg_linhas_sinopse SELECT {ano}, '{tabela}', linha, _nivel, id_geo, no_regiao, no_uf,
      no_municipio, co_municipio, _nivac FROM geo WHERE _nivel <> 'não classificada' AND id_geo IS NOT NULL""")
    con.register("v_m", m[["coluna", "indicador", "eh_agregado"] + DIMS])
    cols = ", ".join(f'"{c}"' for c in m.coluna)
    con.execute(f"""CREATE OR REPLACE TEMP TABLE u AS
      SELECT * FROM (SELECT g.linha, g._nivel, g._nivac, g.id_geo, {', '.join('s.' + chr(34) + c + chr(34) for c in m.coluna)}
                     FROM src s JOIN geo g USING (linha) WHERE g._nivel <> 'não classificada' AND g.id_geo IS NOT NULL)
      UNPIVOT INCLUDE NULLS (bruto FOR coluna IN ({cols}))""")
    con.execute(f"""INSERT INTO fato_sinopse
      WITH b AS (
        SELECT u.*, m.indicador, m.org_academica, m.modalidade, m.eh_agregado, r.id_recorte,
               TRY_CAST(trim(u.bruto) AS DOUBLE) AS num,
               (u.id_geo = 'UF-51' OR (u._nivel = 'Município' AND u.id_geo LIKE '51%')) AS mt
        FROM u JOIN v_m m USING (coluna)
        JOIN dim_recorte_sinopse r ON {' AND '.join(f'r.{d} = m.{d}' for d in DIMS)}),
      s AS (
        SELECT *, CASE
          -- Q09: par de colunas com valores trocados na publicação (detectar_colunas_trocadas.py); valor mantido
          WHEN EXISTS (SELECT 1 FROM v_q09 q WHERE q.ano = {ano} AND q.tabela = '{tabela}' AND q.coluna = b.coluna) THEN 'Q09'
          WHEN {ano} = 2023 AND '{tabela}' = '4.1' AND org_academica = 'IF/Cefet' AND indicador IN ('vagas', 'inscritos')
               AND (mt OR id_geo IN ('REG-Centro-Oeste', 'BR')) THEN 'Q01'
          WHEN indicador = 'inscritos' AND org_academica = 'IF/Cefet' AND {ano} BETWEEN 2018 AND 2023 AND mt
               AND modalidade <> 'A Distância' AND '{tabela}' <> '7.3' THEN 'Q02'
          WHEN indicador = 'ingressantes' AND org_academica = 'IF/Cefet' AND {ano} BETWEEN 2021 AND 2022 AND mt
               AND modalidade <> 'A Distância' AND '{tabela}' <> '7.3' THEN 'Q03'
          -- Q10: célula em total que não fecha, sem evidência a favor (q10_detectar.py); valor mantido
          WHEN EXISTS (SELECT 1 FROM v_q10 q WHERE q.ano = {ano} AND q.tabela = '{tabela}' AND q.linha = b.linha
                       AND q.coluna = b.coluna) THEN 'Q10' END AS ocorr
        FROM b),
      t AS (
        SELECT *, CASE
                       -- R6: EaD não é distribuído por local de oferta (3.1/4.1 modalidade A Distância; 7.3 inteira)
                       WHEN indicador IN ('cursos', 'vagas', 'inscritos') AND _nivel <> 'Brasil'
                            AND (('{tabela}' IN ('3.1', '4.1') AND modalidade = 'A Distância') OR '{tabela}' = '7.3')
                            AND (num = 0 OR bruto IS NULL OR trim(bruto) = '') THEN 'nao_desagregado'
                       WHEN bruto IS NULL OR trim(bruto) = '' THEN 'celula_vazia'
                       WHEN trim(bruto) = '.' THEN 'marcador_ponto'
                       WHEN num IS NULL THEN 'texto_nao_numerico'
                       WHEN ocorr IS NOT NULL THEN 'suspeito'
                       -- 3.1/4.1 e 7.4 (Q13) abaixo do Brasil: modalidade "Total" contém só o presencial
                       WHEN indicador IN ('cursos', 'vagas', 'inscritos') AND _nivel <> 'Brasil'
                            AND '{tabela}' IN ('3.1', '4.1', '7.4') AND modalidade = 'Total' THEN 'somente_presencial'
                       ELSE 'informado' END AS st
        FROM s)
      SELECT {ano}, '{tabela}', id_geo, _nivel, _nivac, indicador, id_recorte,
             CASE WHEN st IN {NULO} THEN NULL ELSE CAST(num AS BIGINT) END, st,
             CASE WHEN st = 'suspeito' THEN ocorr END, eh_agregado,
             CASE WHEN st IN {NULO} OR CAST(num AS BIGINT) <> num THEN bruto END,
             '{meta.aba}', linha, coluna, '{md5}'
      FROM t""")
    if tabela.endswith(".1") and tabela.startswith("1"):
        print(f"{ano}: ... ({round(time.time() - t0)} s)", flush=True)

if SO_TABELAS is None:     # carga parcial de teste: sem fatos dos Anexos, não há visões nem dim_geografia completas
    construir_dim_geografia(con)
    criar_visoes(con)
con.execute("CREATE TABLE IF NOT EXISTS carga_log (quando TIMESTAMP, etapa VARCHAR, situacao VARCHAR)")
con.execute("INSERT INTO carga_log VALUES (current_timestamp, 'carregar_sinopse', 'concluída')")
print(con.execute("SELECT status_valor, count(*) n FROM fato_sinopse GROUP BY 1 ORDER BY 2 DESC").df().to_string(index=False))
print(con.execute("SELECT nivel_geo, count(DISTINCT ano || tabela || linha) linhas FROM fato_sinopse GROUP BY 1 ORDER BY 1").df().to_string(index=False))
print("linhas não classificadas:", con.execute("SELECT count(*) FROM linhas_nao_classificadas_sinopse").fetchone()[0])
print("correções de UF (Q08):")
print(con.execute("""SELECT ano, tabela, linha, rotulo_planilha, co_uf_pelo_rotulo, co_uf_atribuido, motivo
                     FROM correcoes_geografia_sinopse ORDER BY 1, 2, 3""").df().to_string(index=False))
print("chaves duplicadas no fato:", con.execute("""SELECT count(*) FROM (SELECT ano, tabela, id_geo, nivel_academico, indicador,
      id_recorte FROM fato_sinopse GROUP BY ALL HAVING count(*) > 1)""").fetchone()[0])
print(con.execute("SELECT ano, tabela, linha, conteudo FROM linhas_nao_classificadas_sinopse LIMIT 15").df().to_string(index=False))
if SO_TABELAS is None:
    print("geografias:", con.execute("SELECT nivel_geo, count(*) FROM dim_geografia GROUP BY 1 ORDER BY 1").fetchall())
con.close()
print(f"P3 carga concluída em {round((time.time() - t0) / 60, 1)} min")
