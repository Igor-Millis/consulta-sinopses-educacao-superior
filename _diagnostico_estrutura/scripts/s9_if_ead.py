"""Padrao EaD dos Institutos Federais (IF) em Mato Grosso, 2017-2024. Somente leitura.

1) Sinopse 7.3 (EaD): linha "Total Mato Grosso", todas as colunas de IF.
2) Anexo III (EaD): colunas de total do IF (Vagas, Inscritos, Ingressantes, Matriculas, Concluintes)
   - linhas municipio x curso (com UF);
   - linhas pseudo-regiao "Distancia" (nacionais, por curso).
Grava <work>/if_ead_anexo.pkl e <work>/if_ead_73.pkl.

Uso: python -I s9_if_ead.py <work>
"""
import re, sys, zipfile
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
from lxml import etree

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
IND = {"Número de Cursos": "cursos", "Vagas Oferecidas": "vagas", "Candidatos Inscritos": "inscritos",
       "Ingressantes": "ingressantes", "Matrículas": "matriculas", "Concluintes": "concluintes"}


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def stream(f, sheet_name, keep):
    with zipfile.ZipFile(f) as z:
        wb = z.read("xl/workbook.xml").decode("utf8")
        rels = z.read("xl/_rels/workbook.xml.rels").decode("utf8")
        rel = {re.search(r'Id="([^"]+)"', t).group(1): re.search(r'Target="([^"]+)"', t).group(1)
               for t in re.findall(r"<Relationship\b[^>]*>", rels)}
        part = None
        for t in re.findall(r"<sheet\b[^>]*/>", wb):
            if re.search(r'name="([^"]*)"', t).group(1) == sheet_name:
                part = rel[re.search(r'r:id="([^"]*)"', t).group(1)].lstrip("/")
                part = part if part.startswith("xl/") else "xl/" + part
        ss = []
        with z.open("xl/sharedStrings.xml") as fs:
            for _, el in etree.iterparse(fs, tag=NS + "si"):
                ss.append("".join(t.text or "" for t in el.iter(NS + "t"))); el.clear()
        with z.open(part) as fx:
            for _, el in etree.iterparse(fx, tag=NS + "row"):
                d = {}
                for c in el.iter(NS + "c"):
                    n = col2n(re.match(r"[A-Z]+", c.get("r")).group(0))
                    if n in keep:
                        v = c.find(NS + "v")
                        if v is not None:
                            d[n] = ss[int(v.text)] if c.get("t") == "s" else v.text
                r = int(el.get("r"))
                el.clear()
                while el.getprevious() is not None:
                    del el.getparent()[0]
                yield r, d


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def anexo3(args):
    work, y = args
    C = pd.read_pickle(Path(work) / "C.pkl")
    f = next((Path(work) / "xlsx" / str(y)).glob("anexo_III_tab_8_3*.xlsx"))
    cc = C[(C.ano == y) & (C.arquivo == f.name)]
    ids = {code: int(n) for code, n in zip(cc.codigo_variavel, cc.n_coluna)
           if code in ("NO_REGIAO", "NO_UF", "CO_UF", "NO_MUNICIPIO", "CO_MUNICIPIO", "NO_CINE_ROTULO")}
    m = cc[(cc.papel == "medida") & cc.nivel_2.isin(IND) & cc.nivel_3.fillna("").str.startswith("Instituto Federal")
           & (cc.nivel_4.fillna("").str.strip() == "Total")]
    want = {int(n): IND[i] for n, i in zip(m.n_coluna, m.nivel_2)}
    inv = {v: k for k, v in ids.items()}
    out = []
    for r, d in stream(f, cc.aba.iloc[0], set(want) | set(inv)):
        reg = (d.get(ids["NO_REGIAO"]) or "").strip()
        mun = (d.get(ids["CO_MUNICIPIO"]) or "").strip()
        tipo = "municipio" if re.fullmatch(r"\d{7}", mun) else ("Distância" if reg == "Distância" else None)
        if not tipo:
            continue
        rec = {"ano": y, "linha": r, "tipo": tipo, **{inv[k]: (d.get(k) or "").strip() for k in inv}}
        rec.update({name: fnum(d.get(n)) for n, name in want.items()})
        out.append(rec)
    return out


def sin73(work, y):
    C = pd.read_pickle(Path(work) / "C.pkl")
    f = Path(work) / "xlsx" / str(y) / f"Sinopse_Educação_Superior_Municipio_{y}.xlsx"
    cc = C[(C.ano == y) & (C.aba == "7.3") & (C.papel == "medida") & C.rotulo_completo.str.contains("Instituto Federal")]
    want = {int(n): rot.split(" > ", 1)[-1] for n, rot in zip(cc.n_coluna, cc.rotulo_completo)}
    out = []
    for r, d in stream(f, "7.3", set(want) | {1, 2, 3, 4, 5}):
        ids = [(d.get(k) or "").strip() for k in (1, 2, 3, 4, 5)]
        if any(v == "Total Mato Grosso" for v in ids) or ids[0] == "Total Brasil":
            rec = {"ano": y, "linha": r, "recorte": "MT" if "Total Mato Grosso" in ids else "Brasil"}
            rec.update({lab: fnum(d.get(n)) for n, lab in want.items()})
            out.append(rec)
    return out


if __name__ == "__main__":
    work = sys.argv[1]
    s73 = [r for y in range(2017, 2025) for r in sin73(work, y)]
    pd.DataFrame(s73).to_pickle(Path(work) / "if_ead_73.pkl")
    print("7.3 ok", len(s73), flush=True)
    with Pool(8) as p:
        res = p.map(anexo3, [(work, y) for y in range(2017, 2025)])
    df = pd.DataFrame([r for part in res for r in part])
    df.to_pickle(Path(work) / "if_ead_anexo.pkl")
    print("Anexo III ok", len(df), flush=True)
