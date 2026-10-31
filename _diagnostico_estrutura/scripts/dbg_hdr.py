"""Mostra linhas de cabecalho cruas e mesclagens de um perfil. Uso: python -I dbg_hdr.py <json> <linha> [prefixo_mesclagem_linha]"""
import json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
p = json.load(open(sys.argv[1], encoding="utf8"))
r = sys.argv[2]
print({k: v for k, v in list(p["cabecalho"].get(r, {}).items())[:40]})
print([m for m in p["mesclagens"] if re.match(rf"^[A-Z]+{r}:", m)][:60])
