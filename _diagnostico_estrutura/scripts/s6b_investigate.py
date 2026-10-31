"""Investiga pontos levantados pela validacao (somente leitura). Uso: python -I s6b_investigate.py <work>"""
import json, sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 110); pd.set_option("display.max_rows", 300)
work = Path(sys.argv[1])
C = pd.read_pickle(work / "C.pkl"); S = pd.read_pickle(work / "S.pkl"); PR = pd.read_pickle(work / "PR.pkl")


def prof(ano, frag, aba):
    for p in (work / "profiles").glob(f"{ano}__*{frag}*.json"):
        d = json.load(open(p, encoding="utf8"))
        if d["aba"] == aba:
            return d


print("=== (a) códigos especiais 4.3 2019/2020")
for ano in (2019, 2020):
    d = prof(ano, "Municipio", "4.3")
    for c in ("AP", "CK", "EF"):
        v = d["colunas"][c]
        print(ano, c, v["classes"], {k: n for k, n in v["distintos"].items()})
    print("  cabeçalho dessas colunas:", C[(C.ano == ano) & (C.aba == "4.3") & C.coluna.isin(["AP", "CK", "EF"])][["coluna", "rotulo_completo"]].values.tolist())

print("\n=== (b) células inexistentes em medidas (Sinopse), por aba")
m = C[(C.papel == "medida") & (C.celulas_inexistentes > 0)]
print(m.groupby(["ano", "aba"]).agg(n_col=("coluna", "count"), inex=("celulas_inexistentes", "sum"),
                                    reg=("n_registros_aba", "max"), cols=("coluna", lambda s: ",".join(list(s)[:6]))).to_string())

print("\n=== (c) numéricos gravados como texto")
print(C[C.numericos_gravados_como_texto > 0][["ano", "aba", "coluna", "papel", "rotulo_completo", "numericos", "numericos_gravados_como_texto"]].to_string())

print("\n=== (d) caminhos duplicados: 4.1 2017 (colunas) e 2020 3.2")
for ano, aba, filt in ((2017, "4.1 Vagas e Inscritos", "Universidade > Vagas Oferecidas > Total"), (2020, "3.2", "Federal > Federal")):
    x = C[(C.ano == ano) & (C.aba == aba) & C.rotulo_completo.str.contains(filt, regex=False)]
    print(ano, aba, len(x), x[["coluna", "rotulo_completo", "celulas_presentes", "celula_nivel_3", "celula_nivel_4", "celula_nivel_5"]].head(8).to_string())

print("\n=== (e) largura/colunas por ano — Anexos e abas 2020")
print(S[S.conjunto != "Sinopse por município"].pivot_table(index="conjunto", columns="ano", values="n_col_util").to_string())
w = S[(S.tipo_aba == "tabela_dados") & (S.conjunto == "Sinopse por município")].pivot_table(index="chave_tabela", columns="ano", values="n_col_util")
print(w[w.nunique(axis=1) > 1].to_string())

print("\n=== (f) Anexos: motivos de 'provável'")
a = PR[(PR.conjunto != "Sinopse por município") & (PR.classificacao == "Equivalência provável")]
print(a.groupby(["conjunto", "ano"]).evidencias.agg(lambda s: s.value_counts().head(3).to_dict()).to_string())
print(PR[PR.classificacao == "Equivalência parcial"][["conjunto", "ano_anterior", "ano", "coluna_ano", "rotulo_ano_anterior", "rotulo_ano", "evidencias"]].to_string())
