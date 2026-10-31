"""Mostra nomes e dimensoes das abas a partir de inventario_bruto.json (somente leitura).

Uso: python -I s1b_show_sheets.py <inventario_bruto.json> anexos|municipio
"""
import json, sys

inv = json.load(open(sys.argv[1], encoding="utf8"))
modo = sys.argv[2]

if modo == "anexos":
    for w in inv:
        if "anexo" in w["arquivo"]:
            for s in w["abas"]:
                print(f'{w["ano"]} | {w["arquivo"]} | {s["sheet"]} | {s["dimension"]} | {s["xml_size"]:,} bytes XML')

else:
    mun = {w["ano"]: w for w in inv if "Municipio" in w["arquivo"]}
    anos = sorted(mun)
    # uniao ordenada dos nomes de abas
    ordem = []
    for a in anos:
        for s in mun[a]["abas"]:
            if s["sheet"] not in ordem:
                ordem.append(s["sheet"])
    print("aba | " + " | ".join(str(a) for a in anos))
    for nm in ordem:
        cels = []
        for a in anos:
            d = {s["sheet"]: s for s in mun[a]["abas"]}
            s = d.get(nm)
            cels.append(f'{s["dimension"]}{"(" + s["state"] + ")" if s["state"] != "visible" else ""}' if s else "—")
        print(nm + " | " + " | ".join(cels))
