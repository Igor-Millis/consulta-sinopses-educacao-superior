"""Teste rápido manual do interpretador por LLM local: mostra JSON bruto, contrato e tempo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")
from motor.api import catalogo  # noqa: E402
from motor.llm import disponivel, interpretar_llm  # noqa: E402

cat = catalogo()
print("modelo disponível:", disponivel())
for p in sys.argv[1:] or ["Quantos universitários tinha Cariacica em 2023?",
                          "A rede particular domina o ensino superior capixaba?",
                          "Quais as cidades do ES onde mais cresceu o número de formandos desde 2019?"]:
    c, meta = interpretar_llm(p, cat)
    print("=" * 90, "\n", p, f"({meta['segundos']} s)")
    print("bruto:", json.dumps(meta["bruto"], ensure_ascii=False))
    print("erros:", meta["erros"])
    if c:
        print("→", c.indicador, c.tipo, c.anos, [l.nome for l in c.locais], c.listar_municipios_uf, c.filtros, c.quebras,
              c.ordem, c.so_reducao, c.esclarecer)
