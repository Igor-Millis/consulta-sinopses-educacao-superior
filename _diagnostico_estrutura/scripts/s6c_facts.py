"""Fatos pontuais para o relatorio 07 (somente leitura). Uso: python -I s6c_facts.py <work>"""
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 160); pd.set_option("display.max_rows", 200)
w = Path(sys.argv[1])
C = pd.read_pickle(w / "C.pkl"); S = pd.read_pickle(w / "S.pkl"); T2 = pd.read_pickle(w / "T2.pkl"); PR = pd.read_pickle(w / "PR.pkl")
med = C[C.papel == "medida"]
d = med.groupby(["ano", "aba", "rotulo_completo"]).coluna.apply(list)
print("DUPLICADOS:\n", d[d.map(len) > 1].to_string())
print("\nMUDANÇAS RELEVANTES:")
x = T2[T2.mudancas_vs_ano_anterior.str.contains("título|renomeada|nº de colunas|identificadoras", regex=True)]
print(x[["chave_tabela", "ano", "aba", "mudancas_vs_ano_anterior"]].to_string())
print("\nTÍTULOS ALTERADOS:")
for k in x[x.mudancas_vs_ano_anterior.str.contains("título")].chave_tabela.unique():
    print(k, S[S.chave_tabela == k][["ano", "titulo_tabela"]].values.tolist()[-3:])
print("\nABAS SEM DADOS/AUX POR ANO:")
print(S[S.tipo_aba != "tabela_dados"].pivot_table(index="tipo_aba", columns="ano", values="aba", aggfunc="count").to_string())
print("\nREVISÃO MANUAL:", S[S.revisao_manual == "sim"].groupby("tipo_aba").size().to_dict())
print(S[(S.revisao_manual == "sim") & (S.tipo_aba == "tabela_dados")][["ano", "aba", "alertas"]].to_string())
print("\nREGISTROS POR CONJUNTO/ANO:")
print(S[S.tipo_aba == "tabela_dados"].pivot_table(index="conjunto", columns="ano", values="n_registros", aggfunc="sum").to_string())
print("\nNÍVEIS GEO ANEXO I 2024:", S[(S.ano == 2024) & (S.conjunto == "Anexo I — Tabela 8.1")].niveis_geograficos.values)
print("\nNOVOS NÃO IDENTIFICADOS (Sinopse) POR TABELA/ANO:")
u = PR[(PR.classificacao == "Correspondência não identificada")]
print(u.groupby(["chave_tabela", "ano"]).size().to_string())
