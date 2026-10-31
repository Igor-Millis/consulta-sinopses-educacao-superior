"""Respostas do motor × consultas de referência INDEPENDENTES, feitas direto nas tabelas de fato do núcleo
(fato_anexo_curso, fato_sinopse), sem passar pelos marts nem pelo interpretador."""
import pytest

from conftest import um
from motor.api import perguntar

TOT = """(SELECT id_recorte FROM dim_recorte WHERE org_academica='Total' AND grau='Total'
          AND dependencia='Total' AND categoria_privada='Total')"""


def anexos_mun(ref, indicador, ano, ids, extra=""):
    return um(ref, f"""SELECT sum(valor) FROM fato_anexo_curso WHERE nivel_geo='Município' AND id_recorte={TOT}
                       AND indicador=? AND ano=? AND list_contains(?, id_geo) {extra}""", [indicador, ano, ids])


def anexos_uf(ref, indicador, ano, co_uf, anexo=None):
    extra = f"AND anexo = '{anexo}'" if anexo else ""
    return um(ref, f"""SELECT sum(valor) FROM fato_anexo_curso f JOIN dim_geografia g USING (id_geo)
                       WHERE f.nivel_geo='Município' AND id_recorte={TOT} AND indicador=? AND ano=? AND g.co_uf=? {extra}""",
              [indicador, ano, co_uf])


def sinopse_total(ref, tabela, ano, id_geo):
    return um(ref, """SELECT f.valor FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
        WHERE f.tabela=? AND f.ano=? AND f.id_geo=? AND f.nivel_academico IN ('Graduação', 'Total')
          AND r.org_academica='Total' AND r.dependencia='Total' AND r.categoria_privada='Total'
          AND r.sexo='Total' AND r.cor_raca='Total' AND r.faixa_etaria='Total' AND r.modalidade='Total'
        ORDER BY f.nivel_academico LIMIT 1""", [tabela, ano, id_geo])


def test_vila_velha_2024(ref):
    r = perguntar("Quantas matrículas havia em Vila Velha em 2024?")
    esperado = anexos_mun(ref, "matriculas", 2024, ["3205200"])
    assert r.tabela["valor"].iloc[0] == esperado == 27743


def test_es_total_igual_sinopse_5_1(ref):
    r = perguntar("Quantas matrículas havia no Espírito Santo em 2024?")
    assert r.tabela["valor"].iloc[0] == sinopse_total(ref, "5.1", 2024, "UF-32") == 182335


@pytest.mark.parametrize("ano", [2017, 2020, 2024])
def test_serie_es_ano_a_ano(ref, ano):
    r = perguntar("Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?")
    assert r.tabela.loc[ano].iloc[0] == anexos_uf(ref, "matriculas", ano, "32")


def test_participacao_ead_es(ref):
    r = perguntar("Qual a participação do EaD nas matrículas do Espírito Santo em 2024?")
    ead = anexos_uf(ref, "matriculas", 2024, "32", "anexo_iii")
    tot = anexos_uf(ref, "matriculas", 2024, "32")
    assert r.tabela["participação"].iloc[0] == pytest.approx(ead / tot)


def test_ranking_municipios_es(ref):
    r = perguntar("Quais os 10 municípios capixabas com mais matrículas em 2024?")
    lider = ref.execute(f"""SELECT g.no_municipio, sum(valor) v FROM fato_anexo_curso f JOIN dim_geografia g USING (id_geo)
        WHERE f.nivel_geo='Município' AND id_recorte={TOT} AND indicador='matriculas' AND ano=2024 AND g.co_uf='32'
        GROUP BY 1 ORDER BY 2 DESC LIMIT 1""").fetchall()[0]
    assert r.tabela["nome"].iloc[0].startswith(lider[0]) and r.tabela["valor"].iloc[0] == lider[1]
    assert len(r.tabela) == 10


def test_grande_vitoria_por_sexo_fecha_com_anexos(ref, cat):
    r = perguntar("Matrículas por sexo na Grande Vitória em 2023")
    membros = [l for l in cat.aliases["grande vitoria"]["municipios"]]
    ids = [next(l.id_geo for l in cat.nomes_municipio[__import__("motor").semantica.normalizar(m)] if l.co_uf == "32")
           for m in membros]
    assert r.tabela["valor"].sum() == anexos_mun(ref, "matriculas", 2023, ids)


def test_direito_vitoria(ref):
    r = perguntar("Matrículas em Direito em Vitória de 2017 a 2024")
    esperado = um(ref, f"""SELECT sum(valor) FROM fato_anexo_curso f LEFT JOIN xw_cine x USING (co_cine)
        WHERE nivel_geo='Município' AND id_geo='3205309' AND id_recorte={TOT} AND indicador='matriculas' AND ano=2017
          AND coalesce(x.co_cine_ref, f.co_cine)='0421D01'""")
    assert r.tabela.loc[2017].iloc[0] == esperado


def test_ies_es_por_rede_soma_total(ref):
    r = perguntar("Quantas instituições de ensino superior há no ES por rede em 2024?")
    assert r.tabela["valor"].sum() == sinopse_total(ref, "1.1", 2024, "UF-32")


def test_docentes_valor_publicado(ref):
    r = perguntar("Quantos docentes no Rio Grande do Sul em 2022?")
    assert r.tabela["valor"].iloc[0] == sinopse_total(ref, "2.1", 2022, "UF-43")


def test_vagas_ead_municipio_nao_inventa(ref):
    r = perguntar("Quantas vagas a distância em Vitória?")
    assert r.precisa_esclarecer and "Brasil" in r.texto


def test_pergunta_sem_indicador_nao_consulta():
    r = perguntar("Como está Vitória em 2024?")
    assert r.precisa_esclarecer


def test_resposta_tem_fontes_e_limitacoes():
    r = perguntar("Compare Vitória e Serra em concluintes")
    assert "**Fontes**" in r.texto and "Vitória (ES)" in r.texto
    assert "Q10" not in r.texto               # dados dos Anexos: a ocorrência das tabelas 6.3/6.6 não se aplica


def test_q10_aparece_quando_usa_6_6():
    r = perguntar("Concluintes por cor/raça no Espírito Santo em 2018")
    assert "Q10" in r.texto
