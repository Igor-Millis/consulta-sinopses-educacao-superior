"""Segurança do motor: conexão somente leitura, validação do SQL e execução com limites e registro.

Defesa em camadas:
  1. a conexão DuckDB é aberta em read_only (o banco recusa qualquer escrita);
  2. o SQL é validado antes da execução: um único comando, começando por SELECT/WITH, sem palavras-chave de
     escrita, extensões ou acesso a arquivos, e só com tabelas autorizadas (config.TABELAS_AUTORIZADAS);
  3. valores vindos da pergunta entram como parâmetros (?), nunca concatenados no SQL;
  4. tempo máximo (interrupção) e limite de linhas;
  5. toda consulta é registrada em dados/consultas/registro_consultas.jsonl.
"""
import json
import re
import threading
import time
from datetime import datetime

import duckdb

from .config import BANCO, LIMITE_LINHAS, MEMORIA_DUCKDB, REGISTRO, TABELAS_AUTORIZADAS, TEMPO_MAXIMO_S

PROIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|create|alter|attach|detach|copy|export|import|install|load|pragma|set|call|"
    r"vacuum|checkpoint|truncate|replace|grant|revoke|begin|commit|rollback|read_csv\w*|read_parquet|"
    r"read_json\w*|read_text|read_blob|glob|httpfs|system|getenv)\b", re.I)
TABELA = re.compile(r"\b(?:from|join)\s+([a-z_][\w.]*)", re.I)


class SQLRecusado(ValueError):
    pass


def validar_sql(sql: str) -> None:
    s = re.sub(r"'(?:[^']|'')*'", "''", sql)          # ignora o conteúdo de literais
    s_sem_coment = re.sub(r"--[^\n]*|/\*.*?\*/", " ", s, flags=re.S)
    if ";" in s_sem_coment.strip().rstrip(";"):
        raise SQLRecusado("mais de um comando SQL")
    if not re.match(r"^\s*(select|with)\b", s_sem_coment, re.I):
        raise SQLRecusado("só são permitidas consultas SELECT/WITH")
    m = PROIBIDAS.search(s_sem_coment)
    if m:
        raise SQLRecusado(f"palavra-chave não permitida: {m.group(0)}")
    ctes = {c.lower() for c in re.findall(r"\b(\w+)\s+as\s*\(", s_sem_coment, re.I)}
    for t in TABELA.findall(s_sem_coment):
        t = t.lower()
        if t not in TABELAS_AUTORIZADAS and t not in ctes:
            raise SQLRecusado(f"tabela não autorizada: {t}")


_con = None


def conexao():
    global _con
    if _con is None:
        _con = duckdb.connect(str(BANCO), read_only=True)
        _con.execute(f"SET memory_limit = '{MEMORIA_DUCKDB}'")
        _con.execute("SET threads = 4")
    return _con


def executar(sql: str, params=None, pergunta: str | None = None):
    """Valida e executa; devolve um DataFrame. Registra a consulta (mesmo se falhar)."""
    validar_sql(sql)
    con = conexao()
    cursor = con.cursor()
    timer = threading.Timer(TEMPO_MAXIMO_S, cursor.interrupt)
    t0 = time.time()
    erro, n = None, None
    try:
        timer.start()
        df = cursor.execute(sql, params or []).fetch_df()
        n = len(df)
        if n > LIMITE_LINHAS:
            df = df.head(LIMITE_LINHAS)
        return df
    except Exception as e:
        erro = f"{type(e).__name__}: {e}"
        raise
    finally:
        timer.cancel()
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRO, "a", encoding="utf-8") as f:
            f.write(json.dumps({"quando": datetime.now().isoformat(timespec="seconds"), "pergunta": pergunta,
                                "sql": sql, "params": [str(p) for p in (params or [])], "linhas": n,
                                "segundos": round(time.time() - t0, 3), "erro": erro}, ensure_ascii=False) + "\n")
