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


def test_projecao_tendencia_linear_exata():
    from motor.analise import projetar
    y = pd.Series({a: 100 + 10 * (a - 2017) for a in range(2017, 2025)}, dtype=float)
    p = projetar(y)
    assert list(p.index) == [2025, 2026, 2027]
    assert p["previsto"].tolist() == pytest.approx([180, 190, 200])
    assert (p["superior"] - p["inferior"]).tolist() == pytest.approx([0, 0, 0], abs=1e-6)   # sem resíduo


def test_projecao_intervalo_abre_com_horizonte_e_respeita_limites():
    from motor.analise import projetar
    y = pd.Series([10, 14, 9, 13, 8, 12, 7, 11], index=range(2017, 2025), dtype=float)
    p = projetar(y)
    largura = (p["superior"] - p["inferior"]).tolist()
    assert largura[0] < largura[1] < largura[2]
    assert (p["inferior"] <= p["previsto"]).all() and (p["previsto"] <= p["superior"]).all()
    assert (projetar(y * 0 + np.linspace(5, 0.1, 8), minimo=0)["inferior"] >= 0).all()
    assert (projetar(pd.Series(np.linspace(0.5, 0.99, 8), index=range(2017, 2025)), maximo=1.0)["superior"] <= 1).all()


def test_projecao_exige_pontos_e_ignora_ausentes():
    from motor.analise import projetar
    assert projetar(pd.Series([1.0, 2, 3, 4], index=range(2021, 2025))) is None
    y = pd.Series([1.0, 2, np.nan, 4, 5, 6], index=range(2019, 2025))
    assert projetar(y)["previsto"].iloc[0] == pytest.approx(7)
