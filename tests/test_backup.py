"""Reconstrução a partir do backup: o motor dá as MESMAS respostas sobre um banco montado só com os Parquet.

Chamado por pipeline/backup_leve.py (opção --banco-backup). Sem a opção, é pulado.
"""
import pandas as pd
import pytest

import motor.seguranca as seg
from motor.api import perguntar
from motor.semantica import carregar

PERGUNTAS = [
    "Quantas matrículas havia em Vila Velha em 2024?",
    "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?",
    "Quais os 10 municípios capixabas com mais matrículas em 2024?",
    "Quais cursos mais cresceram em ingressantes no ES entre 2019 e 2024?",
    "Matrículas por sexo na Grande Vitória em 2023",
    "Quantas instituições de ensino superior há no ES por rede em 2024?",
    "Qual a participação do EaD nas matrículas do Espírito Santo em 2024?",
    "Concluintes por cor/raça no Espírito Santo em 2018",
]


def _respostas(banco):
    seg._con = None
    carregar.cache_clear()
    original = seg.BANCO
    seg.BANCO = banco
    try:
        return {p: perguntar(p) for p in PERGUNTAS}
    finally:
        seg._con.close()
        seg._con = None
        seg.BANCO = original
        carregar.cache_clear()


def test_backup_reproduz_respostas(request):
    caminho = request.config.getoption("--banco-backup")
    if not caminho:
        pytest.skip("sem --banco-backup")
    principal = _respostas(seg.BANCO)
    backup = _respostas(caminho)
    for p in PERGUNTAS:
        a, b = principal[p], backup[p]
        assert a.precisa_esclarecer == b.precisa_esclarecer, p
        pd.testing.assert_frame_equal(a.tabela.reset_index(drop=True), b.tabela.reset_index(drop=True), obj=p)
