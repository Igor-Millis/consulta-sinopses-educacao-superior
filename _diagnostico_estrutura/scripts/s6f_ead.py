"""Exemplos de linhas municipais do Anexo III (somente leitura). Uso: python -I s6f_ead.py <work>"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
w = Path(sys.argv[1])
for ano in (2017, 2024):
    p = next((w / "profiles").glob(f"{ano}__anexo_III*.json"))
    d = json.load(open(p, encoding="utf8"))
    print("==", ano)
    for r, cells, sig in d["exemplos"]:
        sel = {k: cells.get(k) for k in ("A", "B", "D", "F", "H", "CA", "FP", "JE", "MT", "QI")}
        print(r, sig, sel)
    for s, ex in d["assinatura_exemplo"].items():
        print("  assin", s, ex[0], {k: ex[1].get(k) for k in ("A", "D", "F", "H", "I", "J")})
    for c in ("H", "CA", "FP", "JE", "MT", "QI"):
        v = d["colunas"][c]
        print("  col", c, v["classes"], "max", v["max"])
