"""P3 — Mapeamento das colunas da Sinopse por município: cada coluna de medida → indicador + recorte.

Fonte: _diagnostico_estrutura/03_catalogo_colunas.xlsx (cabeçalho hierárquico reconstruído).
Classificação por VOCABULÁRIO curado (abaixo, gravado em config/vocabulario_sinopse.csv), não por posição.
Regras:
  - nível 1 e rótulos "Total por ...", "Grau de Formação" etc. são legendas (não viram dimensão);
  - "Total" = agregado na dimensão (valor padrão de toda dimensão);
  - um rótulo mais específico substitui o pai na mesma dimensão (Pública → Federal; Vagas Novas → Enem);
  - indicador: do cabeçalho quando existe (4.1, 7.x); senão, pelo número da tabela;
  - correções manuais em config/xw_override_sinopse.csv (mesclagens desalinhadas da 4.1);
  - colunas "sem dados" do catálogo (colunas fantasma de 2020) não são mapeadas.
Interrompe se houver rótulo fora do vocabulário, conflito de dimensão ou recorte duplicado.

Uso: python -I p3_mapear_sinopse.py
"""
import re, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
from comum import ler_catalogo, CONFIG, DIAG, col2n

sys.stdout.reconfigure(encoding="utf-8")
IF = "Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet)"
DIMS = ["org_academica", "dependencia", "categoria_privada", "tipo_privada", "grau", "modalidade", "turno", "sexo",
        "cor_raca", "faixa_etaria", "nacionalidade", "deficiencia", "forma_ingresso", "financiamento",
        "reserva_vagas", "regime_trabalho", "dedicacao_exclusiva", "grau_formacao"]
INDICADORES = {"Número de Cursos": "cursos", "Vagas Oferecidas": "vagas", "Candidatos Inscritos": "inscritos",
               "Ingressantes": "ingressantes", "Matrículas": "matriculas", "Concluintes": "concluintes",
               "Matrículas Trancadas": "matriculas_trancadas", "Matrículas Desvinculadas": "matriculas_desvinculadas",
               "Alunos Transferidos para outros cursos na mesma IES": "alunos_transferidos",
               "Alunos Falecidos": "alunos_falecidos", "Número de Polos": "polos"}
LEGENDAS = {"Grau de Formação", "Regime de Trabalho", "Sexo", "Tipo da Instituição Privada", "Total Geral",
            "Total Geral - Instituições Privadas - Comunitárias e/ou Confessionais"}
