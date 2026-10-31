"""Aplica as marcações Q10 (células) e Q13 (7.4 somente_presencial) no banco principal SEM recarregar a Sinopse.

Uso:
  python -I aplicar_q10_q13.py --comparar PARCIAL.duckdb   compara a recarga controlada (carregar_sinopse.py --banco
                                                           PARCIAL --tabelas 6.3,6.6,7.4) com o banco principal
  python -I aplicar_q10_q13.py --aplicar                   aplica (exige que --comparar tenha passado)
  python -I aplicar_q10_q13.py --reverter DIR              restaura status_valor/id_ocorrencia do backup DIR

Garantias de --aplicar:
  1. backup do estado atual de status_valor/id_ocorrencia de TODAS as células de 6.3, 6.6 e 7.4 em
     dados/backup/<data_hora>_status_pre_q10_q13/ (Parquet) — reversão exata com --reverter;
  2. só as colunas status_valor e id_ocorrencia mudam; só células hoje 'informado'; dentro de uma transação, com as
     contagens esperadas conferidas antes do COMMIT (senão ROLLBACK);
  3. impressão digital de TODAS as demais colunas do fato_sinopse inteiro (126,8 milhões de linhas) antes = depois;
  4. status das células fora do alvo antes = depois.
"""
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import CONFIG, NUCLEO, PROJETO

sys.stdout.reconfigure(encoding="utf-8")
BANCO = NUCLEO / "ijsn.duckdb"
TABS = ("6.3", "6.6", "7.4")
CHAVE = "ano, tabela, linha, coluna"
VALORES = ("ano, tabela, id_geo, nivel_geo, nivel_academico, indicador, id_recorte, valor, eh_agregado, valor_bruto, "
           "aba, linha, coluna, md5_zip")
Q13 = ("tabela = '7.4' AND indicador IN ('cursos', 'vagas', 'inscritos') AND nivel_geo <> 'Brasil' "
       "AND status_valor = 'informado'")


def q10_alvo():
    q = pd.read_csv(CONFIG / "q10_celulas_suspeitas.csv", encoding="utf-8-sig", dtype={"tabela": str, "coluna": str})
    return q[q.papel == "suspeita"][["ano", "tabela", "linha", "coluna"]]


def comparar(parcial):
    con = duckdb.connect(str(BANCO), read_only=True)
    con.execute("SET memory_limit = '3GB'")
    con.execute(f"ATTACH '{Path(parcial).as_posix()}' AS p (READ_ONLY)")
    tabs = ", ".join(f"'{t}'" for t in TABS)
    n_p = con.execute(f"SELECT count(*) FROM p.fato_sinopse").fetchall()[0][0]
    n_m = con.execute(f"SELECT count(*) FROM fato_sinopse WHERE tabela IN ({tabs})").fetchall()[0][0]
    d = con.execute(f"""
      SELECT coalesce(m.ano, p.ano) ano, coalesce(m.tabela, p.tabela) tabela, m.status_valor st_atual,
             p.status_valor st_recarga, p.id_ocorrencia oc_recarga,
             (m.ano IS NULL OR p.ano IS NULL) so_um_lado,
             hash({', '.join('m.' + c.strip() for c in VALORES.split(','))}) <>
             hash({', '.join('p.' + c.strip() for c in VALORES.split(','))}) outra_coluna_difere
      FROM (SELECT * FROM fato_sinopse WHERE tabela IN ({tabs})) m
      FULL JOIN p.fato_sinopse p USING ({CHAVE})
      WHERE m.ano IS NULL OR p.ano IS NULL OR m.status_valor IS DISTINCT FROM p.status_valor
         OR m.id_ocorrencia IS DISTINCT FROM p.id_ocorrencia
         OR hash({', '.join('m.' + c.strip() for c in VALORES.split(','))}) <>
            hash({', '.join('p.' + c.strip() for c in VALORES.split(','))})""").df()
    print(f"linhas: banco principal {n_m:,} × recarga {n_p:,}")
    print(f"diferenças: {len(d):,}")
    if len(d):
        print(d.groupby(["tabela", "st_atual", "st_recarga", "oc_recarga", "so_um_lado", "outra_coluna_difere"],
                        dropna=False).size().to_string())
    q10 = q10_alvo()
    esperado_q10 = len(q10)
    esperado_q13 = con.execute(f"SELECT count(*) FROM fato_sinopse WHERE {Q13}").fetchall()[0][0]
    ok = (n_p == n_m and not d.so_um_lado.any() and not d.outra_coluna_difere.any()
          and (d.st_atual == "informado").all()
          and ((d.oc_recarga == "Q10") & (d.st_recarga == "suspeito")).sum() == esperado_q10
          and ((d.st_recarga == "somente_presencial") & (d.tabela == "7.4")).sum() == esperado_q13
          and len(d) == esperado_q10 + esperado_q13)
    if len(d) == 0 and n_p == n_m:
        print("IDÊNTICOS: o banco principal já tem exatamente o que a recarga produz (marcações aplicadas)")
        return True
    print(f"esperado: Q10 {esperado_q10:,} células → suspeito; Q13 {esperado_q13:,} → somente_presencial")
    print("COMPARAÇÃO OK: a recarga difere do banco atual exatamente nas marcações novas" if ok else "COMPARAÇÃO FALHOU")
    return ok


