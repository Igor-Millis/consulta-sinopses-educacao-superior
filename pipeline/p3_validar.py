"""Validação da P3 (Sinopse por município no núcleo). Somente leitura.

T1  Completude: valores = linhas × colunas mapeadas, por tabela e ano; linhas não classificadas.
T2  Totais internos (só indicadores aditivos): "Total" de cada dimensão = soma das categorias; "Pública" =
    Federal + Estadual + Municipal; "Seleção para Vagas Novas" = Vestibular + Enem + Avaliação Seriada + Seleção Simplificada.
    Resultado POR TABELA E DIMENSÃO: falhas podem indicar categorias que não se somam (um aluno em mais de um
    programa/financiamento) e são relatadas, não "corrigidas".
T3  Geografia (só aditivos): Σ municípios da UF = linha da UF; Σ UFs da região = linha da região;
    Σ regiões + Exterior = Brasil. Por tabela.
T5  Coerência com os Anexos (já validados): 7.2 × Anexo II e 7.3 × Anexo III (Brasil, total geral);
    5.1/6.1/4.2 (Brasil, Graduação, total) × Anexo II + III.
T6  16 valores (2 por ano, incluindo municípios do ES) relidos do XML original por varredura de texto.

Uso: python -I p3_validar.py
"""
import re, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import NUCLEO, QUALIDADE, STAGING, XLSX_TMP, abas, strings_compartilhadas

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300); pd.set_option("display.max_colwidth", 80)
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
con.execute("SET memory_limit = '3GB'")  # modo leve (a rodada com 6 GB foi interrompida por falta de memória)
con.execute("SET threads = 4")
con.execute("SET preserve_insertion_order = false")
DIMS = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
        "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
        "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
ADIT = "indicador IN (SELECT indicador FROM dim_indicador WHERE aditivo)"
ANOS = range(2017, 2025)
div, out = [], []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


# ---------------------------------------------------------------- T1
t1 = con.execute("""SELECT ano, tabela, count(*) AS valores, count(DISTINCT linha) AS linhas FROM fato_sinopse GROUP BY 1, 2""").df()
xw = pd.read_csv(Path(__file__).resolve().parent.parent / "config" / "xw_colunas_sinopse.csv", encoding="utf-8-sig",
                 keep_default_na=False, dtype={"tabela": str})
ncol = xw.groupby(["ano", "tabela"]).size().rename("colunas").reset_index()
t1 = t1.merge(ncol, on=["ano", "tabela"], how="outer")
ok = (t1.valores == t1.linhas * t1.colunas)
nc = con.execute("SELECT count(*) FROM linhas_nao_classificadas_sinopse").fetchone()[0]
p(f"T1 completude: {len(t1)} tabelas×anos | {'OK' if ok.all() else f'FALHA em {(~ok).sum()}'} | valores: {t1.valores.sum():,} | linhas não classificadas: {nc}")
if nc:
    p(con.execute("SELECT tabela, count(*) n, any_value(conteudo) exemplo FROM linhas_nao_classificadas_sinopse GROUP BY 1 ORDER BY 2 DESC").df().head(20).to_string(index=False))
p(con.execute("SELECT status_valor, count(*) n FROM fato_sinopse GROUP BY 1 ORDER BY 2 DESC").df().to_string(index=False))

# ---------------------------------------------------------------- T2
from regras_t2 import pares_totais  # mesma regra usada por q10_detectar.py
P, NAO_EXCL = pares_totais(con)
con.register("v_ne", pd.DataFrame(sorted(NAO_EXCL), columns=["dim", "tabela"]))
con.register("pares", P)
res2 = []
TABS = [t for (t,) in con.execute("SELECT DISTINCT tabela FROM fato_sinopse ORDER BY 1").fetchall()]
for ano, tab in [(a, t) for a in ANOS for t in TABS]:  # modo leve: um ano × uma tabela por vez
    df = con.execute(f"""
      WITH f AS (SELECT tabela, id_geo, nivel_academico, indicador, id_recorte, valor FROM fato_sinopse
                 WHERE ano = {ano} AND tabela = '{tab}' AND {ADIT} AND valor IS NOT NULL),
      -- cada categoria-filha conta uma vez (variantes equivalentes, como IF > Total e IF > Federal, colapsam no máximo)
      s0 AS (SELECT pr.dim, pr.pai_val, f.tabela, f.id_geo, f.nivel_academico, f.indicador, pr.pai, pr.filho_val, max(f.valor) v
             FROM f JOIN pares pr ON pr.filho = f.id_recorte GROUP BY ALL),
      s1 AS (SELECT dim, pai_val, tabela, id_geo, nivel_academico, indicador, pai, sum(v) soma, count(*) nfilhos FROM s0 GROUP BY ALL),
      -- só compara quando o conjunto de categorias-filhas está completo naquela tabela (o maior conjunto observado
      -- para a mesma dimensão); ex.: na 4.2 a forma de ingresso não é aberta no total de cada organização acadêmica
      s AS (SELECT * FROM (SELECT *, max(nfilhos) OVER (PARTITION BY dim, pai_val, tabela) AS nesperado FROM s1)
            WHERE nfilhos = nesperado),
      c AS (SELECT s.*, pa.valor AS valor_pai,
                   EXISTS (SELECT 1 FROM v_ne ne WHERE ne.dim = s.dim AND ne.tabela = s.tabela) AS nao_exclusiva
            FROM s JOIN f pa ON pa.tabela = s.tabela AND pa.id_geo = s.id_geo
            AND pa.nivel_academico = s.nivel_academico AND pa.indicador = s.indicador AND pa.id_recorte = s.pai)
      SELECT {ano} AS ano, tabela, dim, bool_or(nao_exclusiva) AS nao_exclusiva, count(*) AS comparacoes,
             count(*) FILTER (WHERE (NOT nao_exclusiva AND soma <> valor_pai) OR (nao_exclusiva AND soma < valor_pai)) AS falhas,
             count(*) FILTER (WHERE soma > valor_pai) AS soma_maior, count(*) FILTER (WHERE soma < valor_pai) AS soma_menor
      FROM c GROUP BY ALL""").df()
    res2.append(df)
