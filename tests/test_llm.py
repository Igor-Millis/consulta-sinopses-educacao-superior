"""Interpretador por LLM local: resolução determinística de nomes, contrato, falhas do modelo e modo híbrido.

Quase tudo roda sem o modelo (o modelo é substituído por respostas fixas). O teste de integração só roda se o
Ollama local estiver ativo com o modelo configurado.
"""
import urllib.error

import pytest

from motor import llm
from motor.api import perguntar
from motor.contrato import de_json

BASE = {"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": [], "listar": None, "filtros": {},
        "curso": None, "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto", "so_reducao": False}


def _modelo_fixo(monkeypatch, resposta):
    monkeypatch.setattr(llm, "_chamar", lambda texto, cat, modelo: resposta)


def test_url_fixa_local():
    assert llm.URL.startswith("http://127.0.0.1:")


@pytest.mark.parametrize("nome, esperado", [("Vila Velha", "3205200"), ("Espírito Santo", "UF-32"), ("ES", "UF-32"),
                                            ("Sudeste", "REG-Sudeste"), ("região Nordeste", "REG-Nordeste"),
                                            ("Brasil", "BR"), ("Grande Vitória", "GRUPO:grande vitoria"),
                                            ("Viana", "3205101")])
def test_resolver_local(cat, nome, esperado):
    assert llm._resolver_local(nome, cat)[0] == esperado


def test_resolver_local_desconhecido_e_homonimo(cat):
    assert llm._resolver_local("Atlântida", cat)[2]
    assert "mais de um" in llm._resolver_local("Bom Jesus", cat)[2]


def test_curso(cat):
    assert llm._resolver_curso("Direito", cat) == ("0421D01", None)
    assert llm._resolver_curso("Astrologia aplicada", cat)[1]


def test_contrato_valido_vem_do_modelo(cat, monkeypatch):
    _modelo_fixo(monkeypatch, {**BASE, "locais": ["Vila Velha"]})
    c, meta = llm.interpretar_llm("x", cat)
    assert c is not None and [l.id_geo for l in c.locais] == ["3205200"] and not meta["erros"]
    assert any("modelo de linguagem" in s for s in c.supostos)


def test_campos_extras_do_modelo_sao_ignorados(cat, monkeypatch):
    _modelo_fixo(monkeypatch, {**BASE, "locais": ["Vitória"], "sql": "DROP TABLE fato_sinopse", "valor": 999999})
    c, meta = llm.interpretar_llm("x", cat)
    assert c is not None and "sql" not in meta["contrato"] and "valor" not in meta["contrato"]


def test_valor_fora_do_catalogo_e_recusado(cat, monkeypatch):
    _modelo_fixo(monkeypatch, {**BASE, "locais": ["Vitória"], "filtros": {"sexo": "Outro"}})
    c, meta = llm.interpretar_llm("x", cat)
    assert c is None and any("filtro" in e for e in meta["erros"])


def test_local_inventado_vira_esclarecimento(cat, monkeypatch):
    _modelo_fixo(monkeypatch, {**BASE, "locais": ["Atlântida"]})
    c, _ = llm.interpretar_llm("x", cat)
    assert c is not None and c.esclarecer


def test_ano_fora_vira_esclarecimento(cat, monkeypatch):
    _modelo_fixo(monkeypatch, {**BASE, "anos": [2030], "locais": ["Vitória"]})
    c, _ = llm.interpretar_llm("x", cat)
    assert c.esclarecer and any("2030" in e for e in c.esclarecer)


def test_intervalo_de_serie_expandido(cat, monkeypatch):
    _modelo_fixo(monkeypatch, {**BASE, "tipo": "serie", "anos": [2018, 2022], "locais": ["Vitória"]})
    c, _ = llm.interpretar_llm("x", cat)
    assert c.anos == [2018, 2019, 2020, 2021, 2022]


def test_modelo_fora_do_ar(cat, monkeypatch):
    def falha(*a):
        raise urllib.error.URLError("conexão recusada")
    monkeypatch.setattr(llm, "_chamar", falha)
    r = perguntar("algo totalmente fora do padrão das regras", modo="hibrido")
    assert r.precisa_esclarecer and "não produziu uma interpretação válida" in r.texto and r.tabela is None


def test_hibrido_nao_chama_modelo_quando_regras_entendem(cat, monkeypatch):
    def proibido(*a):
        raise AssertionError("o modelo não deveria ser chamado")
    monkeypatch.setattr(llm, "_chamar", proibido)
    r = perguntar("Quantas matrículas havia em Vila Velha em 2024?", modo="hibrido")
    assert r.tabela["valor"].iloc[0] == 27743 and r.interpretador == "regras"


def test_hibrido_usa_modelo_e_numero_vem_do_banco(cat, monkeypatch):
    # o "modelo" interpreta; o número (27.743) só pode vir do banco
    _modelo_fixo(monkeypatch, {**BASE, "locais": ["Vila Velha"]})
    r = perguntar("Me conta aí sobre a galera estudando em VV", modo="hibrido")
    assert r.tabela["valor"].iloc[0] == 27743 and r.interpretador.startswith("modelo de linguagem local")


@pytest.mark.skipif(not llm.disponivel(), reason="Ollama local não está ativo")
def test_integracao_modelo_real(cat):
    c, meta = llm.interpretar_llm("Quantos universitários tinha Cariacica em 2023?", cat)
    assert c is not None and c.indicador == "matriculas" and c.anos == [2023], meta
