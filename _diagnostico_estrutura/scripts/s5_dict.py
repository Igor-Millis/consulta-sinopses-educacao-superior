"""Gera 06_dicionario_variaveis.md a partir dos catalogos intermediarios.

Uso: python -I s5_dict.py <work_dir> <dir_saida>
"""
import re, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd

work, out = Path(sys.argv[1]), Path(sys.argv[2])
S = pd.read_pickle(work / "S.pkl")
C = pd.read_pickle(work / "C.pkl")
HC = pd.read_pickle(work / "HC.pkl")
RC = pd.read_pickle(work / "RC.pkl")
years = sorted(S.ano.unique())
D = S[S.tipo_aba == "tabela_dados"]


def esc(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def yrs(lst):
    lst = sorted(set(int(x) for x in lst))
    if lst == years:
        return "todos (2017–2024)"
    return ", ".join(map(str, lst))


L = []
L.append("# 06 — Dicionário de variáveis (diagnóstico estrutural)\n")
L.append("> Gerado automaticamente a partir das cópias dos XLSX de 2017–2024, com revisão manual dos pontos sinalizados. "
         "Os rótulos são reproduzidos **como estão nas planilhas** (inclusive com erros de grafia e chamadas de nota coladas, como `…Administrativa1-3`). "
         "Para chegar à célula de origem de cada coluna, use `03_catalogo_colunas.xlsx` (colunas `celula_nivel_*` e `celula_codigo`).\n")
L.append("**Convenções**\n")
L.append("- *Indicador*: aquilo que a célula conta (cursos, vagas, matrículas…). *Dimensão/categoria*: os recortes do cabeçalho (organização acadêmica, dependência administrativa…).")
L.append("- *Unidade*: todas as tabelas de dados são **contagens absolutas** (os títulos começam com \"Número de…\"). Não há percentuais, médias nem valores monetários. Em nenhuma coluna de medida foram encontrados decimais ou negativos (ver 04).")
L.append("- *Linha (unidade de observação)*: as linhas são **agregados** (Brasil, Região, UF, Município e, nos Anexos, Município × curso). Não há microdados de alunos, docentes ou instituições.")
L.append("- *Totais*: colunas cujo caminho contém \"Total\" são agregados de outras colunas da mesma aba. Linhas com \"Total Brasil\", \"Total <Região>\" e \"Total <UF>\" são subtotais misturados às linhas de detalhe.")
L.append("- ⚠️ *Totais não aditivos*: nas tabelas de docentes (2.x), cada docente é contado uma vez em cada nível (notas 3–7). Somar municípios ou categorias **não** reproduz os totais.")
L.append("- ⚠️ *Pseudo-regiões*: a coluna \"Região Geográfica\" também contém `Distância` (Anexos I e III) e `Exterior` (Anexos I e III e tabelas 4.x a 7.x da Sinopse).")
L.append("- ⚠️ *Zeros estruturais*: nos Anexos I e III, cursos, vagas e inscritos EaD não são computados por município (notas 2, 6 e 7). Nas linhas municipais esses valores aparecem como 0, sem ser zero real, e os valores verdadeiros estão nas linhas `Distância`.")
L.append("- ⚠️ *Referência geográfica*: as tabelas 1.x e 2.x usam a sede/reitoria da IES. As tabelas 3.x a 7.x e os Anexos usam o local de oferta.\n")

# ------------------------------------------------------------ Anexos
L.append("## 1. Anexos I, II e III — Tabelas 8.1, 8.2 e 8.3 (dados gerais por curso)\n")
L.append("### 1.1 Universo de cada anexo (subtítulo, célula A3) e título (A4)\n")
L.append("| Conjunto | Ano | Subtítulo (A3) | Título (A4) |")
L.append("|---|---|---|---|")
for _, r in D[D.conjunto != "Sinopse por município"].sort_values(["conjunto", "ano"]).iterrows():
    L.append(f"| {r.conjunto} | {r.ano} | {esc(r.subtitulo_universo)} | {esc(r.titulo_tabela)} |")
L.append("")

A = C[C.conjunto != "Sinopse por município"]
L.append("### 1.2 Colunas identificadoras (linha 12 = código da variável)\n")
L.append("| Conjunto | Coluna | Código (linha 12) | Rótulo (linhas 6–7) | Tipo observado | Anos |")
L.append("|---|---|---|---|---|---|")
ida = A[A.papel == "identificador"]
for (conj, col, code, rot), g in ida.groupby(["conjunto", "coluna", "codigo_variavel", "rotulo_completo"]):
    L.append(f"| {conj} | {col} | `{code}` | {esc(rot)} | {', '.join(sorted(set(g.tipo_dado)))} | {yrs(g.ano)} |")
L.append("")
L.append("> ⚠️ **Rótulo × código das colunas B/C:** em alguns anos o rótulo da linha 6 (\"Unidade da Federação\" / \"Código da UF\") e o código da linha 12 (`NO_UF`/`CO_UF`) "
         "estão em ordens diferentes. A tabela acima mostra os pares exatamente como aparecem. O conteúdo das células deve ser conferido em 04 (perfil: categórico × código numérico).\n")

L.append("### 1.3 Indicadores (nível 2 do cabeçalho, linha 7) e prefixos de código\n")
A2 = A[A.papel == "medida"].copy()
A2["indicador"] = A2.nivel_2.fillna("")
A2["prefixo"] = A2.codigo_variavel.fillna("").map(lambda c: re.match(r"^[A-Z]+?(?=[BLT]?\d|T$|T\d|$)", c).group(0) if re.match(r"^[A-Z]+", c) else "")
L.append("| Conjunto | Indicador (rótulo) | Código da coluna total | Faixa de colunas | Nº de colunas | Unidade | Anos |")
L.append("|---|---|---|---|---|---|---|")
for (conj, ind), g in A2.groupby(["conjunto", "indicador"], sort=False):
    g24 = g[g.ano == g.ano.max()]
    first = g24.sort_values("n_coluna").iloc[0]
    rng = f"{g24.sort_values('n_coluna').coluna.iloc[0]}–{g24.sort_values('n_coluna').coluna.iloc[-1]} ({g24.ano.iloc[0]})"
    L.append(f"| {conj} | {esc(ind)} | `{first.codigo_variavel}` | {rng} | {len(g24)} | contagem | {yrs(g.ano)} |")
L.append("")

L.append("### 1.4 Categorias das dimensões de coluna (níveis 3–6)\n")
L.append("| Conjunto | Nível | Categoria (rótulo original) | Anos em que aparece |")
L.append("|---|---|---|---|")
for _, r in HC[(HC.conjunto != "Sinopse por município") & (HC.nivel_cabecalho >= 3)].sort_values(["conjunto", "nivel_cabecalho", "categoria"]).iterrows():
    L.append(f"| {r.conjunto} | {r.nivel_cabecalho} | {esc(r.categoria)} | {yrs(r.anos.split(','))} |")
L.append("")

L.append("### 1.5 Gramática observada dos códigos de variável (linha 12)\n")
L.append("Padrão inferido **empiricamente** a partir do pareamento código × rótulo hierárquico. Não há documentação oficial deste esquema nos arquivos, então ele deve ser validado antes de ser usado como regra de transformação.\n")
samp = A2[A2.ano == A2.ano.max()].drop_duplicates("codigo_variavel")
L.append("| Código | Indicador | Nível 3 | Nível 4 | Nível 5 | Nível 6 |")
L.append("|---|---|---|---|---|---|")
for _, r in samp[samp.conjunto == samp.conjunto.iloc[0]].sort_values("n_coluna").head(60).iterrows():
    L.append(f"| `{r.codigo_variavel}` | {esc(r.nivel_2)} | {esc(r.nivel_3)} | {esc(r.nivel_4)} | {esc(r.nivel_5)} | {esc(r.nivel_6)} |")
L.append("\n*(primeiras 60 colunas de medida do anexo mais recente; a lista completa por ano está em `03_catalogo_colunas.xlsx`)*\n")

L.append("### 1.6 Códigos de variável que mudam entre anos\n")
cod = A2.groupby(["conjunto", "codigo_variavel"]).ano.apply(lambda s: sorted(set(s))).reset_index()
var = cod[cod.ano.map(len) < cod.groupby("conjunto").ano.transform(lambda s: max(len(x) for x in s))]
if len(var):
    L.append("| Conjunto | Código | Anos presentes |")
    L.append("|---|---|---|")
    for _, r in var.sort_values(["conjunto", "codigo_variavel"]).iterrows():
        L.append(f"| {r.conjunto} | `{r.codigo_variavel}` | {yrs(r.ano)} |")
else:
    L.append("Nenhum código de variável muda: o conjunto de códigos é o mesmo em todos os anos de cada anexo.")
L.append("")
# mesmo codigo, rotulo diferente
mult = A2.groupby(["conjunto", "codigo_variavel"]).rotulo_normalizado.nunique()
mult = mult[mult > 1].reset_index()
L.append(f"Mesmo código com rótulo hierárquico diferente entre anos (após a normalização): **{len(mult)}** casos. A lista está em 05 › `pareamento_colunas` (classificação \"Equivalência parcial\").\n")

# ------------------------------------------------------------ Sinopse por municipio
L.append("## 2. Sinopse por município — tabelas 1.x a 7.x\n")
L.append("Cada aba é uma tabela de contagem em que as linhas são Brasil, Região, UF e Município (e, em algumas tabelas, também o Nível Acadêmico do Curso). "
         "As colunas cruzam categorias hierárquicas. Não existe linha de códigos de variável: a identificação das colunas depende só dos rótulos.\n")
M = D[D.conjunto == "Sinopse por município"]
for key, g in sorted(M.groupby("chave_tabela"), key=lambda kv: [int(x) for x in re.findall(r"\d+", kv[0])]):
    g = g.sort_values("ano")
    last = g.iloc[-1]
    L.append(f"### {key} — aba `{last.aba!r}` ({last.ano})\n")
    L.append(f"- **Título ({last.celula_titulo}, {last.ano}):** {esc(last.titulo_tabela)}")
    L.append(f"- **Tema (A2) / universo (A3):** {esc(last.tema_secao)} / {esc(last.subtitulo_universo)}")
    L.append(f"- **Anos presentes:** {yrs(g.ano)}; nomes da aba: {', '.join(sorted({repr(a) for a in g.aba}))}")
    L.append(f"- **Unidade:** {esc(last.unidade_medida_presumida)} · **Indicador (título):** {esc(last.indicador_titulo)}")
    L.append(f"- **Dimensões de linha (identificadores):** {esc(last.colunas_identificadoras)}")
    L.append(f"- **Níveis geográficos ({last.ano}):** {esc(last.niveis_geograficos)}")
    L.append(f"- **Colunas úteis por ano:** " + ", ".join(f"{r.ano}: {r.n_col_util}" for r in g.itertuples()))
    hc = HC[(HC.chave_tabela == key)]
    for lvl, gg in hc.groupby("nivel_cabecalho"):
        allc = [esc(x) for x in gg.categoria]
        varc = [f"{esc(r.categoria)} ({r.anos})" for r in gg.itertuples() if r.situacao != "todos os anos da tabela"]
        txt = "; ".join(allc[:40]) + (" …" if len(allc) > 40 else "")
        L.append(f"- **Categorias — nível {lvl}:** {txt}")
        if varc:
            L.append(f"  - *variam entre anos:* " + "; ".join(varc[:25]) + (" …" if len(varc) > 25 else ""))
    nt = esc(last.notas_texto)
    L.append(f"- **Notas de rodapé ({last.ano}):** {nt[:1500]}{' …' if len(nt) > 1500 else ''}")
    L.append("")

# ------------------------------------------------------------ categorias de linha
L.append("## 3. Categorias das colunas identificadoras (linhas)\n")
L.append("| Conjunto | Tabela | Coluna | Ano | Nº distintos | Adicionados vs ano anterior | Removidos vs ano anterior |")
L.append("|---|---|---|---|---|---|---|")
rc = RC[~RC.coluna_identificadora.str.contains("Munic", na=False)]
rc = rc[rc.chave_tabela.isin(["Anexo I — Tabela 8.1", "Anexo II — Tabela 8.2", "Anexo III — Tabela 8.3", "Tab 4.2", "Tab 5.1", "Tab 1.1"])]
for _, r in rc.sort_values(["conjunto", "chave_tabela", "coluna_identificadora", "ano"]).iterrows():
    L.append(f"| {r.conjunto} | {r.chave_tabela} | {esc(r.coluna_identificadora)} | {r.ano} | {r.n_valores_distintos} | {esc(r.adicionados_vs_ano_anterior)[:400]} | {esc(r.removidos_vs_ano_anterior)[:400]} |")
L.append("\n*(recorte de tabelas representativas; todas as tabelas estão em 05 › `categorias_linhas`)*\n")

(out / "06_dicionario_variaveis.md").write_text("\n".join(L), encoding="utf8")
print("06 ok", len(L), "linhas")
