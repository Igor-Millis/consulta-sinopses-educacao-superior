"""Regra dos totais internos da Sinopse (T2), compartilhada por p3_validar.py (validação) e q10_detectar.py (Q10).

pares_totais(con) devolve os pares (pai, filho) de recortes em que o recorte-pai é o "Total" (ou "Pública" /
"Seleção para Vagas Novas") de uma dimensão e os filhos são as suas categorias, com as demais dimensões iguais.
Extraído sem alteração de p3_validar.py em 31/10/2026 (antes ficava embutido no script).
"""
from pathlib import Path

import pandas as pd

DIMS = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
        "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
        "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
GRUPOS = {("dependencia", "Total"): ("Federal", "Estadual", "Municipal", "Privada"),
          ("dependencia", "Pública"): ("Federal", "Estadual", "Municipal"),
          ("forma_ingresso", "Total"): ("Seleção para Vagas Novas", "Seleção para vagas de programas especiais",
                                         "Seleção para vagas remanescentes", "Outras Formas de Ingresso"),
          ("forma_ingresso", "Seleção para Vagas Novas"): ("Vestibular", "Enem", "Avaliação Seriada", "Seleção Simplificada")}


def pares_totais(con):
    r = con.execute("SELECT * FROM dim_recorte_sinopse").df()
    norm = r.copy()
    norm["categoria_privada"] = norm.categoria_privada.replace("Não se aplica", "Total")
    # IF/Cefet é sempre federal (logo, pública): para o IF, dependência Total ≡ Federal ≡ Pública. Cada coluna do IF
    # pode fazer o papel de qualquer uma das três (chaves alternativas); variantes do mesmo filho colapsam no máximo.
    ifed = (r.org_academica == "IF/Cefet") & r.dependencia.isin(["Total", "Federal", "Pública"])
    alts = []
    for v in ("Total", "Federal", "Pública"):
        a = norm.copy()
        a.loc[ifed, "dependencia"] = v
        alts.append(a)
    NE = pd.read_csv(Path(__file__).resolve().parent.parent / "config" / "categorias_nao_exclusivas.csv", encoding="utf-8-sig")
    nao_excl = {(row.dimensao, t) for row in NE.itertuples() for t in row.tabelas.split(";")}
    pares = []
    for d in DIMS:
        outros = [x for x in DIMS if x != d]
        chave = norm[outros].astype(str).agg("|".join, axis=1)
        chaves_alt = [a[outros].astype(str).agg("|".join, axis=1) for a in alts] if d != "dependencia" else []
        for pai_val in ("Total", "Pública", "Seleção para Vagas Novas"):
            filhos_val = GRUPOS.get((d, pai_val))
            if pai_val != "Total" and filhos_val is None:
                continue
            pais = r[norm[d] == pai_val]
            for i in pais.index:
                casa = chave == chave[i]
                for ca in chaves_alt:
                    casa = casa | (ifed & (ca == chave[i]))
                fi = r[casa & (norm[d] != pai_val) & (norm[d] != "Total") & (r[d] != "Não se aplica")]
                if filhos_val:
                    fi = fi[fi[d].isin(filhos_val)]
                elif d == "dependencia":
                    continue
                for j in fi.index:
                    pares.append((d, pai_val, int(r.id_recorte[i]), int(r.id_recorte[j]), str(norm[d][j])))
    P = pd.DataFrame(pares, columns=["dim", "pai_val", "pai", "filho", "filho_val"]).drop_duplicates()
    return P, nao_excl