V = {  # rótulo limpo → [(dimensão, valor padronizado)]
    "Universidade": [("org_academica", "Universidade")], "Centro Universitário": [("org_academica", "Centro Universitário")],
    "Faculdade": [("org_academica", "Faculdade")], IF: [("org_academica", "IF/Cefet")],
    "Pública": [("dependencia", "Pública")], "Federal": [("dependencia", "Federal")], "Estadual": [("dependencia", "Estadual")],
    "Municipal": [("dependencia", "Municipal")], "Privada": [("dependencia", "Privada")],
    "Privada - Com Fins Lucrativos": [("dependencia", "Privada"), ("categoria_privada", "Com Fins Lucrativos")],
    "Privada - Sem Fins Lucrativos": [("dependencia", "Privada"), ("categoria_privada", "Sem Fins Lucrativos")],
    "Com Fins Lucrativos": [("categoria_privada", "Com Fins Lucrativos")], "Sem Fins Lucrativos": [("categoria_privada", "Sem Fins Lucrativos")],
    "Comunitária": [("tipo_privada", "Comunitária")], "Confessional": [("tipo_privada", "Confessional")],
    "Bacharelado": [("grau", "Bacharelado")], "Licenciatura": [("grau", "Licenciatura")], "Tecnológico": [("grau", "Tecnológico")],
    "Não Aplicável": [("grau", "Não Aplicável")],
    "Presencial": [("modalidade", "Presencial")], "A Distância": [("modalidade", "A Distância")],
    "Diurno": [("turno", "Diurno")], "Noturno": [("turno", "Noturno")],
    "Feminino": [("sexo", "Feminino")], "Masculino": [("sexo", "Masculino")],
    **{k: [("cor_raca", k)] for k in ("Branca", "Preta", "Parda", "Amarela", "Indígena", "Não Dispõe da Informação")},
    "Brasileira": [("nacionalidade", "Brasileira")], "Brasileira - Naturalizado": [("nacionalidade", "Brasileira - Naturalizado")],
    "Estrangeira": [("nacionalidade", "Estrangeira")], "Estrangeiro": [("nacionalidade", "Estrangeira")],
    **{k: [("deficiencia", k)] for k in ("Auditiva", "Baixa Visão", "Cegueira", "Física", "Intelectual", "Múltipla", "Surdez",
                                          "Surdocegueira", "Autismo Infantil", "Síndrome de Asperger", "Síndrome de Rett",
                                          "Transtorno Desintegrativo da Infância", "Transtorno Global do Desenvolvimento (TGD)",
                                          "Transtorno do Espectro Autista (TEA)", "Transtorno do Espectro Autista",
                                          "Superdotação", "Altas habilidades/superdotação", "Visão Monocular")},
    **{k: [("forma_ingresso", k)] for k in ("Seleção para Vagas Novas", "Vestibular", "Enem", "Avaliação Seriada", "Seleção Simplificada",
                                             "Seleção para vagas de programas especiais", "Seleção para vagas remanescentes",
                                             "Outras Formas de Ingresso")},
    **{k: [("financiamento", k)] for k in ("FIES", "ProUni Integral", "ProUni Parcial", "Outros Financiamentos")},
    **{k: [("reserva_vagas", k)] for k in ("Étnico", "Pessoas com Deficiência", "Estudante Procedente de Escola Pública",
                                            "Social / Renda Familiar", "Outros Programas", "Outros", "Estudante Idoso",
                                            "Estudante Internacional", "Estudante Medalhista", "Estudante Preto, Pardo ou Indígena",
                                            "Estudante Quilombola", "Estudante Refugiado", "Estudante Transgênero",
                                            "Estudante de Comunidade Tradicional")},
    **{k: [("regime_trabalho", k)] for k in ("Tempo Integral", "Tempo Parcial", "Horista")},
    "Com Dedicação Exclusiva": [("dedicacao_exclusiva", "Com Dedicação Exclusiva")],
    "Sem Dedicação Exclusiva": [("dedicacao_exclusiva", "Sem Dedicação Exclusiva")],
    **{k: [("grau_formacao", k)] for k in ("Sem Graduação", "Graduação", "Especialização", "Mestrado", "Doutorado")},
}
FILHOS = {("dependencia", "Pública"): {"Federal", "Estadual", "Municipal"},
          ("forma_ingresso", "Seleção para Vagas Novas"): {"Vestibular", "Enem", "Avaliação Seriada", "Seleção Simplificada"}}


def limpar(r):
    r = re.sub(r"\s+", " ", str(r)).strip()
    return re.sub(r"(?<=[a-zA-Zá-úÁ-Ú\)])\d{1,2}(\s?[-–,]\s?\d{1,2})*$", "", r)


def faixa(r):  # "De 19 a 24 Anos" / "65 anos ou mais" / "Até 18 Anos" → faixa etária padronizada
    if re.match(r"^(Até \d+|De \d+ a \d+|\d+) [Aa]nos( ou mais)?$", r):
        return [("faixa_etaria", r.replace("Anos", "anos"))]


def na_faixa(spec, col):
    """spec = "AA" ou faixa "FM:HK"."""
    if ":" not in spec:
        return spec == col
    a, b = spec.split(":")
    return col2n(a) <= col2n(col) <= col2n(b)


def indicador_da_tabela(tab):
    sec, n = (int(x) for x in tab.split("."))
    return {1: "ies", 3: "cursos", 5: "matriculas", 6: "concluintes"}.get(sec) or \
        ({2: "docentes_ies" if n == 10 else "docentes_exercicio", 4: None if n == 1 else "ingressantes", 7: None}[sec])


