"""Ponto de entrada do motor: perguntar("pergunta em português") → Resposta.

Fluxo: interpretar → (esclarecer?) → planejar SQL → executar (somente leitura, validado) → rotular → analisar
(código) → montar resposta (texto, tabela, gráfico, fontes, limitações). Nenhum número é produzido fora do
banco e de `analise`.
"""
from .analise import analisar
from .consultas import buscar, ocorrencias, para_participacao, planejar, rotular
from .interpretador import interpretar
from .resposta import Resposta, esclarecimento, montar, sem_dados
from .seguranca import conexao
from .semantica import carregar


def catalogo():
    return carregar(conexao)


def perguntar(texto: str) -> Resposta:
    cat = catalogo()
    c = interpretar(texto, cat)
    if c.tipo == "compatibilidade":
        return compatibilidade(texto, cat)
    if c.esclarecer:
        return esclarecimento(texto, c, c.esclarecer)
    if c.indicador in cat.derivados:
        return _derivado(texto, c, cat)
    c_exec = para_participacao(c) if c.tipo == "participacao" else c
    plano = planejar(c_exec, cat)
    if plano.esclarecer:
        return esclarecimento(texto, c, plano.esclarecer)
    df = buscar(plano, texto)
    if df.empty:
        return sem_dados(texto, c, plano)
    df, notas = rotular(df, c_exec, cat, plano.aditivo)
    anos_falt = sorted(set(c.anos) - set(df["ano"].unique()))
    if anos_falt:
        notas.append(f"Sem valores publicados para {', '.join(map(str, anos_falt))} neste recorte (ausência, não zero).")
    res = analisar(df, c_exec, plano.dims)
    ids = sorted({x for v in df.get("ocorrencias", []).dropna() for x in str(v).split(";") if x}) \
        if "ocorrencias" in df.columns else []
    tab_anos = []
    if "tabelas" in df.columns:
        tab_anos = {(t, int(a)) for a, ts in zip(df["ano"], df["tabelas"]) if ts for t in str(ts).split(",")}
    ocorr = ocorrencias(ids, tab_anos)
    return montar(texto, c_exec, cat, res, df, plano, notas, ocorr, [(plano.sql, plano.params)])


CHAVES = ["ano", "id_geo", "nivel_geo", "local", "modalidade", "rede", "dependencia", "categoria_privada",
          "org_academica", "grau", "co_curso", "no_curso"]


def _derivado(texto, c, cat) -> Resposta:
    """Razão entre dois indicadores aditivos: numerador e denominador são somados separadamente (por local, grupo e
    recorte) e só então divididos. Nunca média de razões."""
    from copy import deepcopy
    import numpy as np
    d = cat.derivados[c.indicador]
    if c.tipo == "participacao":
        return esclarecimento(texto, c, [f"'{d['nome']}' é uma razão; participação não se aplica. "
                                         "Pergunte o valor, a evolução ou um ranking."])
    partes, planos, notas = {}, [], []
    for papel in ("numerador", "denominador"):
        ck = deepcopy(c)
        ck.indicador = d[papel]
        pl = planejar(ck, cat)
        if pl.esclarecer:
            return esclarecimento(texto, c, pl.esclarecer)
        df = buscar(pl, texto)
        df, nt = rotular(df, ck, cat, True)
        partes[papel], notas = df, notas + nt + pl.notas
        planos.append(pl)
    num, den = partes["numerador"], partes["denominador"]
    if num.empty or den.empty:
        return sem_dados(texto, c, planos[0])
    chaves = [k for k in CHAVES if k in num.columns and k in den.columns]
    m = num.merge(den, on=chaves, suffixes=("_num", "_den"))
    m["valor"] = np.where(m["valor_den"] > 0, m["valor_num"] / m["valor_den"].where(m["valor_den"] > 0), np.nan)
    m["tem_suspeito"] = m["tem_suspeito_num"].fillna(False) | m["tem_suspeito_den"].fillna(False)
    m["origem"] = m["origem_num"]
    if "ocorrencias_num" in m.columns:
        m["ocorrencias"] = m[["ocorrencias_num", "ocorrencias_den"]].apply(
            lambda r: ";".join(sorted({x for v in r.dropna() for x in str(v).split(";") if x})) or None, axis=1)
    res = analisar(m, c, planos[0].dims)
    res.fatos.pop("total", None)
    if "participação_no_conjunto" in res.tabela.columns:
        res.tabela = res.tabela.drop(columns="participação_no_conjunto")
        res.fatos["top"] = res.tabela
    notas.append(f"{d['nome']} = {cat.indicadores[d['numerador']]['nome'].lower()} ÷ "
                 f"{cat.indicadores[d['denominador']]['nome'].lower()}, somados separadamente antes da divisão.")
    ids = sorted({x for v in m.get("ocorrencias", pd_vazio()).dropna() for x in str(v).split(";") if x})
    return montar(texto, c, cat, res, m, planos[0], list(dict.fromkeys(notas)), ocorrencias(ids, []),
                  [(p.sql, p.params) for p in planos])


def pd_vazio():
    import pandas as pd
    return pd.Series(dtype=object)


def compatibilidade(texto, cat) -> Resposta:
    regras = cat.bruto.get("compatibilidade_temporal", {}).get("regras", [])
    linhas = ["**Comparabilidade entre anos (2017–2024)**", "",
              "Por padrão os indicadores são diretamente comparáveis entre anos. Exceções conhecidas:"]
    for r in regras:
        alvo = r.get("dimensao") or ", ".join(r["indicador"] if isinstance(r["indicador"], list) else [r["indicador"]])
        anos = f" (quebra em {', '.join(map(str, r['anos_quebra']))})" if r.get("anos_quebra") else ""
        linhas.append(f"- **{alvo}**{anos} — {r['classificacao'].replace('_', ' ')}: {r['descricao']}")
    linhas += ["", "**Problemas de qualidade documentados na fonte**"]
    from .seguranca import executar
    q = executar("SELECT id, anos, tabela, descricao, situacao FROM qualidade_ocorrencias ORDER BY id", pergunta=texto)
    for _, o in q.iterrows():
        linhas.append(f"- {o['id']} ({o['anos']}; tabela {o['tabela']}): {o['descricao'][:220]}"
                      + ("…" if len(o["descricao"]) > 220 else "") + f" — _{o['situacao']}_")
    return Resposta(texto, "\n".join(linhas), q)


def main(argv=None):
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    args = argv if argv is not None else sys.argv[1:]
    if args:
        print(perguntar(" ".join(args)).texto)
        return
    print("Motor IJSN — pergunte em português (linha vazia para sair).")
    while True:
        try:
            p = input("\n> ").strip()
        except EOFError:
            break
        if not p:
            break
        try:
            print(perguntar(p).texto)
        except Exception as e:   # mostra o erro sem derrubar a sessão; a consulta já foi registrada
            print(f"Erro ao processar a pergunta: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
