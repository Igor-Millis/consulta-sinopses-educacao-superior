"""Q10 — identifica, célula a célula, as inconsistências das tabelas 6.3 e 6.6 (concluintes). Somente leitura.

Regra objetiva (mesma regra T2 da validação, pipeline/regras_t2.py; só categorias EXCLUSIVAS e conjuntos completos):
  cada "comparação" é um total publicado (célula-pai) e as categorias que o compõem (células-filhas) na MESMA linha
  da planilha. Uma comparação falha quando Σ filhas ≠ pai.
  Cada célula participa de várias comparações (ex.: "Masculino × Preta" é filha em sexo e em cor/raça). Então:
    suspeita    — célula com ≥ 1 comparação falha e NENHUMA comparação que fecha (não há evidência a favor dela);
    relacionada — célula em comparação falha, mas que fecha em outra comparação (provavelmente correta);
  Se alguma comparação falha não tiver nenhuma célula "suspeita", todas as células dela viram suspeitas (cobertura
  total: nenhuma inconsistência fica sem marca). Valores NUNCA são alterados.
Todas as tabelas 6.3/6.6 de 2017–2024 são varridas (os anos sem falha confirmam o escopo da Q10).
Saída: config/q10_celulas_suspeitas.csv (lido por carregar_sinopse.py e aplicar_q10_q13.py) e resumo na tela.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import CONFIG, NUCLEO
from regras_t2 import pares_totais

sys.stdout.reconfigure(encoding="utf-8")
ADIT = "indicador IN (SELECT indicador FROM dim_indicador WHERE aditivo)"


def detectar(con, tabelas=("6.3", "6.6"), anos=range(2017, 2025)):
    P, nao_excl = pares_totais(con)
    con.register("pares", P)
    con.register("v_ne", pd.DataFrame(sorted(nao_excl), columns=["dim", "tabela"]))
    comps = []
    for ano in anos:
        for tab in tabelas:
            df = con.execute(f"""
              WITH f AS (SELECT tabela, id_geo, nivel_academico, indicador, id_recorte, valor, aba, linha, coluna
                         FROM fato_sinopse WHERE ano = {ano} AND tabela = '{tab}' AND {ADIT} AND valor IS NOT NULL),
              s0 AS (SELECT pr.dim, pr.pai_val, f.tabela, f.id_geo, f.nivel_academico, f.indicador, pr.pai, pr.filho_val,
                            max(f.valor) v, string_agg(DISTINCT f.coluna, '|') cols
                     FROM f JOIN pares pr ON pr.filho = f.id_recorte GROUP BY ALL),
              s1 AS (SELECT dim, pai_val, tabela, id_geo, nivel_academico, indicador, pai, sum(v) soma, count(*) nfilhos,
                            string_agg(cols, '|') cols_filhas FROM s0 GROUP BY ALL),
              s AS (SELECT * FROM (SELECT *, max(nfilhos) OVER (PARTITION BY dim, pai_val, tabela) nesperado FROM s1)
                    WHERE nfilhos = nesperado)
              SELECT {ano} ano, s.dim, s.pai_val, s.tabela, s.id_geo, s.nivel_academico, s.indicador, s.soma,
                     pa.valor valor_pai, pa.aba, pa.linha, pa.coluna col_pai, s.cols_filhas, s.soma <> pa.valor falha
              FROM s JOIN f pa ON pa.tabela = s.tabela AND pa.id_geo = s.id_geo AND pa.nivel_academico = s.nivel_academico
                   AND pa.indicador = s.indicador AND pa.id_recorte = s.pai
              WHERE NOT EXISTS (SELECT 1 FROM v_ne ne WHERE ne.dim = s.dim AND ne.tabela = s.tabela)""").df()
            comps.append(df)
    C = pd.concat(comps, ignore_index=True)
    C["id_comp"] = range(len(C))
    # explode: uma linha por célula × comparação
    cel = pd.concat([
        C.assign(coluna=C.col_pai, papel_na_comp="pai")[["id_comp", "ano", "tabela", "aba", "linha", "coluna", "falha", "papel_na_comp"]],
        C.assign(coluna=C.cols_filhas.str.split("|")).explode("coluna").assign(papel_na_comp="filha")[
            ["id_comp", "ano", "tabela", "aba", "linha", "coluna", "falha", "papel_na_comp"]],
    ], ignore_index=True)
    chave = ["ano", "tabela", "aba", "linha", "coluna"]
    resumo = cel.groupby(chave).agg(n_falhas=("falha", "sum"), n_comparacoes=("falha", "size")).reset_index()
    resumo["n_ok"] = resumo.n_comparacoes - resumo.n_falhas
    envolvidas = resumo[resumo.n_falhas > 0].copy()
    envolvidas["papel"] = (envolvidas.n_ok == 0).map({True: "suspeita", False: "relacionada"})
    # cobertura: toda comparação falha precisa de ≥ 1 célula suspeita
    susp = set(map(tuple, envolvidas[envolvidas.papel == "suspeita"][chave].values))
    falhas = cel[cel.falha]
    cobertas = falhas.assign(s=[tuple(x) in susp for x in falhas[chave].values]).groupby("id_comp").s.any()
    sem = cobertas[~cobertas].index
    if len(sem):
        extra = set(map(tuple, falhas[falhas.id_comp.isin(sem)][chave].values))
        envolvidas.loc[[tuple(x) in extra for x in envolvidas[chave].values], "papel"] = "suspeita"
    # valor original e identificação de cada célula
    con.register("v_cel", envolvidas[chave])
    det = con.execute("""SELECT f.ano, f.tabela, f.aba, f.linha, f.coluna, f.id_geo, f.nivel_geo, f.indicador, f.id_recorte,
                                f.valor, f.status_valor
                         FROM fato_sinopse f JOIN v_cel c USING (ano, tabela, aba, linha, coluna)""").df()
    out = envolvidas.merge(det, on=chave, how="left")
    out["regra"] = "T2: Σ categorias ≠ total publicado (regras_t2.py)"
    stats = {"comparacoes": len(C), "falhas": int(C.falha.sum()), "sem_cobertura_inicial": len(sem),
             "por_ano_tabela": C[C.falha].groupby(["ano", "tabela"]).size().to_dict()}
    return out.sort_values(chave).reset_index(drop=True), stats


if __name__ == "__main__":
    con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"), read_only=True)
    con.execute("SET memory_limit = '3GB'")
    con.execute("SET threads = 4")
    out, st = detectar(con)
    print(f"comparações: {st['comparacoes']:,} | falhas: {st['falhas']:,} | comparações falhas sem célula suspeita "
          f"pela regra principal (resolvidas marcando todas as células delas): {st['sem_cobertura_inicial']}")
    print("falhas por ano × tabela:", st["por_ano_tabela"])
    print(out.groupby(["ano", "tabela", "papel"]).size().unstack(fill_value=0).to_string())
    print("status atual das suspeitas:", out[out.papel == "suspeita"].status_valor.value_counts().to_dict())
    print(out[out.papel == "suspeita"].sort_values("valor", ascending=False).head(8)[
        ["ano", "tabela", "aba", "linha", "coluna", "id_geo", "valor", "n_falhas", "n_comparacoes"]].to_string(index=False))
    destino = CONFIG / "q10_celulas_suspeitas.csv"
    out.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"{len(out):,} células gravadas em {destino} ({(out.papel == 'suspeita').sum():,} suspeitas)")
