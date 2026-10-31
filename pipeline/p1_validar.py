"""Validação da P1 (Anexo II no núcleo). Somente leitura do núcleo, do staging e das cópias XLSX.

T1  Completude: valores = linhas de dados × 514 colunas de medida, por ano; nenhuma linha não classificada.
T2  Totais internos: coluna "Total" de cada dimensão = soma das categorias (mesma linha, mesmo indicador).
T3  Brasil = soma dos municípios (por curso Cine, indicador e recorte); Brasil geral = soma dos cursos.
T5  Anexo II (Brasil, todos os cursos, recorte Total) = Sinopse 7.2 (linha "Total Brasil", bloco "Total Geral").
T6  Conferência independente: 10 valores sorteados lidos de novo da planilha original com outro leitor (calamine).
Falhas são registradas em dados/qualidade/p1_divergencias.csv e não interrompem a validação.

Uso: python -I p1_validar.py
"""
import random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from python_calamine import CalamineWorkbook
from comum import ler_catalogo, CONFIG, DIAG, NUCLEO, PROJETO, QUALIDADE, STAGING, XLSX_TMP, col2n

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
F = "v_fato_anexo_curso WHERE anexo = 'anexo_ii'"
div = []
out = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


# ---------------------------------------------------------------- T1
t1 = con.execute(f"""SELECT f.ano, count(*) AS valores, count(DISTINCT origem_linha) AS linhas,
       count(*) / count(DISTINCT origem_linha) AS por_linha
  FROM (SELECT ano, regexp_extract(origem, '\\d+$') AS origem_linha FROM {F}) f GROUP BY 1 ORDER BY 1""").df()
stg = con.execute("SELECT ano, count(*) n FROM stg_linhas_anexo WHERE anexo='anexo_ii' GROUP BY 1 ORDER BY 1").df()
nc = con.execute("SELECT count(*) FROM linhas_nao_classificadas WHERE anexo='anexo_ii'").fetchone()[0]
ok1 = (t1.por_linha == 514).all() and (t1.linhas.values == stg.n.values).all() and nc == 0
p("T1 completude:", "OK" if ok1 else "FALHA", "| valores por linha:", sorted(t1.por_linha.unique()),
  "| linhas por ano:", dict(zip(t1.ano, t1.linhas)), "| não classificadas:", nc)
st = con.execute(f"SELECT status_valor, count(*) FROM {F} GROUP BY 1 ORDER BY 2 DESC").fetchall()
p("   status dos valores:", st)

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
t2 = con.execute(f"""
  WITH f AS (SELECT ano, id_geo, co_cine, indicador, id_recorte, valor, origem FROM {F}),
  s AS (SELECT pr.dim, f.ano, f.id_geo, f.co_cine, f.indicador, pr.pai, sum(f.valor) AS soma_filhos, count(*) AS n_filhos
        FROM f JOIN pares pr ON pr.filho = f.id_recorte GROUP BY ALL)
  SELECT s.*, pa.valor AS valor_pai, pa.origem AS origem_pai FROM s
  JOIN f pa ON pa.ano = s.ano AND pa.id_geo = s.id_geo AND pa.co_cine = s.co_cine AND pa.indicador = s.indicador AND pa.id_recorte = s.pai
""").df()
bad2 = t2[t2.soma_filhos != t2.valor_pai]
p(f"T2 totais internos: {len(t2):,} comparações em {t2.pai.nunique()} recortes-pai |",
  "OK" if bad2.empty else f"FALHA em {len(bad2):,}")
p("   comparações por dimensão:", t2.groupby("dim").size().to_dict())
if not bad2.empty:
    p("   falhas por dimensão/ano:", bad2.groupby(["dim", "ano"]).size().to_dict())
    for r in bad2.head(500).itertuples():
        div.append({"teste": "T2", "ano": r.ano, "detalhe": f"{r.dim} pai {r.origem_pai}={r.valor_pai} soma={r.soma_filhos} ({r.n_filhos} filhos)"})

# ---------------------------------------------------------------- T3
t3 = con.execute(f"""
  WITH m AS (SELECT ano, co_cine, indicador, id_recorte, sum(valor) soma FROM {F} AND nivel_geo='Município' GROUP BY ALL),
       b AS (SELECT ano, co_cine, indicador, id_recorte, valor, origem FROM {F} AND nivel_geo='Brasil')
  SELECT b.*, COALESCE(m.soma, 0) AS soma_mun FROM b LEFT JOIN m USING (ano, co_cine, indicador, id_recorte)
  WHERE b.co_cine <> '_TOTAL'""").df()
bad3 = t3[t3.valor != t3.soma_mun]
t3b = con.execute(f"""
  WITH c AS (SELECT ano, indicador, id_recorte, sum(valor) soma FROM {F} AND nivel_geo='Brasil' AND co_cine <> '_TOTAL' GROUP BY ALL)
  SELECT b.ano, b.indicador, b.id_recorte, b.valor, c.soma, b.origem
  FROM v_fato_anexo_curso b JOIN c USING (ano, indicador, id_recorte)
  WHERE b.anexo = 'anexo_ii' AND b.nivel_geo = 'Brasil' AND b.co_cine = '_TOTAL'""").df()
