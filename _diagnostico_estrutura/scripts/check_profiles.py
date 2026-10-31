"""Verifica integridade dos perfis JSON (somente leitura). Uso: python -I check_profiles.py <work>"""
import json, re, sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
work = Path(sys.argv[1])
inv = json.load(open(work / "inventario_bruto.json", encoding="utf8"))
expected = {}
for e in inv:
    for s in e["abas"]:
        safe = re.sub(r"[^\w.-]+", "_", s["sheet"].strip()) or "aba"
        expected[f'{e["ano"]}__{Path(e["arquivo"]).stem}__{safe}.json'] = (e, s)
files = {p.name: p for p in (work / "profiles").glob("*.json")}
print("esperados:", len(expected), "| encontrados:", len(files))
print("faltando:", sorted(set(expected) - set(files)))
print("sobrando:", sorted(set(files) - set(expected)))
# colisao de nomes (duas abas -> mesmo arquivo)
print("colisões de nome:", [k for k, v in Counter(
    f'{e["ano"]}__{Path(e["arquivo"]).stem}__{re.sub(r"[^\w.-]+", "_", s["sheet"].strip()) or "aba"}'
    for e in inv for s in e["abas"]).items() if v > 1])
bad, errs, nodata, stats = [], [], Counter(), Counter()
need = ["ano", "arquivo", "aba", "linhas_xml", "max_linha_util", "cabecalho", "mesclagens", "colunas", "assinaturas_linha"]
for name, p in files.items():
    try:
        d = json.load(open(p, encoding="utf8"))
    except Exception as ex:
        bad.append((name, repr(ex))); continue
    if d.get("erro"):
        errs.append((name, d["erro"])); continue
    miss = [k for k in need if k not in d]
    if miss:
        bad.append((name, "campos ausentes: " + ",".join(miss))); continue
    e, s = expected.get(name, (None, None))
    if s and d["aba"] != s["sheet"]:
        bad.append((name, f"aba {d['aba']!r} != {s['sheet']!r}"))
    # coerencia: linhas lidas x dimensao declarada
    m = re.search(r"(\d+)$", s["dimension"] or "") if s else None
    if m and d["max_linha_util"] and d["max_linha_util"] > int(m.group(1)):
        bad.append((name, f"max_linha_util {d['max_linha_util']} > dimensão {s['dimension']}"))
    stats["com_dados" if d.get("linha_inicio_dados") else "sem_bloco_de_dados"] += 1
print("JSON inválidos/inconsistentes:", bad)
print("abas com erro de leitura:", errs)
print("classificação:", dict(stats))
