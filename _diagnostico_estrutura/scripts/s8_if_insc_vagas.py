"""Investiga inscritos == vagas nos Institutos Federais (IF), Anexo II (presencial), 2017-2024. Somente leitura.

Extrai, por linha municipio x curso, as colunas de total do IF (Federal) para Vagas, Inscritos, Ingressantes e
Matriculas, identificadas pelo catalogo de colunas (C.pkl). Grava <work>/if_linhas.pkl.

Uso: python -I s8_if_insc_vagas.py <work>
"""
import re, sys, zipfile
from multiprocessing import Pool
from pathlib import Path
import pandas as pd
from lxml import etree

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
IND = {"Vagas Oferecidas": "vagas", "Candidatos Inscritos": "inscritos", "Ingressantes": "ingressantes", "Matrículas": "matriculas"}


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def one_year(args):
    work, y = args
    C = pd.read_pickle(Path(work) / "C.pkl")
    f = next((Path(work) / "xlsx" / str(y)).glob("anexo_II_tab_8_2*.xlsx"))
    cc = C[(C.ano == y) & (C.arquivo == f.name)]
    ids = {code: int(n) for code, n in zip(cc.codigo_variavel, cc.n_coluna)
           if code in ("NO_UF", "CO_UF", "NO_MUNICIPIO", "CO_MUNICIPIO", "NO_CINE_ROTULO", "CO_CINE_ROTULO")}
    # coluna de total do IF de cada indicador: caminho "<indicador> > Instituto Federal ... > Total"
    m = cc[(cc.papel == "medida") & cc.nivel_2.isin(IND) & cc.nivel_3.fillna("").str.startswith("Instituto Federal")
           & (cc.nivel_4.fillna("").str.strip() == "Total")]
    want = {int(n): (IND[ind], code) for n, ind, code in zip(m.n_coluna, m.nivel_2, m.codigo_variavel)}
    assert len(want) == 4, (y, want)
    inv = {v: k for k, v in ids.items()}
    keep = set(want) | set(inv)
    with zipfile.ZipFile(f) as z:
        ss = []
        with z.open("xl/sharedStrings.xml") as fs:
            for _, el in etree.iterparse(fs, tag=NS + "si"):
                ss.append("".join(t.text or "" for t in el.iter(NS + "t"))); el.clear()
        part = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet")][0]
        out = []
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
                mun = (d.get(ids["CO_MUNICIPIO"]) or "").strip()
                if not re.fullmatch(r"\d{7}", mun):
                    continue  # so linhas municipio x curso
                rec = {"ano": y, "linha": r, **{inv[k]: (d.get(k) or "").strip() for k in inv}}
                for n, (name, code) in want.items():
                    try:
                        rec[name] = float(d.get(n))
                    except (TypeError, ValueError):
                        rec[name] = None
                    rec["cod_" + name] = code
                out.append(rec)
    return out


if __name__ == "__main__":
    work = sys.argv[1]
    with Pool(8) as p:
        res = p.map(one_year, [(work, y) for y in range(2017, 2025)])
    df = pd.DataFrame([r for part in res for r in part])
    df.to_pickle(Path(work) / "if_linhas.pkl")
    print("linhas municipio x curso:", len(df))
