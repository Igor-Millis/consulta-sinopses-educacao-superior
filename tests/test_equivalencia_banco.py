"""Equivalência de respostas entre o banco principal e outro banco (ex.: compactado): as 61 perguntas da bateria.

python -I -m pytest tests/test_equivalencia_banco.py --banco-alternativo dados/nucleo/ijsn_compactado.duckdb
Compara desfecho, tabela e texto completo (sem as linhas com caminhos de arquivo, que mudam a cada execução).
"""
import re

import pandas as pd
import pytest

import motor.seguranca as seg
from bateria_perguntas import BATERIA
from motor.api import perguntar
from motor.semantica import carregar

PERGUNTAS = [p for ps in BATERIA.values() for p in ps]


def _texto(r):
    return re.sub(r"(?m)^(Gráfico|Tabela \(CSV\)):.*$", "", r.texto)


def _respostas(banco):
    seg._con = None
    carregar.cache_clear()
    original = seg.BANCO
    seg.BANCO = banco
    try:
        return {p: perguntar(p) for p in PERGUNTAS}
    finally:
        if seg._con is not None:
            seg._con.close()
        seg._con = None
        seg.BANCO = original
        carregar.cache_clear()


def test_mesmas_respostas(request):
    alt = request.config.getoption("--banco-alternativo")
    if not alt:
        pytest.skip("sem --banco-alternativo")
    a, b = _respostas(seg.BANCO), _respostas(alt)
    diferentes = []
    for p in PERGUNTAS:
        ra, rb = a[p], b[p]
        if ra.precisa_esclarecer != rb.precisa_esclarecer or _texto(ra) != _texto(rb):
            diferentes.append(p)
        elif ra.tabela is not None:
            try:
                pd.testing.assert_frame_equal(ra.tabela.reset_index(drop=True), rb.tabela.reset_index(drop=True))
            except AssertionError:
                diferentes.append(p)
    assert not diferentes, f"{len(diferentes)} de {len(PERGUNTAS)} respostas diferem: {diferentes}"
