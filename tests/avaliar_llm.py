"""Avaliação dos interpretadores (regras × modelo de linguagem local × híbrido) em perguntas parafraseadas.

Uso: python -I tests/avaliar_llm.py [modelo ...]      (padrão: qwen2.5:3b)
Cada pergunta tem a interpretação esperada (anotada à mão). Campos comparados: indicador, tipo, anos (1º e último),
locais, listar, filtros, quebras, ordem (só ranking/crescimento), so_reducao e se pede esclarecimento.
"Exata" = todos os campos certos. Grava dados/qualidade/avaliacao_llm_<modelo>.csv e um resumo na tela.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd  # noqa: E402

from motor import llm  # noqa: E402
from motor.api import catalogo  # noqa: E402
from motor.contrato import para_json  # noqa: E402
from motor.interpretador import interpretar  # noqa: E402

ES = ["Espírito Santo"]
# (pergunta, esperado). Chaves omitidas = padrão: tipo valor, anos [2024], filtros {}, quebras [], listar None,
# ordem desc, so_reducao False, esclarece False. "tipos" = tipos aceitos quando mais de um é razoável.
PARAFRASES = [
    ("Quantos universitários tinha Cariacica em 2023?", dict(indicador="matriculas", anos=(2023, 2023), locais=["Cariacica"])),
    ("A rede particular domina o ensino superior capixaba?", dict(indicador="matriculas", tipos=["participacao"], locais=ES,
                                                                  filtros={"rede": "Privada"})),
    ("Quais as cidades do ES onde mais cresceu o número de formandos desde 2019?",
     dict(indicador="concluintes", tipos=["crescimento"], anos=(2019, 2024), locais=ES, listar="municipios")),
    ("Me diga o total de alunos de faculdades na Serra em 2022",
     dict(indicador="matriculas", anos=(2022, 2022), locais=["Serra"], filtros={"org_academica": "Faculdade"})),
    ("Em Vila Velha, o EaD cresceu mais que o presencial?",
     dict(indicador="matriculas", tipos=["comparacao", "serie"], anos=(2017, 2024), locais=["Vila Velha"], quebras=["modalidade"])),
    ("Quero ver a evolução dos calouros de Medicina no Brasil",
     dict(indicador="ingressantes", tipos=["serie"], anos=(2017, 2024), locais=["Brasil"], curso="Medicina")),
    ("Qual estado tem mais gente fazendo faculdade?", dict(indicador="matriculas", tipos=["ranking"], locais=[], listar="ufs")),
    ("Quantas pessoas se formaram em Vitória no ano de 2020?", dict(indicador="concluintes", anos=(2020, 2020), locais=["Vitória"])),
    ("Há quantas faculdades e universidades no Espírito Santo?", dict(indicador="ies", locais=ES)),
    ("Quantos professores dão aula no ensino superior de Minas Gerais?", dict(indicador="docentes_exercicio", locais=["Minas Gerais"])),
    ("Mulheres são maioria entre os estudantes capixabas?", dict(indicador="matriculas", tipos=["participacao"], locais=ES,
                                                                 filtros={"sexo": "Feminino"})),
    ("Concorrência por vaga em Direito no ES", dict(indicador="candidatos_por_vaga", locais=ES, curso="Direito")),
    ("Que cursos estão encolhendo no ES desde 2017?", dict(indicador="matriculas", tipos=["crescimento"], anos=(2017, 2024),
                                                           locais=ES, quebras=["curso"], ordem="asc", so_reducao=True)),
    ("Compare Linhares e Colatina em número de ingressantes",
     dict(indicador="ingressantes", tipos=["comparacao"], anos=(2017, 2024), locais=["Linhares", "Colatina"])),
    ("Como andam as matrículas da rede pública no Nordeste?",
     dict(indicador="matriculas", tipos=["serie"], anos=(2017, 2024), locais=["Nordeste"], filtros={"rede": "Pública"})),
    ("Qual a distribuição por cor ou raça dos formandos do ES em 2022?",
     dict(indicador="concluintes", anos=(2022, 2022), locais=ES, quebras=["cor_raca"])),
    ("Quantas vagas de licenciatura foram oferecidas em Cachoeiro de Itapemirim em 2024?",
     dict(indicador="vagas", locais=["Cachoeiro de Itapemirim"], filtros={"grau": "Licenciatura"})),
    ("Quais os 5 municípios capixabas com menos matrículas?",
     dict(indicador="matriculas", tipos=["ranking"], locais=ES, listar="municipios", ordem="asc")),
    ("O número de inscritos no Brasil caiu nos últimos 3 anos?",
     dict(indicador="inscritos", tipos=["serie"], anos=(2022, 2024), locais=["Brasil"])),
    ("Qual o tamanho do ensino a distância em Guarapari?",
     dict(indicador="matriculas", locais=["Guarapari"], filtros={"modalidade": "A Distância"})),
    ("Qual a cotação do dólar hoje?", dict(indicador=None, esclarece=True)),
    ("Quantos alunos estudam em instituições privadas com fins lucrativos no ES?",
     dict(indicador="matriculas", locais=ES, filtros={"categoria_privada": "Com Fins Lucrativos"})),
    ("Faixa etária dos ingressantes de Vitória em 2024", dict(indicador="ingressantes", locais=["Vitória"], quebras=["faixa_etaria"])),
    ("Quantas instituições de ensino superior federais existem no Rio de Janeiro?",
     dict(indicador="ies", locais=["Rio de Janeiro"], filtros={"dependencia": "Federal"})),
]


# Conjunto de CONTROLE (escrito em 31/10/2026 depois do ajuste das regras; nada foi ajustado depois de rodá-lo).
# Mede a generalização: o conjunto PARAFRASES acima foi usado para corrigir as regras e não serve para isso.
CONTROLE = [
    ("Quantos estudantes de graduação havia em Linhares no último ano disponível?", dict(indicador="matriculas", locais=["Linhares"])),
    ("Em que municípios do Espírito Santo há mais vagas oferecidas?", dict(indicador="vagas", tipos=["ranking"], locais=ES, listar="municipios")),
    ("Total de concluintes em São Mateus de 2019 a 2022", dict(indicador="concluintes", tipos=["serie"], anos=(2019, 2022), locais=["São Mateus"])),
    ("Pernambuco ou Ceará: qual tem mais ingressantes?", dict(indicador="ingressantes", tipos=["comparacao"], anos=(2017, 2024), locais=["Pernambuco", "Ceará"])),
    ("Percentual de alunos em universidades no ES em 2023", dict(indicador="matriculas", tipos=["participacao"], anos=(2023, 2023), locais=ES, filtros={"org_academica": "Universidade"})),
    ("Como variou o número de docentes no Brasil entre 2017 e 2024?", dict(indicador="docentes_exercicio", tipos=["serie"], anos=(2017, 2024), locais=["Brasil"])),
    ("Ranking dos estados por concluintes em 2022", dict(indicador="concluintes", tipos=["ranking"], anos=(2022, 2022), locais=[], listar="ufs")),
    ("Quantos ingressantes homens em Vitória em 2024?", dict(indicador="ingressantes", locais=["Vitória"], filtros={"sexo": "Masculino"})),
    ("Matrículas em cursos tecnológicos na Grande Vitória em 2024", dict(indicador="matriculas", locais=["Grande Vitória"], filtros={"grau": "Tecnológico"})),
    ("Qual curso tem mais concluintes no Brasil?", dict(indicador="concluintes", tipos=["ranking"], locais=["Brasil"], quebras=["curso"])),
    ("Evolução das vagas EaD no Brasil", dict(indicador="vagas", tipos=["serie"], anos=(2017, 2024), locais=["Brasil"], filtros={"modalidade": "A Distância"})),
    ("Quantos inscritos por vaga em Medicina no Brasil em 2024?", dict(indicador="candidatos_por_vaga", locais=["Brasil"], curso="Medicina")),
    ("Quais municípios capixabas perderam ingressantes entre 2019 e 2024?", dict(indicador="ingressantes", tipos=["crescimento"], anos=(2019, 2024), locais=ES, listar="municipios", ordem="asc", so_reducao=True)),
    ("Quantas IES privadas há em Vila Velha?", dict(indicador="ies", locais=["Vila Velha"], filtros={"rede": "Privada"})),
    ("Me mostre os ingressantes por cor/raça no Sudeste em 2021", dict(indicador="ingressantes", anos=(2021, 2021), locais=["Sudeste"], quebras=["cor_raca"])),
    ("Qual o melhor time de futebol do Espírito Santo?", dict(indicador=None, esclarece=True)),
]


def esperado_ids(e, cat):
    ids = []
    for nome in e.get("locais", []):
        idg, _, erro = llm._resolver_local(nome, cat)
        assert not erro, (nome, erro)
        ids.append(idg)
    return ids


def comparar(j, e, cat):
    """j = JSON do contrato produzido (ou None); e = esperado. Devolve dict campo → certo?"""
    esclarece = e.get("esclarece", False)
    if j is None or j.get("esclarecer"):
        return {"esclarecimento": esclarece}
    if esclarece:
        return {"esclarecimento": False}
    filtros = dict(j.get("filtros") or {})
    curso = filtros.pop("curso", None)
    if "categoria_privada" in filtros:      # rede/dependência = Privada é redundante com a categoria privada (mesmos dados)
        for d in ("rede", "dependencia"):
            if filtros.get(d) == "Privada":
                del filtros[d]
    f = {
        "indicador": j["indicador"] == e["indicador"],
        "tipo": j["tipo"] in e.get("tipos", ["valor"]),
        "anos": (min(j["anos"]), max(j["anos"])) == e.get("anos", (2024, 2024)) if j["anos"] else False,
        "locais": set(j["locais"]) == set(esperado_ids(e, cat)) or (e.get("listar") == "ufs" and not j["locais"]),
        "listar": (("municipios" if j.get("listar_municipios_uf") else "ufs" if j.get("listar_ufs") else None)
                   == e.get("listar")),
        "filtros": filtros == e.get("filtros", {}),
        "curso": (curso is not None and cat.nome_curso.get(curso, "").lower() == e["curso"].lower()) if e.get("curso")
                 else curso is None,
        "quebras": set(j.get("quebras", [])) == set(e.get("quebras", [])),
    }
    if j["tipo"] in ("ranking", "crescimento"):
        f["ordem"] = j.get("ordem", "desc") == e.get("ordem", "desc")
        f["so_reducao"] = bool(j.get("so_reducao")) == e.get("so_reducao", False)
    return f


def avaliar(nome, interpretar_fn, cat, conjunto=None):
    linhas = []
    for p, e in (conjunto or PARAFRASES):
        t0 = time.time()
        j, origem = interpretar_fn(p)
        f = comparar(j, e, cat)
        linhas.append({"interpretador": nome, "pergunta": p, "exata": all(f.values()), "erros": ",".join(k for k, v in f.items() if not v),
                       "origem": origem, "segundos": round(time.time() - t0, 1)})
        print(f"[{nome}] {'OK ' if all(f.values()) else 'ERR'} {linhas[-1]['segundos']:5.1f}s {origem:6s} {p} {linhas[-1]['erros']}", flush=True)
    return pd.DataFrame(linhas)


def main():
    cat = catalogo()
    controle = "--controle" in sys.argv
    modelos = [a for a in sys.argv[1:] if not a.startswith("--")] or ["qwen2.5:3b"]
    conjunto = CONTROLE if controle else PARAFRASES

    def regras(p):
        c = interpretar(p, cat)
        return para_json(c), "regras"

    def via_llm(modelo):
        def f(p):
            c, meta = llm.interpretar_llm(p, cat, modelo)
            return (para_json(c) if c else meta.get("contrato")), "llm"
        return f

    def hibrido(modelo):
        def f(p):
            c = interpretar(p, cat)
            if not c.nao_entendida:
                return para_json(c), "regras"
            return via_llm(modelo)(p)
        return f

    res = [avaliar("regras", regras, cat, conjunto)]
    for m in modelos:
        res.append(avaliar(f"llm:{m}", via_llm(m), cat, conjunto))
        res.append(avaliar(f"hibrido:{m}", hibrido(m), cat, conjunto))
    df = pd.concat(res, ignore_index=True)
    saida = Path(__file__).resolve().parent.parent / "dados" / "qualidade" / f"avaliacao_llm_{'controle_' if controle else ''}{'_'.join(m.replace(':', '-') for m in modelos)}.csv"
    df.to_csv(saida, sep=";", index=False, encoding="utf-8-sig")
    resumo(df, saida)


def resumo(df, saida):
    df = df.fillna({"erros": ""})
    print("\nRESUMO (n =", df.pergunta.nunique(), "perguntas)")
    print(df.groupby("interpretador").agg(exatas=("exata", "sum"), tempo_medio_s=("segundos", "mean"),
                                          tempo_max_s=("segundos", "max")).to_string())
    print("erros por campo:")
    print(df[df.erros != ""].assign(erro=df.erros.str.split(",")).explode("erro").groupby(["interpretador", "erro"]).size().to_string())
    print(saida)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--resumo"]:
        resumo(pd.read_csv(sys.argv[2], sep=";", encoding="utf-8-sig"), sys.argv[2])
    else:
        main()
