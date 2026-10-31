"""Regressão: cada teste corresponde a um erro encontrado pela bateria de perguntas de 30/10/2026 (bateria_antes).
Os valores de referência vêm de consultas independentes nas tabelas de fato (ver test_referencias.py)."""
import pytest

from conftest import um
from motor.api import perguntar
from motor.interpretador import interpretar
from test_referencias import TOT, anexos_uf


# R01 — temas fora do motor respondiam "matrículas totais" em silêncio ("reserva" virava o município Reserva/PR)
@pytest.mark.parametrize("p, tema", [
    ("Quantos alunos com deficiência no ES?", "deficiência"),
    ("Quantos estudantes têm FIES no ES?", "financiamento"),
    ("Matrículas por reserva de vagas no ES", "reserva de vagas"),
    ("Taxa de evasão em Vitória", "evasão"),
])
def test_r01_tema_indisponivel_explica(cat, p, tema):
    r = perguntar(p)
    assert r.precisa_esclarecer and tema in r.texto.lower() and r.tabela is None


# R02 — "candidatos por vaga" respondia só inscritos; agora razão Σinscritos ÷ Σvagas
def test_r02_candidatos_por_vaga(ref):
    r = perguntar("Relação candidatos por vaga no ES em 2024")
    insc = anexos_uf(ref, "inscritos", 2024, "32")
    vagas = anexos_uf(ref, "vagas", 2024, "32")
    assert r.tabela["valor"].iloc[0] == pytest.approx(insc / vagas)
    assert "1,87" in r.texto


def test_r02_razao_de_grupo_soma_antes_de_dividir(ref, cat):
    r = perguntar("Candidatos por vaga na Grande Vitória em 2024")
    ids = [l for l in interpretar("Grande Vitória", cat).locais][0].membros
    q = f"""SELECT sum(valor) FROM fato_anexo_curso WHERE nivel_geo='Município' AND id_recorte={TOT} AND ano=2024
            AND indicador=? AND list_contains(?, id_geo)"""
    assert r.tabela["valor"].iloc[0] == pytest.approx(um(ref, q, ["inscritos", list(ids)]) / um(ref, q, ["vagas", list(ids)]))


def test_r02_participacao_de_razao_pede_esclarecimento():
    assert perguntar("Qual a participação dos candidatos por vaga no ES?").precisa_esclarecer


# R03 — "total estadual" virava filtro dependência = Estadual
def test_r03_total_estadual_nao_e_dependencia(cat):
    c = interpretar("Qual é a participação de cada município no total estadual de matrículas do ES em 2024?", cat)
    assert "dependencia" not in c.filtros and c.listar_municipios_uf == "32" and c.tipo == "ranking"
    assert c.top_n >= 78


def test_r03_rede_estadual_continua_filtro(cat):
    assert interpretar("matrículas na rede estadual do ES", cat).filtros.get("dependencia") == "Estadual"


# R04 — "quais municípios/cursos perderam/apresentaram redução" devolvia os maiores
def test_r04_municipios_com_reducao(ref):
    r = perguntar("Quais municípios do ES apresentaram redução de matrículas entre 2017 e 2024?")
    assert (r.tabela["variação_absoluta"] < 0).all() and len(r.tabela) >= 1
    v = ref.execute(f"""SELECT sum(valor) FILTER (WHERE ano=2024) - sum(valor) FILTER (WHERE ano=2017)
        FROM fato_anexo_curso WHERE nivel_geo='Município' AND id_geo='3205309' AND id_recorte={TOT}
        AND indicador='matriculas'""").fetchall()[0][0]
    assert r.tabela.iloc[0]["nome"].startswith("Vitória") and r.tabela.iloc[0]["variação_absoluta"] == v


def test_r04_cursos_que_mais_perderam():
    r = perguntar("Quais cursos mais perderam matrículas no ES entre 2017 e 2024?")
    assert (r.tabela["variação_absoluta"] < 0).all()
    assert r.tabela["variação_absoluta"].is_monotonic_increasing


# R05 — "quais municípios possuem maior participação" calculava a participação do ES no Brasil
def test_r05_participacao_de_municipios_e_ranking(cat):
    c = interpretar("Quais municípios possuem maior participação nas matrículas do ES?", cat)
    assert c.tipo == "ranking" and c.listar_municipios_uf == "32"
    r = perguntar("Quais municípios possuem maior participação nas matrículas do ES?")
    assert r.tabela["participação_no_conjunto"].iloc[0] == pytest.approx(50417 / 182335)


# R06 — "por sexo e cor/raça" ignorava a cor/raça em silêncio
def test_r06_duas_dimensoes_da_sinopse_pede_esclarecimento(cat):
    c = interpretar("Ingressantes por sexo e cor/raça no ES em 2024", cat)
    assert {"sexo", "cor_raca"} <= set(c.quebras)
    assert perguntar("Ingressantes por sexo e cor/raça no ES em 2024").precisa_esclarecer


# R07 — "comparadas com 2017" devolvia só 2017
def test_r07_comparado_com_ano(cat):
    c = interpretar("Matrículas em Vitória comparadas com 2017", cat)
    assert c.anos[0] == 2017 and c.anos[-1] == 2024


# R08 — "em qual ano houve maior crescimento/redução": a resposta não trazia a variação ano a ano
def test_r08_variacao_anual():
    r = perguntar("Em qual ano houve a maior redução das matrículas presenciais no ES?")
    assert "maior queda anual: 2020→2021" in r.texto and "nenhuma alta anual" in r.texto


# R10 — "participação das mulheres nas matrículas da rede privada" usava o total geral como denominador
def test_r10_participacao_com_universo(ref):
    r = perguntar("Qual a participação das mulheres nas matrículas da rede privada do ES em 2024?")
    fem_priv = um(ref, """SELECT sum(valor) FROM mart_sinopse_geo WHERE id_geo='UF-32' AND ano=2024 AND indicador='matriculas'
                          AND dimensao='sexo' AND categoria='Feminino' AND rede='Privada'""")
    priv = anexos_uf(ref, "matriculas", 2024, "32") - um(ref, f"""SELECT sum(valor) FROM fato_anexo_curso f
        JOIN dim_geografia g USING (id_geo) JOIN dim_recorte r USING (id_recorte)
        WHERE f.nivel_geo='Município' AND g.co_uf='32' AND f.ano=2024 AND f.indicador='matriculas'
          AND r.dependencia IN ('Federal','Estadual','Municipal') AND r.org_academica<>'Total' AND r.grau<>'Total'
          AND r.categoria_privada<>'Total'""")
    assert r.tabela["todo"].iloc[0] == priv
    assert r.tabela["participação"].iloc[0] == pytest.approx(fem_priv / priv)


def test_r10_sexo_por_rede_bate_com_anexos(ref):
    r = perguntar("Matrículas de mulheres e homens por rede no ES em 2024")
    assert r.tabela["valor"].sum() == anexos_uf(ref, "matriculas", 2024, "32")


# R09 — texto todo em maiúsculas: "SE" (conjunção) não pode virar Sergipe
def test_r09_caixa_alta_se_nao_e_sergipe(cat):
    c = interpretar("QUANTAS MATRÍCULAS SE TEM EM VITÓRIA EM 2024?", cat)
    assert [l.id_geo for l in c.locais] == ["3205309"]


def test_r09_sigla_se_em_texto_normal(cat):
    assert "UF-28" in [l.id_geo for l in interpretar("matrículas em SE em 2024", cat).locais]