bad3b = t3b[t3b.valor != t3b.soma]
p(f"T3 Brasil = Σ municípios: {len(t3):,} comparações |", "OK" if bad3.empty else f"FALHA em {len(bad3):,}",
  f"|| Brasil geral = Σ cursos: {len(t3b):,} |", "OK" if bad3b.empty else f"FALHA em {len(bad3b):,}")
for r in bad3.head(300).itertuples():
    div.append({"teste": "T3", "ano": r.ano, "detalhe": f"{r.origem} Brasil={r.valor} Σmun={r.soma_mun} ({r.indicador}, cine {r.co_cine})"})
for r in bad3b.head(300).itertuples():
    div.append({"teste": "T3b", "ano": r.ano, "detalhe": f"{r.origem} Brasil={r.valor} Σcursos={r.soma}"})

# ---------------------------------------------------------------- T5
c03 = ler_catalogo(DIAG / "03_catalogo_colunas.xlsx", usecols=["ano", "aba", "coluna", "nivel_1", "nivel_2"])
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
MAP = {"Número de Cursos": "cursos", "Vagas Oferecidas": "vagas", "Candidatos Inscritos": "inscritos",
       "Ingressantes": "ingressantes", "Matrículas": "matriculas", "Concluintes": "concluintes"}
idt = con.execute("""SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
                     AND dependencia='Total' AND categoria_privada='Total'""").fetchone()[0]
rows5 = []
for ano in range(2017, 2025):
    cc = c03[(c03.ano == ano) & (c03.aba == "7.2") & c03.nivel_1.astype(str).str.startswith("Total Geral")]
    pqf = str(PROJETO / cat[(cat.ano == ano) & (cat.conjunto == "sinopse") & (cat.aba == "7.2")].parquet.iloc[0]).replace("\\", "/")
    tb = con.execute(f"""SELECT * FROM read_parquet('{pqf}') WHERE trim("A") = 'Total Brasil' ORDER BY linha LIMIT 1""").df().iloc[0]
    an = dict(con.execute(f"SELECT indicador, valor FROM {F} AND ano={ano} AND id_geo='BR' AND co_cine='_TOTAL' AND id_recorte={idt}").fetchall())
    for r in cc.itertuples():
        ind = MAP.get(str(r.nivel_2).strip())
        if ind:
            v72 = float(tb[r.coluna])
            rows5.append({"ano": ano, "indicador": ind, "anexo_ii": an.get(ind), "sinopse_7_2": v72, "celula_7_2": f"7.2!{r.coluna}{int(tb.linha)}"})
t5 = pd.DataFrame(rows5)
bad5 = t5[t5.anexo_ii != t5.sinopse_7_2]
p(f"T5 Anexo II × Sinopse 7.2 (Brasil): {len(t5)} comparações |", "OK" if bad5.empty else f"FALHA em {len(bad5)}")
if not bad5.empty:
    p(bad5.to_string(index=False))
for r in bad5.itertuples():
    div.append({"teste": "T5", "ano": r.ano, "detalhe": f"{r.indicador}: Anexo II={r.anexo_ii} × {r.celula_7_2}={r.sinopse_7_2}"})

# ---------------------------------------------------------------- T6
random.seed(20261030)
# 2 valores não nulos e diferentes de zero por ano: um de município do ES e um de qualquer geografia
amostra = con.execute(f"""SELECT ano, origem, valor, status_valor, indicador, id_geo, co_cine FROM (
    SELECT *, row_number() OVER (PARTITION BY ano, id_geo LIKE '32%' ORDER BY hash(origem || '20261030')) AS rn
    FROM {F} AND status_valor = 'informado' AND valor > 0) WHERE rn = 1""").df()
amostra = amostra.sort_values(["ano", "origem"])
ok6 = 0
p("T6 conferência independente (calamine × núcleo):")
for ano, g in amostra.groupby("ano"):
    arq = cat[(cat.ano == ano) & (cat.conjunto == "anexo_ii")].iloc[0]
    wb = CalamineWorkbook.from_path(str(XLSX_TMP / str(ano) / arq.arquivo))
    data = wb.get_sheet_by_name(arq.aba).to_python(skip_empty_area=False)
    for r in g.itertuples():
        aba, cel = r.origem.split("!")
        letra, lin = "".join(ch for ch in cel if ch.isalpha()), int("".join(ch for ch in cel if ch.isdigit()))
        orig = data[lin - 1][col2n(letra) - 1]
        igual = float(orig) == float(r.valor)
        ok6 += igual
        p(f"   {ano} {arq.arquivo} › {r.origem}: planilha={orig!r} núcleo={r.valor} ({r.indicador}, geo {r.id_geo}, cine {r.co_cine}) → {'OK' if igual else 'DIFERENTE'}")
        if not igual:
            div.append({"teste": "T6", "ano": ano, "detalhe": f"{r.origem} planilha={orig} núcleo={r.valor}"})
p(f"T6: {ok6}/{len(amostra)} iguais")

QUALIDADE.mkdir(parents=True, exist_ok=True)
pd.DataFrame(div, columns=["teste", "ano", "detalhe"]).to_csv(QUALIDADE / "p1_divergencias.csv", index=False, encoding="utf-8-sig")
t5.to_csv(QUALIDADE / "p1_t5_anexo_ii_x_7_2.csv", index=False, encoding="utf-8-sig")
(QUALIDADE / "p1_validacao.txt").write_text("\n".join(out), encoding="utf-8")
con.close()
