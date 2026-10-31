"""Contrato JSON da Consulta (ponto de integração de um modelo de linguagem) e gabarito de interpretações."""
import json
from pathlib import Path

import pandas as pd
import pytest

from gerar_gold import gabarito
from motor.api import perguntar, perguntar_estruturado
from motor.contrato import de_json, esquema, para_json
from motor.interpretador import interpretar

GOLD = [json.loads(x) for x in (Path(__file__).parent / "gold_interpretacoes.jsonl").read_text(encoding="utf-8").splitlines()]


@pytest.mark.parametrize("item", GOLD, ids=[g["pergunta"][:50] for g in GOLD])
def test_gabarito_de_interpretacao(cat, item):
    """O interpretador por regras continua produzindo a interpretação revisada (regressão de interpretação)."""
    assert gabarito(interpretar(item["pergunta"], cat)) == item["esperado"]


@pytest.mark.parametrize("item", GOLD, ids=[g["pergunta"][:50] for g in GOLD])
def test_ida_e_volta(cat, item):
    c = interpretar(item["pergunta"], cat)
    j = json.loads(json.dumps(para_json(c), ensure_ascii=False))
    c2, erros = de_json(j, cat, item["pergunta"])
    if c.esclarecer:                 # interpretação incompleta (ex.: ano 2015): o contrato pode recusar, nunca aceitar errado
        assert c2 is None or c2.esclarecer
        return
    assert not erros, erros
    assert para_json(c2) == para_json(c)


def test_esquema_e_serializavel(cat):
    e = esquema(cat)
    json.dumps(e, ensure_ascii=False)
    assert "candidatos_por_vaga" in e["properties"]["indicador"]["enum"]
    assert "A Distância" in e["properties"]["filtros"]["properties"]["modalidade"]["enum"]


@pytest.mark.parametrize("ruim, trecho", [
    ({"indicador": "salario", "tipo": "valor", "anos": [2024], "locais": ["UF-32"]}, "indicador inexistente"),
    ({"indicador": "matriculas", "tipo": "valor", "anos": [2030], "locais": ["UF-32"]}, "anos"),
    ({"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": ["UF-99"]}, "local inexistente"),
    ({"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": ["UF-32"], "filtros": {"sexo": "Outro"}}, "filtro"),
    ({"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": ["UF-32"], "sql": "DROP TABLE x"}, "campos desconhecidos"),
    ({"indicador": "matriculas", "tipo": "apagar", "anos": [2024], "locais": ["UF-32"]}, "tipo"),
    ({"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": ["UF-32"], "filtros": {"curso": "XXXX"}}, "curso"),
    ("não é json", "objeto"),
])
def test_contrato_recusa_invalido(cat, ruim, trecho):
    c, erros = de_json(ruim, cat)
    assert c is None and any(trecho in e for e in erros)


def test_perguntar_estruturado_recusa_sem_consultar():
    r = perguntar_estruturado({"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": ["UF-99"]})
    assert r.precisa_esclarecer and "UF-99" in r.texto and r.tabela is None


@pytest.mark.parametrize("p", [
    "Quantas matrículas havia em Vila Velha em 2024?",
    "Matrículas por sexo na Grande Vitória em 2023",
    "Relação candidatos por vaga no ES em 2024",
    "Quais municípios do ES apresentaram redução de matrículas entre 2017 e 2024?",
])
def test_caminho_estruturado_da_mesma_resposta(cat, p):
    a = perguntar(p)
    b = perguntar_estruturado(para_json(interpretar(p, cat)), p)
    pd.testing.assert_frame_equal(a.tabela.reset_index(drop=True), b.tabela.reset_index(drop=True))
