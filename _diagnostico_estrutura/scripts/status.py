"""Compara perfis concluidos com o esperado pelo inventario (somente leitura). Uso: python -I status.py <work>"""
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
work = Path(sys.argv[1])
inv = json.load(open(work / "inventario_bruto.json", encoding="utf8"))
done = {p.name for p in (work / "profiles").glob("*.json")}
for e in sorted(inv, key=lambda e: (e["conjunto"], e["ano"])):
    exp = []
    for s in e["abas"]:
        safe = re.sub(r"[^\w.-]+", "_", s["sheet"].strip()) or "aba"
        exp.append(f'{e["ano"]}__{Path(e["arquivo"]).stem}__{safe}.json')
    ok = sum(x in done for x in exp)
    falt = [x.split("__")[-1] for x in exp if x not in done]
    st = "CONCLUÍDO" if ok == len(exp) else "PENDENTE"
    print(f'{st:9} | {e["ano"]} | {e["conjunto"]:24} | {ok}/{len(exp)} abas | XML {sum(s["xml_size"] for s in e["abas"])/2**30:.2f} GB'
          + (f' | faltam: {", ".join(falt[:5])}{"…" if len(falt) > 5 else ""}' if falt else ""))
