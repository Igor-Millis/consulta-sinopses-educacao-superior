"""Contrato de interpretação: a estrutura `Consulta` em JSON, com validação contra o catálogo.

É o ponto de integração de um modelo de linguagem (ver _arquitetura/03_proposta_llm.md): o modelo recebe a pergunta
e o esquema, devolve SÓ este JSON; `de_json` valida tudo (indicador, anos, locais, dimensões e valores) contra o
catálogo e o banco antes de qualquer consulta. O modelo nunca escreve SQL e nunca produz números.
O interpretador por regras produz a mesma estrutura (`para_json(interpretar(...))`).
"""
from .interpretador import Consulta
from .semantica import Local

TIPOS = ["valor", "serie", "ranking", "crescimento", "participacao", "comparacao", "compatibilidade"]
DIMS = ["modalidade", "rede", "dependencia", "categoria_privada", "org_academica", "grau", "sexo", "cor_raca",
        "faixa_etaria", "curso"]


def esquema(cat) -> dict:
    """JSON Schema da Consulta, com os valores permitidos tirados do catálogo (para instruir um modelo)."""
    valores = {d: sorted({canon for _, canon in cat.termos(d)}) for d in DIMS if cat.termos(d)}
    return {
        "type": "object", "additionalProperties": False,
        "required": ["indicador", "tipo", "anos", "locais"],
        "properties": {
            "indicador": {"enum": sorted([*cat.indicadores, *cat.derivados]) + [None]},
            "tipo": {"enum": TIPOS},
            "anos": {"type": "array", "items": {"type": "integer", "minimum": 2017, "maximum": 2024}},
            "locais": {"type": "array", "items": {"type": "string"},
                       "description": "id_geo de dim_geografia (ex.: 'UF-32', '3205200', 'REG-Sudeste', 'BR') "
                                      "ou 'GRUPO:<alias>' (ex.: 'GRUPO:grande vitoria')"},
            "listar_municipios_uf": {"type": ["string", "null"], "description": "código IBGE da UF (ex.: '32')"},
            "listar_ufs": {"type": "boolean"},
            "filtros": {"type": "object", "properties": {d: {"enum": v} for d, v in valores.items()} |
                        {"curso": {"type": "string", "description": "código Cine de referência (xw_cine)"}}},
            "quebras": {"type": "array", "items": {"enum": DIMS}},
            "ordem": {"enum": ["asc", "desc"]}, "top_n": {"type": "integer", "minimum": 1},
            "criterio": {"enum": ["absoluto", "percentual"]}, "so_reducao": {"type": "boolean"},
            "parte_dims": {"type": "array", "items": {"enum": DIMS}},
            "supostos": {"type": "array", "items": {"type": "string"}},
            "esclarecer": {"type": "array", "items": {"type": "string"}},
        },
    }


def para_json(c: Consulta) -> dict:
    locais = [l.id_geo for l in c.locais]
    return {"indicador": c.indicador, "tipo": c.tipo, "anos": list(c.anos), "locais": locais,
            "listar_municipios_uf": c.listar_municipios_uf, "listar_ufs": c.listar_ufs, "filtros": dict(c.filtros),
            "quebras": list(c.quebras), "ordem": c.ordem, "top_n": c.top_n, "criterio": c.criterio,
            "so_reducao": c.so_reducao, "parte_dims": list(c.parte_dims), "supostos": list(c.supostos),
            "esclarecer": list(c.esclarecer)}


def de_json(d: dict, cat, texto: str = "") -> tuple[Consulta | None, list]:
    """Valida o JSON e devolve (Consulta, []) ou (None, erros). Nada é corrigido em silêncio."""
    erros = []
    if not isinstance(d, dict):
        return None, ["o resultado não é um objeto JSON"]
    extras = set(d) - set(esquema(cat)["properties"])
    if extras:
        erros.append(f"campos desconhecidos: {sorted(extras)}")
    ind = d.get("indicador")
    if ind is not None and ind not in cat.indicadores and ind not in cat.derivados:
        erros.append(f"indicador inexistente: {ind}")
    tipo = d.get("tipo", "valor")
    if tipo not in TIPOS:
        erros.append(f"tipo inválido: {tipo}")
    anos = d.get("anos", [])
    if not isinstance(anos, list) or any(not isinstance(a, int) or not 2017 <= a <= 2024 for a in anos):
        erros.append(f"anos fora de 2017–2024 ou inválidos: {anos}")
    locais = []
    for idg in d.get("locais", []):
        if isinstance(idg, str) and idg.startswith("GRUPO:"):
            alvo = cat.aliases.get(idg[6:])
            if not isinstance(alvo, dict):
                erros.append(f"grupo desconhecido: {idg}")
                continue
            ids = tuple(next(l.id_geo for l in cat.nomes_municipio[__import__("motor").semantica.normalizar(m)]
                             if l.co_uf == alvo["uf"]) for m in alvo["municipios"])
            locais.append(Local(idg, idg[6:].title().replace("Vitoria", "Vitória"), "Grupo", alvo["uf"], None, ids))
        elif idg in cat.locais:
            locais.append(cat.locais[idg])
        else:
            erros.append(f"local inexistente em dim_geografia: {idg}")
    ufs_validas = {l.co_uf for l in cat.locais.values() if l.nivel == "UF"}
    lmu = d.get("listar_municipios_uf")
    if lmu is not None and lmu not in ufs_validas:
        erros.append(f"UF inexistente: {lmu}")
    filtros = d.get("filtros", {}) or {}
    for dim, v in filtros.items():
        if dim == "curso":
            if v not in cat.nome_curso:
                erros.append(f"curso inexistente: {v}")
        elif dim not in DIMS or v not in {canon for _, canon in cat.termos(dim)}:
            erros.append(f"filtro inválido: {dim}={v}")
    for q in d.get("quebras", []) + d.get("parte_dims", []):
        if q not in DIMS:
            erros.append(f"dimensão inválida: {q}")
    if d.get("ordem", "desc") not in ("asc", "desc") or d.get("criterio", "absoluto") not in ("absoluto", "percentual"):
        erros.append("ordem/critério inválidos")
    if erros:
        return None, erros
    c = Consulta(texto=texto, indicador=ind, anos=list(anos), locais=locais, listar_municipios_uf=lmu,
                 listar_ufs=bool(d.get("listar_ufs", False)), filtros=dict(filtros), quebras=list(d.get("quebras", [])),
                 tipo=tipo, ordem=d.get("ordem", "desc"), top_n=int(d.get("top_n", 10)),
                 criterio=d.get("criterio", "absoluto"), so_reducao=bool(d.get("so_reducao", False)),
                 parte_dims=list(d.get("parte_dims", [])), supostos=list(d.get("supostos", [])),
                 esclarecer=list(d.get("esclarecer", [])))
    return c, []
