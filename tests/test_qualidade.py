"""Marcações de qualidade no núcleo (Q10 célula a célula, Q13) e como o motor as reconhece."""
from pathlib import Path

import pandas as pd
import pytest

from conftest import um
from motor.api import perguntar

CSV = Path(__file__).resolve().parent.parent / "config" / "q10_celulas_suspeitas.csv"


@pytest.fixture(scope="module")
def q10():
    return pd.read_csv(CSV, encoding="utf-8-sig", dtype={"tabela": str, "coluna": str})


def test_q10_todas_as_suspeitas_marcadas_e_valores_intactos(ref, q10):
    s = q10[q10.papel == "suspeita"]
    ref.register("v_s", s[["ano", "tabela", "linha", "coluna", "valor"]])
    r = ref.execute("""SELECT count(*), count(*) FILTER (WHERE f.status_valor = 'suspeito' AND f.id_ocorrencia = 'Q10'),
                              count(*) FILTER (WHERE f.valor IS NOT DISTINCT FROM s.valor)
                       FROM v_s s JOIN fato_sinopse f USING (ano, tabela, linha, coluna)""").fetchall()[0]
    assert r == (len(s), len(s), len(s)) == (26809, 26809, 26809)


def test_q10_relacionadas_nao_marcadas(ref, q10):
    rel = q10[q10.papel == "relacionada"]
    ref.register("v_r", rel[["ano", "tabela", "linha", "coluna"]])
    assert um(ref, """SELECT count(*) FROM v_r JOIN fato_sinopse f USING (ano, tabela, linha, coluna)
                      WHERE f.id_ocorrencia = 'Q10'""") == 0


def test_q10_so_nos_anos_e_tabelas_documentados(ref):
    fora = um(ref, """SELECT count(*) FROM fato_sinopse WHERE id_ocorrencia = 'Q10'
                      AND NOT (tabela IN ('6.3', '6.6') AND ano IN (2017, 2018, 2019, 2023))""")
    assert fora == 0


def test_q10_nao_marca_tabela_inteira(ref):
    tot, marc = ref.execute("""SELECT count(*), count(*) FILTER (WHERE id_ocorrencia = 'Q10') FROM fato_sinopse
                               WHERE tabela IN ('6.3', '6.6') AND ano IN (2017, 2018, 2019, 2023)""").fetchall()[0]
    assert 0 < marc / tot < 0.02


def test_q13_7_4_abaixo_do_brasil_nao_e_informado(ref):
    assert um(ref, """SELECT count(*) FROM fato_sinopse WHERE tabela = '7.4' AND indicador IN ('cursos','vagas','inscritos')
                      AND nivel_geo <> 'Brasil' AND status_valor = 'informado'""") == 0
    assert um(ref, """SELECT count(*) FROM fato_sinopse WHERE tabela = '7.4' AND status_valor = 'somente_presencial'""") == 45858
    assert um(ref, """SELECT count(*) FROM fato_sinopse WHERE tabela = '7.4' AND nivel_geo = 'Brasil'
                      AND status_valor = 'somente_presencial'""") == 0


def test_motor_avisa_q10_quando_usa_celula_marcada(ref):
    r = perguntar("Concluintes por cor/raça no Brasil em 2017")
    assert "Q10" in r.texto and "suspeitas" in r.texto


def test_motor_nao_avisa_q10_sem_celula_marcada(ref):
    # município com valores de 6.6 em 2018 sem nenhuma célula Q10 nas folhas de cor/raça
    idg, nome = ref.execute("""SELECT m.id_geo, g.no_municipio FROM mart_sinopse_geo m JOIN dim_geografia g USING (id_geo)
        WHERE m.tabela = '6.6' AND m.ano = 2018 AND m.nivel_geo = 'Município' AND g.co_uf = '32'
        GROUP BY ALL HAVING NOT bool_or(m.tem_suspeito) AND sum(m.valor) > 100 ORDER BY sum(m.valor) DESC LIMIT 1""").fetchall()[0]
    r = perguntar(f"Concluintes por cor/raça em {nome} em 2018")
    assert r.tabela is not None and "Q10" not in r.texto, idg


def test_compatibilidade_lista_q13(ref):
    assert "Q13" in perguntar("Quais mudanças metodológicas prejudicam a comparação entre anos?").texto
