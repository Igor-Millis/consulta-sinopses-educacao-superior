"""Consulta (estrutura) → SQL parametrizado sobre os marts; execução segura; rótulos de local.

Valores vindos da pergunta entram só como parâmetros (?). Nomes de coluna vêm de listas fixas deste módulo.
Escolha da fonte:
  ies, docentes                          → mart_sinopse_geo (tabelas 1.1, 2.1, 2.5; valores publicados)
  sexo, cor/raça ou faixa etária pedidos → mart_sinopse_geo (4.6–4.8, 5.5–5.7, 6.5–6.7; soma das folhas)
  curso (quebra ou filtro)               → mart_curso_geo (cursos agrupados pelo código Cine de 2024)
  demais                                 → mart_anexos_geo
"""
from copy import deepcopy
from dataclasses import dataclass, field

import pandas as pd

from .seguranca import executar

DIMS_ANEXOS = ["modalidade", "rede", "dependencia", "categoria_privada", "org_academica", "grau"]
DIMS_SINOPSE = ["sexo", "cor_raca", "faixa_etaria"]
NOME_DIM = {"modalidade": "Modalidade", "rede": "Rede", "dependencia": "Dependência administrativa",
            "categoria_privada": "Categoria privada", "org_academica": "Organização acadêmica", "grau": "Grau acadêmico",
            "sexo": "Sexo", "cor_raca": "Cor/raça", "faixa_etaria": "Faixa etária", "curso": "Curso"}


@dataclass
class Plano:
    fonte: str
    sql: str = ""
    params: list = field(default_factory=list)
    dims: list = field(default_factory=list)       # colunas de quebra presentes no resultado
    aditivo: bool = True
    notas: list = field(default_factory=list)       # limitações específicas desta consulta
    esclarecer: list = field(default_factory=list)


def _ids(c):
    """ids geográficos a buscar (grupos viram seus municípios; pais incluídos para participação)."""
    ids = []
    for l in c.locais:
        ids += list(l.membros) if l.nivel == "Grupo" else [l.id_geo]
        if c.tipo == "participacao" and not c.quebras and not c.filtros:
            if l.nivel in ("Município", "Grupo") and l.co_uf:
                ids.append("UF-" + l.co_uf)
            elif l.nivel in ("UF", "Região"):
                ids.append("BR")
    if c.listar_municipios_uf:
        ids.append("UF-" + c.listar_municipios_uf)
    if c.listar_ufs:
        ids.append("BR")
    return sorted(set(ids))


def _cond_geo(c, params):
    partes = ["list_contains(?, id_geo)"]
    params.append(_ids(c))
    if c.listar_municipios_uf:
        partes.append("(nivel_geo = 'Município' AND id_geo IN (SELECT id_geo FROM dim_geografia "
                      "WHERE nivel_geo = 'Município' AND co_uf = ?))")
        params.append(c.listar_municipios_uf)
    if c.listar_ufs:
        partes.append("nivel_geo = 'UF'")
    return "(" + " OR ".join(partes) + ")"


def planejar(c, cat) -> Plano:
    ind = cat.indicadores[c.indicador]
    pedidas = list(dict.fromkeys([*c.filtros, *c.quebras]))
    if c.indicador in ("ies", "docentes_exercicio") or set(pedidas) & set(DIMS_SINOPSE):
        return _plano_sinopse(c, cat, ind, pedidas)
    if "curso" in pedidas:
        return _plano_curso(c, cat, ind, pedidas)
    return _plano_anexos(c, cat, ind, pedidas)


def _abaixo_brasil(c):
    return c.listar_ufs or c.listar_municipios_uf or any(l.nivel != "Brasil" for l in c.locais)


