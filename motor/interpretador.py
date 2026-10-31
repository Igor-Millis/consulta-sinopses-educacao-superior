"""Interpretador determinístico: pergunta em português → Consulta (estrutura explícita).

Não calcula nada e não acessa dados além dos nomes de locais do catálogo. Toda suposição vira um item em
`consulta.supostos` (mostrado na resposta); o que não dá para decidir vira `consulta.esclarecer`.
Pode ser substituído por um modelo de linguagem que produza a mesma estrutura `Consulta`.
"""
import re
from dataclasses import dataclass, field

from .semantica import Catalogo, Local, normalizar

NUMEROS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8}
QUEBRAS = {  # "por X" → dimensão
    "sexo": "sexo", "genero": "sexo", "cor": "cor_raca", "raca": "cor_raca", "cor raca": "cor_raca",
    "cor/raca": "cor_raca", "faixa etaria": "faixa_etaria", "idade": "faixa_etaria", "modalidade": "modalidade",
    "rede": "rede", "categoria administrativa": "dependencia", "dependencia administrativa": "dependencia",
    "dependencia": "dependencia", "organizacao academica": "org_academica", "tipo de instituicao": "org_academica",
    "grau": "grau", "grau academico": "grau", "curso": "curso", "cursos": "curso", "municipio": "municipio",
    "municipios": "municipio", "estado": "uf", "estados": "uf", "uf": "uf", "regiao": "regiao", "regioes": "regiao",
}


@dataclass
class Consulta:
    texto: str
    indicador: str | None = None
    anos: list = field(default_factory=list)
    locais: list = field(default_factory=list)            # [Local]
    listar_municipios_uf: str | None = None              # co_uf quando a pergunta é sobre "os municípios do ES"
    listar_ufs: bool = False
    filtros: dict = field(default_factory=dict)          # dim → valor canônico
    quebras: list = field(default_factory=list)          # dims a abrir
    tipo: str = "valor"                                   # valor | serie | ranking | crescimento | participacao | comparacao | compatibilidade
    ordem: str = "desc"
    top_n: int = 10
    criterio: str = "absoluto"                             # ranking de crescimento: absoluto | percentual
    parte: dict = field(default_factory=dict)              # participação: recorte do numerador (filtros → quebras)
    supostos: list = field(default_factory=list)
    esclarecer: list = field(default_factory=list)


def _tem(t, *termos):
    return any(re.search(rf"(?<![\w]){re.escape(x)}(?![\w])", t) for x in termos)


def _consumir(t, termo):
    return re.sub(rf"(?<![\w]){re.escape(termo)}(?![\w])", " ", t, count=1)


