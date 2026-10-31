"""Padroes complementares IF MT. Uso: python -I s8c_padroes.py <work>"""
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
df = pd.read_pickle(Path(sys.argv[1]) / "if_linhas.pkl")
d = df[df.vagas > 0]
mt = d[d.CO_UF == "51"]
print("== IF MT: valores mais frequentes de inscritos por ano")
for y in range(2017, 2025):
    print(y, mt[mt.ano == y].inscritos.value_counts().head(6).to_dict())
print("\n== IF MT: linhas com inscritos múltiplo de 100 (%):",
      mt.groupby("ano").inscritos.apply(lambda s: round(100 * ((s % 100) == 0).mean())).to_dict())
oth = d[d.CO_UF != "51"]
print("== IF demais UFs: linhas com inscritos múltiplo de 100 (%):",
      oth.groupby("ano").inscritos.apply(lambda s: round(100 * ((s % 100) == 0).mean())).to_dict())
print("\n== Ingressantes / Matrículas do IF (linhas com vagas>0)")
t = d.assign(uf=d.CO_UF.eq("51").map({True: "MT", False: "demais UFs"})).groupby(["uf", "ano"])[["vagas", "inscritos", "ingressantes", "matriculas"]].sum()
t["ingr_por_vaga"] = (t.ingressantes / t.vagas).round(2)
print(t.to_string())
print("\n== IF: UF-ano com ingressantes/vagas < 0,05 (>=5 linhas)")
u = d.groupby(["NO_UF", "ano"]).agg(linhas=("vagas", "size"), vagas=("vagas", "sum"), ingr=("ingressantes", "sum"))
u["r"] = (u.ingr / u.vagas).round(3)
print(u[(u.r < 0.05) & (u.linhas >= 5)].to_string())
print("\n== IF MT 2022: linhas com ingressantes > 0")
print(mt[(mt.ano == 2022) & (mt.ingressantes > 0)][["linha", "NO_MUNICIPIO", "NO_CINE_ROTULO", "vagas", "inscritos", "ingressantes", "matriculas"]].to_string(index=False))
