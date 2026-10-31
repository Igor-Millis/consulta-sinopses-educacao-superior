"""Etapa 2/3: perfil estrutural de cada aba, lendo o XML da planilha em streaming (lxml.iterparse).

Somente le as copias extraidas; grava um JSON por aba em <work>/profiles/.

Uso: python -I s2_profile.py <work_dir> [n_proc] [filtro_substring]
"""
import json, re, sys, zipfile, time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
from lxml import etree

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
N_ID = 8            # colunas iniciais tratadas como candidatas a identificadores
CAP_DISTINCT = 300  # valores distintos guardados por coluna (nao identificadora)
CAP_ID = 30000      # valores distintos guardados por coluna identificadora
NUM_RE = re.compile(r"^[+-]?(\d+([.,]\d+)?|\d{1,3}(\.\d{3})+(,\d+)?)([eE][+-]?\d+)?$")


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


REF_RE = re.compile(r"([A-Z]+)(\d+)")


def classify(t, v):
    """Classe do valor bruto. Nao converte vazio em zero."""
    if v is None:
        return "sem_valor"
    if v == "":
        return "texto_vazio"
    if v.strip() == "":
        return "so_espacos"
    s = v.strip()
    if NUM_RE.match(s):
        neg = s.startswith("-")
        dec = ("." in s or "," in s or "e" in s.lower())
        base = "num_dec" if dec else "num_int"
        if neg:
            base += "_neg"
        return base + ("" if t in (None, "n") else "_como_texto")
    if s in {"-", "--", "X", "x", "...", "..", "N/A", "NA", "n/a", "*", "**", "***", "(*)", "—", "–", "s/d", "nd", "ND"}:
        return "codigo_especial"
    if len(s) <= 3 and not s.isalnum():
        return "codigo_especial"
    return "texto"


