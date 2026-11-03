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
MAX_SERIES_PROJECAO = 4   # acima disto os envelopes se sobrepõem e o gráfico fica ilegível
NOTA_PROJECAO = ("Projeção: tendência linear (mínimos quadrados) ajustada aos anos observados, com intervalo de "
                 "previsão de 95%. É extrapolação estatística, **não é dado do INEP**: não incorpora mudanças de "
                 "política, demografia ou choques (como 2020), e, com poucos anos de série, o intervalo é largo.")


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


def projecoes(res):
    """Projeção de tendência (analise.projetar) das até MAX_SERIES_PROJECAO séries temporais da resposta."""
    if res.serie is None or res.tipo not in ("serie", "comparacao", "participacao"):
        return {}
    if len(res.serie.columns) > MAX_SERIES_PROJECAO:
        return {}
    from .analise import projetar
    teto = 1.0 if res.tipo == "participacao" else None
    out = {}
    for col in res.serie.columns:
        y = res.serie[col].dropna()
        # só projeta a partir do último ano da série (série encerrada antes não é estendida)
        if not y.empty and y.index[-1] == res.serie.index.max():
            p = projetar(y, maximo=teto)
            if p is not None:
                out[col] = p
    return out


# Princípios de storytelling com dados: o título diz a conclusão; cor só no foco (ES), o resto é contexto em
# cinza; rótulo direto na ponta da linha; grade e eixos recessivos; marcadores só no início e no fim.
FOCO = "Espírito Santo"
CINZA, CINZA_BARRA, FAIXA_PROJ, GRADE_SUAVE = "#9d9c97", "#cfcec9", "#f1f0eb", "#ecebe7"
RODAPE = ("Fonte: INEP — Sinopses Estatísticas da Educação Superior. "
          "Elaboração: Igor L. Millis - Projeto Independente com Dados Públicos.")


def _eh_foco(rotulo):
    return FOCO in str(rotulo)


def _pp(v):
    return f"{v * 100:+.1f}".replace(".", ",").replace("-", "−") + " p.p."   # espaço não separável: o texto não quebra entre número e unidade


def _titulo_serie(s, nome_ind, eh_pct, parte=None):
    """Título-conclusão a partir da série em foco (ES, se houver; senão a maior no último ano)."""
    from .analise import variacao
    cols = [c for c in s.columns if len(s[c].dropna()) >= 2]
    if not cols:
        return None
    foco = next((c for c in cols if _eh_foco(c)), cols[0])
    y = s[foco].dropna()
    a0, a1, v0, v1 = int(y.index[0]), int(y.index[-1]), y.iloc[0], y.iloc[-1]
    periodo = f"entre {a0} e {a1}"
    if eh_pct:
        verbo = "subiu" if v1 - v0 >= 0.0005 else "caiu" if v1 - v0 <= -0.0005 else "ficou estável"
        quem = f" ({parte.lower()})" if parte else ""
        return f"{foco}: participação{quem} {verbo} de {pct(v0)} para {pct(v1)} ({_pp(v1 - v0)}) {periodo}"
    _, vp = variacao(v0, v1)
    if CASAS or pd.isna(vp):   # razões (candidatos por vaga etc.): de → para, sem verbo no plural
        return f"{foco}: {nome_ind.lower()} passou de {n(v0)} para {n(v1)} {periodo}"
    verbo = "cresceram" if vp >= 0.005 else "caíram" if vp <= -0.005 else "ficaram estáveis"
    txt = f"{foco}: {nome_ind.lower()} {verbo}" + (f" {pct(abs(vp))}" if verbo != "ficaram estáveis" else "")
    txt += f" {periodo}"
    outros = [c for c in cols if c != foco]
    if len(outros) == 1:
        y2 = s[outros[0]].dropna()
        _, vp2 = variacao(y2.iloc[0], y2.iloc[-1])
        if not pd.isna(vp2):
            txt += f" ({outros[0]}: {pct(vp2, sinal=True)})"
    return txt


AGREGADOS = {"Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"}


