"""Validação da P2 (Anexos I e III no núcleo, com o Anexo II já carregado). Somente leitura.

T1  Completude: 514 valores por linha; nenhuma linha não classificada; regras de status só pegaram zeros publicados.
T2  Totais internos: "Total" de cada dimensão = soma das categorias (só valores numéricos).
T3  Brasil = Σ Município + Σ Distância + Σ Exterior (número publicado), por curso, indicador e recorte.
T4  Anexo I = Anexo II + Anexo III: Brasil (todos os indicadores); Município (ingressantes, matrículas,
    concluintes); Município cursos/vagas/inscritos do I = II (confirma "somente_presencial");
    Distância e Exterior do I = do III.
T5  Totais Brasil: Anexo III = Sinopse 7.3; Anexo I = 7.2 + 7.3 (bloco "Total Geral").
T6  Conferência independente: 16 valores (2 por ano, Anexos I e III, incluindo municípios do ES) relidos do
    XML original por varredura de texto (regex), sem o leitor usado na carga.

Uso: python -I p2_validar.py
"""
import re, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import ler_catalogo, DIAG, NUCLEO, PROJETO, QUALIDADE, STAGING, XLSX_TMP, abas, strings_compartilhadas

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit = '6GB'")
con.execute("SET preserve_insertion_order = false")
PUB = "COALESCE(valor, TRY_CAST(valor_bruto AS BIGINT))"  # número publicado, mesmo quando o status anula o valor
div, out = [], []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


def falhas(df, cond, teste, fmt, lim=300):
    bad = df[cond]
    for r in bad.head(lim).itertuples():
        div.append({"teste": teste, "ano": getattr(r, "ano", ""), "detalhe": fmt(r)})
    return bad


# ---------------------------------------------------------------- T1
t1 = con.execute("""SELECT anexo, ano, count(*) AS valores, count(DISTINCT linha) AS linhas FROM fato_anexo_curso GROUP BY 1, 2 ORDER BY 1, 2""").df()
stg = con.execute("SELECT anexo, ano, count(*) AS n FROM stg_linhas_anexo GROUP BY 1, 2").df()
t1 = t1.merge(stg, on=["anexo", "ano"])
nc = con.execute("SELECT count(*) FROM linhas_nao_classificadas").fetchone()[0]
ok1 = ((t1.valores == t1.linhas * 514) & (t1.linhas == t1.n)).all() and nc == 0
p("T1 completude:", "OK" if ok1 else "FALHA", f"| não classificadas: {nc}")
p(con.execute("""SELECT anexo, nivel_geo, count(DISTINCT ano||'-'||linha) AS linhas FROM fato_anexo_curso GROUP BY 1, 2 ORDER BY 1, 2""").df().to_string(index=False))
p(con.execute("SELECT anexo, status_valor, count(*) n FROM fato_anexo_curso GROUP BY 1, 2 ORDER BY 1, 3 DESC").df().to_string(index=False))
chk = con.execute("""SELECT
  count(*) FILTER (WHERE anexo='anexo_iii' AND nivel_geo IN ('Município','Exterior') AND indicador IN ('cursos','vagas','inscritos') AND status_valor <> 'nao_desagregado') AS iii_oferta_nao_zero,
  count(*) FILTER (WHERE nivel_geo='Distância' AND indicador NOT IN ('cursos','vagas','inscritos') AND status_valor <> 'nao_aplicavel') AS dist_nao_zero,
  count(*) FILTER (WHERE status_valor IN ('nao_desagregado','nao_aplicavel') AND TRY_CAST(valor_bruto AS DOUBLE) <> 0) AS anulados_nao_zero
  FROM fato_anexo_curso""").df()
p("   regras de status (todos devem ser 0):", chk.iloc[0].to_dict())

