"""Validação da P0: o staging reproduz o que o diagnóstico mediu?

1. Mesmas 662 abas do inventário (01).
2. Para cada aba de dados: células presentes por coluna, da linha de início dos dados em diante,
   iguais a 04_perfil_dados.xlsx › perfil_colunas.celulas_presentes.
3. Número de linhas do staging = linhas_xml do catálogo (02), descontadas linhas totalmente vazias.

Grava dados/qualidade/p0_validacao.csv. Uso: python -I p0_validar.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq
from comum import ler_catalogo, DIAG, PROJETO, QUALIDADE, STAGING

sys.stdout.reconfigure(encoding="utf-8")
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
inv = ler_catalogo(DIAG / "01_inventario_workbooks.xlsx", sheet_name="abas")
c02 = ler_catalogo(DIAG / "02_catalogo_abas.xlsx", sheet_name="abas")
p04 = ler_catalogo(DIAG / "04_perfil_dados.xlsx", sheet_name="perfil_colunas",
                   usecols=["ano", "arquivo", "aba", "coluna", "celulas_presentes"])

k = ["ano", "arquivo", "aba"]
s_cat, s_inv = set(map(tuple, cat[k].values)), set(map(tuple, inv[k].values))
print(f"1. abas no staging: {len(s_cat)} | no inventário: {len(s_inv)} | faltando: {len(s_inv - s_cat)} | sobrando: {len(s_cat - s_inv)}")

res = []
dados = c02[c02.tipo_aba == "tabela_dados"].merge(cat[k + ["parquet", "n_linhas"]], on=k)
esperado = p04.groupby(k)
for _, r in dados.iterrows():
    tb = pq.read_table(PROJETO / r.parquet)
    tb = tb.filter(pc.greater_equal(tb["linha"], int(r.linha_inicio_dados)))
    exp = esperado.get_group((r.ano, r.arquivo, r.aba)).set_index("coluna").celulas_presentes
    div = []
    for col, n_exp in exp.items():
        n_obs = tb.num_rows - tb[col].null_count if col in tb.column_names else 0
        if n_obs != n_exp:
            div.append(f"{col}:{n_obs}≠{n_exp}")
    res.append({"ano": r.ano, "arquivo": r.arquivo, "aba": r.aba, "colunas_conferidas": len(exp),
                "divergencias": len(div), "detalhe": "; ".join(div[:10])})
R = pd.DataFrame(res)
QUALIDADE.mkdir(parents=True, exist_ok=True)
R.to_csv(QUALIDADE / "p0_validacao.csv", index=False, encoding="utf-8-sig")
print(f"2. abas de dados conferidas: {len(R)} | colunas conferidas: {R.colunas_conferidas.sum():,} | "
      f"abas com divergência: {(R.divergencias > 0).sum()} | colunas divergentes: {R.divergencias.sum()}")
if (R.divergencias > 0).any():
    print(R[R.divergencias > 0].head(20).to_string())
print(f"3. linhas no staging: {cat.n_linhas.sum():,} | células: {cat.n_celulas.sum():,} | "
      f"números gravados como texto: {cat.n_num_como_texto.sum():,} | tamanho em disco: "
      f"{sum(f.stat().st_size for f in STAGING.rglob('*.parquet')) / 2**30:.2f} GB")
