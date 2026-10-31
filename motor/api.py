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