# ---------------------------------------------------------------- T2
con.execute("""CREATE TEMP TABLE pares AS
  WITH r AS (SELECT *, CASE WHEN categoria_privada = 'Não se aplica' THEN 'Total' ELSE categoria_privada END AS catn FROM dim_recorte)
  SELECT d.dim, pa.id_recorte AS pai, fi.id_recorte AS filho FROM r pa, r fi,
    (VALUES ('org_academica'), ('grau'), ('dependencia'), ('categoria_privada')) d(dim)
  WHERE (d.dim = 'org_academica' AND pa.org_academica = 'Total' AND fi.org_academica <> 'Total'
           AND fi.grau = pa.grau AND fi.dependencia = pa.dependencia AND fi.catn = pa.catn)
     OR (d.dim = 'grau' AND pa.grau = 'Total' AND fi.grau <> 'Total'
           AND fi.org_academica = pa.org_academica AND fi.dependencia = pa.dependencia AND fi.catn = pa.catn)
     OR (d.dim = 'dependencia' AND pa.dependencia = 'Total' AND fi.dependencia <> 'Total'
           AND fi.org_academica = pa.org_academica AND fi.grau = pa.grau AND fi.catn = pa.catn)
     OR (d.dim = 'categoria_privada' AND pa.categoria_privada = 'Total' AND fi.categoria_privada NOT IN ('Total', 'Não se aplica')
           AND fi.org_academica = pa.org_academica AND fi.grau = pa.grau AND fi.dependencia = pa.dependencia)""")
ANOS = list(range(2017, 2025))
INDS = ["cursos", "vagas", "inscritos", "ingressantes", "matriculas", "concluintes"]


def comparar(nome, sql, fmt):
    """Roda `sql` (colunas: a, b, ano, ...) por pedaços já filtrados; conta comparações e traz só as falhas."""
    n, nbad, exemplos = 0, 0, []
    for q in sql:
        r = con.execute(f"SELECT count(*), count(*) FILTER (WHERE a IS DISTINCT FROM b) FROM ({q})").fetchone()
        n += r[0]; nbad += r[1]
        if r[1] and len(exemplos) < 300:
            exemplos += con.execute(f"SELECT * FROM ({q}) WHERE a IS DISTINCT FROM b LIMIT 100").df().to_dict("records")
    for e in exemplos[:300]:
        div.append({"teste": nome.split(" ")[0], "ano": e.get("ano"), "detalhe": fmt(e)})
    p(f"{nome}: {n:,} comparações |", "OK" if nbad == 0 else f"FALHA em {nbad:,}")
    if exemplos:
        p("   exemplos:", "; ".join(fmt(e) for e in exemplos[:5]))


# T2 — por anexo, ano e indicador
for anexo in ("anexo_iii", "anexo_i"):
    comparar(f"T2 totais internos {anexo}", [f"""
      WITH f AS (SELECT ano, id_geo, co_cine, indicador, id_recorte, valor, aba || '!' || coluna || linha AS origem
                 FROM fato_anexo_curso WHERE anexo = '{anexo}' AND ano = {ano} AND indicador = '{ind}' AND valor IS NOT NULL),
      s AS (SELECT pr.dim, f.ano, f.id_geo, f.co_cine, pr.pai, sum(f.valor) AS b
            FROM f JOIN pares pr ON pr.filho = f.id_recorte GROUP BY ALL)
      SELECT s.dim, s.ano, pa.valor AS a, s.b, pa.origem FROM s
      JOIN f pa ON pa.id_geo = s.id_geo AND pa.co_cine = s.co_cine AND pa.id_recorte = s.pai"""
        for ano in ANOS for ind in INDS],
        lambda e: f"{anexo} {e['dim']} {e['origem']}={e['a']} Σ={e['b']}")

# T3 — Brasil = Σ Município + Σ Distância + Σ Exterior, por anexo e ano
for anexo in ("anexo_iii", "anexo_i"):
    comparar(f"T3 Brasil = Σ mun + Σ Distância + Σ Exterior ({anexo})", [f"""
      WITH d AS (SELECT co_cine, indicador, id_recorte, sum({PUB}) AS soma
                 FROM fato_anexo_curso WHERE anexo = '{anexo}' AND ano = {ano} AND nivel_geo <> 'Brasil' GROUP BY ALL)
      SELECT {ano} AS ano, {PUB.replace('valor', 'x.valor')} AS a, COALESCE(d.soma, 0) AS b, x.indicador,
             x.aba || '!' || x.coluna || x.linha AS origem
      FROM fato_anexo_curso x LEFT JOIN d USING (co_cine, indicador, id_recorte)
      WHERE x.anexo = '{anexo}' AND x.ano = {ano} AND x.nivel_geo = 'Brasil' AND x.co_cine <> '_TOTAL'"""
        for ano in ANOS],
        lambda e: f"{anexo} {e['origem']} Brasil={e['a']} Σ={e['b']} ({e['indicador']})")


