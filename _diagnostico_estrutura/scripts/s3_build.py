"""Etapa 4/5: consolida os perfis JSON em catalogos (xlsx) e numa base intermediaria para os relatorios .md.

Uso: python -I s3_build.py <work_dir> <dir_saida>
"""
import json, re, sys, hashlib, unicodedata
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

work, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
inv = json.load(open(work / "inventario_bruto.json", encoding="utf8"))
profiles = [json.load(open(p, encoding="utf8")) for p in sorted((work / "profiles").glob("*.json"))]
CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def n2col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def norm(s):
    """Normalizacao so para comparar: espacos, caixa, acentos e marcadores de nota colados ao final."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # so digitos colados a letra/parentese (chamada de nota); "De 25 a 29" nao e afetado
    s = re.sub(r"(?<=[a-zA-Z\)])\d{1,2}(\s?[-–,]\s?\d{1,2})*$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip().casefold()


def table_key(conjunto, aba):
    if conjunto != "Sinopse por município":
        return conjunto
    a = aba.strip()
    m = re.match(r"^(\d+(\.\d+)?)\b", a)
    if m and "." in m.group(1):
        return "Tab " + m.group(1)
    m2 = re.match(r"^(\d+)\s+(.*)$", a)
    if m2:  # capas de secao: "7 Dados Gerais" e "Dados Gerais" sao tratadas juntas
        return "Seção " + norm(m2.group(2))
    if norm(a) in ("dados gerais", "dados gerais por curso"):
        return "Seção " + norm(a)
    return "Aux " + a


def sheet_type(p):
    a = p["aba"].strip()
    if p.get("erro"):
        return "erro_leitura"
    if p.get("linha_inicio_dados"):
        return "tabela_dados"
    if a in ("Sinopse_Estatística", "Resumo", "Equipe Técnica", "Como Citar"):
        return "auxiliar_documentacao"
    if a == "Sumário":
        return "auxiliar_sumario"
    if a.startswith("8.1 a 8.3"):
        return "auxiliar_remissiva_anexos"
    if not p.get("max_linha_util"):
        return "vazia"
    return "capa_secao" if table_key(p["conjunto"], a).startswith("Seção") else "outra_sem_dados_revisar"


# ---------------------------------------------------------------- cabecalhos hierarquicos
def parse_range(ref):
    m = re.match(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$", ref)
    c1, r1 = col2n(m.group(1)), int(m.group(2))
    c2, r2 = (col2n(m.group(3)), int(m.group(4))) if m.group(3) else (c1, r1)
    return r1, c1, r2, c2


def resolve_headers(p):
    """Retorna (linhas_titulo, linhas_cabecalho, linha_codigos, colunas{n: {...}})."""
    hdr = {int(r): {col2n(c): v for c, v in cells.items()} for r, cells in p["cabecalho"].items()}
    ds = p["linha_inicio_dados"]
    rows = sorted(r for r in hdr if r < ds)
    title_rows, header_rows = [], []
    started = False
    for r in rows:
        nb = [c for c, v in hdr[r].items() if v.strip()]
        if not started and len(nb) <= 1 and set(hdr[r]) <= {1}:
            title_rows.append(r)
        else:
            started = True
            header_rows.append(r)
    code_row = None
    for r in header_rows:
        vals = [v.strip() for v in hdr[r].values() if v.strip()]
        if len(vals) >= 5 and sum(bool(CODE_RE.match(v)) for v in vals) / len(vals) > 0.8:
            code_row = r
    label_rows = [r for r in header_rows if r != code_row]
    maxc = col2n(p["max_col_util"]) if p.get("max_col_util") else max((max(h) for h in hdr.values() if h), default=1)
    merges = [parse_range(m) for m in p["mesclagens"]]
    cols = {c: {"niveis": [], "fontes": []} for c in range(1, maxc + 1)}
    parent = {c: (1, maxc) for c in range(1, maxc + 1)}
    for r in label_rows:
        lab, span, src, origin = {}, {}, {}, {}
        for (r1, c1, r2, c2) in merges:
            if r1 <= r <= r2:
                v = hdr.get(r1, {}).get(c1, "")
                for c in range(c1, min(c2, maxc) + 1):
                    lab[c] = v
                    span[c] = (c1, c2)
                    src[c] = "mesclagem" if r == r1 else "mesclagem(continuação vertical)"
                    origin[c] = f"{n2col(c1)}{r1}"
        starts = sorted(c for c, v in hdr.get(r, {}).items() if c not in lab and c <= maxc and v != "")
        for i, c in enumerate(starts):
            ps, pe = parent[c]
            nxt = [s for s in starts[i + 1:] if s <= pe]
            end = min((nxt[0] - 1) if nxt else pe, pe)
            # nao propaga sobre colunas ja cobertas por mesclagem
            e = c
            while e + 1 <= end and (e + 1) not in lab:
                e += 1
            for k in range(c, e + 1):
                lab[k] = hdr[r][c]
                span[k] = (c, e)
                src[k] = "célula" if k == c else "propagado"
                origin[k] = f"{n2col(c)}{r}"
        # legenda mesclada (>= 2 colunas) que cobre so parte do grupo: estende sobre vizinhas sem rotulo no mesmo pai.
        # So no 1o nivel (legenda geral). Em niveis inferiores uma lacuna pode ser mesclagem desalinhada na origem
        # (ex.: 4.1 de 2017-2021, "Candidatos Inscritos" comeca em AB8 e nao em AA8): fica vazio e vai para revisao.
        for c in (range(2, maxc + 1) if r == label_rows[0] else ()):
            vazio = c not in lab or (lab[c] == "" and src[c].startswith("mesclagem"))  # inclui mesclagem vazia contigua
            if vazio and (c - 1) in lab and lab[c - 1] != "" and parent[c] == parent[c - 1] \
                    and src[c - 1] in ("mesclagem", "mesclagem(continuação vertical)", "propagado(legenda mesclada)") \
                    and (span[c - 1][1] - span[c - 1][0] >= 1):
                lab[c], src[c], origin[c], span[c] = lab[c - 1], "propagado(legenda mesclada)", origin[c - 1], span[c - 1]
        ext = {}
        for c, o in origin.items():
            lo, hi = ext.get(o, (c, c))
            ext[o] = (min(lo, c), max(hi, c))
        for c in span:
            span[c] = (min(span[c][0], ext[origin[c]][0]), max(span[c][1], ext[origin[c]][1]))
        for c in range(1, maxc + 1):
            if c in lab:
                v = lab[c]
                txt = v.strip()
                cols[c]["niveis"].append((r, txt, src[c], v != "" and txt == "", origin[c]))
                parent[c] = span[c]
    codes = {}
    if code_row:
        codes = {c: v.strip() for c, v in hdr[code_row].items()}
    for c in cols:
        # lacuna: linha sem rotulo entre linhas com rotulo -> nivel vazio explicito (∅)
        got = {x[0] for x in cols[c]["niveis"]}
        if got:
            for r in label_rows:
                if min(got) < r < max(got) and r not in got:
                    cols[c]["niveis"].append((r, "", "lacuna (sem rótulo nesta linha)", False, f"{n2col(c)}{r}"))
            cols[c]["niveis"].sort(key=lambda x: x[0])
        lv = []
        last_cell = None
        for (r, txt, src, blank, cell) in cols[c]["niveis"]:
            if src.startswith("mesclagem(continuação") and cell == last_cell:
                continue
            last_cell = cell
            lv.append({"linha": r, "rotulo": txt, "fonte": src, "so_espacos": blank, "celula": cell})
        cols[c]["niveis"] = lv
        cols[c]["codigo"] = codes.get(c, "")
    return title_rows, label_rows, code_row, cols


# ---------------------------------------------------------------- consolidacao por aba
sheets, columns, notes_rows, examples_rows, levels_rows, specials_rows, cats = [], [], [], [], [], [], []
title_cells = {}
for p in profiles:
    key = table_key(p["conjunto"], p["aba"])
    st = sheet_type(p)
    base = {"ano": p["ano"], "conjunto": p["conjunto"], "arquivo": p["arquivo"], "aba": p["aba"], "chave_tabela": key}
    hdr = p.get("cabecalho", {})
    rec = {**base, "tipo_aba": st, "estado_aba": p.get("estado_aba"),
           "dimensao_declarada": p.get("dimensao_declarada"),
           "max_linha_util": p.get("max_linha_util"), "max_col_util": p.get("max_col_util"),
           "n_col_util": col2n(p["max_col_util"]) if p.get("max_col_util") else 0,
           "linhas_xml": p.get("linhas_xml"), "linhas_ocultas": p.get("linhas_ocultas"),
           "colunas_ocultas": ", ".join(p.get("colunas_ocultas", [])),
           "n_mesclagens": len(p.get("mesclagens", [])), "erro": p.get("erro", "")}
    if st != "tabela_dados":
        txt = []
        for r, cells in sorted(hdr.items(), key=lambda x: int(x[0])):
            for c, v in cells.items():
                if v.strip():
                    txt.append(f"{c}{r}: {v.strip()}")
        rec["conteudo_texto"] = " ¦ ".join(txt)[:30000]
        rec["revisao_manual"] = "sim — conteúdo textual/auxiliar; conferir visualmente" if st != "vazia" else ""
        sheets.append(rec)
        continue

    title_rows, label_rows, code_row, cols = resolve_headers(p)
    hdrn = {int(r): cells for r, cells in hdr.items()}
    tit = [(f"A{r}", hdrn[r].get("A", "").strip()) for r in title_rows]
    rec["titulos"] = " ¦ ".join(f"{c}: {v}" for c, v in tit)
    title_cells[(p["ano"], p["arquivo"], p["aba"])] = tit
    titulo_tabela = next((v for c, v in reversed(tit) if re.match(r"^\d", v)), tit[-1][1] if tit else "")
    rec["titulo_tabela"] = titulo_tabela
    rec["subtitulo_universo"] = tit[-2][1] if len(tit) >= 2 else ""
    rec["tema_secao"] = tit[1][1] if len(tit) >= 3 else ""
    rec["celula_titulo"] = next((c for c, v in reversed(tit) if v == titulo_tabela), "")
    rec["linhas_cabecalho"] = f"{label_rows[0]}–{label_rows[-1]}" if label_rows else ""
    rec["n_niveis_cabecalho"] = len(label_rows)
    rec["linha_codigos_variaveis"] = code_row or ""
    rec["linha_inicio_dados"] = p["linha_inicio_dados"]
    rec["ultima_linha_com_numero"] = p["ultima_linha_com_numero"]

    # colunas identificadoras: a esquerda da primeira coluna cujo caminho contem "Total"
    first_total = None
    for c in sorted(cols):
        if any(l["rotulo"].strip().lower() == "total" or l["rotulo"].lower().startswith("total ") for l in cols[c]["niveis"]):
            first_total = c
            break
    if first_total is None:
        first_total = 1
        for c in sorted(cols):
            cl = p["colunas"].get(n2col(c), {}).get("classes", {})
            if sum(v for k, v in cl.items() if k.startswith("num")) > sum(cl.values()) * 0.5 and c > 1:
                first_total = c
                break
    id_cols = list(range(1, first_total))
    rec["colunas_identificadoras"] = ", ".join(
        f"{n2col(c)}={(cols[c]['niveis'][0]['rotulo'] if cols[c]['niveis'] else '?')}" + (f" [{cols[c]['codigo']}]" if cols[c]["codigo"] else "")
        for c in id_cols)
    rec["n_colunas_medida"] = rec["n_col_util"] - len(id_cols)

    # notas (rodape)
    nts = p.get("notas", [])
    rec["n_linhas_nota"] = len(nts)
    rec["fonte"] = " ".join(v for r, cells in nts for c, v in cells.items() if v.strip().lower().startswith("fonte"))
    rec["notas_texto"] = " ¦ ".join(f"A{r}: " + " ".join(v.strip() for v in cells.values()) for r, cells in nts)
    rec["hash_notas"] = hashlib.md5(norm(" ".join(" ".join(c.values()) for _, c in nts)).encode()).hexdigest()[:10]
    for r, cells in nts:
        for c, v in cells.items():
            notes_rows.append({**base, "celula": f"{c}{r}", "texto": v.strip()})

    # niveis de agregacao
    sigs = p.get("assinaturas_linha", {})
    n_block = sum(sigs.values())
    n_note_rows = sum(1 for r, _ in nts)
    rec["linhas_bloco_dados"] = n_block
    rec["n_registros"] = n_block - n_note_rows
    colA = p["colunas"].get("A", {}).get("distintos", {})
    lev = Counter()
    lev["Brasil (A='Total Brasil')"] = colA.get("Total Brasil", 0)
    lev["Região (A='Total <região>')"] = sum(v for k, v in colA.items() if k.strip().startswith("Total ") and k.strip() != "Total Brasil")
    # UF: a coluna B contem "Total <UF>"
    colB = p["colunas"].get("B", {}).get("distintos", {})
    lev["UF (B='Total <UF>')"] = sum(v for k, v in colB.items() if k.strip().lower().startswith("total"))
    # municipio: coluna identificadora cujo rotulo comeca com "Código do Município"
    mun_code_col = next((c for c in id_cols if cols[c]["niveis"] and norm(cols[c]["niveis"][0]["rotulo"]).startswith("codigo do municipio")), None)
    if mun_code_col:
        cl = p["colunas"].get(n2col(mun_code_col), {}).get("classes", {})
        lev["Município (código preenchido)"] = sum(v for k, v in cl.items() if k.startswith("num"))
    rec["niveis_geograficos"] = "; ".join(f"{k}: {v}" for k, v in lev.items() if v)
    for k, v in lev.items():
        levels_rows.append({**base, "nivel": k, "n_linhas": v, "metodo": "contagem de valores nas colunas identificadoras"})
    for s, n in sigs.items():
        ex = p.get("assinatura_exemplo", {}).get(s)
        levels_rows.append({**base, "nivel": f"assinatura {s}", "n_linhas": n,
                            "metodo": "padrão de preenchimento A..H (T=começa com 'Total', v=valor, .=vazio)",
                            "exemplo_linha": ex[0] if ex else "", "exemplo": json.dumps(ex[1], ensure_ascii=False) if ex else ""})
    has_mun = bool(mun_code_col)
    has_course = any(cols[c]["niveis"] and "curso" in norm(" ".join(l["rotulo"] for l in cols[c]["niveis"])) for c in id_cols)
    extra = [cols[c]["niveis"][0]["rotulo"] for c in id_cols if cols[c]["niveis"]
             and not re.search(r"regiao|unidade da federacao|codigo da uf|municipio|curso", norm(cols[c]["niveis"][0]["rotulo"]))]
    uo = "linha agregada por " + ("município" if has_mun else "área geográfica (Brasil/Região/UF)")
    if has_course:
        uo += " × curso (rótulo Cine)"
    if extra:
        uo += " × " + " × ".join(extra)
    rec["unidade_observacao_linha"] = uo
    rec["nivel_geografico"] = "Brasil, Região, UF" + (", Município" if has_mun else "") + " (totais e detalhe na mesma aba)"
    tt = norm(titulo_tabela)
    m = re.search(r"(numero|media|percentual|taxa|proporcao|idade)[^,]*?de ([a-z ]+?)(,| por| em| nos| nas| segundo|$)", tt)
    rec["indicador_titulo"] = m.group(0).rstrip(", ") if m else ""
    rec["unidade_medida_presumida"] = ("contagem (número absoluto)" if tt.split(" - ", 1)[-1].startswith("numero") or "numero de" in tt
                                        else "verificar — título não indica contagem")
    flags = []
    if any(l["so_espacos"] for c in cols for l in cols[c]["niveis"]):
        flags.append("rótulos de cabeçalho preenchidos só com espaços")
    if not label_rows:
        flags.append("cabeçalho não localizado")
    if rec["n_col_util"] and p.get("dimensao_declarada") and not p["dimensao_declarada"].endswith(str(p.get("max_linha_util"))):
        flags.append("dimensão declarada difere da área útil")
    if p["ultima_linha_com_numero"] and p["max_linha_util"] and p["max_linha_util"] - p["ultima_linha_com_numero"] > 40:
        flags.append("muitas linhas não numéricas após os dados")
    rec["alertas"] = "; ".join(flags)
    rec["revisao_manual"] = "sim" if (not label_rows or "verificar" in rec["unidade_medida_presumida"]) else ""

    # exemplos
    for (r, cells, sig) in p.get("exemplos", [])[:5]:
        ids = {c: v for c, v in cells.items() if col2n(c) <= max(id_cols or [0])}
        meas = [(c, v) for c, v in cells.items() if col2n(c) > max(id_cols or [0])][:12]
        examples_rows.append({**base, "linha": r, "celula_inicial": f"A{r}", "assinatura": sig,
                              "identificadores": json.dumps(ids, ensure_ascii=False),
                              "primeiras_medidas": "; ".join(f"{c}={v}" for c, v in meas),
                              "n_celulas_na_linha": len(cells)})

    # colunas
    tot_rows = rec["n_registros"]
    for c in sorted(cols):
        L = n2col(c)
        prof = p["colunas"].get(L, {"classes": {}, "distintos": {}, "min": None, "max": None, "distintos_truncado": False})
        cl = prof["classes"]
        nums = sum(v for k, v in cl.items() if k.startswith("num"))
        txt = cl.get("texto", 0)
        present = sum(cl.values())
        lv = cols[c]["niveis"]
        path = " > ".join(l["rotulo"] if l["rotulo"] else "∅" for l in lv)
        is_id = c in id_cols
        if is_id:
            role = "identificador"
        elif present == 0:
            role = "sem dados"
        else:
            role = "medida"
        if nums and nums >= 0.95 * (present - cl.get("texto_vazio", 0) - cl.get("so_espacos", 0)):
            tipo = "numérico" + (" (gravado como texto)" if any(k.endswith("_como_texto") for k in cl) else "")
            if is_id:
                tipo = "código numérico"
        elif txt and txt >= 0.5 * present:
            nd = prof.get("n_distintos_guardados", 0)
            tipo = "categórico" if (nd <= 50 and not prof.get("distintos_truncado")) else "textual/alta cardinalidade"
        elif present == 0:
            tipo = "vazio"
        else:
            tipo = "misto"
        specials = {k: v for k, v in prof["distintos"].items() if (not is_id) and k.strip() and not re.match(r"^[+-]?\d[\d.,]*$", k.strip())}
        for k, v in specials.items():
            specials_rows.append({**base, "coluna": L, "valor": k, "ocorrencias": v})
        columns.append({
            **base, "coluna": L, "n_coluna": c, "papel": role,
            "codigo_variavel": cols[c]["codigo"],
            "celula_codigo": f"{L}{code_row}" if code_row and cols[c]["codigo"] else "",
            **{f"nivel_{i + 1}": (lv[i]["rotulo"] if i < len(lv) else "") for i in range(6)},
            **{f"celula_nivel_{i + 1}": (lv[i]["celula"] if i < len(lv) else "") for i in range(6)},
            "metodo_rotulo": ", ".join(sorted({l["fonte"] for l in lv})),
            "rotulo_so_espacos": "sim" if any(l["so_espacos"] for l in lv) else "",
            "rotulo_completo": path, "rotulo_normalizado": " > ".join(norm(l["rotulo"]) for l in lv),
            "coluna_agregada_total": "sim" if any(norm(l["rotulo"]) == "total" or norm(l["rotulo"]).startswith("total ") for l in lv) else "",
            "tipo_dado": tipo, "n_registros_aba": tot_rows, "celulas_presentes": present,
            "celulas_inexistentes": max(tot_rows - present, 0) if not is_id else max(rec["linhas_bloco_dados"] - present, 0),
            "texto_vazio": cl.get("texto_vazio", 0), "so_espacos": cl.get("so_espacos", 0),
            "numericos": nums, "numericos_gravados_como_texto": sum(v for k, v in cl.items() if k.endswith("_como_texto")),
            "negativos": sum(v for k, v in cl.items() if "_neg" in k), "decimais": sum(v for k, v in cl.items() if k.startswith("num_dec")),
            "textos": txt, "codigos_especiais": cl.get("codigo_especial", 0),
            "min": prof.get("min"), "max": prof.get("max"),
            "valores_nao_numericos_exemplo": "; ".join(f"{k!r}×{v}" for k, v in list(specials.items())[:8]),
            "n_distintos_guardados": prof.get("n_distintos_guardados", 0) if (is_id or not nums) else "",
            "distintos_truncado": "sim" if prof.get("distintos_truncado") else "",
            "alerta_rotulo": ("coluna sem nenhum dado — provável área formatada fora da tabela; rótulo herdado não é confiável" if role == "sem dados"
                              else "nível do cabeçalho sem rótulo (∅) — possível mesclagem desalinhada na origem; revisar manualmente" if "∅" in path
                              else ""),
        })
        if is_id:
            for v, n in prof["distintos"].items():
                cats.append({**base, "coluna": L, "rotulo_coluna": lv[0]["rotulo"] if lv else "", "valor": v, "ocorrencias": n})
    n_alert = sum(1 for x in columns if (x["ano"], x["arquivo"], x["aba"]) == (p["ano"], p["arquivo"], p["aba"]) and x["alerta_rotulo"])
    if n_alert:
        rec["alertas"] = "; ".join(filter(None, [rec["alertas"], f"{n_alert} coluna(s) com alerta de rótulo (ver 03)"]))
        rec["revisao_manual"] = "sim"
    sheets.append(rec)

S = pd.DataFrame(sheets)
C = pd.DataFrame(columns)
S.to_pickle(work / "S.pkl"); C.to_pickle(work / "C.pkl")
pd.DataFrame(cats).to_pickle(work / "cats.pkl")
pd.DataFrame(notes_rows).to_pickle(work / "notes.pkl")

# ---------------------------------------------------------------- 01 inventario
wb_rows, ab_rows = [], []
for e in inv:
    sub = S[(S.ano == e["ano"]) & (S.arquivo == e["arquivo"])]
    aux = sub[sub.tipo_aba != "tabela_dados"]
    wb_rows.append({"ano": e["ano"], "conjunto": e["conjunto"], "arquivo_zip": e["zip"], "caminho_no_zip": e["caminho_no_zip"],
                    "arquivo": e["arquivo"], "tamanho_bytes": e["tamanho_bytes"], "tamanho_MB": round(e["tamanho_bytes"] / 2**20, 1),
                    "tamanho_compactado_bytes": e["tamanho_compactado_bytes"], "n_abas": e["n_abas"],
                    "n_abas_dados": int((sub.tipo_aba == "tabela_dados").sum()), "n_abas_auxiliares_ou_vazias": len(aux),
                    "abas": " | ".join(repr(s["sheet"]) for s in e["abas"]),
                    "abas_auxiliares_ou_vazias": " | ".join(f"{a!r} ({t})" for a, t in zip(aux.aba, aux.tipo_aba)),
                    "partes_ooxml_extra": ", ".join(x for x in e["partes"] if any(k in x for k in ("drawing", "media", "chart", "comments", "externalLink", "vbaProject", "pivot", "table")))})
    for i, s in enumerate(e["abas"], 1):
        r = sub[sub.aba == s["sheet"]]
        r = r.iloc[0] if len(r) else {}
        dim = s["dimension"] or ""
        m = re.match(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?", dim)
        ab_rows.append({"ano": e["ano"], "conjunto": e["conjunto"], "arquivo": e["arquivo"], "ordem": i, "aba": s["sheet"],
                        "aba_repr": repr(s["sheet"]), "estado": s["state"], "dimensao_declarada": dim,
                        "linhas_declaradas": int(m.group(4) or m.group(2)) if m else None,
                        "colunas_declaradas": col2n(m.group(3) or m.group(1)) if m else None,
                        "max_linha_util": r.get("max_linha_util"), "max_col_util": r.get("max_col_util"),
                        "n_col_util": r.get("n_col_util"), "tipo_aba": r.get("tipo_aba"), "parte_xml": s["xml_part"],
                        "tamanho_xml_bytes": s["xml_size"]})
with pd.ExcelWriter(out / "01_inventario_workbooks.xlsx") as w:
    pd.DataFrame(wb_rows).to_excel(w, sheet_name="workbooks", index=False)
    pd.DataFrame(ab_rows).to_excel(w, sheet_name="abas", index=False)

# ---------------------------------------------------------------- 02 catalogo de abas
cols02 = ["ano", "conjunto", "arquivo", "aba", "chave_tabela", "tipo_aba", "estado_aba", "tema_secao", "subtitulo_universo",
          "titulo_tabela", "celula_titulo", "titulos", "linhas_cabecalho", "n_niveis_cabecalho", "linha_codigos_variaveis",
          "linha_inicio_dados", "ultima_linha_com_numero", "max_linha_util", "max_col_util", "dimensao_declarada", "n_col_util",
          "colunas_identificadoras", "n_colunas_medida", "n_registros", "linhas_bloco_dados", "unidade_observacao_linha",
          "nivel_geografico", "niveis_geograficos", "indicador_titulo", "unidade_medida_presumida", "fonte", "n_linhas_nota",
          "notas_texto", "hash_notas", "n_mesclagens", "linhas_ocultas", "colunas_ocultas", "alertas", "revisao_manual",
          "conteudo_texto", "erro"]
with pd.ExcelWriter(out / "02_catalogo_abas.xlsx") as w:
    S.reindex(columns=cols02).sort_values(["conjunto", "chave_tabela", "ano"]).to_excel(w, sheet_name="abas", index=False)
    pd.DataFrame(notes_rows).to_excel(w, sheet_name="notas_rodape", index=False)

# ---------------------------------------------------------------- 03 catalogo de colunas
c03 = ["ano", "conjunto", "arquivo", "aba", "chave_tabela", "coluna", "n_coluna", "papel", "codigo_variavel", "celula_codigo"] + \
      [f"nivel_{i}" for i in range(1, 7)] + [f"celula_nivel_{i}" for i in range(1, 7)] + \
      ["rotulo_completo", "metodo_rotulo", "rotulo_so_espacos", "coluna_agregada_total", "tipo_dado", "alerta_rotulo"]
with pd.ExcelWriter(out / "03_catalogo_colunas.xlsx") as w:
    C[c03].to_excel(w, sheet_name="colunas", index=False)

# ---------------------------------------------------------------- 04 perfil
c04 = ["ano", "conjunto", "arquivo", "aba", "chave_tabela", "coluna", "papel", "rotulo_completo", "tipo_dado", "n_registros_aba",
       "celulas_presentes", "celulas_inexistentes", "texto_vazio", "so_espacos", "numericos", "numericos_gravados_como_texto",
       "negativos", "decimais", "textos", "codigos_especiais", "min", "max", "valores_nao_numericos_exemplo",
       "n_distintos_guardados", "distintos_truncado"]
P = S[S.tipo_aba == "tabela_dados"][["ano", "conjunto", "arquivo", "aba", "chave_tabela", "linha_inicio_dados", "ultima_linha_com_numero",
                                     "n_registros", "linhas_bloco_dados", "n_col_util", "niveis_geograficos", "unidade_observacao_linha"]].copy()
agg = C.groupby(["ano", "arquivo", "aba"]).agg(
    colunas_com_ausencia=("celulas_inexistentes", lambda s: int((s > 0).sum())),
    colunas_texto_vazio=("texto_vazio", lambda s: int((s > 0).sum())),
    colunas_com_codigo_especial=("codigos_especiais", lambda s: int((s > 0).sum())),
    colunas_num_como_texto=("numericos_gravados_como_texto", lambda s: int((s > 0).sum())),
    colunas_com_decimais=("decimais", lambda s: int((s > 0).sum())),
    colunas_com_negativos=("negativos", lambda s: int((s > 0).sum())),
).reset_index()
P = P.merge(agg, on=["ano", "arquivo", "aba"], how="left")
SP = pd.DataFrame(specials_rows)
with pd.ExcelWriter(out / "04_perfil_dados.xlsx") as w:
    P.to_excel(w, sheet_name="resumo_abas", index=False)
    pd.DataFrame(levels_rows).to_excel(w, sheet_name="niveis_agregacao", index=False)
    pd.DataFrame(examples_rows).to_excel(w, sheet_name="exemplos", index=False)
    C[c04].to_excel(w, sheet_name="perfil_colunas", index=False)
    (SP.groupby(["conjunto", "valor"]).agg(ocorrencias=("ocorrencias", "sum"), n_colunas=("coluna", "count"),
                                           anos=("ano", lambda s: ",".join(map(str, sorted(set(s)))))).reset_index()
     if len(SP) else pd.DataFrame()).to_excel(w, sheet_name="valores_nao_numericos", index=False)
print("01-04 ok", len(S), "abas", len(C), "colunas")
