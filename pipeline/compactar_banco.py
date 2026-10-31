"""Compactação do banco: copia o banco para um arquivo NOVO (COPY FROM DATABASE), valida e só então troca.

Uso:
  python -I compactar_banco.py --copiar     → dados/nucleo/ijsn_compactado.duckdb (o original é aberto só para leitura)
  python -I compactar_banco.py --validar    → compara original × compactado (relatório em dados/qualidade/)
  python -I compactar_banco.py --trocar     → exige validação OK registrada; renomeia o original para
                                              ijsn_pre_compactacao_<data_hora>.duckdb (NÃO apaga) e o compactado
                                              para ijsn.duckdb
  python -I compactar_banco.py --reverter ARQUIVO  → desfaz a troca (o compactado vira ijsn_compactado_revertido.duckdb)
Validação: mesmas tabelas e visões (com a mesma definição), mesmas contagens, mesmos tipos de coluna, mesma
impressão digital de conteúdo (soma de hash de todas as linhas) em TODAS as tabelas, e todas as visões compilam.
A equivalência das respostas do motor é testada à parte (tests/test_equivalencia_banco.py).
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
ORIG = NUCLEO / "ijsn.duckdb"
NOVO = NUCLEO / "ijsn_compactado.duckdb"
REL = NUCLEO.parent / "qualidade" / "compactacao_validacao.json"


def copiar():
    if NOVO.exists():
        raise SystemExit(f"{NOVO} já existe — não sobrescrevo; remova ou renomeie antes")
    t0 = time.time()
    con = duckdb.connect()
    con.execute("SET memory_limit = '3GB'")
    con.execute("SET threads = 4")
    con.execute("SET preserve_insertion_order = true")
    con.execute(f"ATTACH '{ORIG.as_posix()}' AS o (READ_ONLY)")
    con.execute(f"ATTACH '{NOVO.as_posix()}' AS n")
    con.execute("COPY FROM DATABASE o TO n")
    con.execute("DETACH n")
    print(f"copiado em {(time.time() - t0) / 60:.1f} min: {ORIG.stat().st_size / 2**30:.2f} GB → {NOVO.stat().st_size / 2**30:.2f} GB")


def _info(con, db):
    tabs = {t: {"linhas": con.execute(f"SELECT count(*) FROM {db}.{t}").fetchall()[0][0],
                "colunas": [list(r[:2]) for r in con.execute(f"DESCRIBE {db}.{t}").fetchall()],
                "digital": str(con.execute(f"SELECT sum(hash(x)::HUGEINT) FROM {db}.{t} x").fetchall()[0][0])}
            for (t,) in con.execute(f"SELECT table_name FROM duckdb_tables() WHERE database_name = '{db}' ORDER BY 1").fetchall()}
    vis = dict(con.execute(f"SELECT view_name, sql FROM duckdb_views() WHERE database_name = '{db}' AND NOT internal").fetchall())
    return tabs, vis


def validar():
    t0 = time.time()
    con = duckdb.connect()
    con.execute("SET memory_limit = '3GB'")
    con.execute("SET threads = 4")
    con.execute(f"ATTACH '{ORIG.as_posix()}' AS o (READ_ONLY)")
    con.execute(f"ATTACH '{NOVO.as_posix()}' AS n (READ_ONLY)")
    to, vo = _info(con, "o")
    print(f"original lido ({time.time() - t0:.0f} s)", flush=True)
    tn, vn = _info(con, "n")
    print(f"compactado lido ({time.time() - t0:.0f} s)", flush=True)
    problemas = []
    if set(to) != set(tn):
        problemas.append(f"tabelas diferentes: {sorted(set(to) ^ set(tn))}")
    for t in sorted(set(to) & set(tn)):
        for k in ("linhas", "colunas", "digital"):
            if to[t][k] != tn[t][k]:
                problemas.append(f"{t}: {k} difere")
    if set(vo) != set(vn) or any(vo[v].replace('"o".', "") != vn[v].replace('"n".', "") for v in vo if v in vn):
        problemas.append("visões diferentes")
    con.close()
    # visões compilam no compactado (aberto sozinho, como o motor abre)
    c2 = duckdb.connect(str(NOVO), read_only=True)
    for v in vn:
        try:
            c2.execute(f"SELECT * FROM {v} LIMIT 0").fetchall()
        except Exception as e:
            problemas.append(f"visão {v} não compila: {e}")
    c2.close()
    rel = {"quando": datetime.now().isoformat(timespec="seconds"), "original_bytes": ORIG.stat().st_size,
           "compactado_bytes": NOVO.stat().st_size, "tabelas": len(to), "visoes": len(vo),
           "linhas_total": sum(x["linhas"] for x in to.values()), "problemas": problemas, "ok": not problemas,
           "detalhe": {t: {"linhas": to[t]["linhas"], "digital_igual": to[t]["digital"] == tn.get(t, {}).get("digital")}
                       for t in to}}
    REL.write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(to)} tabelas, {len(vo)} visões, {rel['linhas_total']:,} linhas; "
          f"{ORIG.stat().st_size / 2**30:.2f} GB → {NOVO.stat().st_size / 2**30:.2f} GB ({time.time() - t0:.0f} s)")
    print("VALIDAÇÃO OK" if not problemas else f"VALIDAÇÃO FALHOU: {problemas}")
    return not problemas


def trocar():
    rel = json.loads(REL.read_text(encoding="utf-8"))
    if not rel["ok"] or rel["compactado_bytes"] != NOVO.stat().st_size:
        raise SystemExit("validação ausente, com falha ou feita sobre outro arquivo: não troco")
    guarda = NUCLEO / f"ijsn_pre_compactacao_{datetime.now():%Y%m%d_%H%M%S}.duckdb"
    ORIG.rename(guarda)
    NOVO.rename(ORIG)
    print(f"original preservado em {guarda.name}; compactado agora é {ORIG.name}")
    print(f"para reverter: python -I pipeline/compactar_banco.py --reverter {guarda.name}")


def reverter(nome):
    guarda = NUCLEO / nome
    ORIG.rename(NUCLEO / "ijsn_compactado_revertido.duckdb")
    guarda.rename(ORIG)
    print(f"revertido: {nome} voltou a ser ijsn.duckdb")


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else ""
    if acao == "--copiar":
        copiar()
    elif acao == "--validar":
        sys.exit(0 if validar() else 1)
    elif acao == "--trocar":
        trocar()
    elif acao == "--reverter":
        reverter(sys.argv[2])
    else:
        print(__doc__)
