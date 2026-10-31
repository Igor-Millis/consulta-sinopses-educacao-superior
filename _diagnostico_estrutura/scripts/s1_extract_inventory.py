"""Etapa 1: extrai copias dos XLSX (somente leitura dos ZIPs originais) e levanta o inventario bruto.

Uso: python -I s1_extract_inventory.py <dir_zips> <dir_work>
"""
import json, re, sys, zipfile, shutil
from pathlib import Path

src, work = Path(sys.argv[1]), Path(sys.argv[2])
xdir = work / "xlsx"
xdir.mkdir(parents=True, exist_ok=True)

def fix_name(info):
    # Nomes sem a flag UTF-8 foram gravados em cp850 (OEM Windows) e o Python os le como cp437
    if info.flag_bits & 0x800:
        return info.filename
    try:
        return info.filename.encode("cp437").decode("cp850")
    except Exception:
        return info.filename

def classify(name):
    n = name.lower()
    if "municipio" in n: return "Sinopse por município"
    if "anexo_iii" in n: return "Anexo III — Tabela 8.3"
    if "anexo_ii" in n: return "Anexo II — Tabela 8.2"
    if "anexo_i" in n: return "Anexo I — Tabela 8.1"
    return "?"

inv = []
for zp in sorted(src.glob("sinopse_educacao_superior_*.zip")):
    year = int(re.search(r"(\d{4})", zp.name).group(1))
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            orig = fix_name(info)
            if not orig.lower().endswith(".xlsx"):
                continue
            base = orig.split("/")[-1]
            dest = xdir / str(year) / base
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists() or dest.stat().st_size != info.file_size:
                with z.open(info) as fi, open(dest, "wb") as fo:
                    shutil.copyfileobj(fi, fo, 16 * 1024 * 1024)
            # inventario a partir do pacote OOXML
            with zipfile.ZipFile(dest) as x:
                wb = x.read("xl/workbook.xml").decode("utf8")
                rels = x.read("xl/_rels/workbook.xml.rels").decode("utf8")
                relmap = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
                relmap.update({b: a for a, b in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
                sheets = []
                for m in re.finditer(r"<sheet\b[^>]*/>", wb):
                    tag = m.group(0)
                    nm = re.search(r'name="([^"]*)"', tag).group(1)
                    st = re.search(r'state="([^"]*)"', tag)
                    rid = re.search(r'r:id="([^"]*)"', tag).group(1)
                    tgt = relmap[rid].lstrip("/")
                    if not tgt.startswith("xl/"):
                        tgt = "xl/" + tgt
                    si = x.getinfo(tgt)
                    with x.open(si) as f:
                        head = f.read(4096).decode("utf8", "replace")
                    dm = re.search(r'<dimension ref="([^"]+)"', head)
                    sheets.append({
                        "sheet": nm, "state": st.group(1) if st else "visible",
                        "xml_part": tgt, "xml_size": si.file_size,
                        "dimension": dm.group(1) if dm else None,
                    })
                names = x.namelist()
            inv.append({
                "ano": year, "zip": zp.name, "caminho_no_zip": orig, "arquivo": base,
                "conjunto": classify(base), "tamanho_bytes": info.file_size,
                "tamanho_compactado_bytes": info.compress_size, "copia": str(dest),
                "n_abas": len(sheets), "abas": sheets,
                "tem_sharedStrings": "xl/sharedStrings.xml" in names,
                "partes": [n for n in names if not n.startswith("xl/worksheets/sheet")],
            })
            print(year, base, len(sheets), flush=True)

(work / "inventario_bruto.json").write_text(json.dumps(inv, ensure_ascii=False, indent=1), encoding="utf8")
