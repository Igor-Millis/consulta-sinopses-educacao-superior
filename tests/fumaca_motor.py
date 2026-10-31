"""Teste de fumaça manual: roda perguntas de exemplo e imprime as respostas (não é pytest)."""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")
from motor.api import catalogo, perguntar  # noqa: E402
from motor.interpretador import interpretar  # noqa: E402

PERGUNTAS = sys.argv[1:] or [
    "Quantas matrículas havia em Vila Velha em 2024?",
    "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?",
    "Compare as matrículas presenciais e a distância no ES nos últimos 5 anos",
    "Quais os 10 municípios capixabas com mais matrículas em 2024?",
    "Quais cursos mais cresceram em ingressantes no ES entre 2019 e 2024?",
    "Qual a participação do EaD nas matrículas do Espírito Santo?",
    "Matrículas por sexo na Grande Vitória em 2023",
    "Compare Vitória e Serra em concluintes",
    "Quantas instituições de ensino superior há no ES por rede?",
    "Matrículas em Direito em Vitória de 2017 a 2024",
    "Quais mudanças metodológicas prejudicam a comparação entre anos?",
    "Quantos docentes no Rio Grande do Sul em 2022?",
    "Qual a participação de Vila Velha nas matrículas do ES?",
    "Quantas vagas a distância em Vitória?",
]
cat = catalogo()
for p in PERGUNTAS:
    print("=" * 100)
    print("P:", p)
    c = interpretar(p, cat)
    print("   →", {"ind": c.indicador, "tipo": c.tipo, "anos": c.anos, "locais": [l.nome for l in c.locais],
                   "mun_uf": c.listar_municipios_uf, "ufs": c.listar_ufs, "filtros": c.filtros, "quebras": c.quebras,
                   "crit": c.criterio})
    try:
        r = perguntar(p)
        print(r.texto[:2500])
    except Exception:
        traceback.print_exc()
