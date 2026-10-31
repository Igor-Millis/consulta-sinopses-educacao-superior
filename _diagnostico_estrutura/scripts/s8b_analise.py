"""Analise de inscritos == vagas no IF (Anexo II). Uso: python -I s8b_analise.py <work>"""
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400); pd.set_option("display.max_colwidth", 60)
w = Path(sys.argv[1])
df = pd.read_pickle(w / "if_linhas.pkl")
print("códigos usados:", df.groupby("ano")[["cod_vagas", "cod_inscritos", "cod_ingressantes", "cod_matriculas"]].first().to_string(), "\n")
d = df[df.vagas > 0].copy()
d["igual"] = d.inscritos == d.vagas
d["menor"] = d.inscritos < d.vagas

# 1) MT por ano
mt = d[d.CO_UF == "51"]
g = mt.groupby("ano").agg(linhas=("igual", "size"), iguais=("igual", "sum"), insc_menor_que_vagas=("menor", "sum"),
                          vagas=("vagas", "sum"), inscritos=("inscritos", "sum"), ingressantes=("ingressantes", "sum"))
g["insc_por_vaga"] = (g.inscritos / g.vagas).round(2)
g["pct_iguais"] = (100 * g.iguais / g.linhas).round(1)
print("== IF em Mato Grosso (linhas com vagas > 0)\n", g.to_string(), "\n")

# 2) Todas as UFs: % de linhas iguais por ano
u = d.groupby(["NO_UF", "ano"]).igual.mean().mul(100).round(0).unstack()
print("== % de linhas IF com inscritos == vagas, por UF e ano\n", u.to_string(), "\n")
nat = d.groupby("ano").agg(linhas=("igual", "size"), iguais=("igual", "sum"))
nat["pct"] = (100 * nat.iguais / nat.linhas).round(1)
print("== Brasil (IF)\n", nat.to_string(), "\n")

# 3) UF-ano com >= 80% de igualdade (padrao suspeito)
s = d.groupby(["NO_UF", "ano"]).agg(linhas=("igual", "size"), pct=("igual", "mean"))
print("== UF-ano com >= 80% iguais e >= 5 linhas\n", s[(s.pct >= 0.8) & (s.linhas >= 5)].round(2).to_string(), "\n")

# 4) Detalhe MT 2021-2023
cols = ["ano", "linha", "NO_MUNICIPIO", "NO_CINE_ROTULO", "vagas", "inscritos", "ingressantes", "matriculas"]
print("== Detalhe MT 2021–2023\n", mt[mt.ano.isin([2021, 2022, 2023])].sort_values(["NO_MUNICIPIO", "NO_CINE_ROTULO", "ano"])[cols].to_string(index=False))

# 5) mesmo curso/municipio: 2022 vs 2021 e 2023
p = mt.pivot_table(index=["NO_MUNICIPIO", "NO_CINE_ROTULO"], columns="ano", values=["vagas", "inscritos"], aggfunc="sum")
print("\n== Pareado por município × curso (vagas / inscritos)\n", p.loc[:, (slice(None), [2021, 2022, 2023])].to_string())

# 6) ingressantes > inscritos (inconsistencia logica?) no IF MT
x = mt[mt.ingressantes > mt.inscritos]
print("\n== IF MT: linhas com ingressantes > inscritos:", len(x), x.groupby("ano").size().to_dict())
