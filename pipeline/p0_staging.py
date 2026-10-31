"""P0 — Manifesto das fontes e staging fiel de todas as abas (2017–2024).

Para cada ZIP: registra tamanho e MD5 em config/manifesto_fontes.csv; extrai cópias dos XLSX para
TEMP (fora do projeto); grava cada aba em dados/staging/<ano>/<arquivo>/<aba>.parquet com:
  - linha (número da linha na planilha)
  - uma coluna de texto por letra (A, B, ...), com o valor exatamente como está no XML
    (texto compartilhado resolvido; célula sem valor = nulo; texto vazio "" preservado)
  - _num_como_texto: letras das células numéricas gravadas como texto na linha (regra R11)
  - _extra: células além da dimensão declarada (JSON), se houver
Nada é convertido, filtrado ou descartado.

Uso: python -I p0_staging.py [n_processos]
"""
import csv, datetime, json, re, shutil, sys, time, zipfile
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pyarrow as pa
import pyarrow.parquet as pq
from comum import (ANOS, CONFIG, PROJETO, STAGING, URL_INEP, XLSX_TMP, abas, col2n, conjunto, linhas,
                   md5, n2col, nome_no_zip, nome_seguro, strings_compartilhadas)

NUM = re.compile(r"^\s*[+-]?\d+([.,]\d+)?\s*$")
LOTE = 5000


def manifesto():
    rows = []
    for ano in ANOS:
        zp = PROJETO / f"sinopse_educacao_superior_{ano}.zip"
        rows.append({"ano": ano, "arquivo_zip": zp.name, "bytes": zp.stat().st_size, "md5": md5(zp),
                     "url_inep": URL_INEP.format(ano=ano),
                     "registrado_em": datetime.date.today().isoformat(),
                     "observacao": "MD5 conferido com o site do Inep em 30/10/2026 (idêntico); tabela 4.1 sem a correção do IFMT"
                     if ano == 2023 else ""})
    CONFIG.mkdir(exist_ok=True)
    with open(CONFIG / "manifesto_fontes.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    return {r["ano"]: r["md5"] for r in rows}


def extrair(ano):
    zp = PROJETO / f"sinopse_educacao_superior_{ano}.zip"
    out = []
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            nome = nome_no_zip(info)
            if not nome.lower().endswith(".xlsx"):
                continue
            dest = XLSX_TMP / str(ano) / nome.split("/")[-1]
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists() or dest.stat().st_size != info.file_size:
                with z.open(info) as fi, open(dest, "wb") as fo:
                    shutil.copyfileobj(fi, fo, 16 * 1024 * 1024)
            out.append((ano, dest, nome))
    return out


def gravar_aba(z, ss, aba, parte, dim, destino):
    m = re.match(r"([A-Z]+)\d+(?::([A-Z]+)\d+)?$", dim or "A1")
    maxc = col2n(m.group(2) or m.group(1))
    letras = [n2col(i) for i in range(1, maxc + 1)]
    schema = pa.schema([("linha", pa.int32())] + [(c, pa.string()) for c in letras]
                       + [("_num_como_texto", pa.string()), ("_extra", pa.string())])
    tmp = destino.with_suffix(".parquet.tmp")
    writer = pq.ParquetWriter(tmp, schema, compression="zstd")
    buf = {k: [] for k in schema.names}
    n_lin = n_cel = n_txtnum = 0

    def flush():
        if buf["linha"]:
            writer.write_table(pa.table(buf, schema=schema))
            for k in buf:
                buf[k].clear()

    for r, cel in linhas(z, parte, ss):
        if not cel:
            continue
        n_lin += 1
        n_cel += len(cel)
        buf["linha"].append(r)
        txtnum, extra = [], {}
        for i, c in enumerate(letras, 1):
            tv = cel.get(i)
            buf[c].append(None if tv is None else tv[1])
            if tv is not None and tv[0] in ("s", "str", "inlineStr") and NUM.match(tv[1]):
                txtnum.append(c)
        for i, tv in cel.items():
            if i > maxc:
                extra[n2col(i)] = tv[1]
        n_txtnum += len(txtnum)
        buf["_num_como_texto"].append(",".join(txtnum) or None)
        buf["_extra"].append(json.dumps(extra, ensure_ascii=False) if extra else None)
        if len(buf["linha"]) >= LOTE:
            flush()
    flush()
    writer.close()
    tmp.replace(destino)
    return n_lin, maxc, n_cel, n_txtnum


def processar(args):
    ano, xlsx, nome_zip, md5_zip = args
    res = []
    with zipfile.ZipFile(xlsx) as z:
        ss = strings_compartilhadas(z)
        for aba, parte, dim in abas(z):
            t0 = time.time()
            destino = STAGING / str(ano) / xlsx.stem / f"{nome_seguro(aba)}.parquet"
            destino.parent.mkdir(parents=True, exist_ok=True)
            n_lin, n_col, n_cel, n_txt = gravar_aba(z, ss, aba, parte, dim, destino)
            res.append({"ano": ano, "conjunto": conjunto(xlsx.name), "arquivo": xlsx.name, "caminho_no_zip": nome_zip,
                        "aba": aba, "aba_repr": repr(aba), "parquet": str(destino.relative_to(PROJETO)),
                        "dimensao_declarada": dim, "n_linhas": n_lin, "n_colunas": n_col, "n_celulas": n_cel,
                        "n_num_como_texto": n_txt, "segundos": round(time.time() - t0, 1), "md5_zip": md5_zip})
    print(f"{ano} {xlsx.name}: {len(res)} aba(s)", flush=True)
    return res


if __name__ == "__main__":
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    t0 = time.time()
    md5s = manifesto()
    print("manifesto ok", flush=True)
    jobs = [(ano, x, n, md5s[ano]) for ano in ANOS for (ano, x, n) in extrair(ano)]
    print(f"extração ok: {len(jobs)} XLSX em {XLSX_TMP}", flush=True)
    jobs.sort(key=lambda j: -j[1].stat().st_size)
    with Pool(nproc) as p:
        cat = [r for part in p.imap_unordered(processar, jobs) for r in part]
    cat.sort(key=lambda r: (r["ano"], r["arquivo"], r["parquet"]))
    with open(STAGING / "_catalogo_staging.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(cat[0]))
        w.writeheader(); w.writerows(cat)
    print(f"P0 concluída: {len(cat)} abas em {round((time.time() - t0) / 60, 1)} min", flush=True)