def _plano_anexos(c, cat, ind, pedidas):
    pl = Plano("mart_anexos_geo", aditivo=True)
    params = [c.indicador, c.anos]
    where = ["indicador = ?", "list_contains(?, ano)", _cond_geo(c, params)]
    for d, v in c.filtros.items():
        if d not in DIMS_ANEXOS:
            pl.esclarecer.append(f"O filtro '{NOME_DIM.get(d, d)}' não pode ser combinado com {ind['nome'].lower()} "
                                 "nesta fonte.")
            continue
        where.append(f"{d} = ?")
        params.append(v)
    pl.dims = [d for d in c.quebras if d in DIMS_ANEXOS]
    sel = ", ".join(["ano", "id_geo", "nivel_geo", *pl.dims])
    pl.sql = (f"SELECT {sel}, sum(valor) AS valor, bool_or(tem_suspeito) AS tem_suspeito, "
              f"string_agg(DISTINCT ocorrencias, ';') AS ocorrencias, min(origem_exemplo) AS origem "
              f"FROM mart_anexos_geo WHERE {' AND '.join(where)} GROUP BY ALL ORDER BY ALL")
    pl.params = params
    if c.indicador in ("cursos", "vagas", "inscritos") and _abaixo_brasil(c):
        if c.filtros.get("modalidade") == "A Distância":
            pl.esclarecer.append(f"Não há dados de {ind['nome'].lower()} a distância (EaD) por município, UF ou "
                                 "região: o INEP só publica esse número no total Brasil.")
        else:
            pl.notas.append(f"{ind['nome']}: abaixo do Brasil só existe o presencial (o EaD não é publicado por local).")
    return pl


def _plano_curso(c, cat, ind, pedidas):
    pl = Plano("mart_curso_geo", aditivo=True)
    if any(l.nivel == "Região" for l in c.locais):
        pl.esclarecer.append("Por curso, os dados estão disponíveis para município, UF e Brasil (não por região).")
    params = [c.indicador, c.anos]
    where = ["indicador = ?", "list_contains(?, ano)", _cond_geo(c, params)]
    for d, v in c.filtros.items():
        if d == "modalidade":
            where.append("modalidade = ?")
            params.append(v)
        elif d == "curso":
            where.append("coalesce(co_cine_ref, co_cine) = ?")
            params.append(v)
        else:
            pl.esclarecer.append(f"Por curso não há abertura por {NOME_DIM.get(d, d).lower()} (só modalidade).")
    pl.dims = (["curso"] if "curso" in c.quebras else []) + (["modalidade"] if "modalidade" in c.quebras else [])
    sel_curso = "coalesce(co_cine_ref, co_cine) AS co_curso, " if "curso" in pl.dims else ""
    grp_mod = "modalidade, " if "modalidade" in pl.dims else ""
    pl.sql = (f"SELECT ano, id_geo, nivel_geo, {sel_curso}{grp_mod}max(no_cine) AS no_curso, sum(valor) AS valor, "
              f"bool_or(tem_suspeito) AS tem_suspeito, min(origem) AS origem "
              f"FROM mart_curso_geo WHERE {' AND '.join(where)} GROUP BY ALL ORDER BY ALL")
    if "curso" not in pl.dims:   # filtro de um curso: não agrupa por curso
        pl.sql = pl.sql.replace("max(no_cine) AS no_curso, ", "")
    pl.params = params
    if 2024 in c.anos and min(c.anos) < 2024:
        pl.notas.append("Cursos: a Cine Brasil foi revisada em 2024; 13 cursos mudaram de código mantendo o nome e "
                        "foram ligados pela tabela xw_cine. Cursos que só existem em parte dos anos aparecem só nesses anos.")
    if c.indicador in ("cursos", "vagas", "inscritos") and _abaixo_brasil(c):
        pl.notas.append(f"{ind['nome']}: abaixo do Brasil só existe o presencial (o EaD não é publicado por local).")
    return pl


ORG_FOLHA = ["rede", "dependencia", "categoria_privada", "org_academica"]


