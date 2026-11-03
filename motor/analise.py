"""Cálculos estatísticos em código (determinísticos, testáveis). Nada aqui é estimado pelo modelo de linguagem.

Regras:
  - variação absoluta = último − primeiro; variação % = (último − primeiro) / primeiro (indefinida se primeiro = 0);
  - taxa média anual (CAGR) = (último / primeiro) ^ (1 / (anos decorridos)) − 1, só com primeiro > 0 e último > 0;
  - participação = parte / todo do MESMO ano, local e fonte;
  - ausência de valor (sem linha) ≠ zero: anos sem dado são listados como ausentes e não entram nos cálculos;
  - ranking de crescimento por variação absoluta (padrão) ou percentual com base mínima (evita % de bases pequenas).
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

BASE_MINIMA_PERCENTUAL = 100   # ranking por % só entre itens com pelo menos isto no ano inicial


@dataclass
class Resultado:
    tipo: str
    tabela: pd.DataFrame                      # tabela principal (já calculada)
    fatos: dict = field(default_factory=dict) # números-chave para o texto
    serie: pd.DataFrame | None = None         # para gráfico de linhas (ano × série)
    barras: pd.DataFrame | None = None        # para gráfico de barras (rótulo, valor)
    avisos: list = field(default_factory=list)


def variacao(v0, v1):
    abs_ = v1 - v0
    pct = (v1 - v0) / v0 if v0 not in (0, None) and not pd.isna(v0) else np.nan
    return abs_, pct


def cagr(v0, v1, anos):
    if anos <= 0 or v0 is None or v1 is None or pd.isna(v0) or pd.isna(v1) or v0 <= 0 or v1 <= 0:
        return np.nan
    return (v1 / v0) ** (1 / anos) - 1


HORIZONTE_PROJECAO = 3     # anos projetados além do último ano observado
MIN_PONTOS_PROJECAO = 5    # menos que isto: sem projeção (tendência pouco informativa)
# t de Student bicaudal 95% (0,975) por graus de liberdade; acima de 30 usa 1,96
_T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
         11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042}


def _t975(gl):
    return next((_T975[k] for k in sorted(_T975) if k >= gl), 1.96)


def projetar(y: pd.Series, horizonte=HORIZONTE_PROJECAO, minimo=0.0, maximo=None):
    """Tendência linear (MQO sobre o ano) com intervalo de PREVISÃO de 95%.

    ŷ(t) = a + b·t;  IC = ŷ ± t(n−2) · s · √(1 + 1/n + (t − t̄)² / Σ(tᵢ − t̄)²), s = √(SQR / (n − 2)).
    Anos ausentes ficam fora do ajuste (ausência ≠ zero). Valores e limites são cortados em [minimo, maximo]
    (contagens não ficam negativas; participações ficam entre 0 e 1). Retorna DataFrame (ano, previsto,
    inferior, superior) ou None se houver menos de MIN_PONTOS_PROJECAO anos com dado.
    """
    y = y.dropna()
    if len(y) < MIN_PONTOS_PROJECAO:
        return None
    t = y.index.to_numpy(dtype=float)
    v = y.to_numpy(dtype=float)
    nobs = len(t)
    b, a = np.polyfit(t, v, 1)
    s = np.sqrt(((v - (a + b * t)) ** 2).sum() / (nobs - 2))
    sxx = ((t - t.mean()) ** 2).sum()
    anos = np.arange(int(t.max()) + 1, int(t.max()) + 1 + horizonte)
    prev = a + b * anos
    meia = _t975(nobs - 2) * s * np.sqrt(1 + 1 / nobs + (anos - t.mean()) ** 2 / sxx)
    out = pd.DataFrame({"ano": anos, "previsto": prev, "inferior": prev - meia, "superior": prev + meia})
    out[["previsto", "inferior", "superior"]] = out[["previsto", "inferior", "superior"]].clip(lower=minimo, upper=maximo)
    return out.set_index("ano")


def ano_ultrapassagem(serie_a: pd.Series, serie_b: pd.Series):
    """Primeiro ano em que a ordem entre A e B se inverte em relação ao primeiro ano comum. None se nunca."""
    comum = serie_a.dropna().index.intersection(serie_b.dropna().index).sort_values()
    if len(comum) < 2:
        return None
    sinal0 = np.sign(serie_a[comum[0]] - serie_b[comum[0]])
    for ano in comum[1:]:
        s = np.sign(serie_a[ano] - serie_b[ano])
        if s != 0 and sinal0 != 0 and s != sinal0:
            return int(ano)
    return None


def _txt(s: pd.Series) -> pd.Series:
    """Texto sem NaN (no pandas 3, astype(str) preserva valores ausentes)."""
    return s.map(lambda v: "—" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v))


def _juntar(df: pd.DataFrame) -> pd.Series:
    return df.apply(_txt).agg(" — ".join, axis=1) if len(df.columns) else pd.Series("", index=df.index)


def _rotulo(df, dims):
    if not dims:
        return df["local"]
    partes = [df["local"]] if df["local"].nunique() > 1 else []
    partes += [_txt(df[d]) for d in dims]
    r = partes[0]
    for p in partes[1:]:
        r = r + " — " + p
    return r


def _anos_ausentes(df, anos, chave):
    aus = {}
    for k, g in df.groupby(chave):
        faltam = sorted(set(anos) - set(g["ano"]))
        if faltam:
            aus[k] = faltam
    return aus


def analisar(df: pd.DataFrame, c, dims: list) -> Resultado:
    df = df.copy()
    df["serie"] = _rotulo(df, [d for d in dims if d != "curso"] + (["no_curso"] if "curso" in dims else []))
    if c.tipo in ("ranking", "crescimento"):
        return _ranking(df, c, dims)
    if c.tipo == "participacao":
        return _participacao(df, c, dims)
    if c.tipo in ("serie", "comparacao") or len(c.anos) > 1:
        return _serie(df, c, dims)
    return _valor(df, c, dims)


def _valor(df, c, dims):
    ano = max(c.anos)
    d = df[df["ano"] == ano]
    tab = d[["serie", "valor"]].sort_values("valor", ascending=False).reset_index(drop=True)
    tab.columns = ["recorte", "valor"]
    fatos = {"ano": ano, "n": len(tab)}
    if len(tab) == 1:
        fatos["valor"] = tab["valor"].iloc[0]
        fatos["recorte"] = tab["recorte"].iloc[0]
    else:
        fatos["total"] = tab["valor"].sum() if dims else None
    return Resultado("valor", tab, fatos, barras=tab if len(tab) > 1 else None)


def _serie(df, c, dims):
    piv = df.pivot_table(index="ano", columns="serie", values="valor", aggfunc="sum").sort_index()
    piv = piv[piv.ffill().iloc[-1].sort_values(ascending=False).index]   # maior no último ano primeiro
    linhas = []
    for s in piv.columns:
        col = piv[s].dropna()
        if col.empty:
            continue
        a0, a1 = int(col.index[0]), int(col.index[-1])
        v0, v1 = col.iloc[0], col.iloc[-1]
        va, vp = variacao(v0, v1)
        linhas.append({"série": s, "ano_inicial": a0, "valor_inicial": v0, "ano_final": a1, "valor_final": v1,
                       "variação_absoluta": va, "variação_%": vp, "taxa_média_anual": cagr(v0, v1, a1 - a0),
                       "máximo": col.max(), "ano_do_máximo": int(col.idxmax()),
                       "mínimo": col.min(), "ano_do_mínimo": int(col.idxmin())})
    resumo = pd.DataFrame(linhas)
    fatos = {"anos": [int(a) for a in piv.index], "ausentes": _anos_ausentes(df, c.anos, "serie")}
    if len(piv.columns) == 2 and c.tipo == "comparacao":
        a, b = piv.columns
        fatos["ultrapassagem"] = ano_ultrapassagem(piv[a], piv[b])
        ult = piv.index.max()
        if not pd.isna(piv.loc[ult, a]) and not pd.isna(piv.loc[ult, b]) and piv.loc[ult, b]:
            fatos["razao_final"] = piv.loc[ult, a] / piv.loc[ult, b]
            fatos["diferenca_final"] = piv.loc[ult, a] - piv.loc[ult, b]
        fatos["series"] = (a, b)
    tab = piv.copy()
    tab.index.name = "ano"
    return Resultado(c.tipo if c.tipo in ("serie", "comparacao") else "serie", tab, fatos, serie=piv,
                     avisos=[])


def _participacao(df, c, dims):
    filtros_como_quebra = {d: v for d, v in c.parte.items() if d in dims}
    if filtros_como_quebra:          # participação de um recorte (ex.: EaD) no total do mesmo local/ano
        sel = pd.Series(True, index=df.index)
        for d, v in filtros_como_quebra.items():
            sel &= df[d] == v
        outras = [d for d in dims if d not in filtros_como_quebra]
        chave = ["ano", "local", *outras]
        num = df[sel].groupby(chave, as_index=False)["valor"].sum().rename(columns={"valor": "parte"})
        den = df.groupby(chave, as_index=False)["valor"].sum().rename(columns={"valor": "todo"})
        tab = den.merge(num, on=chave, how="left")[[*chave, "parte", "todo"]]
        # parte sem linha fica ausente (participação indefinida), nunca zero por suposição
        rotulo_parte = " e ".join(str(v) for v in filtros_como_quebra.values())
    elif dims:                       # participação de cada categoria no total
        chave = ["ano", "local"]
        tab = df.copy()
        tab["todo"] = tab.groupby(chave)["valor"].transform("sum")
        tab = tab.rename(columns={"valor": "parte"})[["ano", "local", *dims, "parte", "todo"]]
        rotulo_parte = None
    else:                            # participação do local no local "pai" (município → UF; UF → Brasil)
        pais = {"Município": "UF", "Grupo": "UF", "UF": "Brasil", "Região": "Brasil"}
        e_pai = lambda l: any(((("UF-" + x.co_uf) if pais.get(x.nivel) == "UF" else "BR") == l.id_geo)
                              for x in c.locais if x is not l and x.nivel in pais)
        filhos = [l for l in c.locais if l.nivel in pais and not e_pai(l)] or [l for l in c.locais if l.nivel in pais]
        linhas = []
        for l in filhos:
            id_pai = ("UF-" + l.co_uf) if pais[l.nivel] == "UF" else "BR"
            for ano in sorted(df["ano"].unique()):
                p = df[(df["ano"] == ano) & (df["id_geo"] == l.id_geo)]["valor"].sum(min_count=1)
                t = df[(df["ano"] == ano) & (df["id_geo"] == id_pai)]["valor"].sum(min_count=1)
                nome_pai = df.loc[df["id_geo"] == id_pai, "local"].iloc[0] if (df["id_geo"] == id_pai).any() else id_pai
                linhas.append({"ano": ano, "local": l.nome, "em relação a": nome_pai, "parte": p, "todo": t})
        tab = pd.DataFrame(linhas)
        rotulo_parte = None
    if tab.empty:
        return Resultado("participacao", tab, {})
    tab["participação"] = tab["parte"] / tab["todo"]
    tab.loc[tab["todo"].isna() | (tab["todo"] == 0), "participação"] = np.nan
    fatos = {"rotulo_parte": rotulo_parte, "anos": sorted(int(a) for a in tab["ano"].unique())}
    ult = tab[tab["ano"] == tab["ano"].max()]
    fatos["ultimo"] = ult
    serie = None
    if tab["ano"].nunique() > 1:
        cols = [x for x in tab.columns if x not in ("ano", "parte", "todo", "participação", "em relação a")]
        tab["_s"] = _juntar(tab[cols]) if cols else "participação"
        serie = tab.pivot_table(index="ano", columns="_s", values="participação", aggfunc="first")
        tab = tab.drop(columns="_s")
        p0 = tab[tab["ano"] == tab["ano"].min()]
        fatos["primeiro"] = p0
    barras = None
    if serie is None and len(ult) > 1:
        barras = ult.assign(recorte=_juntar(ult.drop(columns=["ano", "parte", "todo", "participação"], errors="ignore")))[
            ["recorte", "participação"]]
    return Resultado("participacao", tab.reset_index(drop=True), fatos, serie=serie, barras=barras)


def _ranking(df, c, dims):
    # entidade = local (listar municípios/UFs) ou curso
    if "curso" in dims:
        ent = "co_curso"
        nomes = df.sort_values("ano").groupby("co_curso")["no_curso"].last()
        alvo = df[df["nivel_geo"] != "Grupo"] if len(c.locais) <= 1 else df
    else:
        ent = "id_geo"
        nivel = "Município" if c.listar_municipios_uf else "UF"
        alvo = df[df["nivel_geo"] == nivel]
        nomes = df.groupby("id_geo")["local"].first()
    asc = c.ordem == "asc"
    ano1 = max(c.anos)
    if c.tipo == "crescimento":
        ano0 = min(c.anos)
        v0 = alvo[alvo["ano"] == ano0].groupby(ent)["valor"].sum()
        v1 = alvo[alvo["ano"] == ano1].groupby(ent)["valor"].sum()
        tab = pd.DataFrame({f"valor_{ano0}": v0, f"valor_{ano1}": v1})
        tab["variação_absoluta"] = tab[f"valor_{ano1}"] - tab[f"valor_{ano0}"]
        tab["variação_%"] = tab["variação_absoluta"] / tab[f"valor_{ano0}"]
        tab.loc[~(tab[f"valor_{ano0}"] > 0), "variação_%"] = np.nan
        criterio = getattr(c, "criterio", "absoluto")
        if criterio == "percentual":
            base = tab[tab[f"valor_{ano0}"] >= BASE_MINIMA_PERCENTUAL]
            tab = base.sort_values("variação_%", ascending=asc)
        else:
            tab = tab.sort_values("variação_absoluta", ascending=asc)
        tab = tab.dropna(subset=["variação_absoluta"]) if criterio != "percentual" else tab
        if getattr(c, "so_reducao", False):
            tab = tab[tab["variação_absoluta"] < 0]
        fatos = {"ano0": ano0, "ano1": ano1, "criterio": criterio, "n_total": len(tab),
                 "sem_base": int((v0.reindex(v1.index).isna()).sum()), "so_reducao": getattr(c, "so_reducao", False)}
        col_barra = "variação_absoluta" if criterio != "percentual" else "variação_%"
    else:
        v1 = alvo[alvo["ano"] == ano1].groupby(ent)["valor"].sum()
        tab = pd.DataFrame({"valor": v1}).sort_values("valor", ascending=asc)
        total = v1.sum()
        tab["participação_no_conjunto"] = tab["valor"] / total if total else np.nan
        fatos = {"ano1": ano1, "n_total": len(tab), "total_conjunto": total}
        col_barra = "valor"
    tab.insert(0, "nome", tab.index.map(nomes))
    tab = tab.reset_index(drop=True)
    tab.index = tab.index + 1
    tab.index.name = "posição"
    top = tab.head(c.top_n)
    fatos["top"] = top
    return Resultado(c.tipo, top, fatos, barras=top[["nome", col_barra]].rename(
        columns={"nome": "recorte", col_barra: "valor"}))
