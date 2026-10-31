"""Camada semântica: carrega o catálogo (YAML) e resolve termos em português para indicadores, dimensões e locais."""
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache

import yaml

from ..config import CATALOGO


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^\w\s/-]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


@dataclass
class Local:
    id_geo: str
    nome: str
    nivel: str
    co_uf: str | None = None
    sg_uf: str | None = None
    membros: tuple = ()          # nivel "Grupo" (ex.: Grande Vitória): ids de município somados


@dataclass
class Catalogo:
    bruto: dict
    indicadores: dict = field(default_factory=dict)        # id -> dict
    sin_indicador: list = field(default_factory=list)     # [(termo normalizado, id)] mais longo primeiro
    sin_dimensao: dict = field(default_factory=dict)      # dimensao -> [(termo, valor canônico)]
    locais: dict = field(default_factory=dict)            # id_geo -> Local
    nomes_municipio: dict = field(default_factory=dict)   # nome normalizado -> [Local]
    nomes_uf: dict = field(default_factory=dict)          # nome normalizado -> Local
    aliases: dict = field(default_factory=dict)
    nomes_curso: dict = field(default_factory=dict)       # nome normalizado -> código Cine de referência (2024)
    nome_curso: dict = field(default_factory=dict)        # código de referência -> nome

    def termos(self, dim):
        return self.sin_dimensao.get(dim, [])


def _ordenar(pares):
    return sorted(pares, key=lambda p: -len(p[0]))


@lru_cache(maxsize=1)
def carregar(con_factory=None) -> Catalogo:
    """Carrega o catálogo. `con_factory` devolve uma conexão DuckDB somente leitura (para os nomes de locais)."""
    with open(CATALOGO, encoding="utf-8") as f:
        bruto = yaml.safe_load(f)
    cat = Catalogo(bruto=bruto)
    cat.indicadores = bruto["indicadores"]
    pares = []
    for iid, d in cat.indicadores.items():
        for t in [iid, d["nome"], *d.get("sinonimos", [])]:
            pares.append((normalizar(t), iid))
    cat.sin_indicador = _ordenar(set(pares))
    for dim, d in bruto["dimensoes"].items():
        if "valores" in d:
            cat.sin_dimensao[dim] = _ordenar({(normalizar(t), canon) for canon, ts in d["valores"].items()
                                              for t in [canon, *ts]})
    cat.aliases = {normalizar(k): v for k, v in bruto.get("aliases_geo", {}).items()}
    if con_factory is not None:
        con = con_factory()
        for id_geo, nivel, nome, co_uf, sg_uf in con.execute(
                """SELECT id_geo, nivel_geo,
                          CASE nivel_geo WHEN 'Município' THEN no_municipio WHEN 'UF' THEN no_uf
                               WHEN 'Região' THEN no_regiao WHEN 'Brasil' THEN 'Brasil' ELSE coalesce(no_municipio, id_geo) END,
                          co_uf, sg_uf FROM dim_geografia""").fetchall():
            loc = Local(id_geo, nome, nivel, co_uf, sg_uf)
            cat.locais[id_geo] = loc
            if nivel == "Município":
                cat.nomes_municipio.setdefault(normalizar(nome), []).append(loc)
            elif nivel == "UF":
                cat.nomes_uf[normalizar(nome)] = loc
        for sg, co in con.execute("SELECT sg_uf, co_uf FROM dim_uf").fetchall():
            cat.nomes_uf.setdefault("sigla:" + sg, cat.locais.get("UF-" + co))
        for ref, nome in con.execute("""SELECT coalesce(co_cine_ref, co_cine) ref, arg_max(no_cine, ano_fim)
                                        FROM xw_cine GROUP BY 1""").fetchall():
            cat.nome_curso[ref] = nome
            cat.nomes_curso.setdefault(normalizar(nome), ref)
    return cat