R2 = pd.concat(res2)
tot2 = R2.groupby(["tabela", "dim", "nao_exclusiva"])[["comparacoes", "falhas", "soma_maior", "soma_menor"]].sum().reset_index()
ex = R2[~R2.nao_exclusiva]; ne = R2[R2.nao_exclusiva]
p(f"T2 totais internos — categorias exclusivas: {ex.comparacoes.sum():,} comparações (Total = Σ categorias) | falhas: {ex.falhas.sum():,} "
  f"({100 * ex.falhas.sum() / max(ex.comparacoes.sum(), 1):.3f}%)")
p(f"T2 totais internos — categorias NÃO exclusivas (notas oficiais): {ne.comparacoes.sum():,} comparações (Σ categorias ≥ Total) | "
  f"falhas: {ne.falhas.sum():,} | casos em que Σ > Total (esperado): {ne.soma_maior.sum():,}")
p("   tabela × dimensão com falhas:")
p(tot2[tot2.falhas > 0].sort_values("falhas", ascending=False).head(40).to_string(index=False))
R2.to_csv(QUALIDADE / "p3_t2_por_tabela.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- T3
res3 = []
for ano in ANOS:
    df = con.execute(f"""
      WITH f AS (SELECT fs.tabela, fs.id_geo, fs.nivel_geo, fs.nivel_academico, fs.indicador, fs.id_recorte, fs.valor, fs.status_valor,
                        g.co_uf, g.no_regiao FROM fato_sinopse fs LEFT JOIN dim_geografia g USING (id_geo)
                 WHERE fs.ano = {ano} AND fs.indicador IN (SELECT indicador FROM dim_indicador WHERE aditivo)),
      k AS (SELECT tabela, nivel_academico, indicador, id_recorte FROM f),
      mun AS (SELECT tabela, nivel_academico, indicador, id_recorte, 'UF-' || co_uf AS alvo, sum(valor) s FROM f WHERE nivel_geo = 'Município' GROUP BY ALL),
      uf AS (SELECT tabela, nivel_academico, indicador, id_recorte, 'REG-' || no_regiao AS alvo, sum(valor) s FROM f WHERE nivel_geo = 'UF' GROUP BY ALL),
      -- "somente_presencial" (3.1/4.1 abaixo do Brasil) não pode somar ao Brasil (presencial + EaD): fica fora desta comparação
      reg AS (SELECT tabela, nivel_academico, indicador, id_recorte, 'BR' AS alvo, sum(valor) s FROM f
              WHERE nivel_geo IN ('Região', 'Exterior') AND status_valor <> 'somente_presencial' GROUP BY ALL),
      cmp AS (
        SELECT 'municípios → UF' AS nivel, x.*, f.valor FROM mun x JOIN f ON f.id_geo = x.alvo AND f.tabela = x.tabela
               AND f.nivel_academico = x.nivel_academico AND f.indicador = x.indicador AND f.id_recorte = x.id_recorte
        UNION ALL
        SELECT 'UFs → região', x.*, f.valor FROM uf x JOIN f ON f.id_geo = x.alvo AND f.tabela = x.tabela
               AND f.nivel_academico = x.nivel_academico AND f.indicador = x.indicador AND f.id_recorte = x.id_recorte
        UNION ALL
        SELECT 'regiões + Exterior → Brasil', x.*, f.valor FROM reg x JOIN f ON f.id_geo = x.alvo AND f.tabela = x.tabela
               AND f.nivel_academico = x.nivel_academico AND f.indicador = x.indicador AND f.id_recorte = x.id_recorte)
      -- só compara quando há números dos dois lados (linhas "não desagregado" não têm valor: não é falha)
      SELECT {ano} AS ano, tabela, nivel, count(*) AS comparacoes,
             count(*) FILTER (WHERE s <> valor) AS falhas FROM cmp WHERE s IS NOT NULL AND valor IS NOT NULL GROUP BY ALL""").df()
    res3.append(df)
R3 = pd.concat(res3)
p(f"T3 geografia: {R3.comparacoes.sum():,} comparações | falhas: {R3.falhas.sum():,}")
t3 = R3.groupby(["tabela", "nivel"])[["comparacoes", "falhas"]].sum().reset_index()
p(t3[t3.falhas > 0].sort_values("falhas", ascending=False).head(30).to_string(index=False))
f3a = R3[R3.falhas > 0].groupby(["ano", "tabela"]).falhas.sum()
p("   falhas por ano e tabela (até 30):", f3a.head(30).to_dict())
R3.to_csv(QUALIDADE / "p3_t3_por_tabela.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- T5
TOT = " AND ".join(f"{d} IN ('Total', 'Não se aplica')" for d in DIMS)
idt = con.execute("""SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
                     AND dependencia='Total' AND categoria_privada='Total'""").fetchone()[0]
t5 = con.execute(f"""
  WITH s AS (SELECT ano, tabela, nivel_academico, indicador, valor FROM fato_sinopse
             WHERE id_geo = 'BR' AND id_recorte IN (SELECT id_recorte FROM dim_recorte_sinopse WHERE {TOT})),
       a AS (SELECT ano, anexo, indicador, valor FROM fato_anexo_curso
             WHERE id_geo = 'BR' AND co_cine = '_TOTAL' AND id_recorte = {idt}),
       ii AS (SELECT ano, indicador, valor FROM a WHERE anexo = 'anexo_ii'),
       iii AS (SELECT ano, indicador, valor FROM a WHERE anexo = 'anexo_iii'),
       soma AS (SELECT ano, indicador, sum(valor) valor FROM a GROUP BY ALL)
  SELECT '7.2 × Anexo II' AS teste, s.ano, s.indicador, s.valor AS sinopse, ii.valor AS anexo FROM s JOIN ii USING (ano, indicador)
   WHERE s.tabela = '7.2' AND s.nivel_academico = 'Total'
  UNION ALL
  SELECT '7.3 × Anexo III', s.ano, s.indicador, s.valor, iii.valor FROM s JOIN iii USING (ano, indicador)
   WHERE s.tabela = '7.3' AND s.nivel_academico = 'Total'
  UNION ALL
  SELECT s.tabela || ' (Graduação) × Anexo II + III', s.ano, s.indicador, s.valor, soma.valor FROM s JOIN soma USING (ano, indicador)
   WHERE s.tabela IN ('5.1', '6.1', '4.2') AND s.nivel_academico = 'Graduação'
  ORDER BY 1, 2, 3""").df()
b5 = t5[t5.sinopse != t5.anexo]
p(f"T5 Sinopse × Anexos: {len(t5)} comparações | {'OK' if b5.empty else f'FALHA em {len(b5)}'}")
p("   por teste:", t5.groupby("teste").size().to_dict())
if not b5.empty:
    p(b5.to_string(index=False))
t5.to_csv(QUALIDADE / "p3_t5_sinopse_x_anexos.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- T6
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
am = con.execute("""SELECT ano, tabela, aba, linha, coluna, valor, indicador, id_geo FROM (
    SELECT *, row_number() OVER (PARTITION BY ano, id_geo LIKE '32%' ORDER BY hash(aba || coluna || linha || '20261030')) rn
    FROM fato_sinopse WHERE valor > 0 AND nivel_geo = 'Município') WHERE rn = 1 ORDER BY ano""").df()
CEL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', re.S)
ok6 = 0
p("T6 conferência independente (varredura do XML original × núcleo):")
for ano, g in am.groupby("ano"):
    arq = cat[(cat.ano == ano) & (cat.conjunto == "sinopse")].iloc[0].arquivo
    with zipfile.ZipFile(XLSX_TMP / str(ano) / arq) as z:
        ss = strings_compartilhadas(z)
        partes = {nm: pt for nm, pt, _ in abas(z)}
        for r in g.itertuples():
            with z.open(partes[r.aba]) as f:
                txt = f.read().decode("utf8", "ignore")
            i = txt.find(f'<row r="{r.linha}"'); j = txt.find("</row>", i)
            orig = None
            for m in CEL.finditer(txt[i:j]):
                if m.group(1) == r.coluna:
                    vm = re.search(r"<v>(.*?)</v>", m.group(4) or "")
                    orig = vm.group(1) if vm else None
                    if orig is not None and 't="s"' in m.group(3):
                        orig = ss[int(orig)]
            igual = orig is not None and float(orig) == float(r.valor)
            ok6 += igual
            p(f"   {ano} › {r.aba}!{r.coluna}{r.linha}: XML={orig!r} núcleo={r.valor} ({r.indicador}, geo {r.id_geo}) → {'OK' if igual else 'DIFERENTE'}")
p(f"T6: {ok6}/{len(am)} iguais")

(QUALIDADE / "p3_validacao.txt").write_text("\n".join(out), encoding="utf-8")
con.close()
