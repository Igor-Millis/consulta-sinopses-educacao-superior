"""Mais fatos para o 07. Uso: python -I s6d_facts.py <work>"""
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200); pd.set_option("display.max_rows", 200)
w = Path(sys.argv[1])
S = pd.read_pickle(w / "S.pkl"); HC = pd.read_pickle(w / "HC.pkl"); C = pd.read_pickle(w / "C.pkl")
for k in ("Tab 7.4", "Tab 1.2", "Tab 2.10"):
    r = S[(S.chave_tabela == k) & (S.ano == 2024)].iloc[0]
    print(k, "|", r.titulo_tabela, "|", r.unidade_medida_presumida, "|", r.colunas_identificadoras, "|", r.niveis_geograficos)
for k in ("Tab 2.9", "Tab 4.9", "Tab 4.15", "Tab 5.12"):
    v = HC[(HC.chave_tabela == k) & (HC.situacao != "todos os anos da tabela")]
    print("\n==", k); print(v[["nivel_cabecalho", "categoria", "anos"]].head(40).to_string())
print("\n5.12 ids:", S[S.chave_tabela == "Tab 5.12"][["ano", "colunas_identificadoras"]].values.tolist())
print("\nSumário 2023 conteúdo (trecho):", S[(S.ano == 2023) & (S.aba == "Sumário")].conteudo_texto.values[0][:1500])
print("\nCapa '3 Cursos' 2023:", S[(S.ano == 2023) & (S.aba == "3 Cursos")].conteudo_texto.values[0][:1500])
