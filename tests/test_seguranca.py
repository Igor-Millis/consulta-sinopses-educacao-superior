"""Segurança do motor: só SELECT/WITH, só tabelas autorizadas, sem arquivos/extensões, conexão somente leitura."""
import duckdb
import pytest

from motor.seguranca import SQLRecusado, conexao, executar, validar_sql

ACEITAS = [
    "SELECT ano, sum(valor) FROM mart_anexos_geo WHERE indicador = ? GROUP BY ALL",
    "WITH x AS (SELECT * FROM mart_curso_geo) SELECT count(*) FROM x",
    "SELECT * FROM dim_geografia g JOIN dim_uf u ON g.co_uf = u.co_uf",
    "SELECT 'drop table x; delete' AS texto FROM dim_uf",          # palavras proibidas só dentro de literal
]
RECUSADAS = [
    "DROP TABLE fato_sinopse",
    "DELETE FROM mart_anexos_geo",
    "UPDATE mart_anexos_geo SET valor = 0",
    "INSERT INTO dim_uf VALUES ('XX', '99')",
    "CREATE TABLE t AS SELECT 1",
    "SELECT 1 FROM dim_uf; DROP TABLE dim_uf",
    "SELECT * FROM read_csv('C:/Windows/win.ini')",
    "SELECT * FROM read_parquet('x.parquet')",
    "ATTACH 'outro.duckdb'",
    "COPY dim_uf TO 'saida.csv'",
    "PRAGMA database_list",
    "INSTALL httpfs",
    "SELECT * FROM stg_linhas_anexo",                              # tabela não autorizada
    "SELECT * FROM dim_uf JOIN carga_log ON true",
    "SELECT getenv('PATH') FROM dim_uf",
    "/* comentário */ DROP TABLE dim_uf",
    "SELECT * FROM dim_uf -- ok\n; DELETE FROM dim_uf",
]


@pytest.mark.parametrize("sql", ACEITAS)
def test_aceita(sql):
    validar_sql(sql)


@pytest.mark.parametrize("sql", RECUSADAS)
def test_recusa(sql):
    with pytest.raises(SQLRecusado):
        validar_sql(sql)


def test_conexao_somente_leitura(cat):
    with pytest.raises(duckdb.Error):
        conexao().cursor().execute("CREATE TABLE teste_escrita AS SELECT 1")


def test_executar_recusa_antes_de_tocar_no_banco(cat):
    with pytest.raises(SQLRecusado):
        executar("DELETE FROM mart_anexos_geo")


def test_parametros_nao_sao_interpretados_como_sql(cat):
    df = executar("SELECT count(*) AS n FROM dim_uf WHERE sg_uf = ?", ["ES' OR '1'='1"])
    assert df["n"].iloc[0] == 0