def _plano_sinopse_folhas(c, cat, ind, pedidas):
    """Matrículas/ingressantes/concluintes por sexo, cor/raça ou faixa etária: o mart guarda as folhas
    org. acadêmica × dependência × categoria privada, que podem ser filtradas ou abertas (rede, dependência...)."""
    pl = Plano("mart_sinopse_geo", aditivo=True)
    sinop = [d for d in pedidas if d in DIMS_SINOPSE]
    org = [d for d in pedidas if d in ORG_FOLHA]
    extras = [d for d in pedidas if d not in DIMS_SINOPSE + ORG_FOLHA]
    if extras:
        pl.esclarecer.append(
            f"Para {ind['nome'].lower()} por {', '.join(NOME_DIM[d].lower() for d in sinop)}, a Sinopse não traz "
            f"cruzamento com {', '.join(NOME_DIM.get(d, d).lower() for d in extras)} por localidade "
            "(dá para combinar com rede, dependência administrativa, categoria privada e organização acadêmica).")
    if len(sinop) > 1:
        pl.esclarecer.append("A Sinopse publica, por localidade, uma dimensão de cada vez "
                             f"({' ou '.join(NOME_DIM[d].lower() for d in sinop)}). Qual delas?")
    if pl.esclarecer:
        return pl
    dim = sinop[0]
    params = [c.indicador, c.anos]
    where = ["indicador = ?", "list_contains(?, ano)", _cond_geo(c, params), "dimensao = ?", "modo = 'soma das folhas'"]
    params.append(dim)
    if dim in c.filtros:
        where.append("categoria = ?")
        params.append(c.filtros[dim])
    for d in org:
        if d in c.filtros:
            where.append(f"{d} = ?")
            params.append(c.filtros[d])
    pl.dims = ([dim] if dim in c.quebras else []) + [d for d in org if d in c.quebras]
    cols = "".join(("categoria AS " + d if d == dim else d) + ", " for d in pl.dims)
    pl.sql = (f"SELECT ano, id_geo, nivel_geo, {cols}sum(valor) AS valor, bool_or(tem_suspeito) AS tem_suspeito, "
              f"string_agg(DISTINCT ocorrencias, ';') AS ocorrencias, min(origem) AS origem, "
              f"string_agg(DISTINCT tabela, ',') AS tabelas "
              f"FROM mart_sinopse_geo WHERE {' AND '.join(where)} GROUP BY ALL ORDER BY ALL")
    pl.params = params
    pl.notas.append(f"{NOME_DIM[dim]}: Sinopse, soma das folhas publicadas por organização acadêmica × dependência "
                    "× categoria privada, nível Graduação; inclui presencial e a distância.")
    return pl


def _plano_sinopse(c, cat, ind, pedidas):
    if c.indicador not in ("ies", "docentes_exercicio"):
        return _plano_sinopse_folhas(c, cat, ind, pedidas)
    pl = Plano("mart_sinopse_geo", aditivo=bool(ind.get("aditivo", True)))
    disp = {"ies": ["dependencia", "rede", "org_academica"],
            "docentes_exercicio": ["dependencia", "rede", "org_academica", "sexo"]}.get(c.indicador, DIMS_SINOPSE)
    extras = [d for d in pedidas if d not in disp]
    sinop = [d for d in pedidas if d in disp]
    if extras:
        pl.esclarecer.append(
            f"Para {ind['nome'].lower()}" + (f" por {', '.join(NOME_DIM.get(d, d).lower() for d in sinop)}" if sinop else "")
            + f", a Sinopse não traz cruzamento com {', '.join(NOME_DIM.get(d, d).lower() for d in extras)} "
            "por localidade. Pergunte por uma dimensão de cada vez.")
    if len(sinop) > 1:
        pl.esclarecer.append("A Sinopse publica, por localidade, uma dimensão de cada vez "
                             f"({' ou '.join(NOME_DIM[d].lower() for d in sinop)}). Qual delas?")
    if pl.esclarecer:
        return pl
    dim = sinop[0] if sinop else None
    params = [c.indicador, c.anos]
    where = ["indicador = ?", "list_contains(?, ano)", _cond_geo(c, params)]
    if dim is None:
        where.append("dimensao = 'total'")
        if c.indicador not in ("ies", "docentes_exercicio"):
            pl.esclarecer.append("Sem dimensão da Sinopse.")   # não deveria acontecer (planejar desvia antes)
    elif dim == "rede":
        where.append("dimensao = 'dependencia' AND categoria IN ('Pública', 'Privada')")
    elif dim == "dependencia":
        where.append("dimensao = 'dependencia' AND categoria <> 'Pública'")   # 'Pública' é agregado publicado
    else:
        where.append("dimensao = ?")
        params.append(dim)
    if dim in c.filtros:
        where.append("categoria = ?")
        params.append(c.filtros[dim])
    pl.dims = [dim] if dim and dim in c.quebras else []
    col = f"categoria AS {dim}, " if pl.dims else ""
    pl.sql = (f"SELECT ano, id_geo, nivel_geo, {col}sum(valor) AS valor, bool_or(tem_suspeito) AS tem_suspeito, "
              f"string_agg(DISTINCT ocorrencias, ';') AS ocorrencias, min(origem) AS origem, "
              f"string_agg(DISTINCT tabela, ',') AS tabelas "
              f"FROM mart_sinopse_geo WHERE {' AND '.join(where)} GROUP BY ALL ORDER BY ALL")
    pl.params = params
    if c.indicador == "ies" and dim == "org_academica":
        pl.notas.append("Na tabela 1.1, IF/Cefet aparece só dentro da dependência Federal; por organização acadêmica "
                        "constam Universidade, Centro Universitário e Faculdade.")
    if dim in DIMS_SINOPSE and c.indicador not in ("ies", "docentes_exercicio"):
        pl.notas.append(f"{NOME_DIM[dim]}: soma das categorias publicadas por organização acadêmica e dependência "
                        "(Sinopse), nível Graduação; inclui presencial e a distância.")
    return pl


