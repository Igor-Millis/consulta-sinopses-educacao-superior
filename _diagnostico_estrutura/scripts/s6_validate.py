"""Validacao dos entregaveis contra os perfis originais + checagens tematicas. Somente leitura.

Uso: python -I s6_validate.py <work> <dir_saida>   -> imprime relatorio e grava <work>/validacao.json
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
work, out = Path(sys.argv[1]), Path(sys.argv[2])
R = {}


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


# ---------------------------------------------------------------- 1. arquivos abrem e tem conteudo
files = ["01_inventario_workbooks.xlsx", "02_catalogo_abas.xlsx", "03_catalogo_colunas.xlsx", "04_perfil_dados.xlsx",
         "05_comparacao_estrutural.xlsx", "06_dicionario_variaveis.md"]
R["arquivos"] = {}
xl = {}
for f in files:
    p = out / f
    if not p.exists():
        R["arquivos"][f] = "AUSENTE"; continue
    if f.endswith(".xlsx"):
        wb = load_workbook(p, read_only=True)
        info = {ws.title: ws.max_row for ws in wb.worksheets}
        wb.close()
        xl[f] = {sh: pd.read_excel(p, sheet_name=sh, engine="openpyxl") for sh in info}
        R["arquivos"][f] = {"bytes": p.stat().st_size, "abas_linhas": {k: len(v) for k, v in xl[f].items()}}
    else:
        R["arquivos"][f] = {"bytes": p.stat().st_size, "linhas": len(p.read_text(encoding="utf8").splitlines())}

# ---------------------------------------------------------------- 2. coerencia com perfis
profiles = {}
for p in (work / "profiles").glob("*.json"):
    d = json.load(open(p, encoding="utf8"))
    profiles[(d["ano"], d["arquivo"], d["aba"])] = d
ab = xl["01_inventario_workbooks.xlsx"]["abas"]
wbk = xl["01_inventario_workbooks.xlsx"]["workbooks"]
cat = xl["02_catalogo_abas.xlsx"]["abas"]
cols = xl["03_catalogo_colunas.xlsx"]["colunas"]
perf = xl["04_perfil_dados.xlsx"]["perfil_colunas"]
coer = {}
coer["abas_no_01"] = len(ab); coer["abas_no_02"] = len(cat); coer["perfis"] = len(profiles)
coer["soma_n_abas_workbooks"] = int(wbk.n_abas.sum())
# numero de colunas por aba de dados = max_col_util do perfil
mism_cols, mism_rows, mism_cells = [], [], []
cg = cols.groupby(["ano", "arquivo", "aba"]).size()
for k, d in profiles.items():
    if not d.get("linha_inicio_dados"):
        continue
    n = cg.get(k, 0)
    if n != col2n(d["max_col_util"]):
        mism_cols.append((k, n, d["max_col_util"]))
    r = cat[(cat.ano == k[0]) & (cat.arquivo == k[1]) & (cat.aba == k[2])].iloc[0]
    if r.linhas_bloco_dados != sum(d["assinaturas_linha"].values()):
        mism_rows.append(k)
# celulas presentes no 04 = soma das classes no perfil
pg = perf.set_index(["ano", "arquivo", "aba", "coluna"]).celulas_presentes
for k, d in list(profiles.items()):
    if not d.get("linha_inicio_dados"):
        continue
    for c, v in d["colunas"].items():
        key = (*k, c)
        if key in pg.index and int(pg[key]) != sum(v["classes"].values()):
            mism_cells.append(key)
coer["divergencias_n_colunas"] = mism_cols[:20]
coer["divergencias_linhas_bloco"] = mism_rows[:20]
coer["divergencias_celulas_presentes"] = mism_cells[:20]
coer["n_div_celulas"] = len(mism_cells)
coer["colunas_no_03"] = len(cols); coer["colunas_no_04"] = len(perf)
R["coerencia"] = coer

# ---------------------------------------------------------------- 3. cabecalhos hierarquicos
D = cat[cat.tipo_aba == "tabela_dados"]
h = {}
h["abas_sem_cabecalho"] = D[D.linhas_cabecalho.isna()][["ano", "arquivo", "aba"]].values.tolist()
h["n_niveis_dist"] = D.n_niveis_cabecalho.value_counts().sort_index().to_dict()
med = cols[cols.papel == "medida"]
h["medidas_com_nivel_vazio(∅)"] = int(med.rotulo_completo.fillna("").str.contains("∅").sum())
h["medidas_sem_rotulo"] = int(med.rotulo_completo.isna().sum() + (med.rotulo_completo == "").sum())
h["exemplos_∅"] = med[med.rotulo_completo.fillna("").str.contains("∅")][["ano", "aba", "coluna", "rotulo_completo"]].head(15).values.tolist()
h["metodos"] = Counter(m for s in cols.metodo_rotulo.fillna("") for m in s.split(", ") if m)
h["colunas_rotulo_so_espacos"] = int((cols.rotulo_so_espacos == "sim").sum())
# rotulos duplicados dentro da mesma aba (mesmo caminho completo em mais de uma coluna)
dup = med.groupby(["ano", "arquivo", "aba", "rotulo_completo"]).size()
dup = dup[dup > 1].reset_index()
h["caminhos_duplicados_na_aba"] = len(dup)
h["exemplos_duplicados"] = dup.head(15).values.tolist()
# mesclagens
mg = Counter()
for k, d in profiles.items():
    mg[k[1].split("_")[0] if "anexo" in k[1] else "Sinopse"] += len(d["mesclagens"])
h["mesclagens_por_conjunto"] = dict(mg)
# mesclagens que cruzam a area de dados (deveriam estar so no cabecalho)
cross = []
for k, d in profiles.items():
    ds = d.get("linha_inicio_dados")
    if not ds:
        continue
    for m in d["mesclagens"]:
        mm = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", m)
        if mm and int(mm.group(4)) >= ds and int(mm.group(2)) < (d.get("ultima_linha_com_numero") or 0):
            cross.append((k, m))
h["mesclagens_na_area_de_dados"] = len(cross)
h["exemplos_mesclagens_area_dados"] = [(list(k), m) for k, m in cross[:10]]
R["cabecalhos"] = h

# ---------------------------------------------------------------- 4. codigos CINE
cine = {}
anex = {k: d for k, d in profiles.items() if "anexo" in k[1]}
for k, d in sorted(anex.items()):
    g = d["colunas"].get("G", {}); f = d["colunas"].get("F", {})
    vals = g.get("distintos", {})
    quoted = sum(n for v, n in vals.items() if v.startswith('"') and v.endswith('"'))
    raw = {v.strip('"') for v in vals if v.strip()}
    pat = Counter(("ok" if re.match(r"^\d{4}[A-Z]\d{2}$", v) else "outro:" + v) for v in raw)
    cine[f"{k[0]} {k[1][:9]}"] = {
        "n_codigos_distintos": len(raw), "n_nomes_distintos": len([v for v in f.get("distintos", {}) if v.strip()]),
        "celulas_com_aspas_literais": quoted, "truncado": g.get("distintos_truncado"),
        "fora_do_padrao_4dig+letra+2dig": [p for p in pat if p != "ok"][:10],
        "classes_G": g.get("classes"),
    }
R["cine"] = cine
# relacao nome x codigo: precisa das linhas; usa exemplos de assinatura nao basta -> registra limitacao
# evolucao do conjunto de codigos
sets = defaultdict(dict)
for k, d in anex.items():
    sets[k[1][:9].rstrip("_")][k[0]] = {v.strip('"') for v in d["colunas"].get("G", {}).get("distintos", {}) if v.strip()}
ev = {}
for conj, by in sets.items():
    ys = sorted(by)
    ev[conj] = [{"ano": y, "n": len(by[y]), "novos": len(by[y] - by[ys[i - 1]]) if i else None,
                 "saem": len(by[ys[i - 1]] - by[y]) if i else None} for i, y in enumerate(ys)]
R["cine_evolucao"] = ev

# ---------------------------------------------------------------- 5. tipos de dados
t = {}
t["tipo_dado_medidas"] = med.tipo_dado.value_counts().to_dict()
t["tipo_dado_identificadores"] = cols[cols.papel == "identificador"].tipo_dado.value_counts().to_dict()
pm = perf[perf.papel == "medida"]
t["medidas_com_decimais"] = int((pm.decimais > 0).sum()); t["medidas_com_negativos"] = int((pm.negativos > 0).sum())
t["medidas_com_texto"] = int((pm.textos > 0).sum()); t["medidas_com_codigo_especial"] = int((pm.codigos_especiais > 0).sum())
t["medidas_com_texto_vazio"] = int((pm.texto_vazio > 0).sum()); t["medidas_com_celula_inexistente"] = int((pm.celulas_inexistentes > 0).sum())
t["medidas_num_gravado_texto"] = int((pm.numericos_gravados_como_texto > 0).sum())
t["medidas_num_nativo"] = int(((pm.numericos > 0) & (pm.numericos_gravados_como_texto == 0)).sum())
t["exemplos_medidas_nao_numericas"] = pm[(pm.textos > 0) | (pm.codigos_especiais > 0)][["ano", "aba", "coluna", "valores_nao_numericos_exemplo"]].head(20).values.tolist()
vn = xl["04_perfil_dados.xlsx"]["valores_nao_numericos"]
t["valores_nao_numericos_top"] = (vn.sort_values("ocorrencias", ascending=False).head(25).values.tolist()
                                  if "ocorrencias" in vn else "nenhum valor não numérico em colunas de medida")
# texto vazio vs inexistente por conjunto
t["texto_vazio_por_conjunto"] = pm.groupby("conjunto").texto_vazio.sum().to_dict()
t["inexistentes_por_conjunto"] = pm.groupby("conjunto").celulas_inexistentes.sum().to_dict()
R["tipos"] = t

# ---------------------------------------------------------------- 6. diferencas entre anos
c5 = xl["05_comparacao_estrutural.xlsx"]
pr = c5["pareamento_colunas"]
R["anos"] = {
    "classificacao_geral": pr.classificacao.value_counts().to_dict(),
    "classificacao_por_conjunto": pr.groupby(["conjunto", "classificacao"]).size().unstack(fill_value=0).to_dict(orient="index"),
    "abas_x_anos_situacao": c5["abas_x_anos"].situacao.value_counts().to_dict(),
    "mudancas": Counter(m.split(" ")[0] + " " + m.split(" ")[1] if m.startswith("nº") else m
                        for s in c5["evolucao_tabelas"].mudancas_vs_ano_anterior.fillna("") for m in s.split("; ") if m),
}
(work / "validacao.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf8")
print(json.dumps(R, ensure_ascii=False, indent=1, default=str)[:60000])
