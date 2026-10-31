"""Verifica se vagas/inscritos dos Institutos Federais (IF) em Mato Grosso de 2023 refletem a correcao do IFMT.

Le as copias extraidas em streaming (somente leitura) e compara 2022, 2023 e 2024.
- Sinopse (4.1, 7.2, 7.3): linhas "Total Brasil" e "Total Mato Grosso", colunas IF de Vagas/Inscritos.
- Anexos I e II: soma das linhas municipais com CO_UF = 51 e linha "Total Brasil", colunas IF de Vagas/Inscritos.

Uso: python -I s7_ifmt.py <work>
"""
import re, sys, zipfile
from collections import defaultdict
from pathlib import Path
import pandas as pd
from lxml import etree

sys.stdout.reconfigure(encoding="utf-8")
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
work = Path(sys.argv[1])
C = pd.read_pickle(work / "C.pkl")
YEARS = (2022, 2023, 2024)


def col2n(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def sheet_part(z, name):
    wb = z.read("xl/workbook.xml").decode("utf8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf8")
    rel = {}
    for m in re.finditer(r"<Relationship\b[^>]*>", rels):
        t = m.group(0)
        rel[re.search(r'Id="([^"]+)"', t).group(1)] = re.search(r'Target="([^"]+)"', t).group(1)
    for m in re.finditer(r"<sheet\b[^>]*/>", wb):
        t = m.group(0)
        if re.search(r'name="([^"]*)"', t).group(1) == name:
            tgt = rel[re.search(r'r:id="([^"]*)"', t).group(1)].lstrip("/")
            return tgt if tgt.startswith("xl/") else "xl/" + tgt


def shared(z):
    out = []
    if "xl/sharedStrings.xml" in z.namelist():
        with z.open("xl/sharedStrings.xml") as f:
            for _, el in etree.iterparse(f, tag=NS + "si"):
                out.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
    return out


def rows(xlsx, sheet, want):
    """Gera (linha, {col: valor}) apenas para as colunas em `want` (numeros) + A..E."""
    with zipfile.ZipFile(xlsx) as z:
        ss = shared(z)
        with z.open(sheet_part(z, sheet)) as f:
            for _, el in etree.iterparse(f, tag=NS + "row"):
                d = {}
                for c in el.iter(NS + "c"):
                    n = col2n(re.match(r"[A-Z]+", c.get("r")).group(0))
                    if n <= 7 or n in want:
                        v = c.find(NS + "v")
                        if v is None:
                            continue
                        v = v.text
                        if c.get("t") == "s":
                            v = ss[int(v)]
                        d[n] = v
                yield int(el.get("r")), d
                el.clear()
                while el.getprevious() is not None:
                    del el.getparent()[0]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


res = []
# ------------------------------------------------ Sinopse 4.1 / 7.2 / 7.3
for y in YEARS:
    f = work / "xlsx" / str(y) / f"Sinopse_Educação_Superior_Municipio_{y}.xlsx"
    for aba_key in ("4.1 Vagas e Inscritos", "7.2", "7.3"):
        cc = C[(C.ano == y) & (C.aba == aba_key) & (C.papel == "medida")]
        cc = cc[cc.rotulo_completo.str.contains("Instituto Federal") &
                cc.rotulo_completo.str.contains("Vaga|Inscrit", regex=True)]
        want = {int(n): (col, rot) for n, col, rot in zip(cc.n_coluna, cc.coluna, cc.rotulo_completo)}
        for r, d in rows(f, aba_key, set(want)):
            a, b, cnv = (d.get(1) or "").strip(), (d.get(2) or "").strip(), (d.get(3) or "").strip()
            if a == "Total Brasil" or b == "Total Mato Grosso":
                for n, (col, rot) in want.items():
                    res.append({"fonte": f"Sinopse {aba_key}", "ano": y, "linha": r,
                                "recorte": ("Brasil" if a == "Total Brasil" else "Mato Grosso") + (f" [{cnv}]" if cnv and not cnv.startswith(("Total", "Mato")) else ""),
                                "coluna": col, "rotulo": rot.split(" > ", 1)[-1], "valor": num(d.get(n))})
# ------------------------------------------------ Anexos I e II
for y in YEARS:
    for frag, conj in (("anexo_II_tab_8_2", "Anexo II"), ("anexo_I_tab_8_1", "Anexo I")):
        f = next((work / "xlsx" / str(y)).glob(f"{frag}*.xlsx"))
        aba = "8_2" if (y == 2023 and conj == "Anexo II") else ("8.2" if conj == "Anexo II" else "8.1")
        cc = C[(C.ano == y) & (C.arquivo == f.name)]
        uf_col = int(cc[cc.codigo_variavel == "CO_UF"].n_coluna.iloc[0])
        m = cc[(cc.papel == "medida") & cc.rotulo_completo.str.contains("Instituto Federal") &
               cc.nivel_2.isin(["Vagas Oferecidas", "Candidatos Inscritos"])]
        # so as colunas de total do IF por indicador e por dependencia (sem quebra por grau)
        want = {int(n): (col, code, rot) for n, col, code, rot in zip(m.n_coluna, m.coluna, m.codigo_variavel, m.rotulo_completo)}
        tot = defaultdict(float)
        brasil = {}
        for r, d in rows(f, aba, set(want)):
            a = (d.get(1) or "").strip()
            if a == "Total Brasil" and not brasil and not (d.get(6) or "").strip():
                brasil = {n: num(d.get(n)) for n in want}
            elif (d.get(uf_col) or "").strip() == "51":
                for n in want:
                    tot[n] += num(d.get(n)) or 0
        for n, (col, code, rot) in want.items():
            res.append({"fonte": conj, "ano": y, "linha": "soma CO_UF=51", "recorte": "Mato Grosso", "coluna": col,
                        "rotulo": f"{code} | " + rot.split(" > ", 1)[-1], "valor": tot[n]})
            res.append({"fonte": conj, "ano": y, "linha": "Total Brasil", "recorte": "Brasil", "coluna": col,
                        "rotulo": f"{code} | " + rot.split(" > ", 1)[-1], "valor": brasil.get(n)})
    print("ok", y, file=sys.stderr, flush=True)

R = pd.DataFrame(res)
R.to_pickle(work / "ifmt.pkl")
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 140); pd.set_option("display.max_rows", 500)
pv = R.pivot_table(index=["fonte", "recorte", "rotulo"], columns="ano", values="valor", aggfunc="sum")
print(pv.to_string())
