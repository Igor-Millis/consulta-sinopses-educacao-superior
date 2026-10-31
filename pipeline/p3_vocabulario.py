"""P3 — Levanta o vocabulário dos cabeçalhos da Sinopse por município (somente leitura do catálogo 03).

Grava dados/qualidade/p3_vocabulario.csv: rótulo limpo, nível, nº de colunas, tabelas e anos em que aparece.
Serve de base para o mapeamento curado config/vocabulario_sinopse.csv.

Uso: python -I p3_vocabulario.py
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
from comum import ler_catalogo, DIAG, QUALIDADE

sys.stdout.reconfigure(encoding="utf-8")


def limpar(r):
    r = re.sub(r"\s+", " ", str(r)).strip()
    return re.sub(r"(?<=[a-zA-Zá-úÁ-Ú\)])\d{1,2}(\s?[-–,]\s?\d{1,2})*$", "", r)


c = ler_catalogo(DIAG / "03_catalogo_colunas.xlsx")
c = c[(c.conjunto == "Sinopse por município") & (c.papel == "medida")]
print("colunas de medida da Sinopse:", len(c), "| abas×anos:", c.groupby(["ano", "aba"]).ngroups)
rows = []
for lv in range(1, 7):
    s = c[["ano", "chave_tabela", f"nivel_{lv}"]].dropna()
    s = s.assign(rotulo=s[f"nivel_{lv}"].map(limpar))
    for rot, g in s.groupby("rotulo"):
        rows.append({"nivel": lv, "rotulo": rot, "n_colunas": len(g),
                     "tabelas": ",".join(sorted(set(g.chave_tabela), key=lambda k: [int(x) for x in re.findall(r"\d+", k)])),
                     "anos": ",".join(map(str, sorted(set(g.ano))))})
V = pd.DataFrame(rows)
V.to_csv(QUALIDADE / "p3_vocabulario.csv", index=False, encoding="utf-8-sig")
print("rótulos distintos por nível:", V.groupby("nivel").size().to_dict(), "| distintos no total:", V.rotulo.nunique())
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 600); pd.set_option("display.max_colwidth", 70)
print(V[V.nivel >= 2].drop_duplicates("rotulo").sort_values("rotulo")[["rotulo", "n_colunas", "tabelas"]].to_string(index=False))
