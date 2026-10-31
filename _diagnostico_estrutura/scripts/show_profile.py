"""Resumo legivel de um JSON de perfil. Uso: python -I show_profile.py <json> [n_cols]"""
import json, sys

p = json.load(open(sys.argv[1], encoding="utf8"))
nc = int(sys.argv[2]) if len(sys.argv) > 2 else 15
for k in ("ano", "arquivo", "aba", "dimensao_declarada", "linhas_xml", "max_linha_util", "max_col_util",
          "linha_inicio_dados", "ultima_linha_com_numero", "linhas_ocultas", "colunas_ocultas", "segundos", "erro"):
    print(k, "=", p.get(k))
print("mesclagens:", len(p.get("mesclagens", [])), p.get("mesclagens", [])[:40])
print("--- cabecalho")
for r, cells in p.get("cabecalho", {}).items():
    items = list(cells.items())
    print(r, "|", " | ".join(f"{c}={v[:45]!r}" for c, v in items[:nc]), "..." if len(items) > nc else "")
print("--- assinaturas", p.get("assinaturas_linha"))
for s, ex in p.get("assinatura_exemplo", {}).items():
    print("  ", s, ex)
print("--- colunas (primeiras)")
for c, d in list(p.get("colunas", {}).items())[:nc]:
    print(c, d["classes"], "min", d["min"], "max", d["max"], "ndist", d["n_distintos_guardados"],
          list(d["distintos"].items())[:6])
print("--- notas", len(p.get("notas", [])))
for n in p.get("notas", [])[:15]:
    print("  ", n)
print("--- cauda")
for t in p.get("cauda", [])[-12:]:
    print("  ", t[0], dict(list(t[1].items())[:6]))