c = ler_catalogo(DIAG / "03_catalogo_colunas.xlsx")
c = c[(c.conjunto == "Sinopse por município") & (c.papel == "medida")].copy()
c["tabela"] = c.chave_tabela.str.replace("Tab ", "", regex=False)
ov = pd.read_csv(CONFIG / "xw_override_sinopse.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
rows, erros, ignoradas = [], [], []
for r in c.itertuples():
    d, ind, usados = {k: "Total" for k in DIMS}, None, []
    if ((ov.tabela == r.tabela) & ov.coluna.map(lambda c: na_faixa(c, r.coluna)) & (ov.campo == "ignorar")
            & ov.anos.map(lambda a: int(a[:4]) <= r.ano <= int(a[-4:]))).any():
        ignoradas.append((r.ano, r.tabela, r.coluna)); continue
    # níveis lidos do rótulo completo (o catálogo 03 só tem colunas nivel_1..6; a tabela 2.2 tem 7 níveis)
    for lab in str(r.rotulo_completo).split(" > ")[1:]:
        if lab == "∅":
            continue
        lab = limpar(lab)
        if lab in ("Total", "") or lab in LEGENDAS or lab.startswith("Total por "):
            continue
        if lab in INDICADORES:
            ind = INDICADORES[lab]; continue
        regra = V.get(lab) or faixa(lab)
        if not regra:
            erros.append((r.ano, r.tabela, r.coluna, "rótulo fora do vocabulário", lab)); continue
        for dim, val in regra:
            atual = d[dim]
            if atual == "Total" or val in FILHOS.get((dim, atual), ()):
                d[dim] = val
            elif atual != val:
                erros.append((r.ano, r.tabela, r.coluna, f"conflito em {dim}: {atual} × {val}", r.rotulo_completo))
        usados.append(lab)
    for o in ov[(ov.tabela == r.tabela) & (ov.coluna == r.coluna)].itertuples():
        a1, a2 = (int(x) for x in o.anos.split("-"))
        if a1 <= r.ano <= a2:
            if o.campo == "indicador":
                ind = o.valor
            else:
                d[o.campo] = o.valor
    padrao = indicador_da_tabela(r.tabela)
    if ind is None:
        ind = padrao
    if ind is None:
        erros.append((r.ano, r.tabela, r.coluna, "indicador não identificado", r.rotulo_completo)); continue
    if d["dependencia"] in ("Pública", "Federal", "Estadual", "Municipal") and d["categoria_privada"] == "Total":
        d["categoria_privada"] = "Não se aplica"
    rows.append({"ano": r.ano, "tabela": r.tabela, "aba": r.aba, "arquivo": r.arquivo, "coluna": r.coluna,
                 "indicador": ind, **d, "eh_agregado": any(v in ("Total", "Pública") for v in d.values()),
                 "rotulo_completo": r.rotulo_completo, "alerta_diagnostico": r.alerta_rotulo if isinstance(r.alerta_rotulo, str) else "",
                 "corrigido_manualmente": "sim" if ((ov.tabela == r.tabela) & (ov.coluna == r.coluna)).any() else ""})
X = pd.DataFrame(rows)
if erros:
    print("ERROS:", len(erros))
    for e in erros[:40]:
        print("  ", e)
    sys.exit(1)
dup = X.duplicated(["ano", "tabela", "indicador"] + DIMS, keep=False)
if dup.any():
    print("ERRO: recortes duplicados:", dup.sum())
    print(X[dup][["ano", "tabela", "coluna", "indicador", "rotulo_completo"]].head(30).to_string())
    sys.exit(1)
X.to_csv(CONFIG / "xw_colunas_sinopse.csv", index=False, encoding="utf-8-sig")
voc = [{"rotulo": k, "dimensao": dim, "valor": val} for k, regras in V.items() for dim, val in regras] + \
      [{"rotulo": k, "dimensao": "indicador", "valor": v} for k, v in INDICADORES.items()] + \
      [{"rotulo": k, "dimensao": "(legenda)", "valor": ""} for k in sorted(LEGENDAS)]
pd.DataFrame(voc).to_csv(CONFIG / "vocabulario_sinopse.csv", index=False, encoding="utf-8-sig")
print(f"colunas mapeadas: {len(X):,} | tabelas×anos: {X.groupby(['ano', 'tabela']).ngroups} | indicadores: {sorted(X.indicador.unique())}")
print("corrigidas manualmente:", (X.corrigido_manualmente == 'sim').sum(), "| com alerta do diagnóstico:", (X.alerta_diagnostico != "").sum(),
      "| ignoradas (só no staging):", len(ignoradas), sorted({(a, t) for a, t, _ in ignoradas}))
pd.DataFrame(ignoradas, columns=["ano", "tabela", "coluna"]).to_csv(CONFIG / "xw_colunas_sinopse_ignoradas.csv", index=False, encoding="utf-8-sig")
print("valores por dimensão:", {k: X[k].nunique() for k in DIMS})
