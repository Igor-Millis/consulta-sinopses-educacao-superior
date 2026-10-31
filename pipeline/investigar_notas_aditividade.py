"""Procura nas notas de rodapé (2024) indicações de categorias não exclusivas ou totais não aditivos (somente leitura)."""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import DIAG, ler_catalogo

sys.stdout.reconfigure(encoding="utf-8")
n = ler_catalogo(DIAG / "02_catalogo_abas.xlsx", sheet_name="notas_rodape")
n = n[(n.ano == 2024) & (n.conjunto == "Sinopse por município")]
pat = r"mais de um|mais de uma|uma única vez|uma vez|não representa a soma|simultane|pode(m)? (ter|possuir|estar|ser|optar)|acumul"
x = n[n.texto.str.contains(pat, case=False, regex=True)].copy()
x["nota"] = x.texto.str.strip().str.replace(r"^(Notas:)?\s*\d+\s*-\s*", "", regex=True)
for nota, g in x.groupby("nota"):
    tabs = sorted({t.replace("Tab ", "") for t in g.chave_tabela}, key=lambda s: [int(v) for v in s.split(".")])
    print(f"[{', '.join(tabs)}]\n   {nota[:400]}\n")
