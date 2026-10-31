"""Conversor mínimo do markdown das respostas do motor para HTML (negrito, código, listas, tabelas, parágrafos).

Todo texto é escapado ANTES da formatação: nenhum HTML vindo dos dados ou da pergunta é interpretado pelo navegador.
"""
import html
import re


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![\w*])_(\(.+?\))_(?![\w*])", r"<em>\1</em>", s)
    return s


def para_html(md: str) -> str:
    saida, lista, tabela = [], [], []

    def fecha_lista():
        if lista:
            saida.append("<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in lista) + "</ul>")
            lista.clear()

    def fecha_tabela():
        if tabela:
            linhas = [l for l in tabela if not re.fullmatch(r"\|(\s*-+\s*\|)+", l.replace(":", ""))]
            cel = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas]
            cab, corpo = cel[0], cel[1:]
            num = re.compile(r"^[−+\-]?[\d.]+(,\d+)?%?$|^—$")
            th = "".join(f"<th scope='col'>{_inline(c)}</th>" for c in cab)
            tr = "".join("<tr>" + "".join(f"<td{' class=num' if num.match(c) else ''}>{_inline(c)}</td>" for c in r) + "</tr>"
                         for r in corpo)
            saida.append(f"<div class='tabela'><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>")
            tabela.clear()

    for linha in md.splitlines():
        if linha.startswith("|"):
            fecha_lista()
            tabela.append(linha)
            continue
        fecha_tabela()
        if linha.startswith("- "):
            lista.append(linha[2:])
            continue
        fecha_lista()
        if linha.strip():
            saida.append(f"<p>{_inline(linha)}</p>")
    fecha_lista()
    fecha_tabela()
    return "\n".join(saida)
