"""Bateria extensiva de perguntas: roda cada pergunta no motor e registra interpretação, desfecho e tempo.

Uso: python -I tests/bateria_perguntas.py [rotulo]
Saídas: dados/qualidade/bateria_<rotulo>.md (respostas completas) e bateria_<rotulo>.csv (uma linha por pergunta).
Desfechos: respondida | esclarecimento | sem_dados | ERRO. A avaliação (certo/errado) é feita por pessoa e registrada
em ACOMPANHAMENTO.md; os casos errados viram testes em tests/test_regressao.py.
"""
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd  # noqa: E402

from motor.api import catalogo, perguntar  # noqa: E402
from motor.interpretador import interpretar  # noqa: E402

BATERIA = {
    "A básicas": [
        "Quantas matrículas existem no Espírito Santo em 2024?",
        "Quais são os dez municípios capixabas com mais matrículas em 2024?",
        "Quantas matrículas presenciais existem no ES?",
        "Quantas matrículas EaD existem no ES?",
        "Qual é o total de matrículas por município no ES?",
        "Qual é a distribuição das matrículas do ES por categoria administrativa?",
        "Quantas matrículas existem na rede pública do ES?",
        "Quantas matrículas existem na rede privada do Espírito Santo?",
    ],
    "B evolução": [
        "Como evoluíram as matrículas no ES entre 2017 e 2024?",
        "Como evoluíram as matrículas presenciais no ES?",
        "Como evoluíram as matrículas EaD no ES?",
        "Qual foi a variação percentual das matrículas no ES entre 2017 e 2024?",
        "Em qual ano houve o maior crescimento das matrículas no ES?",
        "Em qual ano houve a maior redução das matrículas presenciais no ES?",
        "Qual foi o crescimento acumulado das matrículas no ES no período?",
    ],
    "C geografia": [
        "Compare o Espírito Santo com o Sudeste e o Brasil em matrículas",
        "Quais municípios possuem maior participação nas matrículas do ES?",
        "Quais municípios do ES tiveram maior crescimento percentual de matrículas entre 2017 e 2024?",
        "Quais municípios do ES apresentaram redução de matrículas entre 2017 e 2024?",
        "Compare Vitória, Vila Velha, Serra e Cariacica em matrículas",
        "Qual é a participação de cada município no total estadual de matrículas do ES em 2024?",
        "Quais estados têm mais matrículas em 2024?",
        "Qual a participação do ES nas matrículas do Brasil?",
    ],
    "D dimensões": [
        "Como as matrículas do ES se distribuem por sexo em 2024?",
        "Como se distribuem as matrículas do ES por cor/raça em 2024?",
        "Matrículas por faixa etária no Espírito Santo em 2024",
        "Qual a participação das mulheres nas matrículas do ES em 2024?",
        "Matrículas do ES por organização acadêmica em 2024",
        "Matrículas do ES por grau acadêmico em 2024",
        "Matrículas a distância na rede privada do ES em 2024",
        "Ingressantes por sexo e cor/raça no ES em 2024",
        "Concluintes por cor/raça no ES em 2018",
        "Matrículas de mulheres na rede pública do ES",
    ],
    "E cursos": [
        "Quais cursos têm mais matrículas no ES em 2024?",
        "Quais cursos mais cresceram em ingressantes no ES entre 2019 e 2024?",
        "Quais cursos tiveram maior crescimento percentual de matrículas no ES entre 2019 e 2024?",
        "Matrículas em Medicina no Espírito Santo de 2017 a 2024",
        "Quantos concluintes de Pedagogia em Vitória em 2023?",
        "Quantos cursos de graduação existem no ES em 2024?",
        "Vagas oferecidas em Direito no ES em 2024",
        "Quais cursos mais perderam matrículas no ES entre 2017 e 2024?",
    ],
    "F outros indicadores": [
        "Quantas instituições de ensino superior há no ES em 2024?",
        "Quantos docentes em exercício no ES em 2024?",
        "Docentes por sexo no ES em 2023",
        "Quantos inscritos em processos seletivos no ES em 2024?",
        "Quantas vagas foram oferecidas no Brasil a distância em 2024?",
        "Relação candidatos por vaga no ES em 2024",
        "Taxa de conclusão no ES",
    ],
    "G limites e robustez": [
        "Como está Vitória em 2024?",
        "Matrículas no ES em 2015",
        "Quantas vagas a distância em Vitória?",
        "Matrículas em Bom Jesus em 2024",
        "matriculas em vila velha 2024",
        "Quantas MATRÍCULAS em VITÓRIA?",
        "Quantos alunos com deficiência no ES?",
        "Quantos estudantes têm FIES no ES?",
        "Matrículas por reserva de vagas no ES",
        "Quais mudanças metodológicas prejudicam a comparação entre anos?",
        "Matrículas em Vitória comparadas com 2017",
        "DROP TABLE fato_sinopse",
        "Matrículas no ES; DELETE FROM mart_anexos_geo",
    ],
}


def main():
    rotulo = sys.argv[1] if len(sys.argv) > 1 else "atual"
    cat = catalogo()
    saida = Path(__file__).resolve().parent.parent / "dados" / "qualidade"
    linhas, md = [], [f"# Bateria de perguntas — {rotulo}\n"]
    for grupo, perguntas in BATERIA.items():
        md.append(f"\n## {grupo}\n")
        for p in perguntas:
            c = interpretar(p, cat)
            t0 = time.time()
            try:
                r = perguntar(p)
                desf = "esclarecimento" if r.precisa_esclarecer else (
                    "sem_dados" if r.tabela is None and r.texto.startswith("Não há valores") else "respondida")
                texto = r.texto
            except Exception as e:
                desf, texto = "ERRO", traceback.format_exc()
            seg = time.time() - t0
            interp = (f"ind={c.indicador} tipo={c.tipo} anos={c.anos[0] if c.anos else ''}–{c.anos[-1] if c.anos else ''} "
                      f"locais={[l.nome for l in c.locais]} mun_uf={c.listar_municipios_uf} ufs={c.listar_ufs} "
                      f"filtros={c.filtros} quebras={c.quebras} crit={c.criterio}")
            primeira = next((x for x in texto.splitlines() if x.strip()), "")[:220]
            linhas.append({"grupo": grupo, "pergunta": p, "desfecho": desf, "segundos": round(seg, 2),
                           "interpretacao": interp, "primeira_linha": primeira})
            md.append(f"### {p}\n`{interp}` — **{desf}** ({seg:.1f} s)\n\n{texto}\n")
            print(f"[{desf:14s}] {seg:4.1f}s {p}\n      {interp}\n      {primeira}", flush=True)
    pd.DataFrame(linhas).to_csv(saida / f"bateria_{rotulo}.csv", sep=";", index=False, encoding="utf-8-sig")
    (saida / f"bateria_{rotulo}.md").write_text("\n".join(md), encoding="utf-8")
    df = pd.DataFrame(linhas)
    print("\n", df["desfecho"].value_counts().to_string(), f"\ntempo médio {df['segundos'].mean():.2f} s, máx {df['segundos'].max():.1f} s")


if __name__ == "__main__":
    main()
