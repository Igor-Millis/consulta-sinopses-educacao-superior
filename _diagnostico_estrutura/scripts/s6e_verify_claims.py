"""Verifica afirmacoes do relatorio 07 (somente leitura). Uso: python -I s6e_verify_claims.py <work>"""
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 300)
w = Path(sys.argv[1])
S = pd.read_pickle(w / "S.pkl"); N = pd.read_pickle(w / "notes.pkl")
print("notas com 'polo':", N[N.texto.str.contains("polo", case=False)].groupby(["conjunto", "chave_tabela"]).size().head(20).to_dict())
print(N[N.texto.str.contains("polo", case=False)].texto.drop_duplicates().head(5).tolist())
print("\nnotas com 'sede' / 'local de oferta' (2024):")
n24 = N[N.ano == 2024]
for pat in ("sede", "local de oferta"):
    print(pat, sorted(n24[n24.texto.str.contains(pat, case=False)].chave_tabela.unique().tolist())[:80])
print("\nnotas 2.1 2024:", N[(N.ano == 2024) & (N.chave_tabela == "Tab 2.1")].texto.tolist())
D = S[S.tipo_aba == "tabela_dados"]
print("\nlinhas ocultas total:", D.linhas_ocultas.sum(), "| abas com colunas ocultas:", (D.colunas_ocultas.fillna("") != "").sum())
print(D[D.colunas_ocultas.fillna("") != ""][["ano", "aba", "colunas_ocultas"]].head(10).to_string())
x = D[(D.ano == 2024) & D.colunas_identificadoras.str.contains("Nível Acadêmico")]
print("\ntabelas com Nível Acadêmico (2024):", len(x), sorted(x.chave_tabela.tolist()))
print("\n2.1 2020:", D[(D.ano == 2020) & (D.aba == "2.1")][["dimensao_declarada", "max_col_util"]].values.tolist())
