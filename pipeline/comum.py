"""Funções e caminhos compartilhados pelo pipeline.

Princípios: os ZIPs nunca são alterados; as cópias dos XLSX ficam fora do projeto (TEMP);
nenhum valor é convertido ou descartado no staging.
"""
import hashlib, os, re, zipfile
from pathlib import Path
from lxml import etree

PROJETO = Path(__file__).resolve().parent.parent
CONFIG = PROJETO / "config"
STAGING = PROJETO / "dados" / "staging"
NUCLEO = PROJETO / "dados" / "nucleo"
QUALIDADE = PROJETO / "dados" / "qualidade"
DIAG = PROJETO / "_diagnostico_estrutura"
XLSX_TMP = Path(os.environ.get("TEMP", PROJETO)) / "ijsn_pipeline" / "xlsx"
ANOS = list(range(2017, 2025))
URL_INEP = "https://download.inep.gov.br/informacoes_estatisticas/sinopses_estatisticas/sinopses_educacao_superior/sinopse_educacao_superior_{ano}.zip"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_COL = re.compile(r"[A-Z]+")


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


def ler_catalogo(path, **kw):
    """Lê um catálogo .xlsx do diagnóstico. Só célula vazia vira ausente: a coluna de letra "NA" não pode virar NaN."""
    import pandas as pd
    return pd.read_excel(path, engine="openpyxl", keep_default_na=False, na_values=[""], **kw)


def md5(path, bloco=16 * 1024 * 1024):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while b := f.read(bloco):
            h.update(b)
    return h.hexdigest().upper()


def nome_no_zip(info):
    """Nomes sem a flag UTF-8 foram gravados em cp850 e o Python os lê como cp437."""
    if info.flag_bits & 0x800:
        return info.filename
    try:
        return info.filename.encode("cp437").decode("cp850")
    except UnicodeError:
        return info.filename


def conjunto(nome_arquivo):
    n = nome_arquivo.lower()
    if "municipio" in n:
        return "sinopse"
    if "anexo_iii" in n:
        return "anexo_iii"
    if "anexo_ii" in n:
        return "anexo_ii"
    if "anexo_i" in n:
        return "anexo_i"
    raise ValueError(nome_arquivo)


def nome_seguro(aba):
    return re.sub(r"[^\w.-]+", "_", aba.strip()) or "aba"


def abas(z):
    """Lista (nome_aba, parte_xml, dimensao_declarada) na ordem do workbook."""
    wb = z.read("xl/workbook.xml").decode("utf8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf8")
    rel = {re.search(r'Id="([^"]+)"', t).group(1): re.search(r'Target="([^"]+)"', t).group(1)
           for t in re.findall(r"<Relationship\b[^>]*>", rels)}
    out = []
    for t in re.findall(r"<sheet\b[^>]*/>", wb):
        nome = re.search(r'name="([^"]*)"', t).group(1)
        parte = rel[re.search(r'r:id="([^"]*)"', t).group(1)].lstrip("/")
        parte = parte if parte.startswith("xl/") else "xl/" + parte
        with z.open(parte) as f:
            head = f.read(4096).decode("utf8", "replace")
        m = re.search(r'<dimension ref="([^"]+)"', head)
        out.append((_unescape(nome), parte, m.group(1) if m else None))
    return out


def _unescape(s):
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'")


def strings_compartilhadas(z):
    out = []
    if "xl/sharedStrings.xml" in z.namelist():
        with z.open("xl/sharedStrings.xml") as f:
            for _, el in etree.iterparse(f, tag=NS + "si"):
                out.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
                while el.getprevious() is not None:
                    del el.getparent()[0]
    return out


def linhas(z, parte, ss):
    """Gera (numero_linha, {n_coluna: (tipo, valor_texto)}) em streaming. Células sem <v> são omitidas."""
    with z.open(parte) as f:
        for _, el in etree.iterparse(f, tag=NS + "row"):
            d = {}
            for c in el.iter(NS + "c"):
                t = c.get("t")
                if t == "inlineStr":
                    v = "".join(x.text or "" for x in c.iter(NS + "t"))
                else:
                    ve = c.find(NS + "v")
                    if ve is None:
                        continue
                    v = ve.text or ""
                    if t == "s":
                        v = ss[int(v)]
                d[col2n(_COL.match(c.get("r")).group(0))] = (t or "n", v)
            r = int(el.get("r"))
            el.clear()
            while el.getprevious() is not None:
                del el.getparent()[0]
            yield r, d
