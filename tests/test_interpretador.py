"""Interpretação das perguntas: estrutura esperada, suposições explícitas e pedidos de esclarecimento."""
from motor.interpretador import interpretar


def ids(c):
    return [l.id_geo for l in c.locais]


def test_valor_simples(cat):
    c = interpretar("Quantas matrículas havia em Vila Velha em 2024?", cat)
    assert (c.indicador, c.tipo, c.anos) == ("matriculas", "valor", [2024])
    assert ids(c) == ["3205200"]


def test_intervalo_de_anos_e_serie(cat):
    c = interpretar("Como evoluíram os ingressantes no Espírito Santo entre 2018 e 2022?", cat)
    assert c.indicador == "ingressantes" and c.tipo == "serie" and c.anos == [2018, 2019, 2020, 2021, 2022]
    assert ids(c) == ["UF-32"]


def test_ultimos_n_anos_vira_suposto(cat):
    c = interpretar("matrículas no ES nos últimos 3 anos", cat)
    assert c.anos == [2022, 2023, 2024]
    assert any("últimos 3 anos" in s for s in c.supostos)


def test_rio_grande_do_sul_nao_vira_regiao_sul(cat):
    c = interpretar("docentes no Rio Grande do Sul em 2022", cat)
    assert ids(c) == ["UF-43"]


def test_regiao(cat):
    c = interpretar("matrículas na região Sul em 2024", cat)
    assert ids(c) == ["REG-Sul"]


def test_grande_vitoria_e_grupo_de_7(cat):
    c = interpretar("matrículas na Grande Vitória em 2023", cat)
    assert c.locais[0].nivel == "Grupo" and len(c.locais[0].membros) == 7


def test_ranking_municipios_capixabas(cat):
    c = interpretar("Quais os 5 municípios capixabas com mais concluintes?", cat)
    assert c.tipo == "ranking" and c.listar_municipios_uf == "32" and c.top_n == 5


def test_crescimento_de_cursos_percentual(cat):
    c = interpretar("Quais cursos tiveram maior crescimento percentual de matrículas no ES entre 2019 e 2024?", cat)
    assert c.tipo == "crescimento" and c.criterio == "percentual" and "curso" in c.quebras
    assert c.anos[0] == 2019 and c.anos[-1] == 2024


def test_participacao_ead(cat):
    c = interpretar("Qual a participação do EaD nas matrículas do Espírito Santo em 2024?", cat)
    assert c.tipo == "participacao" and c.filtros == {"modalidade": "A Distância"}


def test_duas_categorias_viram_quebra(cat):
    c = interpretar("Compare matrículas presenciais e a distância no ES", cat)
    assert "modalidade" in c.quebras and "modalidade" not in c.filtros


def test_curso_pelo_nome(cat):
    c = interpretar("matrículas em Direito em Vitória em 2020", cat)
    assert c.filtros.get("curso") == "0421D01" and ids(c) == ["3205309"]


def test_sem_indicador_pede_esclarecimento(cat):
    c = interpretar("Como está Vitória em 2024?", cat)
    assert c.esclarecer and c.indicador is None


def test_ano_fora_da_serie_pede_esclarecimento(cat):
    c = interpretar("matrículas no ES em 2015", cat)
    assert any("2015" in e for e in c.esclarecer)


def test_municipio_homonimo_prefere_es_com_suposto(cat):
    c = interpretar("matrículas em Viana em 2024", cat)
    assert ids(c) == ["3205101"] and any("Viana" in s for s in c.supostos)


def test_homonimo_fora_do_es_pede_esclarecimento(cat):
    c = interpretar("matrículas em Bom Jesus em 2024", cat)
    assert c.esclarecer


def test_sem_local_usa_brasil_com_suposto(cat):
    c = interpretar("quantos concluintes em 2024?", cat)
    assert ids(c) == ["BR"] and any("Brasil" in s for s in c.supostos)


def test_compatibilidade(cat):
    assert interpretar("Quais mudanças metodológicas prejudicam a comparação entre anos?", cat).tipo == "compatibilidade"
