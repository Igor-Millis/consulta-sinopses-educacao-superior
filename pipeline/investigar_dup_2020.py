"""Colunas duplicadas da Sinopse 2020 (3.2 e 4.4): têm dados? (somente leitura)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
from comum import ler_catalogo, DIAG, col2n

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120); pd.set_option("display.max_rows", 100)
src = Path(__file__).with_name("p3_mapear_sinopse.py").read_text(encoding="utf-8").split("dup = X.duplicated")[0]
ns = {"__file__": str(Path(__file__).with_name("p3_mapear_sinopse.py"))}
exec(compile(src, "p3_mapear_sinopse.py", "exec"), ns)
X, DIMS = ns["X"], ns["DIMS"]
k = ["ano", "tabela", "indicador"] + DIMS
g = X[X.duplicated(k, keep=False)].copy()
p04 = ler_catalogo(DIAG / "04_perfil_dados.xlsx", sheet_name="perfil_colunas",
                   usecols=["ano", "aba", "coluna", "celulas_presentes", "numericos", "max"])
g = g.merge(p04, on=["ano", "aba", "coluna"], how="left")
g["n"] = g.coluna.map(col2n)
for tab, gg in g.groupby("tabela"):
    print(f"== 2020 {tab}: {len(gg)} colunas em {gg.groupby(k).ngroups} recortes repetidos | faixa {gg.sort_values('n').coluna.iloc[0]}–{gg.sort_values('n').coluna.iloc[-1]}")
    print("   células presentes nessas colunas:", gg.celulas_presentes.describe()[["min", "max"]].to_dict(), "| máx. valor:", gg["max"].max())
    print(gg.sort_values("n")[["coluna", "celulas_presentes", "max", "rotulo_completo"]].head(8).to_string(index=False))