def interpretar(texto: str, cat: Catalogo, ano_max: int = 2024, ano_min: int = 2017) -> Consulta:
    c = Consulta(texto=texto)
    t = normalizar(texto)
    original = texto

    # ---------------- tipo de pergunta
    if _tem(t, "mudancas metodologicas", "mudanca metodologica", "comparabilidade", "comparaveis", "comparavel",
            "mudancas de classificacao", "quebra de serie", "prejudicam a comparacao"):
        c.tipo = "compatibilidade"
        return c

    # ---------------- anos
    anos = [int(a) for a in re.findall(r"\b(20[12]\d)\b", t)]
    m = re.search(r"\bultimos? (\d+|" + "|".join(NUMEROS) + r") anos\b", t)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else NUMEROS[m.group(1)]
        c.anos = list(range(ano_max - n + 1, ano_max + 1))
        c.supostos.append(f"'últimos {n} anos' = {c.anos[0]}–{c.anos[-1]} (último ano disponível: {ano_max})")
    elif len(anos) >= 2 and _tem(t, "entre", "de", "desde", "ate", "a"):
        c.anos = list(range(min(anos), max(anos) + 1))
    elif anos:
        c.anos = sorted(set(anos))
    fora = [a for a in c.anos if a < ano_min or a > ano_max]
    if fora:
        c.esclarecer.append(f"Os dados cobrem {ano_min}–{ano_max}; não há dados para {', '.join(map(str, fora))}.")

    serie = _tem(t, "evolu", "evoluiram", "evoluiu", "evolucao", "historico", "serie", "ao longo", "tendencia",
                 "variacao", "cresceu", "cresceram", "crescimento", "aumentou", "diminuiu", "queda", "reducao")
    serie = serie or any(w.startswith("evolu") or w.startswith("cresc") for w in t.split())

    # ---------------- dimensão curso e listas de lugares ("quais cursos", "municípios capixabas")
    lista_cursos = _tem(t, "quais cursos", "por curso", "cursos que", "cursos com", "cursos mais", "cursos de maior",
                        "cursos que mais")
    if lista_cursos:
        c.quebras.append("curso")
        t = t.replace("cursos", " ")

    # ---------------- locais: aliases, UFs e municípios numa só passada, nome mais longo primeiro
    # (assim "Rio Grande do Sul" e "Rio Novo do Sul" vencem a região "sul"); cada trecho achado é consumido.
    restante = t
    termos = [(a, "alias") for a in cat.aliases]
    termos += [(n, "uf") for n, l in cat.nomes_uf.items() if not n.startswith("sigla:") and l is not None]
    termos += [(n, "mun") for n in cat.nomes_municipio if len(n) >= 4]
    achados = []                                      # (posição no texto, tipo, termo)
    for termo, tipo in sorted(termos, key=lambda x: -len(x[0])):
        m = re.search(rf"(?<![\w]){re.escape(termo)}(?![\w])", restante)
        if m:
            achados.append((m.start(), tipo, termo))
            restante = restante[:m.start()] + " " * len(termo) + restante[m.end():]
    achados.sort()
    ufs_citadas = {cat.nomes_uf[x].co_uf for _, tp, x in achados if tp == "uf"}
    ufs_citadas |= {cat.locais[cat.aliases[x]].co_uf for _, tp, x in achados
                    if tp == "alias" and isinstance(cat.aliases[x], str) and cat.aliases[x].startswith("UF-")
                    and cat.aliases[x] in cat.locais}
    for _, tipo, termo in achados:
        if tipo == "alias":
            alvo = cat.aliases[termo]
            if isinstance(alvo, dict):
                ids = []
                for nome in alvo["municipios"]:
                    loc = next((l for l in cat.nomes_municipio.get(normalizar(nome), []) if l.co_uf == alvo["uf"]), None)
                    if loc:
                        ids.append(loc.id_geo)
                rotulo = termo.title().replace("Vitoria", "Vitória")
                c.locais.append(Local("GRUPO:" + termo, rotulo, "Grupo", alvo["uf"], None, tuple(ids)))
                c.supostos.append(f"'{rotulo}' = soma de {', '.join(alvo['municipios'])}")
            elif alvo in cat.locais and cat.locais[alvo] not in c.locais:
                c.locais.append(cat.locais[alvo])
        elif tipo == "uf":
            if cat.nomes_uf[termo] not in c.locais:
                c.locais.append(cat.nomes_uf[termo])
        else:
            cands = cat.nomes_municipio[termo]
            escolhidos = [l for l in cands if l.co_uf in ufs_citadas] or cands
            if len(escolhidos) > 1 and any(l.co_uf == "32" for l in escolhidos):
                es = next(l for l in escolhidos if l.co_uf == "32")
                c.supostos.append(f"'{es.nome}' existe em mais de uma UF ("
                                  + ", ".join(l.sg_uf for l in escolhidos) + "): usei o do ES")
                escolhidos = [es]
            if len(escolhidos) > 1:
                c.esclarecer.append(f"Há mais de um município chamado '{escolhidos[0].nome}': "
                                    + ", ".join(f"{l.nome} ({l.sg_uf})" for l in escolhidos) + ". Qual deles?")
            elif escolhidos[0] not in c.locais:
                c.locais.append(escolhidos[0])
    for sg in re.findall(r"\b([A-Z]{2})\b", original):  # siglas só em maiúsculas no texto original
        loc = cat.nomes_uf.get("sigla:" + sg)
        if loc and loc not in c.locais:
            c.locais.append(loc)
    # curso citado pelo nome (rótulo Cine), nome mais longo primeiro
    for nome in sorted(cat.nomes_curso, key=len, reverse=True):
        if len(nome) >= 5 and _tem(restante, nome):
            c.filtros["curso"] = cat.nomes_curso[nome]
            restante = _consumir(restante, nome)
            break
    # "municípios capixabas / do ES" → listar municípios da UF
    if _tem(t, "municipios", "cidades") and not lista_cursos:
        ufs = [l for l in c.locais if l.nivel == "UF"]
        if len(ufs) == 1 and not [l for l in c.locais if l.nivel == "Município"]:
            c.listar_municipios_uf = ufs[0].co_uf
    if _tem(t, "por estado", "por uf", "entre os estados", "quais estados", "por estados"):
        c.listar_ufs = True

    # ---------------- indicador
    for termo, iid in cat.sin_indicador:
        if _tem(restante, termo):
            c.indicador = iid
            break
    if c.indicador is None and lista_cursos:
        c.indicador = "matriculas"
        c.supostos.append("indicador não citado: usei matrículas para medir os cursos")
    if c.indicador is None and _tem(t, "ensino superior", "graduacao") and not _tem(t, "instituic", "docente", "professor"):
        c.indicador = "matriculas"
        c.supostos.append("indicador não citado explicitamente: usei matrículas")
    if c.indicador is None:
        c.esclarecer.append("Qual indicador? Opções: matrículas, ingressantes, concluintes, cursos, vagas, "
                            "inscritos, instituições (IES) ou docentes.")

    # ---------------- filtros e quebras por dimensão
    for dim in ("modalidade", "rede", "dependencia", "categoria_privada", "org_academica", "grau", "sexo", "cor_raca"):
        achados = []
        for termo, canon in cat.termos(dim):
            if _tem(restante, termo) and canon not in achados:
                achados.append(canon)
        if dim == "dependencia" and set(achados) <= {"Privada"}:
            achados = []  # "privada" é tratada como rede
        if len(achados) >= 2:
            if dim not in c.quebras:
                c.quebras.append(dim)
        elif len(achados) == 1:
            c.filtros[dim] = achados[0]
    m = re.search(r"\bpor (" + "|".join(sorted(QUEBRAS, key=len, reverse=True)) + r")\b", t)
    if m:
        d = QUEBRAS[m.group(1)]
        if d == "municipio":
            ufs = [l for l in c.locais if l.nivel == "UF"]
            if ufs:
                c.listar_municipios_uf = ufs[0].co_uf
        elif d == "uf":
            c.listar_ufs = True
        elif d not in c.quebras:
            c.quebras.append(d)
            c.filtros.pop(d, None)
    if _tem(t, "categoria administrativa") and "dependencia" not in c.quebras and "rede" not in c.quebras:
        c.quebras.append("dependencia")

    # ---------------- tipo de análise
    ranking = _tem(t, "maior", "maiores", "menor", "menores", "ranking", "top", "mais", "principais", "lideram")
    if _tem(t, "menor", "menores"):
        c.ordem = "asc"
    m = re.search(r"\b(\d+) (municipios|cursos|estados|maiores|principais)\b", t)
    if m:
        c.top_n = int(m.group(1))
    cresc_pct = _tem(t, "crescimento percentual", "variacao percentual", "crescimento relativo", "em percentual",
                     "proporcionalmente", "em termos percentuais")
    if cresc_pct:
        c.criterio = "percentual"
    if _tem(t, "participacao", "proporcao", "percentual", "parcela", "fatia", "porcentagem") and not cresc_pct:
        c.tipo = "participacao"
    elif ranking and ("curso" in c.quebras or c.listar_municipios_uf or c.listar_ufs) and serie:
        c.tipo = "crescimento"
    elif ranking and ("curso" in c.quebras or c.listar_municipios_uf or c.listar_ufs):
        c.tipo = "ranking"
    elif len(c.locais) >= 2 or _tem(t, "compare", "comparar", "comparacao", "compara", "versus", "em relacao"):
        c.tipo = "comparacao"
    elif serie or len(c.anos) > 1:
        c.tipo = "serie"

    # ---------------- defaults explícitos
    if not c.anos:
        if c.tipo in ("serie", "comparacao", "crescimento") or (c.tipo == "participacao" and serie):
            c.anos = list(range(ano_min, ano_max + 1))
            c.supostos.append(f"período não informado: usei toda a série {ano_min}–{ano_max}")
        else:
            c.anos = [ano_max]
            c.supostos.append(f"ano não informado: usei o mais recente ({ano_max})")
    if c.tipo == "crescimento" and len(c.anos) < 2:
        c.anos = [c.anos[0] - 5 if c.anos[0] - 5 >= ano_min else ano_min, c.anos[0]]
    if not c.locais and not c.listar_ufs:
        c.locais.append(cat.locais.get("BR") or Local("BR", "Brasil", "Brasil"))
        c.supostos.append("local não informado: usei o Brasil")
    if c.listar_ufs and not [l for l in c.locais if l.nivel != "Brasil"]:
        c.locais = []
    return c
