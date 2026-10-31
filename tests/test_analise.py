"""Regras estatísticas da camada de análise (unitário, sem banco)."""
import math

import numpy as np
import pandas as pd
import pytest

from motor.analise import ano_ultrapassagem, cagr, variacao


def test_variacao():
    assert variacao(100, 150) == (50, 0.5)
    a, p = variacao(0, 10)
    assert a == 10 and math.isnan(p)          # % indefinida com base zero


def test_cagr():
    assert cagr(100, 121, 2) == pytest.approx(0.10)
    assert math.isnan(cagr(0, 10, 3))
    assert math.isnan(cagr(100, 120, 0))


def test_ano_ultrapassagem():
    a = pd.Series({2020: 10, 2021: 12, 2022: 20, 2023: 25})
    b = pd.Series({2020: 15, 2021: 14, 2022: 18, 2023: 19})
    assert ano_ultrapassagem(a, b) == 2022
    assert ano_ultrapassagem(b * 0 + 1, b) is None


def test_ultrapassagem_ignora_anos_ausentes():
    a = pd.Series({2020: 10, 2021: np.nan, 2022: 20})
    b = pd.Series({2020: 15, 2021: 1, 2022: 18})
    assert ano_ultrapassagem(a, b) == 2022


def test_formatacao_brasileira():
    from motor.resposta import n, pct
    assert n(1234567) == "1.234.567"
    assert n(1234.5, 1) == "1.234,5"
    assert pct(0.1234) == "12,3%"
    assert pct(0.05, sinal=True) == "+5,0%"
    assert n(float("nan")) == "—"
