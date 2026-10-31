"""Confirma na FONTE ORIGINAL (XML bruto das planilhas, sem passar pelo pipeline) os valores das ocorrências
Q02, Q03 e Q10, e compara com o núcleo. Somente leitura. Se a cópia do XLSX não existir em TEMP, extrai do ZIP.

Conclusão por caso: 'fonte' (o XML original traz o mesmo valor do núcleo → problema na publicação do INEP) ou
'processamento' (o núcleo difere do XML → erro nosso).

Uso: python -I qualidade_confirmar_fonte.py   → grava dados/qualidade/confirmacao_fonte_Q02_Q03_Q10.csv
"""
import re, shutil, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
import pandas as pd
from comum import PROJETO, QUALIDADE, STAGING, XLSX_TMP, abas, nome_no_zip, strings_compartilhadas

sys.stdout.reconfigure(encoding="utf-8")
con = duckdb.connect(str(PROJETO / "dados" / "nucleo" / "ijsn.duckdb"), read_only=True)
cat = pd.read_csv(STAGING / "_catalogo_staging.csv", encoding="utf-8-sig")
CEL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', re.S)


def xlsx(ano, arquivo):
    dest = XLSX_TMP / str(ano) / arquivo
    if not dest.exists():
        with zipfile.ZipFile(PROJETO / f"sinopse_educacao_superior_{ano}.zip") as z:
            for info in z.infolist():
                if nome_no_zip(info).endswith("/" + arquivo):
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(info) as fi, open(dest, "wb") as fo:
                        shutil.copyfileobj(fi, fo, 16 * 1024 * 1024)
    return dest


def ler_xml(ano, conjunto, aba, linha, colunas):
    arq = cat[(cat.ano == ano) & (cat.conjunto == conjunto) & (cat.aba == aba)].iloc[0].arquivo
    with zipfile.ZipFile(xlsx(ano, arq)) as z:
        ss = strings_compartilhadas(z)
        parte = next(pt for nm, pt, _ in abas(z) if nm == aba)
        resto, achado = "", None
        with z.open(parte) as f:
            while achado is None:
                b = f.read(32 * 1024 * 1024).decode("utf8", "ignore")
                if not b:
                    break
                txt = resto + b
                i = txt.find(f'<row r="{linha}"')
                j = txt.find("</row>", i) if i >= 0 else -1
                if j >= 0:
                    achado = txt[i:j]
                resto = txt[-300000:]
    out = {}
    for m in CEL.finditer(achado or ""):
        if m.group(1) in colunas:
            vm = re.search(r"<v>(.*?)</v>", m.group(4) or "")
            v = vm.group(1) if vm else None
            out[m.group(1)] = ss[int(v)] if (v is not None and 't="s"' in m.group(3)) else v
    return arq, out


casos = []
# ---- Q10: 6.6 (2023 com falha; 2022 sem falha), Brasil, Graduação, Faculdade privada c/ fins, cor Branca e Preta
for ano in (2023, 2022):
    q = con.execute(f"""SELECT f.aba, f.linha, f.coluna, f.valor, r.cor_raca, r.sexo FROM fato_sinopse f
        JOIN dim_recorte_sinopse r USING (id_recorte)
        WHERE f.ano={ano} AND f.tabela='6.6' AND f.id_geo='BR' AND f.nivel_academico='Graduação'
          AND r.org_academica='Faculdade' AND r.dependencia='Privada' AND r.categoria_privada='Com Fins Lucrativos'
          AND r.cor_raca IN ('Branca','Preta') ORDER BY r.cor_raca, r.sexo""").df()
    arq, xml = ler_xml(ano, "sinopse", q.aba.iloc[0], int(q.linha.iloc[0]), set(q.coluna))
    for r in q.itertuples():
        casos.append({"ocorrencia": "Q10", "ano": ano, "arquivo": arq, "celula": f"{r.aba}!{r.coluna}{r.linha}",
                      "descricao": f"Brasil, Graduação, Faculdade privada c/ fins, {r.cor_raca}, sexo {r.sexo}",
                      "valor_xml_original": xml.get(r.coluna), "valor_nucleo": r.valor})
# ---- Q02/Q03: Anexo II, IF Federal em MT (Alta Floresta – Administração), 2021–2023: vagas, inscritos, ingressantes
for ano in (2021, 2022, 2023):
    q = con.execute(f"""SELECT f.aba, f.linha, f.coluna, f.indicador, f.valor FROM fato_anexo_curso f
        JOIN dim_recorte r USING (id_recorte) JOIN dim_geografia g USING (id_geo)
        JOIN dim_curso_cine c ON c.ano = f.ano AND c.co_cine = f.co_cine
        WHERE f.ano={ano} AND f.anexo='anexo_ii' AND g.no_municipio='Alta Floresta' AND g.co_uf='51'
          AND c.no_cine='Administração' AND r.org_academica='IF/Cefet' AND r.grau='Total'
          AND r.dependencia='Total' AND r.categoria_privada='Total'
          AND f.indicador IN ('vagas','inscritos','ingressantes','matriculas')""").df()
    if q.empty:
        continue
    arq, xml = ler_xml(ano, "anexo_ii", q.aba.iloc[0], int(q.linha.iloc[0]), set(q.coluna))
    for r in q.itertuples():
        casos.append({"ocorrencia": "Q02" if r.indicador == "inscritos" else ("Q03" if r.indicador == "ingressantes" else "contexto"),
                      "ano": ano, "arquivo": arq, "celula": f"{r.aba}!{r.coluna}{r.linha}",
                      "descricao": f"IF/Cefet, Alta Floresta (MT), Administração — {r.indicador}",
                      "valor_xml_original": xml.get(r.coluna), "valor_nucleo": r.valor})
R = pd.DataFrame(casos)
R["conclusao"] = [("fonte" if (x is not None and float(x) == float(n)) else "processamento") for x, n in
                  zip(R.valor_xml_original, R.valor_nucleo)]
R.to_csv(QUALIDADE / "confirmacao_fonte_Q02_Q03_Q10.csv", index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
print(R.drop(columns=["arquivo"]).to_string(index=False))
print("\nconclusões:", R.groupby(["ocorrencia", "conclusao"]).size().to_dict())
