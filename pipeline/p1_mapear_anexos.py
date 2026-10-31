"""P1 — Gera config/xw_colunas_anexos.csv: cada coluna de medida dos Anexos → indicador e recorte.

Fonte: _diagnostico_estrutura/03_catalogo_colunas.xlsx (cabeçalho hierárquico já reconstruído).
Regra R1: a coluna é identificada pelo CÓDIGO da linha 12; os rótulos só classificam as dimensões.
Classificação por vocabulário (a ordem dos níveis varia: no IF a dependência vem antes do grau).
"Total" = agregado na dimensão; categoria privada = "Não se aplica" para dependências públicas.
Qualquer rótulo fora do vocabulário interrompe a geração (nada é classificado por palpite).

Uso: python -I p1_mapear_anexos.py
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
from comum import ler_catalogo, CONFIG, DIAG

sys.stdout.reconfigure(encoding="utf-8")
INDICADOR = {"Número de Cursos": "cursos", "Vagas Oferecidas": "vagas", "Candidatos Inscritos": "inscritos",
             "Ingressantes": "ingressantes", "Matrículas": "matriculas", "Concluintes": "concluintes"}
VOCAB = {
    "org_academica": {"Universidade", "Centro Universitário", "Faculdade",
                      "Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet)"},
    "grau": {"Bacharelado", "Licenciatura", "Tecnológico", "Não Aplicável"},
    "dependencia": {"Federal", "Estadual", "Municipal", "Privada"},
    "categoria_privada": {"Com Fins Lucrativos", "Sem Fins Lucrativos"},
}
ABREV_ORG = {"Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet)": "IF/Cefet"}


def limpar(r):
    r = re.sub(r"\s+", " ", str(r)).strip()
    return re.sub(r"(?<=[a-zA-Zá-ú\)])\d{1,2}(\s?[-–,]\s?\d{1,2})*$", "", r)  # chamada de nota colada


c = ler_catalogo(DIAG / "03_catalogo_colunas.xlsx")
c = c[c.conjunto.str.startswith("Anexo") & (c.papel == "medida")].copy()
c["conj"] = c.conjunto.map({"Anexo I — Tabela 8.1": "anexo_i", "Anexo II — Tabela 8.2": "anexo_ii", "Anexo III — Tabela 8.3": "anexo_iii"})
rows, erros = [], []
for r in c.itertuples():
    ind = INDICADOR.get(limpar(r.nivel_2))
    if ind is None:
        erros.append((r.ano, r.arquivo, r.coluna, "indicador", r.nivel_2)); continue
    d = {k: "Total" for k in VOCAB}
    for lv in (r.nivel_3, r.nivel_4, r.nivel_5, r.nivel_6):
        if pd.isna(lv):
            continue
        lab = limpar(lv)
        if lab == "Total":
            continue
        dim = next((k for k, voc in VOCAB.items() if lab in voc), None)
        if dim is None:
            erros.append((r.ano, r.arquivo, r.coluna, "rótulo fora do vocabulário", lv)); continue
        if d[dim] != "Total":
            erros.append((r.ano, r.arquivo, r.coluna, f"dimensão {dim} repetida", lv)); continue
        d[dim] = lab
    if d["dependencia"] in ("Federal", "Estadual", "Municipal"):
        d["categoria_privada"] = "Não se aplica"
    d["org_academica"] = ABREV_ORG.get(d["org_academica"], d["org_academica"])
    rows.append({"ano": r.ano, "conjunto": r.conj, "arquivo": r.arquivo, "aba": r.aba, "coluna": r.coluna,
                 "codigo_variavel": r.codigo_variavel, "celula_codigo": r.celula_codigo, "indicador": ind, **d,
                 "eh_agregado": any(v == "Total" for v in d.values()),
                 "rotulo_completo": r.rotulo_completo, "revisado_manualmente": "não"})
X = pd.DataFrame(rows)
if erros:
    print("ERROS de classificação:", len(erros))
    for e in erros[:30]:
        print("  ", e)
    sys.exit(1)
dup = X.duplicated(["ano", "conjunto", "indicador", "org_academica", "grau", "dependencia", "categoria_privada"], keep=False)
if dup.any():
    print("ERRO: recortes duplicados", X[dup].head(20).to_string()); sys.exit(1)
cod = X.groupby(["conjunto", "codigo_variavel"])[["indicador", "org_academica", "grau", "dependencia", "categoria_privada"]].nunique()
inst = cod[(cod > 1).any(axis=1)]
print(f"colunas mapeadas: {len(X):,} | por conjunto/ano: {X.groupby(['conjunto', 'ano']).size().unique().tolist()} | "
      f"códigos com classificação diferente entre anos: {len(inst)}")
CONFIG.mkdir(exist_ok=True)
X.to_csv(CONFIG / "xw_colunas_anexos.csv", index=False, encoding="utf-8-sig")
print("gravado:", CONFIG / "xw_colunas_anexos.csv")
