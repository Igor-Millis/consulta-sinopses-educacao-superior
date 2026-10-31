"""Analise do padrao EaD do IF em MT. Uso: python -I s9b_analise_ead.py <work>"""
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300); pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 70)
w = Path(sys.argv[1])
s73 = pd.read_pickle(w / "if_ead_73.pkl")
A = pd.read_pickle(w / "if_ead_anexo.pkl")

print("== Sinopse 7.3 — IF, linha Total Mato Grosso e Total Brasil (colunas não nulas)")
for rec, g in s73.groupby("recorte"):
    g = g.drop(columns=["linha"]).set_index("ano").drop(columns="recorte").dropna(axis=1, how="all")
    g.columns = [c.replace("Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet) > ", "IF > ") for c in g.columns]
    print("--", rec); print(g.T.to_string())

M = A[A.tipo == "municipio"]
mt = M[M.CO_UF == "51"]
print("\n== Anexo III — IF em municípios de MT (polos): somas por ano")
print(mt.groupby("ano")[["vagas", "inscritos", "ingressantes", "matriculas", "concluintes"]].sum().assign(
    linhas=mt.groupby("ano").size(), linhas_com_matricula=mt[mt.matriculas > 0].groupby("ano").size()).to_string())
print("\n== Anexo III — IF, linhas municipais de TODAS as UFs: vagas/inscritos não nulos?")
print(M.groupby("ano")[["vagas", "inscritos"]].apply(lambda g: (g.fillna(0) != 0).sum()).to_string())

D = A[(A.tipo == "Distância") & (A.vagas > 0)]
D = D.assign(igual=D.inscritos == D.vagas)
print("\n== Anexo III — linhas 'Distância' (nacional, por curso), IF com vagas > 0")
print(D.groupby("ano").agg(cursos=("igual", "size"), iguais=("igual", "sum"), vagas=("vagas", "sum"),
                           inscritos=("inscritos", "sum")).assign(pct=lambda x: (100 * x.iguais / x.cursos).round(1),
                                                                    insc_por_vaga=lambda x: (x.inscritos / x.vagas).round(2)).to_string())
print("\n== cursos 'Distância' com inscritos == vagas (IF)")
print(D[D.igual][["ano", "NO_CINE_ROTULO", "vagas", "inscritos", "ingressantes", "matriculas"]].to_string(index=False))

print("\n== IF MT polos: detalhe por curso (matrículas), 2020–2024")
p = mt.pivot_table(index="NO_CINE_ROTULO", columns="ano", values=["ingressantes", "matriculas"], aggfunc="sum").fillna(0)
print(p.loc[p.sum(axis=1) > 0].to_string())