# T4 — Anexo I = II + III, por ano
def t4(nome, where_i, where_outros):
    comparar(f"T4 {nome}", [f"""
      WITH i AS (SELECT id_geo, co_cine, indicador, id_recorte, {PUB} AS a, aba || '!' || coluna || linha AS origem
                 FROM fato_anexo_curso WHERE anexo = 'anexo_i' AND ano = {ano} AND {where_i}),
           o AS (SELECT id_geo, co_cine, indicador, id_recorte, sum({PUB}) AS b
                 FROM fato_anexo_curso WHERE ano = {ano} AND {where_outros} GROUP BY ALL)
      SELECT {ano} AS ano, i.a, COALESCE(o.b, 0) AS b, i.indicador, i.origem
      FROM i LEFT JOIN o USING (id_geo, co_cine, indicador, id_recorte)""" for ano in ANOS],
        lambda e: f"{nome}: {e['origem']} I={e['a']} outros={e['b']}")


t4("Brasil: I = II + III", "nivel_geo = 'Brasil'", "anexo IN ('anexo_ii','anexo_iii') AND nivel_geo = 'Brasil'")
t4("Município ingr/matr/concl: I = II + III", "nivel_geo = 'Município' AND indicador NOT IN ('cursos','vagas','inscritos')",
   "anexo IN ('anexo_ii','anexo_iii') AND nivel_geo = 'Município' AND indicador NOT IN ('cursos','vagas','inscritos')")
t4("Município cursos/vagas/inscritos: I = II (somente presencial)", "nivel_geo = 'Município' AND indicador IN ('cursos','vagas','inscritos')",
   "anexo = 'anexo_ii' AND nivel_geo = 'Município' AND indicador IN ('cursos','vagas','inscritos')")
t4("Distância e Exterior: I = III", "nivel_geo IN ('Distância','Exterior')", "anexo = 'anexo_iii' AND nivel_geo IN ('Distância','Exterior')")

# ---------------------------------------------------------------- T5
c03 = ler_catalogo(DIAG / "03_catalogo_colunas.xlsx", usecols=["ano", "aba", "coluna", "nivel_1", "nivel_2"])
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
MAP = {"Número de Cursos": "cursos", "Vagas Oferecidas": "vagas", "Candidatos Inscritos": "inscritos",
       "Ingressantes": "ingressantes", "Matrículas": "matriculas", "Concluintes": "concluintes"}
idt = con.execute("""SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
                     AND dependencia='Total' AND categoria_privada='Total'""").fetchone()[0]


def sinopse_total(ano, aba):
    cc = c03[(c03.ano == ano) & (c03.aba == aba) & c03.nivel_1.astype(str).str.startswith("Total Geral")]
    pqf = str(PROJETO / cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba == aba)].parquet.iloc[0]).replace("\\", "/")
    tb = con.execute(f"""SELECT * FROM read_parquet('{pqf}') WHERE trim("A") = 'Total Brasil' ORDER BY linha LIMIT 1""").df().iloc[0]
    return {MAP[str(r.nivel_2).strip()]: (float(tb[r.coluna]), f"{aba}!{r.coluna}{int(tb.linha)}")
            for r in cc.itertuples() if str(r.nivel_2).strip() in MAP}


rows5 = []
for ano in range(2017, 2025):
    s72, s73 = sinopse_total(ano, "7.2"), sinopse_total(ano, "7.3")
    an = {(a, i): v for a, i, v in con.execute(f"""SELECT anexo, indicador, {PUB} FROM fato_anexo_curso
          WHERE ano={ano} AND id_geo='BR' AND co_cine='_TOTAL' AND id_recorte={idt}""").fetchall()}
    for ind in MAP.values():
        rows5.append({"ano": ano, "indicador": ind, "anexo_iii": an.get(("anexo_iii", ind)), "sinopse_7_3": s73[ind][0],
                      "anexo_i": an.get(("anexo_i", ind)), "sinopse_7_2_mais_7_3": s72[ind][0] + s73[ind][0],
                      "celulas": f"{s72[ind][1]} + {s73[ind][1]}"})