def digitais(con):
    v = con.execute(f"SELECT count(*), sum(hash({VALORES})::HUGEINT) FROM fato_sinopse").fetchall()[0]
    s = con.execute(f"""SELECT sum(hash(ano, tabela, linha, coluna, status_valor, id_ocorrencia)::HUGEINT)
                        FROM fato_sinopse WHERE NOT (tabela IN {TABS})""").fetchall()[0][0]
    return v, s


def aplicar():
    con = duckdb.connect(str(BANCO))
    con.execute("SET memory_limit = '3GB'")
    con.execute("SET threads = 4")
    t0 = time.time()
    destino = PROJETO / "dados" / "backup" / f"{datetime.now():%Y%m%d_%H%M%S}_status_pre_q10_q13"
    destino.mkdir(parents=True, exist_ok=False)
    arq = destino / "status_6.3_6.6_7.4.parquet"
    con.execute(f"""COPY (SELECT {CHAVE}, status_valor, id_ocorrencia FROM fato_sinopse WHERE tabela IN {TABS})
                    TO '{arq.as_posix()}' (FORMAT parquet, COMPRESSION zstd)""")
    n_bkp = con.execute(f"SELECT count(*) FROM read_parquet('{arq.as_posix()}')").fetchall()[0][0]
    print(f"backup do status: {arq} ({n_bkp:,} células)", flush=True)
    antes_v, antes_s = digitais(con)
    print(f"digital antes: {antes_v} ({time.time() - t0:.0f} s)", flush=True)
    con.register("v_q10", q10_alvo())
    esperado_q10 = len(q10_alvo())
    esperado_q13 = con.execute(f"SELECT count(*) FROM fato_sinopse WHERE {Q13}").fetchall()[0][0]
    con.execute("BEGIN TRANSACTION")
    n1 = con.execute(f"""UPDATE fato_sinopse f SET status_valor = 'suspeito', id_ocorrencia = 'Q10'
                         FROM v_q10 q WHERE f.ano = q.ano AND f.tabela = q.tabela AND f.linha = q.linha
                         AND f.coluna = q.coluna AND f.status_valor = 'informado'""").fetchall()[0][0]
    n2 = con.execute(f"UPDATE fato_sinopse SET status_valor = 'somente_presencial' WHERE {Q13}").fetchall()[0][0]
    if n1 != esperado_q10 or n2 != esperado_q13:
        con.execute("ROLLBACK")
        raise SystemExit(f"ROLLBACK: Q10 {n1} ≠ {esperado_q10} ou Q13 {n2} ≠ {esperado_q13}")
    con.execute("COMMIT")
    depois_v, depois_s = digitais(con)
    ok = antes_v == depois_v and antes_s == depois_s
    print(f"Q10: {n1:,} células → suspeito/Q10 | Q13: {n2:,} → somente_presencial")
    print(f"digital dos valores e demais colunas: {'IGUAL' if antes_v == depois_v else 'DIFERENTE'}; "
          f"status fora de 6.3/6.6/7.4: {'IGUAL' if antes_s == depois_s else 'DIFERENTE'}")
    con.execute("CREATE TABLE IF NOT EXISTS carga_log (quando TIMESTAMP, etapa VARCHAR, situacao VARCHAR)")
    con.execute("INSERT INTO carga_log VALUES (current_timestamp, ?, ?)",
                ["aplicar_q10_q13", f"Q10 {n1}; Q13 {n2}; backup {destino.name}; verificação {'OK' if ok else 'FALHOU'}"])
    con.close()
    print(f"concluído em {time.time() - t0:.0f} s — {'OK' if ok else 'VERIFICAÇÃO FALHOU: reverter com --reverter ' + str(destino)}")
    return ok


def reverter(destino):
    arq = (Path(destino) / "status_6.3_6.6_7.4.parquet").as_posix()
    con = duckdb.connect(str(BANCO))
    con.execute("SET memory_limit = '3GB'")
    n = con.execute(f"""UPDATE fato_sinopse f SET status_valor = b.status_valor, id_ocorrencia = b.id_ocorrencia
                        FROM read_parquet('{arq}') b WHERE f.ano = b.ano AND f.tabela = b.tabela AND f.linha = b.linha
                        AND f.coluna = b.coluna""").fetchall()[0][0]
    con.execute("INSERT INTO carga_log VALUES (current_timestamp, 'reverter_q10_q13', ?)", [f"{n} células restauradas"])
    print(f"{n:,} células restauradas de {arq}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--comparar"]:
        sys.exit(0 if comparar(sys.argv[2]) else 1)
    if sys.argv[1:2] == ["--aplicar"]:
        sys.exit(0 if aplicar() else 1)
    if sys.argv[1:2] == ["--reverter"]:
        reverter(sys.argv[2])
