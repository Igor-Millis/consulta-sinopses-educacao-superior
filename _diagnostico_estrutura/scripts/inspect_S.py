"""Inspecao do catalogo de abas. Uso: python -I inspect_S.py <work> <ano> <substr_arquivo> [campos...]"""
import sys
import pandas as pd

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90); pd.set_option("display.max_rows", 500)
S = pd.read_pickle(sys.argv[1] + "/S.pkl")
sub = S[(S.ano == int(sys.argv[2])) & S.arquivo.str.contains(sys.argv[3])]
fields = sys.argv[4:] or ["aba", "tipo_aba", "titulo_tabela", "linhas_cabecalho", "linha_inicio_dados", "n_registros",
                          "colunas_identificadoras", "niveis_geograficos", "alertas"]
for _, r in sub.iterrows():
    print("—" * 20, r["aba"])
    for f in fields:
        print(f"  {f}: {r.get(f)}")