t5 = pd.DataFrame(rows5)
b5 = t5[(t5.anexo_iii != t5.sinopse_7_3) | (t5.anexo_i != t5.sinopse_7_2_mais_7_3)]
p(f"T5 totais Brasil × Sinopse (7.3 e 7.2+7.3): {len(t5) * 2} comparações |", "OK" if b5.empty else f"FALHA em {len(b5)}")
if not b5.empty:
    p(b5.to_string(index=False))
for r in b5.itertuples():
    div.append({"teste": "T5", "ano": r.ano, "detalhe": f"{r.indicador}: III={r.anexo_iii} × 7.3={r.sinopse_7_3}; I={r.anexo_i} × 7.2+7.3={r.sinopse_7_2_mais_7_3} ({r.celulas})"})

# ---------------------------------------------------------------- T6
am = con.execute(f"""SELECT ano, anexo, aba, linha, coluna, {PUB} AS v, status_valor, indicador, id_geo FROM (
    SELECT *, row_number() OVER (PARTITION BY ano, id_geo LIKE '32%' ORDER BY hash(aba || coluna || linha || '20261030')) rn
    FROM fato_anexo_curso WHERE anexo = (CASE WHEN ano % 2 = 0 THEN 'anexo_i' ELSE 'anexo_iii' END)
      AND {PUB} > 0) WHERE rn = 1 ORDER BY ano""").df()
CEL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', re.S)
ok6 = 0
p("T6 conferência independente (varredura do XML original × núcleo):")
for (ano, anexo), g in am.groupby(["ano", "anexo"]):
    arq = cat[(cat.ano == ano) & (cat.conjunto == anexo)].iloc[0]
    alvo = {int(r.linha) for r in g.itertuples()}
    achados = {}
    with zipfile.ZipFile(XLSX_TMP / str(ano) / arq.arquivo) as z:
        ss = strings_compartilhadas(z)
        parte = next(pt for nm, pt, _ in abas(z) if nm == arq.aba)
        resto = ""
        with z.open(parte) as f:
            while alvo - set(achados):
                bloco = f.read(32 * 1024 * 1024).decode("utf8", "ignore")
                if not bloco:
                    break
                txt = resto + bloco
                for lin in list(alvo - set(achados)):
                    i = txt.find(f'<row r="{lin}"')
                    j = txt.find("</row>", i) if i >= 0 else -1
                    if j >= 0:
                        achados[lin] = txt[i:j]
                resto = txt[-200000:]
    for r in g.itertuples():
        row = achados.get(int(r.linha), "")
        orig = None
        for m in CEL.finditer(row):
            if m.group(1) == r.coluna:
                vm = re.search(r"<v>(.*?)</v>", m.group(4) or "")
                orig = vm.group(1) if vm else None
                if orig is not None and 't="s"' in m.group(3):
                    orig = ss[int(orig)]
        igual = orig is not None and float(orig) == float(r.v)
        ok6 += igual
        p(f"   {ano} {arq.arquivo} › {r.aba}!{r.coluna}{r.linha}: XML={orig!r} núcleo={r.v} ({r.indicador}, geo {r.id_geo}, {r.status_valor}) → {'OK' if igual else 'DIFERENTE'}")
        if not igual:
            div.append({"teste": "T6", "ano": ano, "detalhe": f"{r.aba}!{r.coluna}{r.linha} XML={orig} núcleo={r.v}"})
p(f"T6: {ok6}/{len(am)} iguais")

QUALIDADE.mkdir(parents=True, exist_ok=True)
pd.DataFrame(div, columns=["teste", "ano", "detalhe"]).to_csv(QUALIDADE / "p2_divergencias.csv", index=False, encoding="utf-8-sig")
t5.to_csv(QUALIDADE / "p2_t5_anexos_x_sinopse.csv", index=False, encoding="utf-8-sig")
(QUALIDADE / "p2_validacao.txt").write_text("\n".join(out), encoding="utf-8")
con.close()