def _titulo_barras(b, nome_ind, res):
    """Posição do foco. Ranking/crescimento: ordem e total vêm da análise (as barras são só o top)."""
    focos = [i for i, r in enumerate(b["recorte"]) if _eh_foco(r)]
    if len(focos) != 1 or len(b) < 3:
        return None
    pos = focos[0] + 1
    if res.tipo == "crescimento":
        f = res.fatos
        if f.get("so_reducao"):
            return f"{FOCO}: {pos}ª maior queda entre {f['n_total']} em {nome_ind.lower()} ({f['ano0']}→{f['ano1']})"
        crit = "em % " if f.get("criterio") == "percentual" else ""
        return f"{FOCO}: {pos}º lugar entre {f['n_total']} no crescimento {crit}de {nome_ind.lower()} ({f['ano0']}→{f['ano1']})"
    total = res.fatos.get("n_total", len(b)) if res.tipo == "ranking" else len(b)
    v = b.iloc[:, 1].tolist()
    ordem = " (do menor para o maior)" if res.tipo == "ranking" and v == sorted(v) and v[0] != v[-1] else ""
    return f"{FOCO}: {pos}º lugar entre {total} em {nome_ind.lower()}{ordem}"


def _sem_agregados(b):
    """Brasil e regiões achatam as barras das UFs e não entram na posição: saem do gráfico (ficam na tabela)."""
    agreg = b["recorte"].astype(str).isin(AGREGADOS)
    if agreg.any() and (~agreg).sum() >= 3:
        return b[~agreg].reset_index(drop=True), sorted(b.loc[agreg, "recorte"].astype(str))
    return b, []


def _afastar(ys, folga):
    """Empurra posições verticais (fração do eixo) para que rótulos vizinhos não se sobreponham."""
    ordem = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for k in range(1, len(ordem)):
        a, b = ordem[k - 1], ordem[k]
        out[b] = max(out[b], out[a] + folga)
    excesso = out[ordem[-1]] - 1.02 if ordem else 0
    if excesso > 0:
        out = [v - excesso for v in out]
    return out


def _cabecalho(fig, titulo, subtitulo):
    import textwrap
    if not titulo:   # sem conclusão calculável: a descrição sobe para título
        titulo, subtitulo = subtitulo, ""
    linhas = textwrap.wrap(titulo, 70)
    y = 0.965
    if linhas:
        fig.text(0.02, y, "\n".join(linhas), fontsize=13.5, color=TINTA, fontweight="semibold", va="top",
                 linespacing=1.25)
        y -= 0.052 * len(linhas) + 0.008
    fig.text(0.02, y, subtitulo, fontsize=9.5, color=TINTA2, va="top")
    return y - 0.045   # topo disponível para a área do gráfico


