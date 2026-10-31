"""P4 — Tabelas de correspondência entre anos (crosswalks). Não alteram nenhum dado: dizem como comparar.

1. config/xw_cine.csv: cada código Cine × anos em que aparece; códigos que mudam com o MESMO nome são ligados
   (co_cine_ref = código mais recente com aquele nome); classificação: estável | código alterado (mesmo nome) |
   nome alterado (mesmo código) | só em parte dos anos.
2. config/xw_deficiencia.csv e config/xw_reserva_vagas.csv: categoria original → classe comparável + equivalência
   (confirmada | provável | parcial | não comparável), com a justificativa. Curadas à mão a partir do diagnóstico.
3. Grava as três no núcleo (xw_*) e cria visões comparáveis.

Uso: python -I p4_crosswalks.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import CONFIG, NUCLEO

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(NUCLEO / "ijsn.duckdb"))
con.execute("SET memory_limit = '3GB'")

# ---------------------------------------------------------------- 1. Cine
c = con.execute("""SELECT ano, co_cine, no_cine FROM dim_curso_cine WHERE co_cine <> '_TOTAL'""").df()
c["no_norm"] = c.no_cine.str.strip().str.casefold()
anos_cod = c.groupby("co_cine").ano.apply(lambda s: sorted(set(s)))
nomes_cod = c.groupby("co_cine").no_norm.apply(lambda s: sorted(set(s)))
ult_por_nome = c.sort_values("ano").groupby("no_norm").co_cine.last()
rows = []
todos = sorted(c.ano.unique())
for cod, anos in anos_cod.items():
    nomes = nomes_cod[cod]
    nome_ult = c[(c.co_cine == cod)].sort_values("ano").no_cine.iloc[-1]
    ref = ult_por_nome[c[(c.co_cine == cod)].sort_values("ano").no_norm.iloc[-1]]
    if anos == todos and len(nomes) == 1:
        tipo, eq = "estável", "confirmada"
    elif ref != cod:
        tipo, eq = "código alterado (mesmo nome)", "provável"
    elif len(nomes) > 1:
        tipo, eq = "nome alterado (mesmo código)", "provável"
    else:
        tipo, eq = "só em parte dos anos", "não identificada"
    rows.append({"co_cine": cod, "no_cine": nome_ult, "anos": ",".join(map(str, anos)), "ano_inicio": anos[0],
                 "ano_fim": anos[-1], "n_anos": len(anos), "nomes_distintos": " | ".join(nomes),
                 "co_cine_ref": ref, "tipo": tipo, "equivalencia": eq})
X = pd.DataFrame(rows).sort_values("co_cine")
X.to_csv(CONFIG / "xw_cine.csv", index=False, encoding="utf-8-sig")
print("Cine:", X.tipo.value_counts().to_dict())
print("   entram/saem em 2024:", (X.ano_inicio == 2024).sum(), "/", ((X.ano_fim == 2023)).sum(),
      "| ligados por nome:", (X.tipo == "código alterado (mesmo nome)").sum())

# ---------------------------------------------------------------- 2. deficiência e reserva de vagas (curadas)
DEF = [
    ("Auditiva", "Auditiva", "confirmada", "Mesma categoria em todos os anos"),
    ("Baixa Visão", "Baixa Visão", "confirmada", ""), ("Cegueira", "Cegueira", "confirmada", ""),
    ("Física", "Física", "confirmada", ""), ("Intelectual", "Intelectual", "confirmada", ""),
    ("Surdez", "Surdez", "confirmada", ""), ("Surdocegueira", "Surdocegueira", "confirmada", ""),
    ("Múltipla", "Múltipla", "não comparável", "Existe só até 2019 (alunos) — descontinuada"),
    ("Autismo Infantil", "TEA/TGD (agregado)", "parcial", "2017–2020; integrado ao TGD (2021–22) e ao TEA (2023–24)"),
    ("Síndrome de Asperger", "TEA/TGD (agregado)", "parcial", "2017–2019; ver Autismo Infantil"),
    ("Síndrome de Rett", "TEA/TGD (agregado)", "parcial", "2017–2019; ver Autismo Infantil"),
    ("Transtorno Desintegrativo da Infância", "TEA/TGD (agregado)", "parcial", "2017–2019; ver Autismo Infantil"),
    ("Transtorno Global do Desenvolvimento (TGD)", "TEA/TGD (agregado)", "provável", "2021–2022 (alunos); 2022 (docentes)"),
    ("Transtorno do Espectro Autista (TEA)", "TEA/TGD (agregado)", "provável", "2023–2024 (alunos)"),
    ("Transtorno do Espectro Autista", "TEA/TGD (agregado)", "provável", "2023–2024 (docentes, tabela 2.9)"),
    ("Superdotação", "Altas habilidades/superdotação", "provável", "Rótulo dos alunos"),
    ("Altas habilidades/superdotação", "Altas habilidades/superdotação", "provável", "Rótulo dos docentes (2.9, a partir de 2022)"),
    ("Visão Monocular", "Visão Monocular", "não comparável", "Nova em 2024: antes os casos estavam em outra categoria ou fora"),
]
RES = [
    ("Pessoas com Deficiência", "Pessoas com Deficiência", "confirmada", ""),
    ("Estudante Procedente de Escola Pública", "Escola Pública", "confirmada", ""),
    ("Social / Renda Familiar", "Social / Renda Familiar", "confirmada", ""),
    ("Outros Programas", "Outros", "provável", "Rótulo das tabelas 4.15/5.14/6.14"),
    ("Outros", "Outros", "provável", "Rótulo das tabelas 4.16–4.17/5.15–5.16/6.15–6.16"),
    ("Étnico", "Étnico-racial (agregado)", "parcial", "2017–2023; em 2024 dividido em categorias novas"),
    ("Estudante Preto, Pardo ou Indígena", "Étnico-racial (agregado)", "parcial", "2024; parte do antigo 'Étnico'"),
    ("Estudante Quilombola", "Étnico-racial (agregado)", "parcial", "2024; provavelmente no antigo 'Étnico' (hipótese)"),
    ("Estudante de Comunidade Tradicional", "Étnico-racial (agregado)", "parcial", "2024; hipótese — confirmar com o INEP"),
    ("Estudante Idoso", "Novas categorias 2024", "não comparável", "Nova em 2024"),
    ("Estudante Internacional", "Novas categorias 2024", "não comparável", "Nova em 2024"),
    ("Estudante Medalhista", "Novas categorias 2024", "não comparável", "Nova em 2024"),
    ("Estudante Refugiado", "Novas categorias 2024", "não comparável", "Nova em 2024"),
    ("Estudante Transgênero", "Novas categorias 2024", "não comparável", "Nova em 2024"),
]
for nome, lista, dim in (("xw_deficiencia", DEF, "deficiencia"), ("xw_reserva_vagas", RES, "reserva_vagas")):
    df = pd.DataFrame(lista, columns=["categoria_original", "classe_comparavel", "equivalencia", "observacao"])
    usados = set(con.execute(f"SELECT DISTINCT {dim} FROM dim_recorte_sinopse WHERE {dim} <> 'Total'").df()[dim])
    falt = usados - set(df.categoria_original)
    assert not falt, f"{nome}: categorias sem correspondência: {falt}"
    df.to_csv(CONFIG / f"{nome}.csv", index=False, encoding="utf-8-sig")
    con.register("v", df)
    con.execute(f"CREATE OR REPLACE TABLE {nome} AS SELECT * FROM v")
    print(f"{nome}: {len(df)} categorias → {df.classe_comparavel.nunique()} classes")
con.register("v", X)
con.execute("CREATE OR REPLACE TABLE xw_cine AS SELECT * FROM v")

# ---------------------------------------------------------------- 3. visões comparáveis
con.execute("""CREATE OR REPLACE VIEW v_sinopse_deficiencia_comparavel AS
  SELECT f.ano, f.tabela, f.id_geo, f.nivel_geo, f.nivel_academico, f.indicador, r.sexo, x.classe_comparavel,
         x.equivalencia, sum(f.valor) AS valor, count(*) AS n_categorias_somadas,
         'ATENÇÃO: um aluno pode ter mais de uma deficiência — somar classes pode contar o mesmo aluno mais de uma vez' AS aviso
  FROM fato_sinopse f JOIN dim_recorte_sinopse r USING (id_recorte)
  JOIN xw_deficiencia x ON x.categoria_original = r.deficiencia
  WHERE r.deficiencia <> 'Total' AND f.valor IS NOT NULL
  GROUP BY ALL""")
con.execute("""CREATE OR REPLACE VIEW v_anexo_curso_cine_ref AS
  SELECT f.*, x.co_cine_ref, x.tipo AS tipo_cine, x.equivalencia AS equivalencia_cine
  FROM fato_anexo_curso f LEFT JOIN xw_cine x ON x.co_cine = f.co_cine""")
con.execute("INSERT INTO carga_log VALUES (current_timestamp, 'p4_crosswalks', 'concluída')")
con.close()
print("P4 concluída")
