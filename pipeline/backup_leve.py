"""Backup leve: todas as tabelas do banco EXCETO os dois fatos (reconstruíveis a partir dos ZIPs), em Parquet.

Uso:  python -I pipeline/backup_leve.py            → cria dados/backup/AAAAMMDD_HHMMSS/ (nunca sobrescreve)
      python -I pipeline/backup_leve.py --validar DIR  → só valida um backup existente

Conteúdo: <tabela>.parquet (zstd), visoes.sql (definição das visões), manifesto.json (linhas, colunas e tipos,
bytes, sha256 do arquivo, impressão digital do conteúdo, commit git de config/ e do código).
Validação (grava validacao.txt no diretório):
  1. cada Parquet é lido de volta: linhas, nomes e tipos de coluna iguais ao banco;
  2. impressão digital do conteúdo igual (soma de hash() de todas as linhas — independe da ordem);
  3. o sha256 do arquivo confere com o manifesto;
  4. reconstrução: um banco novo é montado só com os Parquet (+ visões que não dependem dos fatos) e
     tests/test_backup.py roda perguntas do motor nele e no banco principal, comparando as respostas.
Os fatos (fato_anexo_curso, fato_sinopse) não entram: ~737 milhões de linhas, reconstruídos por P1–P3.
"""
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from comum import NUCLEO, PROJETO

