"""Monta a resposta em português: resposta direta, tabela, gráfico (PNG), interpretação, supostos, fontes e limitações.

Todo número do texto vem de `analise.Resultado` (calculado em código). Formatação brasileira: 1.234.567 e 12,3%.
"""
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .config import SAIDAS

# Paleta categórica de referência (skill dataviz, validada): ordem fixa, nunca reciclada
CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
TINTA, TINTA2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
MAX_SERIES = 8


@dataclass
class Resposta:
    pergunta: str
    texto: str
    tabela: pd.DataFrame | None = None
    grafico: Path | None = None
    csv: Path | None = None
    consulta: object = None
    sql: list = field(default_factory=list)
    precisa_esclarecer: bool = False
    interpretador: str = "regras"

    def __str__(self):
        return self.texto


CASAS = 0   # casas decimais dos valores da resposta corrente (indicadores derivados usam 2)


def n(v, casas=None):
    casas = CASAS if casas is None else casas
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v, casas=1, sinal=False):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    s = f"{v * 100:+.{casas}f}" if sinal else f"{v * 100:.{casas}f}"
    return s.replace(".", ",") + "%"


def sn(v):
    return ("+" if v > 0 else "") + n(v) if v is not None and not pd.isna(v) else "—"


def _md_tabela(df: pd.DataFrame, max_linhas=30) -> str:
    d = df.head(max_linhas).copy()
    if d.index.name or not isinstance(d.index, pd.RangeIndex):
        d = d.reset_index()
    cols = list(d.columns)
    fmt = []
    for c in cols:
        if "%" in str(c) or "participação" in str(c) or "taxa" in str(c):
            fmt.append(lambda v: pct(v))
        elif c in ("ano", "ano_inicial", "ano_final", "ano_do_máximo", "ano_do_mínimo", "posição"):
            fmt.append(lambda v: str(int(v)) if not pd.isna(v) else "—")
        elif pd.api.types.is_numeric_dtype(d[c]):
            fmt.append(lambda v: n(v))
        else:
            fmt.append(lambda v: "—" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v))
    linhas = ["| " + " | ".join(str(c).replace("_", " ") for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in d.iterrows():
        linhas.append("| " + " | ".join(f(r[c]) for f, c in zip(fmt, cols)) + " |")
    if len(df) > max_linhas:
        linhas.append(f"\n_(mostrando {max_linhas} de {len(df)} linhas; a tabela completa está no CSV)_")
    return "\n".join(linhas)


def _arquivo(pergunta, ext):
    SAIDAS.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^a-z0-9]+", "_", pergunta.lower())[:50].strip("_") or "consulta"
    return SAIDAS / f"{datetime.now():%Y%m%d_%H%M%S}_{base}.{ext}"


def grafico(res, titulo, unidade, pergunta):
    if res.serie is None and res.barras is None:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
    fig.patch.set_facecolor(FUNDO)
    ax.set_facecolor(FUNDO)
    eh_pct = res.tipo == "participacao" or (res.barras is not None and res.fatos.get("criterio") == "percentual")
    fmt = FuncFormatter(lambda v, _: pct(v, 0) if eh_pct else n(v))
    if res.serie is not None:
        s = res.serie
        if len(s.columns) > MAX_SERIES:   # dobra o excedente: mostra as maiores no último ano
            s = s[s.iloc[-1].sort_values(ascending=False).index[:MAX_SERIES]]
        for i, col in enumerate(s.columns):
            y = s[col]
            ax.plot(s.index, y, color=CORES[i], linewidth=2, marker="o", markersize=5, label=str(col))
            ult = y.dropna()
            if len(s.columns) <= 4 and not ult.empty:
                ax.annotate(pct(ult.iloc[-1]) if eh_pct else n(ult.iloc[-1]), (ult.index[-1], ult.iloc[-1]),
                            xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=TINTA)
        ax.set_xticks(list(s.index))
        ax.yaxis.set_major_formatter(fmt)
        if len(s.columns) >= 2:
            ax.legend(frameon=False, fontsize=9, labelcolor=TINTA2)
        if not eh_pct:
            ax.set_ylim(bottom=0)
    else:
        b = res.barras.dropna().head(20).iloc[::-1]
        ax.barh(b["recorte"].astype(str), b.iloc[:, 1], color=CORES[0], height=0.6)
        ax.xaxis.set_major_formatter(fmt)
        for y, v in enumerate(b.iloc[:, 1]):
            ax.annotate(pct(v) if eh_pct else n(v), (v, y), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=8, color=TINTA)
        ax.axvline(0, color=TINTA2, linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(GRADE)
    ax.tick_params(colors=TINTA2, labelsize=9)
    ax.grid(axis="y" if res.serie is not None else "x", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
    fig.text(0.01, 0.01, "Fonte: INEP — Sinopses Estatísticas da Educação Superior (Graduação). Elaboração: Igor L. Millis - Projeto Independente com Dados Públicos.",
             fontsize=7, color=TINTA2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    caminho = _arquivo(pergunta, "png")
    fig.savefig(caminho, facecolor=FUNDO)
    plt.close(fig)
    return caminho


def descrever_recorte(c, cat):
    partes = []
    for d, v in c.filtros.items():
        if d == "curso":
            partes.append(f"curso {cat.nome_curso.get(v, v)}")
        else:
            partes.append(str(v).lower() if d in ("rede", "modalidade", "dependencia") else str(v))
    return (" (" + ", ".join(partes) + ")") if partes else ""


def principal(res, c, cat, unidade, nome_ind):
    f = res.fatos
    loc = ", ".join(l.nome for l in c.locais) or "UFs"
    rec = descrever_recorte(c, cat)
    if res.tipo == "valor":
        if "valor" in f:
            return f"**{nome_ind}{rec} — {f['recorte']}, {f['ano']}: {n(f['valor'])} {unidade}.**"
        tot = f" (soma das categorias: {n(f['total'])})" if f.get("total") else ""
        return f"**{nome_ind}{rec} — {loc}, {f['ano']}**{tot}:"
    if res.tipo in ("serie", "comparacao"):
        tab = res.tabela
        frases = []
        resumo = _resumo_serie(res)
        for _, r in resumo.iterrows():
            frases.append(f"**{r['série']}**: {n(r['valor_inicial'])} em {r['ano_inicial']} → {n(r['valor_final'])} em "
                          f"{r['ano_final']} ({sn(r['variação_absoluta'])}; {pct(r['variação_%'], sinal=True)}; "
                          f"média de {pct(r['taxa_média_anual'], sinal=True)} ao ano).")
        if res.serie is not None and len(res.serie.columns) <= 4:
            for col in res.serie.columns:
                y = res.serie[col].dropna()
                d = y.diff().dropna()
                if len(d) >= 2:
                    i_alta, i_queda = d.idxmax(), d.idxmin()
                    ant = lambda a: int(y.index[list(y.index).index(a) - 1])
                    if d[i_alta] > 0:
                        txt = f"{col} — maior alta anual: {ant(i_alta)}→{int(i_alta)} ({sn(d[i_alta])}"
                        txt += f"; {pct(d[i_alta] / y[ant(i_alta)], sinal=True)})" if y[ant(i_alta)] else ")"
                    else:
                        txt = f"{col} — nenhuma alta anual no período"
                    if d[i_queda] < 0:
                        txt += f"; maior queda anual: {ant(i_queda)}→{int(i_queda)} ({sn(d[i_queda])}"
                        txt += f"; {pct(d[i_queda] / y[ant(i_queda)], sinal=True)})" if y[ant(i_queda)] else ")"
                    else:
                        txt += "; nenhuma queda anual no período"
                    frases.append(txt + ".")
        if f.get("ultrapassagem"):
            a, b = f["series"]
            frases.append(f"A ordem entre {a} e {b} se inverteu em **{f['ultrapassagem']}**.")
        elif res.tipo == "comparacao" and f.get("series"):
            frases.append("Não houve inversão de posição entre as duas séries no período.")
        if f.get("razao_final") is not None and res.tipo == "comparacao":
            a, b = f["series"]
            frases.append(f"No último ano, {a} tem {n(f['razao_final'], 2)} vezes o valor de {b} "
                          f"(diferença de {n(f['diferenca_final'])}).")
        return f"**{nome_ind}{rec} — {min(f['anos'])}–{max(f['anos'])}**\n\n" + "\n".join("- " + x for x in frases)
    if res.tipo == "participacao":
        u = f.get("ultimo")
        if u is None or u.empty:
            return "Não há dados para calcular a participação."
        ano = int(u["ano"].max())
        linhas = []
        for _, r in u.iterrows():
            rot = " — ".join(str(r[k]) for k in u.columns if k not in ("ano", "parte", "todo", "participação", "em relação a"))
            ref = f" em {r['em relação a']}" if "em relação a" in u.columns else ""
            parte = f"{f['rotulo_parte']} em " if f.get("rotulo_parte") else ""
            linhas.append(f"{parte}{rot}{ref}: **{pct(r['participação'])}** ({n(r['parte'])} de {n(r['todo'])})")
        txt = f"**Participação — {nome_ind.lower()}{rec}, {ano}**\n\n" + "\n".join("- " + x for x in linhas)
        p0 = f.get("primeiro")
        if p0 is not None and len(p0) == len(u) == 1:
            txt += (f"\n- Em {int(p0['ano'].iloc[0])} era {pct(p0['participação'].iloc[0])} "
                    f"({pct(u['participação'].iloc[0] - p0['participação'].iloc[0], sinal=True).replace('%', ' p.p.')}).")
        return txt
    if res.tipo == "ranking":
        top = f["top"]
        ent = "cursos" if "curso" in c.quebras else ("municípios" if c.listar_municipios_uf else "UFs")
        ordem = "menores" if c.ordem == "asc" else "maiores"
        lider = top.iloc[0]
        return (f"**{len(top)} {ordem} {ent} em {nome_ind.lower()}{rec} — {loc}, {f['ano1']}** "
                f"(de {f['n_total']} com dados). Primeiro: **{lider['nome']}** com {n(lider['valor'])}"
                + (f" ({pct(lider['participação_no_conjunto'])} do conjunto)" if "participação_no_conjunto" in top.columns else "")
                + ".")
    if res.tipo == "crescimento":
        top = f["top"]
        if top.empty:
            return "Nenhum item com dados nos dois anos para comparar."
        ent = "cursos" if "curso" in c.quebras else ("municípios" if c.listar_municipios_uf else "UFs")
        crit = "variação percentual" if f["criterio"] == "percentual" else "variação absoluta"
        if f.get("so_reducao"):
            return (f"**{len(f['top'])} de {f['n_total']} {ent} com redução em {nome_ind.lower()}{rec} — {loc}, "
                    f"{f['ano0']}→{f['ano1']}** (maiores quedas primeiro, por {crit}).") if not top.empty else (
                    f"Nenhum dos {ent} com dados nos dois anos teve redução em {nome_ind.lower()}{rec} entre "
                    f"{f['ano0']} e {f['ano1']}.")
        lider = top.iloc[0]
        return (f"**{ent.capitalize()} com {'menor' if c.ordem == 'asc' else 'maior'} crescimento em "
                f"{nome_ind.lower()}{rec} — {loc}, {f['ano0']}→{f['ano1']}** (ordenado por {crit}). "
                f"Primeiro: **{lider['nome']}**: {n(lider[f'valor_{f['ano0']}'])} → {n(lider[f'valor_{f['ano1']}'])} "
                f"({sn(lider['variação_absoluta'])}; {pct(lider['variação_%'], sinal=True)}).")
    return ""


def _resumo_serie(res):
    s = res.serie
    linhas = []
    from .analise import cagr, variacao
    for col in s.columns:
        y = s[col].dropna()
        if y.empty:
            continue
        va, vp = variacao(y.iloc[0], y.iloc[-1])
        linhas.append({"série": col, "ano_inicial": int(y.index[0]), "valor_inicial": y.iloc[0],
                       "ano_final": int(y.index[-1]), "valor_final": y.iloc[-1], "variação_absoluta": va,
                       "variação_%": vp, "taxa_média_anual": cagr(y.iloc[0], y.iloc[-1], y.index[-1] - y.index[0])})
    r = pd.DataFrame(linhas)
    return r.sort_values("valor_final", ascending=False).head(MAX_SERIES) if not r.empty else r


def interpretacao(res, c):
    f = res.fatos
    frases = []
    if res.tipo in ("serie", "comparacao") and res.serie is not None:
        for col in list(res.serie.columns)[:4]:
            y = res.serie[col].dropna()
            if len(y) >= 3:
                d = np.sign(np.diff(y.values))
                if (d > 0).all():
                    frases.append(f"{col}: crescimento em todos os anos da série.")
                elif (d < 0).all():
                    frases.append(f"{col}: queda em todos os anos da série.")
                else:
                    frases.append(f"{col}: trajetória com oscilações (máximo em {int(y.idxmax())}, mínimo em {int(y.idxmin())}).")
    if f.get("ausentes"):
        for k, anos in f["ausentes"].items():
            frases.append(f"{k}: sem dado publicado em {', '.join(map(str, anos))} (ausência, não zero).")
    if res.tipo == "crescimento" and f.get("criterio") == "percentual":
        from .analise import BASE_MINIMA_PERCENTUAL
        frases.append(f"Para a variação percentual, só entram itens com pelo menos {BASE_MINIMA_PERCENTUAL} no ano inicial.")
    if res.tipo == "crescimento" and f.get("sem_base"):
        frases.append(f"{f['sem_base']} item(ns) não existiam no ano inicial (sem base de comparação) e ficaram fora.")
    return frases


def montar(pergunta, c, cat, res, df_bruto, plano, notas_extra, ocorr, sqls) -> Resposta:
    global CASAS
    ind = cat.indicadores.get(c.indicador) or cat.derivados[c.indicador]
    CASAS = ind.get("casas", 0)
    try:
        return _montar(pergunta, c, cat, res, df_bruto, plano, notas_extra, ocorr, sqls, ind)
    finally:
        CASAS = 0


def _montar(pergunta, c, cat, res, df_bruto, plano, notas_extra, ocorr, sqls, ind) -> Resposta:
    partes = [principal(res, c, cat, ind["unidade"], ind["nome"])]
    tabela = res.tabela
    if tabela is not None and not tabela.empty:
        partes.append(_md_tabela(tabela))
    interp = interpretacao(res, c)
    if interp:
        partes.append("**Interpretação**\n" + "\n".join("- " + x for x in interp))
    if c.supostos:
        partes.append("**Como a pergunta foi entendida**\n" + "\n".join("- " + x for x in c.supostos))
    fontes = [f"- Dados: {cat.bruto['fonte_dados']}."]
    fontes.append(f"- Camada de consulta: `{plano.fonte}` — {cat.bruto['fontes'][plano.fonte]['descricao']}")
    if "tabelas" in df_bruto.columns:
        tabs = sorted({t for v in df_bruto["tabelas"].dropna() for t in str(v).split(",")})
        fontes.append(f"- Tabela(s) da Sinopse: {', '.join(tabs)}.")
    if "origem" in df_bruto.columns:
        celulas = [o for o in df_bruto["origem"].dropna() if not str(o).startswith("Σ")]
        if celulas:
            fontes.append(f"- Rastreabilidade: cada valor guarda a célula de origem (aba!célula; exemplo: `{celulas[0]}`).")
        elif not df_bruto["origem"].dropna().empty:
            fontes.append("- Rastreabilidade: valores de UF e região são a soma dos municípios no mart; cada valor "
                          "municipal guarda a sua célula de origem (aba!célula).")
    fontes.append(f"- Definição: {ind['definicao']}")
    partes.append("**Fontes**\n" + "\n".join(fontes))
    lim = list(dict.fromkeys([*plano.notas, *notas_extra, *ind.get("limitacoes", [])]))
    if "tem_suspeito" in df_bruto.columns and df_bruto["tem_suspeito"].fillna(False).any():
        n_s, n_t = int(df_bruto["tem_suspeito"].fillna(False).sum()), len(df_bruto)
        lim.append(f"**{n_s} de {n_t}** valores usados contêm células marcadas como **suspeitas** na publicação do "
                   "INEP (mantidas como publicadas; ver ocorrências abaixo). Use esses números com cautela.")
    for _, o in ocorr.iterrows():
        lim.append(f"Ocorrência {o['id']} ({o['anos']}, tabela {o['tabela']}): {o['descricao'][:300]}"
                   + ("…" if len(o["descricao"]) > 300 else ""))
    if lim:
        partes.append("**Limitações**\n" + "\n".join("- " + x for x in lim))
    nome_ind = ind["nome"]
    titulo = f"{nome_ind}{descrever_recorte(c, cat)} — " + (", ".join(l.nome for l in c.locais) or "UFs")
    png = grafico(res, titulo, ind["unidade"], pergunta)
    csv = None
    if tabela is not None and not tabela.empty:
        csv = _arquivo(pergunta, "csv")
        tabela.to_csv(csv, sep=";", decimal=",", encoding="utf-8-sig")
    if png:
        partes.append(f"Gráfico: `{png}`")
    if csv:
        partes.append(f"Tabela (CSV): `{csv}`")
    return Resposta(pergunta, "\n\n".join(partes), tabela, png, csv, c, sqls)


def esclarecimento(pergunta, c, motivos) -> Resposta:
    txt = "Preciso de um esclarecimento antes de consultar os dados:\n\n" + "\n".join("- " + m for m in motivos)
    if c.supostos:
        txt += "\n\nO que já entendi:\n" + "\n".join("- " + s for s in c.supostos)
    return Resposta(pergunta, txt, consulta=c, precisa_esclarecer=True)


def sem_dados(pergunta, c, plano) -> Resposta:
    txt = ("Não há valores publicados para esse recorte. A ausência de linha **não** é tratada como zero.\n\n"
           f"Recorte procurado: indicador {c.indicador}, anos {c.anos}, locais "
           f"{[l.nome for l in c.locais] or 'UFs'}, filtros {c.filtros or 'nenhum'}.")
    if plano.notas:
        txt += "\n\n" + "\n".join("- " + x for x in plano.notas)
    return Resposta(pergunta, txt, consulta=c)