def grafico(res, titulo, unidade, pergunta, proj=None, nome_ind=None):
    if res.serie is None and res.barras is None:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter, MaxNLocator
    nome_ind = nome_ind or titulo.split(" — ")[0]
    eh_pct = res.tipo == "participacao" or (res.barras is not None and res.fatos.get("criterio") == "percentual")
    fv = (lambda v: pct(v)) if eh_pct else (lambda v: n(v))
    fig = plt.figure(figsize=(10, 5.6), dpi=120)
    fig.patch.set_facecolor(FUNDO)
    parte = res.fatos.get("rotulo_parte") if res.tipo == "participacao" else None
    subtitulo = (f"Participação{' de ' + parte if parte else ''} (%) — " if res.tipo == "participacao" else "") + titulo
    if res.serie is not None:
        s = res.serie
        if len(s.columns) > MAX_SERIES:   # dobra o excedente: mostra as maiores no último ano
            s = s[s.iloc[-1].sort_values(ascending=False).index[:MAX_SERIES]]
        cols = list(s.columns)
        rotular = len(cols) <= 4
        focos = [c for c in cols if _eh_foco(c)]
        cinza_contexto = rotular and 0 < len(focos) < len(cols)
        cor = {c: (CORES[focos.index(c)] if c in focos else CINZA) if cinza_contexto else CORES[i]
               for i, c in enumerate(cols)}
        destaque = {c: (c in focos) if focos else (i == 0) for i, c in enumerate(cols)}
        if proj:
            a_proj = sorted({a for p in proj.values() for a in p.index})
            subtitulo += f" · {min(a_proj)}–{max(a_proj)}: projeção de tendência (faixa = intervalo de 95%)"
        topo = _cabecalho(fig, _titulo_serie(s, nome_ind, eh_pct, parte), subtitulo)
        ax = fig.add_axes((0.075, 0.1, (0.74 if rotular else 0.9) - 0.075, topo - 0.1 - (0.05 if len(cols) >= 2 else 0)))
        ax.set_facecolor(FUNDO)
        fins = []
        for c in cols:
            y = s[c].dropna()
            if y.empty:
                continue
            lw, z = (2.6, 3) if destaque[c] else (1.8, 2)
            ax.plot(y.index, y.values, color=cor[c], linewidth=lw, zorder=z, solid_capstyle="round")
            ax.plot([y.index[0], y.index[-1]], [y.iloc[0], y.iloc[-1]], "o", color=cor[c], markersize=6.5,
                    markeredgecolor=FUNDO, markeredgewidth=1.5, zorder=z + 1)
            ultimo = (y.index[-1], y.iloc[-1])
            p = (proj or {}).get(c)
            if p is not None:   # tracejado a partir do último observado + envelope de 95%
                xs = [y.index[-1], *p.index]
                ax.fill_between(xs, [y.iloc[-1], *p["inferior"]], [y.iloc[-1], *p["superior"]],
                                color=cor[c], alpha=0.16 if destaque[c] else 0.10, linewidth=0, zorder=1)
                ax.plot(xs, [y.iloc[-1], *p["previsto"]], color=cor[c], linewidth=lw * 0.75, linestyle=(0, (4, 3)),
                        zorder=z)
                ax.plot(p.index[-1], p["previsto"].iloc[-1], "o", color=cor[c], markerfacecolor=FUNDO,
                        markersize=6, markeredgewidth=1.6, zorder=z + 1)
                ultimo = (p.index[-1], p["previsto"].iloc[-1])
            if destaque[c] and (len(cols) <= 2 or cinza_contexto or not focos):
                ax.annotate(fv(y.iloc[0]), (y.index[0], y.iloc[0]), xytext=(0, 9), textcoords="offset points",
                            ha="center", fontsize=9, color=TINTA2)
            texto = f"{y.index[-1]}: {fv(y.iloc[-1])}"
            if p is not None:
                texto += f"\n{p.index[-1]}: {fv(p['previsto'].iloc[-1])} (proj.)"
            fins.append((c, ultimo, texto))
        ax.yaxis.set_major_locator(MaxNLocator(6, steps=[1, 2, 5, 10]))   # sem passos de 2,5 (marca "18%" em 17,5%)
        ax.margins(y=0.14)
        y0, y1 = ax.get_ylim()
        casas_pct = 0 if (y1 - y0) >= 0.08 else 1   # faixa estreita: 17,5% e não "18%"
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: pct(v, casas_pct) if eh_pct else n(v)))
        anos_x = list(s.index) + (a_proj if proj else [])
        ax.set_xticks(anos_x)
        ax.set_xlim(min(anos_x) - 0.4, max(anos_x) + 0.25)
        if proj:   # período projetado com fundo próprio: o leitor vê onde acabam os dados
            ax.axvspan(s.index.max() + 0.5, max(anos_x) + 0.25, color=FAIXA_PROJ, linewidth=0, zorder=0)
            ax.text(s.index.max() + 0.6, 0.98, "Projeção", transform=ax.get_xaxis_transform(), ha="left",
                    va="top", fontsize=9, color=TINTA2, fontstyle="italic")
        if rotular and fins:
            y0, y1 = ax.get_ylim()
            alvo = [(u[1] - y0) / (y1 - y0) for _, u, _ in fins]
            pos = _afastar(alvo, 0.15 if any("\n" in t for *_, t in fins) else 0.11)
            for (c, u, texto), py in zip(fins, pos):   # nome + valores na ponta, alinhados ao último ponto
                ax.text(1.02, py, str(c), transform=ax.transAxes, fontsize=10, color=TINTA, va="bottom",
                        fontweight="semibold" if destaque[c] else "normal", clip_on=False)
                ax.text(1.02, py - 0.006, texto, transform=ax.transAxes, fontsize=8.5, color=TINTA2, va="top",
                        linespacing=1.3, clip_on=False)
        if len(cols) >= 2:   # legenda sempre presente com 2+ séries (identidade nunca só pela cor)
            alcas = [Line2D([], [], color=cor[c], linewidth=2.6 if destaque[c] else 1.8) for c in cols]
            ax.legend(alcas, [str(c) for c in cols], loc="lower left", bbox_to_anchor=(0, 1.0), ncol=min(len(cols), 4),
                      frameon=False, fontsize=8.5, labelcolor=TINTA2, handlelength=1.8, borderaxespad=0.3)
        ax.grid(axis="y", color=GRADE_SUAVE, linewidth=0.8)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color(GRADE)
        ax.tick_params(axis="y", length=0, colors=TINTA2, labelsize=8.5)
        ax.tick_params(axis="x", colors=TINTA2, labelsize=9, color=GRADE)
    else:
        f = res.fatos
        if res.tipo == "crescimento":   # as barras são a variação, não o nível: o título precisa dizer
            subtitulo += (f" · variação {'percentual' if f.get('criterio') == 'percentual' else 'absoluta'}"
                          f" {f['ano0']}→{f['ano1']}" + (" (só reduções)" if f.get("so_reducao") else ""))
        elif f.get("ano1") or f.get("ano"):
            subtitulo += f" · {f.get('ano1') or f.get('ano')}"
        b = res.barras.dropna().reset_index(drop=True)
        if res.tipo not in ("ranking", "crescimento"):   # ranking e crescimento já vêm na ordem pedida
            b = b.sort_values(b.columns[1], ascending=False).reset_index(drop=True)
            b, fora = _sem_agregados(b)
            if fora:
                subtitulo += f" · {', '.join(fora)} fora do gráfico (valores na tabela)"
        titulo_acao = _titulo_barras(b, nome_ind, res)
        if len(b) > 20:   # mostra as 20 maiores; o foco entra mesmo se estiver abaixo delas
            foco_fora = b.iloc[20:][b.iloc[20:]["recorte"].map(_eh_foco)]
            b = pd.concat([b.head(20 - len(foco_fora)), foco_fora]) if len(foco_fora) <= 3 else b.head(20)
        rotulos = b["recorte"].astype(str).tolist()
        topo = _cabecalho(fig, titulo_acao, subtitulo)
        esq = min(0.42, 0.03 + 0.0078 * max(len(r) for r in rotulos))
        ax = fig.add_axes((esq, 0.08, 0.9 - esq, topo - 0.08))
        ax.set_facecolor(FUNDO)
        tem_foco = any(_eh_foco(r) for r in rotulos)
        vals = b.iloc[:, 1].tolist()
        ypos = list(range(len(b)))[::-1]
        cores = [CORES[0] if (_eh_foco(r) or not tem_foco) else CINZA_BARRA for r in rotulos]
        ax.barh(ypos, vals, color=cores, height=0.68, zorder=2)
        ax.set_yticks(ypos, rotulos)
        for t, r in zip(ax.get_yticklabels(), rotulos):
            if tem_foco and _eh_foco(r):
                t.set_color(TINTA)
                t.set_fontweight("semibold")
        amp = max(abs(v) for v in vals) or 1
        for yy, v, r in zip(ypos, vals, rotulos):
            ax.annotate(fv(v), (v, yy), xytext=(4 if v >= 0 else -4, 0), textcoords="offset points",
                        ha="left" if v >= 0 else "right", va="center", fontsize=8.5,
                        color=TINTA if (tem_foco and _eh_foco(r)) else TINTA2,
                        fontweight="semibold" if (tem_foco and _eh_foco(r)) else "normal")
        ax.set_xlim(min(0, min(vals)) - (0.12 * amp if min(vals) < 0 else 0), max(0, max(vals)) + 0.12 * amp)
        if min(vals) < 0:
            ax.axvline(0, color=TINTA2, linewidth=0.8, zorder=3)
        ax.set_xticks([])
        for lado in ("top", "right", "bottom", "left"):
            ax.spines[lado].set_visible(False)
        ax.tick_params(axis="y", length=0, colors=TINTA2, labelsize=9)
    fig.text(0.02, 0.015, RODAPE, fontsize=7, color=TINTA2)
    caminho = _arquivo(pergunta, "png")
    fig.savefig(caminho, facecolor=FUNDO)
    plt.close(fig)
    return caminho


def _texto_projecao(proj, eh_pct):
    f = (lambda v: pct(v)) if eh_pct else (lambda v: n(v))
    anos = sorted({a for p in proj.values() for a in p.index})
    linhas = []
    for col, p in proj.items():
        linhas.append(f"{col}: " + "; ".join(f"{a}: **{f(r['previsto'])}** ({f(r['inferior'])} a {f(r['superior'])})"
                                            for a, r in p.iterrows()) + ".")
    return (f"**Projeção {min(anos)}–{max(anos)}** (tendência linear; entre parênteses, intervalo de 95%)\n"
            + "\n".join("- " + x for x in linhas))


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
    proj = projecoes(res)
    if proj:
        partes.append(_texto_projecao(proj, res.tipo == "participacao"))
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
    if proj:
        lim.append(NOTA_PROJECAO)
    if lim:
        partes.append("**Limitações**\n" + "\n".join("- " + x for x in lim))
    nome_ind = ind["nome"]
    titulo = f"{nome_ind}{descrever_recorte(c, cat)} — " + (", ".join(l.nome for l in c.locais) or "UFs")
    png = grafico(res, titulo, ind["unidade"], pergunta, proj, nome_ind)
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