sys.stdout.reconfigure(encoding="utf-8")
BANCO = NUCLEO / "ijsn.duckdb"
EXCLUIR = {"fato_anexo_curso", "fato_sinopse"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def digital(con, origem):
    # soma (em HUGEINT) do hash de cada linha: igual para o mesmo multiconjunto de linhas, em qualquer ordem
    return str(con.execute(f"SELECT coalesce(sum(hash(t)::HUGEINT), 0), count(*) FROM {origem} t").fetchall()[0])


def esquema(con, origem):
    return [(r[0], r[1]) for r in con.execute(f"DESCRIBE SELECT * FROM {origem}").fetchall()]


def exportar():
    destino = PROJETO / "dados" / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
    destino.mkdir(parents=True, exist_ok=False)          # nunca sobrescreve
    con = duckdb.connect(str(BANCO), read_only=True)
    con.execute("SET memory_limit = '2GB'")
    con.execute("SET threads = 4")
    tabelas = [r[0] for r in con.execute("SELECT table_name FROM duckdb_tables() ORDER BY 1").fetchall()
               if r[0] not in EXCLUIR]
    commit = subprocess.run(["git", "-C", str(PROJETO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", str(PROJETO), "status", "--porcelain", "config", "pipeline"],
                          capture_output=True, text=True).stdout.strip()
    man = {"criado": datetime.now().isoformat(timespec="seconds"), "banco": str(BANCO),
           "banco_bytes": BANCO.stat().st_size, "git_commit": commit, "git_config_pipeline_alterado": bool(sujo),
           "excluidas": {t: "fato — reconstruir por P1–P3 a partir dos ZIPs" for t in sorted(EXCLUIR)}, "tabelas": {}}
    # Parquet não tem inteiro de 128 bits: HUGEINT seria gravado como DOUBLE (tipo alterado). Recusa em vez de degradar.
    huge = [(t, c) for t in tabelas for c, tp in esquema(con, t) if tp in ("HUGEINT", "UHUGEINT")]
    if huge:
        raise SystemExit(f"colunas HUGEINT não têm tipo equivalente em Parquet: {huge} — converta na origem (BIGINT)")
    for t in tabelas:
        arq = destino / f"{t}.parquet"
        con.execute(f"COPY {t} TO '{arq.as_posix()}' (FORMAT parquet, COMPRESSION zstd)")
        man["tabelas"][t] = {"arquivo": arq.name, "linhas": con.execute(f"SELECT count(*) FROM {t}").fetchall()[0][0],
                             "colunas": esquema(con, t), "bytes": arq.stat().st_size, "sha256": sha256(arq),
                             "digital": digital(con, t)}
        print(f"  {t}: {man['tabelas'][t]['linhas']:,} linhas, {arq.stat().st_size / 2**20:.1f} MB", flush=True)
    visoes = con.execute("SELECT view_name, sql FROM duckdb_views() WHERE NOT internal ORDER BY 1").fetchall()
    (destino / "visoes.sql").write_text("\n\n".join(f"-- {v}\n{s}" for v, s in visoes), encoding="utf-8")
    man["visoes"] = [v for v, _ in visoes]
    man["total_bytes"] = sum(x["bytes"] for x in man["tabelas"].values())
    (destino / "manifesto.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    con.close()
    print(f"backup: {destino} — {len(tabelas)} tabelas, {man['total_bytes'] / 2**20:.1f} MB")
    return destino


def validar(destino: Path):
    destino = Path(destino)
    man = json.loads((destino / "manifesto.json").read_text(encoding="utf-8"))
    banco = duckdb.connect(str(BANCO), read_only=True)
    banco.execute("SET memory_limit = '2GB'")
    mem = duckdb.connect()
    mem.execute("SET memory_limit = '2GB'")
    linhas, falhas = [], 0
    for t, info in man["tabelas"].items():
        arq = (destino / info["arquivo"]).as_posix()
        src = f"read_parquet('{arq}')"
        checks = {
            "linhas": mem.execute(f"SELECT count(*) FROM {src}").fetchall()[0][0] == info["linhas"]
                      == banco.execute(f"SELECT count(*) FROM {t}").fetchall()[0][0],
            "esquema": [list(x) for x in esquema(mem, src)] == [list(x) for x in info["colunas"]],
            "conteudo": digital(mem, src) == info["digital"] == digital(banco, t),
            "sha256": sha256(destino / info["arquivo"]) == info["sha256"],
        }
        ok = all(checks.values())
        falhas += not ok
        linhas.append(f"{'OK   ' if ok else 'FALHA'} {t}: {info['linhas']:,} linhas " +
                      " ".join(f"{k}={'ok' if v else 'DIFERENTE'}" for k, v in checks.items()))
        print(linhas[-1], flush=True)
    banco.close()
    # reconstrução: banco novo só com os Parquet
    recon = destino / "reconstrucao_teste.duckdb"
    if recon.exists():
        recon.unlink()
    r = duckdb.connect(str(recon))
    for t, info in man["tabelas"].items():
        r.execute(f"CREATE TABLE {t} AS SELECT * FROM read_parquet('{(destino / info['arquivo']).as_posix()}')")
    r.close()
    t0 = time.time()
    res = subprocess.run([sys.executable, "-I", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                          str(PROJETO / "tests" / "test_backup.py"), "--banco-backup", str(recon)],
                         capture_output=True, text=True, cwd=str(PROJETO / "tests"))
    ult = (res.stdout.strip().splitlines() or ["(sem saída)"])[-1]
    linhas.append(f"{'OK   ' if res.returncode == 0 else 'FALHA'} reconstrução: motor sobre o banco refeito só com "
                  f"os Parquet × banco principal — {ult} ({time.time() - t0:.0f} s)")
    if res.returncode != 0:
        linhas.append(res.stdout[-3000:])
        falhas += 1
    print(linhas[-1])
    recon.unlink(missing_ok=True)
    resumo = f"{'VÁLIDO' if falhas == 0 else 'INVÁLIDO'}: {len(man['tabelas'])} tabelas, {falhas} falha(s)"
    linhas.append(resumo)
    (destino / "validacao.txt").write_text(f"validado em {datetime.now():%d/%m/%Y %H:%M:%S}\n" + "\n".join(linhas),
                                           encoding="utf-8")
    print(resumo)
    return falhas == 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--validar":
        sys.exit(0 if validar(Path(sys.argv[2])) else 1)
    d = exportar()
    sys.exit(0 if validar(d) else 1)
