"""Imprime as celulas nao vazias das primeiras N linhas de uma aba (streaming, somente leitura).

Uso: python -I peek.py <xlsx> <aba> <n_linhas> [max_col]
"""
import sys
from openpyxl import load_workbook

path, sheet, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
maxc = int(sys.argv[4]) if len(sys.argv) > 4 else None
wb = load_workbook(path, read_only=True, data_only=True)
ws = wb[sheet]
for row in ws.iter_rows(min_row=1, max_row=n, max_col=maxc):
    cells = [(c.coordinate, c.value) for c in row if c.value is not None and hasattr(c, "coordinate")]
    if cells:
        print(" | ".join(f"{k}={str(v)[:60]!r}" for k, v in cells))
wb.close()