def para_participacao(c):
    """Participação com filtros: os filtros viram quebras (uma só consulta dá numerador e denominador)."""
    c2 = deepcopy(c)
    for d in list(c2.filtros):
        if c2.parte_dims and d not in c2.parte_dims:
            continue                       # filtro de universo: fica como filtro (entra no denominador)
        if d not in c2.quebras and d != "curso":
            c2.quebras.append(d)
            c2.parte[d] = c2.filtros.pop(d)
    return c2


def rotular(df: pd.DataFrame, c, cat, aditivo: bool) -> tuple[pd.DataFrame, list]:
    """Acrescenta 'local' (rótulo) e soma os municípios de grupos (ex.: Grande Vitória) quando o indicador é aditivo."""
    notas = []
    if df.empty:
        return df.assign(local=pd.Series(dtype=str)), notas
    nomes = {}
    for idg in df["id_geo"].unique():
        loc = cat.locais.get(idg)
        if loc is None:
            nomes[idg] = idg
        elif loc.nivel == "Município":
            nomes[idg] = f"{loc.nome} ({loc.sg_uf})"
        elif loc.nivel == "UF":
            nomes[idg] = loc.nome or loc.sg_uf
        else:
            nomes[idg] = loc.nome or idg
    df = df.assign(local=df["id_geo"].map(nomes))
    grupos = [l for l in c.locais if l.nivel == "Grupo"]
    for g in grupos:
        membros = df[df["id_geo"].isin(g.membros)]
        if membros.empty:
            continue
        if not aditivo:
            notas.append(f"{g.nome}: o indicador não é aditivo; os municípios são mostrados separadamente (sem somar).")
            continue
        chaves = [k for k in ["ano", *[x for x in df.columns if x in DIMS_ANEXOS + DIMS_SINOPSE + ["curso", "co_curso", "no_curso"]]]
                  if k in df.columns]
        soma = membros.groupby(chaves, dropna=False, as_index=False).agg(
            valor=("valor", "sum"), tem_suspeito=("tem_suspeito", "any"),
            **({"ocorrencias": ("ocorrencias", lambda s: ";".join(sorted({x for v in s.dropna() for x in str(v).split(";") if x})) or None)}
               if "ocorrencias" in df.columns else {}),
            **({"tabelas": ("tabelas", lambda s: ",".join(sorted({x for v in s.dropna() for x in str(v).split(",") if x})))}
               if "tabelas" in df.columns else {}),
            origem=("origem", "min"))
        soma["id_geo"], soma["nivel_geo"], soma["local"] = g.id_geo, "Grupo", g.nome
        faltam = set(g.membros) - set(membros["id_geo"])
        if faltam:
            notas.append(f"{g.nome}: {len(faltam)} município(s) sem valor no recorte pedido (contados como ausentes, não como zero).")
        df = pd.concat([df[~df["id_geo"].isin(g.membros) | df["id_geo"].isin(
            [l.id_geo for l in c.locais if l.nivel == "Município"])], soma], ignore_index=True)
    return df, notas


def buscar(plano: Plano, pergunta: str) -> pd.DataFrame:
    return executar(plano.sql, plano.params, pergunta)


def ocorrencias(ids=None, tabelas_anos=None) -> pd.DataFrame:
    """Ocorrências de qualidade pertinentes: por id (Anexos) ou por tabela × ano (Sinopse)."""
    q = executar("SELECT id, anos, tabela, indicadores, descricao, situacao FROM qualidade_ocorrencias ORDER BY id")
    if q.empty:
        return q
    sel = pd.Series(False, index=q.index)
    if ids:
        sel |= q["id"].isin(ids)
    for tab, ano in (tabelas_anos or []):
        for i, r in q.iterrows():
            if tab in str(r["tabela"]).split(";") and _ano_em(ano, str(r["anos"])):
                sel[i] = True
    return q[sel]


def _ano_em(ano, texto):
    for parte in texto.replace(",", ";").split(";"):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-")[:2]
            if a.strip().isdigit() and b.strip().isdigit() and int(a) <= ano <= int(b):
                return True
        elif parte.isdigit() and int(parte) == ano:
            return True
    return False
