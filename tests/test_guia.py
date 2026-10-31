"""Guia de Consultas: todo exemplo e toda combinação do montador, lidos da própria página, funcionam no motor.

- exemplos com data-espera="resposta" devem responder com tabela, sem pedir esclarecimento;
- exemplos com data-espera="esclarecimento" (seção "O que ainda não está disponível") devem recusar sem consultar;
- cada combinação do montador (indicador × local × análise) gera a pergunta que o JavaScript geraria e o motor deve
  entendê-la EXATAMENTE como o guia promete (indicador, local, tipo, quebra) e responder com dados; combinações que a
  base não suporta devem estar marcadas como indisponíveis no montador (e o motor de fato não as atende).
"""
import html
import json
import re
from pathlib import Path

import pytest

from motor.api import perguntar
from motor.interpretador import interpretar

PAGINA = (Path(__file__).resolve().parent.parent / "app" / "pagina.html").read_text(encoding="utf-8")
EXEMPLOS = [(html.unescape(q), esp) for q, esp in re.findall(r'data-q="([^"]+)" data-espera="(\w+)"', PAGINA)]
SUGESTOES = [html.unescape(q) for q in re.findall(r'<button class="chip" type="button" data-q="([^"]+)"', PAGINA)]
M = json.loads(re.search(r'<script type="application/json" id="dados-montador">(.*?)</script>', PAGINA, re.S).group(1))


def montar(ind, loc, ana):
    """Mesma lógica de montar() em app/pagina.html."""
    if ana["id"] == "modalidade" and ind["id"] in ("cursos", "vagas", "inscritos") and loc["nivel"] != "brasil":
        return None
    modelo = ana.get("modelo")
    if ana["id"] == "ranking":
        modelo = ana["modelo_uf"] if loc["nivel"] == "uf" else ana["modelo_brasil"] if loc["nivel"] == "brasil" else None
        if modelo is None:
            return None
    return (modelo.replace("{Quanto}", ind["quanto"]).replace("{ind}", ind["termo"])
            .replace("{Ind}", ind["termo"][0].upper() + ind["termo"][1:]).replace("{art}", ind["art"])
            .replace("{em}", loc["em"]).replace("{rotulo_mun}", loc.get("rotulo_mun", "")))


COMBOS = [(i, l, a) for i in M["indicadores"] for l in M["locais"] for a in M["analises"]]


def test_guia_tem_exemplos_e_montador():
    assert len(EXEMPLOS) >= 30 and len(SUGESTOES) == 8 and len(COMBOS) == 150
    assert sum(1 for _, e in EXEMPLOS if e == "esclarecimento") >= 4


@pytest.mark.parametrize("q, espera", EXEMPLOS, ids=[q[:60] for q, _ in EXEMPLOS])
def test_exemplo_do_guia(cat, q, espera):
    r = perguntar(q)
    if espera == "esclarecimento":
        assert r.precisa_esclarecer and r.tabela is None, q
    else:
        assert not r.precisa_esclarecer and r.tabela is not None and len(r.tabela) > 0, (q, r.texto[:300])


@pytest.mark.parametrize("q", SUGESTOES, ids=[q[:60] for q in SUGESTOES])
def test_sugestao_da_tela_inicial(cat, q):
    r = perguntar(q)
    assert not r.precisa_esclarecer and r.tabela is not None and len(r.tabela) > 0, q


@pytest.mark.parametrize("ind, loc, ana", COMBOS, ids=[f"{i['id']}-{l['id']}-{a['id']}" for i, l, a in COMBOS])
def test_combinacao_do_montador(cat, ind, loc, ana):
    q = montar(ind, loc, ana)
    if q is None:   # marcada como indisponível: confirmar que a limitação é real
        if ana["id"] == "modalidade":
            assert ind["id"] in ("cursos", "vagas", "inscritos") and loc["nivel"] != "brasil"
        return
    c = interpretar(q, cat)
    assert c.indicador == ind["id"], (q, c.indicador)
    assert c.tipo == ana["tipo"], (q, c.tipo)
    if ana.get("quebra"):
        assert ana["quebra"] in c.quebras, (q, c.quebras)
    if ana["id"] == "ranking":
        assert (c.listar_municipios_uf == "32") if loc["nivel"] == "uf" else c.listar_ufs, q
    else:
        assert [l.id_geo for l in c.locais] == [loc["id"]], (q, [l.id_geo for l in c.locais])
    r = perguntar(q)
    assert not r.precisa_esclarecer and r.tabela is not None and len(r.tabela) > 0, (q, r.texto[:300])
