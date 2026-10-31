"""Etapa 4: comparacao estrutural entre anos (05_comparacao_estrutural.xlsx) e tabelas-base para os .md.

Uso: python -I s4_compare.py <work_dir> <dir_saida>
"""
import re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd

work, out = Path(sys.argv[1]), Path(sys.argv[2])
S = pd.read_pickle(work / "S.pkl")
C = pd.read_pickle(work / "C.pkl")
cats = pd.read_pickle(work / "cats.pkl")
UNIVERSO = {"presenciais", "presencial", "distancia", "sequenciais", "graduacao", "comunitarias", "confessionais",
            "exercicio", "ingressantes", "matriculas", "concluintes", "vagas", "inscritos", "cursos", "docentes", "instituicoes"}


def strip_acc(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def norm_title(t):
    t = strip_acc(t).casefold()
    t = re.sub(r"\b(19|20)\d{2}\b", "", t)
    t = re.sub(r"[^\w]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


S["titulo_norm"] = S.titulo_tabela.map(norm_title)
S["universo_norm"] = S.subtitulo_universo.map(norm_title)
data = S[S.tipo_aba == "tabela_dados"].copy()
years = sorted(S.ano.unique())

# ------------------------------------------------ abas x anos
tab_rows = []
for key, g in S.groupby("chave_tabela"):
    row = {"conjunto": g.conjunto.iloc[0], "chave_tabela": key}
    for y in years:
        r = g[g.ano == y]
        row[str(y)] = repr(r.aba.iloc[0]) if len(r) else "—"
    names = {a for a in g.aba}
    pres = sorted(g.ano.unique())
    obs = []
    if len(names) > 1:
        obs.append("nome da aba varia: " + " / ".join(repr(n) for n in sorted(names)))
    if len(pres) < len(years):
        obs.append("ausente em: " + ", ".join(str(y) for y in years if y not in pres))
    row["anos_presentes"] = len(pres)
    row["situacao"] = ("presente em todos os anos" if len(pres) == len(years) else
                       f"adicionada em {pres[0]}" if pres[0] > years[0] and pres[-1] == years[-1] else
                       f"removida após {pres[-1]}" if pres[-1] < years[-1] else "intermitente")
    row["observacoes"] = "; ".join(obs)
    tab_rows.append(row)
T1 = pd.DataFrame(tab_rows).sort_values(["conjunto", "chave_tabela"])

# ------------------------------------------------ evolucao por tabela (metadados)
evo = []
for key, g in data.groupby("chave_tabela"):
    g = g.sort_values("ano")
    prev = None
    for _, r in g.iterrows():
        e = {"conjunto": r.conjunto, "chave_tabela": key, "ano": r.ano, "aba": r.aba, "titulo_tabela": r.titulo_tabela,
             "subtitulo_universo": r.subtitulo_universo, "linhas_cabecalho": r.linhas_cabecalho,
             "linha_codigos_variaveis": r.linha_codigos_variaveis, "linha_inicio_dados": r.linha_inicio_dados,
             "n_col_util": r.n_col_util, "colunas_identificadoras": r.colunas_identificadoras,
             "n_registros": r.n_registros, "niveis_geograficos": r.niveis_geograficos, "hash_notas": r.hash_notas}
        if prev is not None:
            ch = []
            if r.aba != prev.aba: ch.append("aba renomeada")
            if r.titulo_norm != prev.titulo_norm: ch.append("título alterado")
            if r.universo_norm != prev.universo_norm: ch.append("subtítulo/universo alterado")
            if r.linhas_cabecalho != prev.linhas_cabecalho: ch.append("posição do cabeçalho alterada")
            if r.linha_inicio_dados != prev.linha_inicio_dados: ch.append("linha de início dos dados alterada")
            if r.n_col_util != prev.n_col_util: ch.append(f"nº de colunas {prev.n_col_util}→{r.n_col_util}")
            if r.colunas_identificadoras != prev.colunas_identificadoras: ch.append("colunas identificadoras alteradas")
            if r.hash_notas != prev.hash_notas: ch.append("notas de rodapé alteradas")
            e["mudancas_vs_ano_anterior"] = "; ".join(ch) or "sem mudança estrutural detectada"
        else:
            e["mudancas_vs_ano_anterior"] = "(primeiro ano disponível)"
        evo.append(e)
        prev = r
T2 = pd.DataFrame(evo)

# ------------------------------------------------ colunas: pares de anos consecutivos
C = C.merge(S[["ano", "arquivo", "aba", "titulo_norm", "universo_norm", "hash_notas"]], on=["ano", "arquivo", "aba"], how="left")
C["leaf"] = C.rotulo_normalizado.fillna("").map(lambda s: s.split(" > ")[-1] if s else "")
C["is_anexo"] = C.conjunto != "Sinopse por município"
C["chave_col"] = C.apply(lambda r: r.codigo_variavel if (r.is_anexo and r.codigo_variavel) else r.rotulo_normalizado, axis=1)
# desambigua chaves repetidas dentro da mesma aba
C["ocorr"] = C.groupby(["ano", "arquivo", "aba", "chave_col"]).cumcount()
C["chave_col_u"] = C.chave_col + C.ocorr.map(lambda i: f" #{i + 1}" if i else "")

pairs = []
for key, g in C.groupby("chave_tabela"):
    ys = sorted(g.ano.unique())
    for y0, y1 in zip(ys, ys[1:]):
        a, b = g[g.ano == y0], g[g.ano == y1]
        ta, tb = a.titulo_norm.iloc[0], b.titulo_norm.iloc[0]
        ua, ub = a.universo_norm.iloc[0], b.universo_norm.iloc[0]
        wa, wb = set(ta.split()) | set(ua.split()), set(tb.split()) | set(ub.split())
        univ_change = bool((wa ^ wb) & UNIVERSO)
        title_change = (ta != tb) or (ua != ub)
        notes_change = a.hash_notas.iloc[0] != b.hash_notas.iloc[0]
        ia = {k: r for k, r in zip(a.chave_col_u, a.itertuples())}
        used = set()
        leaf_a = defaultdict(list)
        for r in a.itertuples():
            leaf_a[(r.papel, r.leaf, r.nivel_1 if not r.is_anexo else "")].append(r)
        for r in b.itertuples():
            m = ia.get(r.chave_col_u)
            how = "chave exata (" + ("código da variável" if r.is_anexo and r.codigo_variavel else "rótulo hierárquico completo") + ")"
            if m is None:
                cands = [x for x in leaf_a.get((r.papel, r.leaf, r.nivel_1 if not r.is_anexo else ""), []) if x.chave_col_u not in used]
                if len(cands) == 1:
                    m = cands[0]
                    how = "rótulo final igual, caminho diferente"
            ev = []
            if m is None:
                cls = "Correspondência não identificada"
                ev.append(f"coluna presente em {y1} sem correspondente em {y0}")
            else:
                used.add(m.chave_col_u)
                same_path = m.rotulo_normalizado == r.rotulo_normalizado
                same_code = (m.codigo_variavel or "") == (r.codigo_variavel or "")
                same_pos = m.coluna == r.coluna
                if not same_path: ev.append("rótulo hierárquico difere")
                if r.is_anexo and not same_code: ev.append(f"código {m.codigo_variavel}→{r.codigo_variavel}")
                if not same_pos: ev.append(f"posição {m.coluna}→{r.coluna}")
                if title_change: ev.append("título/subtítulo da tabela difere")
                if notes_change: ev.append("notas de rodapé diferem")
                if m.tipo_dado != r.tipo_dado: ev.append(f"tipo {m.tipo_dado}→{r.tipo_dado}")
                if univ_change:
                    cls = "Não comparável"
                    ev.append("universo da tabela mudou: " + ", ".join(sorted((wa ^ wb) & UNIVERSO)))
                elif how.startswith("rótulo final"):
                    cls = "Equivalência parcial"
                elif r.is_anexo and r.codigo_variavel and same_code and not same_path:
                    cls = "Equivalência parcial"
                elif same_path and same_code and same_pos and not title_change and not notes_change:
                    cls = "Equivalência confirmada"
                elif same_path and same_code:
                    cls = "Equivalência provável"
                else:
                    cls = "Equivalência parcial"
            pairs.append({"conjunto": r.conjunto, "chave_tabela": key, "ano_anterior": y0, "ano": y1,
                          "coluna_ano_anterior": m.coluna if m is not None else "", "coluna_ano": r.coluna,
                          "codigo_ano_anterior": (m.codigo_variavel if m is not None else ""), "codigo_ano": r.codigo_variavel,
                          "rotulo_ano_anterior": m.rotulo_completo if m is not None else "", "rotulo_ano": r.rotulo_completo,
                          "papel": r.papel, "criterio_pareamento": how if m is not None else "", "classificacao": cls,
                          "evidencias": "; ".join(ev)})
        for r in a.itertuples():
            if r.chave_col_u not in used:
                pairs.append({"conjunto": r.conjunto, "chave_tabela": key, "ano_anterior": y0, "ano": y1,
                              "coluna_ano_anterior": r.coluna, "coluna_ano": "", "codigo_ano_anterior": r.codigo_variavel,
                              "codigo_ano": "", "rotulo_ano_anterior": r.rotulo_completo, "rotulo_ano": "", "papel": r.papel,
                              "criterio_pareamento": "", "classificacao": "Correspondência não identificada",
                              "evidencias": f"coluna presente em {y0} sem correspondente em {y1} (removida ou renomeada)"})
PR = pd.DataFrame(pairs)
RES = PR.pivot_table(index=["conjunto", "chave_tabela", "ano_anterior", "ano"], columns="classificacao",
                     values="papel", aggfunc="count", fill_value=0).reset_index()

# ------------------------------------------------ categorias dos cabecalhos
hc = []
for key, g in C[C.papel != "identificador"].groupby("chave_tabela"):
    for lvl in range(1, 7):
        col = f"nivel_{lvl}"
        sets = {y: set(x for x in gg[col].fillna("") if x) for y, gg in g.groupby("ano")}
        allv = sorted(set().union(*sets.values())) if sets else []
        if not allv:
            continue
        for v in allv:
            pres = [y for y in sets if v in sets[y]]
            hc.append({"conjunto": g.conjunto.iloc[0], "chave_tabela": key, "nivel_cabecalho": lvl, "categoria": v,
                       "anos": ",".join(map(str, pres)), "n_anos": len(pres),
                       "situacao": "todos os anos da tabela" if len(pres) == len(sets) else "variável entre anos"})
HC = pd.DataFrame(hc)

# ------------------------------------------------ categorias das colunas identificadoras (linhas)
cats["rotulo_n"] = cats.rotulo_coluna.map(lambda s: strip_acc(s).casefold().strip())
rc = []
for (conj, key, rot), g in cats.groupby(["conjunto", "chave_tabela", "rotulo_n"]):
    sets = {y: set(gg.valor) for y, gg in g.groupby("ano")}
    ys = sorted(sets)
    if rot.startswith("codigo do municipio") or rot.startswith("municipio"):
        for y in ys:
            rc.append({"conjunto": conj, "chave_tabela": key, "coluna_identificadora": g.rotulo_coluna.iloc[0], "ano": y,
                       "n_valores_distintos": len(sets[y]), "adicionados_vs_ano_anterior": "", "removidos_vs_ano_anterior": "",
                       "n_adicionados": len(sets[y] - sets[ys[ys.index(y) - 1]]) if ys.index(y) else "",
                       "n_removidos": len(sets[ys[ys.index(y) - 1]] - sets[y]) if ys.index(y) else ""})
        continue
    for i, y in enumerate(ys):
        add = sorted(sets[y] - sets[ys[i - 1]]) if i else []
        rem = sorted(sets[ys[i - 1]] - sets[y]) if i else []
        rc.append({"conjunto": conj, "chave_tabela": key, "coluna_identificadora": g.rotulo_coluna.iloc[0], "ano": y,
                   "n_valores_distintos": len(sets[y]),
                   "adicionados_vs_ano_anterior": " | ".join(add[:60]) + (" …" if len(add) > 60 else ""),
                   "removidos_vs_ano_anterior": " | ".join(rem[:60]) + (" …" if len(rem) > 60 else ""),
                   "n_adicionados": len(add) if i else "", "n_removidos": len(rem) if i else ""})
RC = pd.DataFrame(rc)

legend = pd.DataFrame([
    ("Equivalência confirmada", "Mesma chave (código da variável nos Anexos; rótulo hierárquico completo na Sinopse por município), mesmo rótulo, mesma posição, mesmo título e subtítulo da tabela (sem o ano) e mesmas notas de rodapé. É uma confirmação ESTRUTURAL: a confirmação semântica depende das notas técnicas do Censo."),
    ("Equivalência provável", "Mesma chave e mesmo rótulo, mas mudou a posição, o título da tabela ou as notas de rodapé."),
    ("Equivalência parcial", "Pareadas pelo rótulo final com caminho hierárquico diferente, ou mesmo código com rótulo diferente. Pode haver desagregação, agregação ou mudança de categoria."),
    ("Não comparável", "A tabela mudou de universo entre os anos (palavras como presenciais, a distância, sequenciais, comunitárias etc. entraram ou saíram do título ou subtítulo)."),
    ("Correspondência não identificada", "A coluna existe em apenas um dos dois anos do par (incluída, removida ou renomeada de forma não rastreável)."),
], columns=["classificacao", "criterio"])

with pd.ExcelWriter(out / "05_comparacao_estrutural.xlsx") as w:
    legend.to_excel(w, sheet_name="legenda", index=False)
    T1.to_excel(w, sheet_name="abas_x_anos", index=False)
    T2.to_excel(w, sheet_name="evolucao_tabelas", index=False)
    RES.to_excel(w, sheet_name="resumo_pareamento", index=False)
    PR.to_excel(w, sheet_name="pareamento_colunas", index=False)
    HC.to_excel(w, sheet_name="categorias_cabecalho", index=False)
    RC.to_excel(w, sheet_name="categorias_linhas", index=False)

for n, df in [("T1", T1), ("T2", T2), ("PR", PR), ("RES", RES), ("HC", HC), ("RC", RC)]:
    df.to_pickle(work / f"{n}.pkl")
print("05 ok", len(PR), "pares")
