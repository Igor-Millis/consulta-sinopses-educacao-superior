"""Capturas de tela reais da interface com o Edge em modo headless (executa o JavaScript da página).

Uso: python -I tests/capturas_interface.py [porta] [pasta_saida]
Gera PNGs da tela inicial e de respostas (via ?q=) em larguras de desktop, notebook e celular. Só leitura.
"""
import subprocess
import sys
import urllib.parse
from pathlib import Path

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
porta = sys.argv[1] if len(sys.argv) > 1 else "8765"
saida = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "dados" / "qualidade" / "capturas")
saida.mkdir(parents=True, exist_ok=True)
base = f"http://127.0.0.1:{porta}/"
CASOS = [
    ("inicio_desktop", "", 1440, 1000),
    ("inicio_celular", "", 390, 1500),
    ("valor_desktop", "Quantas matrículas havia em Vila Velha em 2024?", 1440, 1500),
    ("serie_desktop", "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?", 1440, 2300),
    ("ranking_notebook", "Quais os 10 municípios capixabas com mais matrículas em 2024?", 1100, 2300),
    ("participacao_desktop", "Qual a participação das mulheres nas matrículas da rede privada do ES em 2024?", 1440, 1500),
    ("esclarecimento_desktop", "Quantos alunos com deficiência no ES?", 1440, 900),
    ("q10_desktop", "Concluintes por cor/raça no Brasil em 2017", 1440, 2000),
    ("serie_celular", "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?", 390, 3400),
]
for nome, q, w, h in CASOS:
    url = base + ("?q=" + urllib.parse.quote(q) if q else "")
    arq = saida / f"{nome}.png"
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
                    "--virtual-time-budget=15000", f"--screenshot={arq}", url], capture_output=True, timeout=120)
    print(f"{'OK' if arq.exists() else 'FALHA'} {arq}")
