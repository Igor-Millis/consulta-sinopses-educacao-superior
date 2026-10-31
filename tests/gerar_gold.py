"""Gera tests/gold_interpretacoes.jsonl: a interpretação esperada (JSON do contrato) de cada pergunta da bateria.

Só rodar depois de REVISAR as respostas da bateria (dados/qualidade/bateria_<rotulo>.md): o arquivo vira a referência
(i) de regressão do interpretador por regras (test_contrato.py) e (ii) de avaliação de um modelo de linguagem.
Textos de suposição/esclarecimento não entram (só se houve esclarecimento), para o gabarito não depender da redação.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from motor.api import catalogo  # noqa: E402
from motor.contrato import para_json  # noqa: E402
from motor.interpretador import interpretar  # noqa: E402
from bateria_perguntas import BATERIA  # noqa: E402


def gabarito(c):
    j = para_json(c)
    j["pede_esclarecimento"] = bool(j.pop("esclarecer"))
    j.pop("supostos")
    return j


if __name__ == "__main__":
    cat = catalogo()
    saida = Path(__file__).resolve().parent / "gold_interpretacoes.jsonl"
    with open(saida, "w", encoding="utf-8") as f:
        for grupo, perguntas in BATERIA.items():
            for p in perguntas:
                f.write(json.dumps({"grupo": grupo, "pergunta": p, "esperado": gabarito(interpretar(p, cat))},
                                   ensure_ascii=False) + "\n")
    print(saida)