def load_shared(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    out = []
    with z.open("xl/sharedStrings.xml") as f:
        for _, el in etree.iterparse(f, tag=NS + "si"):
            out.append("".join(t.text or "" for t in el.iter(NS + "t")))
            el.clear()
            while el.getprevious() is not None:
                del el.getparent()[0]
    return out


def profile_sheet(z, shared, sheet_name, part, meta):
    t0 = time.time()
    header_rows = {}          # linha -> {col: valor} (linhas antes dos dados)
    tail = []                 # ultimas linhas nao vazias
    notes = []                # linhas de texto longo apos o inicio dos dados
    merges = []
    hidden_rows = 0
    hidden_cols = []
    col_class = {}            # col -> Counter(classe)
    col_distinct = {}         # col -> Counter(valor) (cap)
    col_overflow = set()
    col_max = {}
    col_min = {}
    sig_count = Counter()
    sig_example = {}
    examples = []
    data_start = None
    last_data_row = None
    max_row = max_col = 0
    n_rows_xml = 0
    cache = {}
    first_rows_dump_limit = 400  # abas pequenas (capa, sumario): guarda tudo ate aqui

    with z.open(part) as f:
        for ev, el in etree.iterparse(f, events=("end",), tag=(NS + "row", NS + "mergeCell", NS + "col")):
            tag = el.tag[len(NS):]
            if tag == "mergeCell":
                merges.append(el.get("ref"))
                el.clear()
                continue
            if tag == "col":
                if el.get("hidden") in ("1", "true"):
                    hidden_cols.append(f'{n2col(int(el.get("min")))}:{n2col(int(el.get("max")))}')
                continue
            n_rows_xml += 1
            r = int(el.get("r"))
            if el.get("hidden") in ("1", "true"):
                hidden_rows += 1
            cells = {}
            for c in el.iter(NS + "c"):
                ref = c.get("r")
                t = c.get("t")
                if t == "inlineStr":
                    v = "".join(x.text or "" for x in c.iter(NS + "t"))
                else:
                    ve = c.find(NS + "v")
                    v = None if ve is None else ve.text
                    if t == "s" and v is not None:
                        v = shared[int(v)]
                if v is None:
                    continue
                cells[col2n(REF_RE.match(ref).group(1))] = (t, v)
            el.clear()
            while el.getprevious() is not None:
                del el.getparent()[0]
            if not cells:
                continue
            nonblank = {k: tv for k, tv in cells.items() if tv[1].strip() != ""}
            if nonblank:
                max_row = r
                max_col = max(max_col, max(nonblank))
                tail.append((r, {n2col(k): tv[1] for k, tv in nonblank.items()}))
                if len(tail) > 40:
                    tail.pop(0)
            a = cells.get(1, (None, ""))[1].strip()
            if data_start is None:
                if r > 4 and (a.startswith("Total Brasil") or a == "Brasil" or a == "Total"):
                    data_start = r
                else:
                    if nonblank and r <= first_rows_dump_limit:
                        header_rows[r] = {n2col(k): tv[1] for k, tv in cells.items()}
                    continue
            # ---- linhas de dados ----
            n_num = 0
            for k, (t, v) in cells.items():
                key = (t, v)
                cl = cache.get(key)
                if cl is None:
                    cl = classify(t, v)
                    if len(cache) < 2_000_000:
                        cache[key] = cl
                cc = col_class.get(k)
                if cc is None:
                    cc = col_class[k] = Counter()
                    col_distinct[k] = Counter()
                cc[cl] += 1
                if cl.startswith("num"):
                    n_num += 1
                    try:
                        x = float(v.replace(",", ".")) if "," in v and "." not in v else float(v)
                        if k not in col_max or x > col_max[k]:
                            col_max[k] = x
                        if k not in col_min or x < col_min[k]:
                            col_min[k] = x
                    except ValueError:
                        pass
                    if k > N_ID:
                        continue
                cap = CAP_ID if k <= N_ID else CAP_DISTINCT
                d = col_distinct[k]
                if v in d or len(d) < cap:
                    d[v] += 1
                else:
                    col_overflow.add(k)
            if n_num:
                last_data_row = r
            else:
                txt = " ".join(tv[1] for tv in nonblank.values())
                if len(txt) > 40 or re.match(r"^(Fonte|Nota|Obs|\(?\d+\)?\s*[-–.])", a):
                    if len(notes) < 200:
                        notes.append((r, {n2col(k): tv[1] for k, tv in nonblank.items()}))
            sig = []
            for k in range(1, N_ID + 1):
                v = cells.get(k, (None, ""))[1].strip()
                sig.append("" if v == "" else ("T" if v.lower().startswith("total") else "v"))
            sig = "".join(s or "." for s in sig)
            sig_count[sig] += 1
            if sig not in sig_example:
                sig_example[sig] = (r, {n2col(k): cells[k][1] for k in sorted(cells) if k <= N_ID + 2})
            if len(examples) < 3 or (len(examples) < 5 and sig not in {e[2] for e in examples}):
                examples.append((r, {n2col(k): tv[1] for k, tv in sorted(cells.items())}, sig))

    cols = {}
    for k in sorted(col_class):
        cols[n2col(k)] = {
            "classes": dict(col_class[k]),
            "distintos": dict(col_distinct[k].most_common(60 if k > N_ID else CAP_ID)),
            "n_distintos_guardados": len(col_distinct[k]),
            "distintos_truncado": k in col_overflow,
            "min": col_min.get(k), "max": col_max.get(k),
        }
    return {
        **meta, "aba": sheet_name, "xml_part": part,
        "linhas_xml": n_rows_xml, "max_linha_util": max_row, "max_col_util": n2col(max_col) if max_col else None,
        "linha_inicio_dados": data_start, "ultima_linha_com_numero": last_data_row,
        "cabecalho": {str(k): v for k, v in header_rows.items()},
        "mesclagens": merges, "linhas_ocultas": hidden_rows, "colunas_ocultas": hidden_cols,
        "colunas": cols, "assinaturas_linha": dict(sig_count),
        "assinatura_exemplo": {k: v for k, v in sig_example.items()},
        "exemplos": examples, "notas": notes, "cauda": tail,
        "segundos": round(time.time() - t0, 1),
    }


def job(args):
    work, entry, sheets = args
    out_dir = Path(work) / "profiles"
    res = []
    with zipfile.ZipFile(entry["copia"]) as z:
        shared = load_shared(z)
        for s in sheets:
            safe = re.sub(r"[^\w.-]+", "_", s["sheet"].strip()) or "aba"
            fn = out_dir / f'{entry["ano"]}__{Path(entry["arquivo"]).stem}__{safe}.json'
            if fn.exists():
                continue
            meta = {"ano": entry["ano"], "arquivo": entry["arquivo"], "conjunto": entry["conjunto"],
                    "estado_aba": s["state"], "dimensao_declarada": s["dimension"]}
            try:
                p = profile_sheet(z, shared, s["sheet"], s["xml_part"], meta)
            except Exception as e:  # registra a falha em vez de descartar a aba
                p = {**meta, "aba": s["sheet"], "erro": repr(e)}
            fn.write_text(json.dumps(p, ensure_ascii=False), encoding="utf8")
            res.append(f'{entry["ano"]} {entry["arquivo"]} {s["sheet"]} {p.get("segundos")}s')
    return res


if __name__ == "__main__":
    work = sys.argv[1]
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    filt = sys.argv[3] if len(sys.argv) > 3 else ""
    (Path(work) / "profiles").mkdir(exist_ok=True)
    inv = json.load(open(Path(work) / "inventario_bruto.json", encoding="utf8"))
    jobs = []
    for e in inv:
        if filt not in e["arquivo"] + str(e["ano"]):
            continue
        if e["n_abas"] == 1:
            jobs.append((work, e, e["abas"], e["abas"][0]["xml_size"]))
        else:
            jobs.append((work, e, e["abas"], sum(s["xml_size"] for s in e["abas"])))
    jobs.sort(key=lambda j: -j[3])
    with Pool(nproc) as pool:
        for res in pool.imap_unordered(job, [j[:3] for j in jobs]):
            for line in res:
                print(line, flush=True)
