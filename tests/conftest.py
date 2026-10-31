import sys
from pathlib import Path

import duckdb
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
BANCO = RAIZ / "dados" / "nucleo" / "ijsn.duckdb"


def pytest_addoption(parser):
    parser.addoption("--banco-backup", default=None, help="banco reconstruído a partir do backup Parquet (test_backup)")


@pytest.fixture(scope="session")
def cat():
    if not BANCO.exists():
        pytest.skip("banco não encontrado")
    from motor.api import catalogo
    return catalogo()


@pytest.fixture(scope="session")
def ref():
    """Conexão independente (somente leitura) para consultas de referência direto nas tabelas de fato."""
    if not BANCO.exists():
        pytest.skip("banco não encontrado")
    from motor.seguranca import conexao
    return conexao().cursor()


def um(ref, sql, params=None):
    return ref.execute(sql, params or []).fetchall()[0][0]
