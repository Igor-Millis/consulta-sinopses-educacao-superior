"""Interpretador por modelo de linguagem LOCAL (Ollama em 127.0.0.1), ligado ao motor só pelo contrato.

O modelo recebe a pergunta, o esquema e exemplos e devolve um JSON com NOMES (de locais e cursos), nunca códigos,
SQL ou números de resultado. Este módulo:
  1. chama o Ollama local com saída restrita por JSON Schema (format=esquema) e temperatura 0;
  2. resolve os nomes de forma determinística no catálogo (mesmas regras de homônimos do interpretador por regras);
  3. monta o JSON do contrato, que é validado por contrato.de_json antes de qualquer consulta.
Qualquer falha (servidor ausente, tempo esgotado, JSON inválido, nome não resolvido) vira pedido de esclarecimento.
Endereço fixo em 127.0.0.1: nenhum dado sai do computador.
"""
import json
import time
import urllib.request

from .interpretador import Consulta
from .semantica import normalizar

URL = "http://127.0.0.1:11434/api/chat"       # só local (não configurável de propósito)
MODELO = "qwen2.5:3b"
TEMPO_MAXIMO_S = 180
DIMS_FILTRO = ["modalidade", "rede", "dependencia", "categoria_privada", "org_academica", "grau", "sexo", "cor_raca"]
DIMS_QUEBRA = DIMS_FILTRO + ["faixa_etaria", "curso"]
TIPOS = ["valor", "serie", "ranking", "crescimento", "participacao", "comparacao", "compatibilidade"]


def esquema_llm(cat) -> dict:
    valores = {d: sorted({canon for _, canon in cat.termos(d)}) for d in DIMS_FILTRO}
    return {
        "type": "object",
        "properties": {
            "indicador": {"type": ["string", "null"], "enum": sorted([*cat.indicadores, *cat.derivados]) + [None]},
            "tipo": {"type": "string", "enum": TIPOS},
            "anos": {"type": "array", "items": {"type": "integer"}},
            "locais": {"type": "array", "items": {"type": "string"}},
            "listar": {"type": ["string", "null"], "enum": ["municipios", "ufs", None]},
            "filtros": {"type": "object", "properties": {d: {"type": "string", "enum": v} for d, v in valores.items()}},
            "curso": {"type": ["string", "null"]},
            "quebras": {"type": "array", "items": {"type": "string", "enum": DIMS_QUEBRA}},
            "ordem": {"type": "string", "enum": ["desc", "asc"]},
            "top_n": {"type": "integer"},
            "criterio": {"type": "string", "enum": ["absoluto", "percentual"]},
            "so_reducao": {"type": "boolean"},
        },
        "required": ["indicador", "tipo", "anos", "locais", "listar", "filtros", "curso", "quebras", "ordem", "top_n",
                     "criterio", "so_reducao"],
    }


EXEMPLOS = [
    ("Quantas matrículas havia em Vila Velha em 2024?",
     {"indicador": "matriculas", "tipo": "valor", "anos": [2024], "locais": ["Vila Velha"], "listar": None,
      "filtros": {}, "curso": None, "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto", "so_reducao": False}),
    ("Como o número de calouros evoluiu no Espírito Santo de 2018 a 2023?",
     {"indicador": "ingressantes", "tipo": "serie", "anos": [2018, 2023], "locais": ["Espírito Santo"], "listar": None,
      "filtros": {}, "curso": None, "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto", "so_reducao": False}),
    ("Qual cidade capixaba forma mais gente?",
     {"indicador": "concluintes", "tipo": "ranking", "anos": [], "locais": ["Espírito Santo"], "listar": "municipios",
      "filtros": {}, "curso": None, "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto", "so_reducao": False}),
    ("O ensino a distância já supera o presencial em matrículas no ES?",
     {"indicador": "matriculas", "tipo": "comparacao", "anos": [], "locais": ["Espírito Santo"], "listar": None,
      "filtros": {}, "curso": None, "quebras": ["modalidade"], "ordem": "desc", "top_n": 10, "criterio": "absoluto",
      "so_reducao": False}),
    ("Que fatia das vagas de Vitória é de instituições públicas?",
     {"indicador": "vagas", "tipo": "participacao", "anos": [], "locais": ["Vitória"], "listar": None,
      "filtros": {"rede": "Pública"}, "curso": None, "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto",
      "so_reducao": False}),
    ("Cursos de Enfermagem: quantos alunos novos entraram em Serra em 2022?",
     {"indicador": "ingressantes", "tipo": "valor", "anos": [2022], "locais": ["Serra"], "listar": None, "filtros": {},
      "curso": "Enfermagem", "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto", "so_reducao": False}),
    ("Quais 5 cursos perderam mais estudantes no Brasil entre 2017 e 2024?",
     {"indicador": "matriculas", "tipo": "crescimento", "anos": [2017, 2024], "locais": ["Brasil"], "listar": None,
      "filtros": {}, "curso": None, "quebras": ["curso"], "ordem": "asc", "top_n": 5, "criterio": "absoluto",
      "so_reducao": True}),
    ("Qual a previsão do tempo para amanhã?",
     {"indicador": None, "tipo": "valor", "anos": [], "locais": [], "listar": None, "filtros": {}, "curso": None,
      "quebras": [], "ordem": "desc", "top_n": 10, "criterio": "absoluto", "so_reducao": False}),
]


def _prompt(cat):
    inds = "\n".join(f"- {k}: {v['nome']} — {v['definicao']} Sinônimos: {', '.join(v.get('sinonimos', [])[:10])}."
                     for k, v in {**cat.indicadores, **cat.derivados}.items())
    inds += ("\n  (universitários, alunos, estudantes = matriculas; calouros, novos alunos = ingressantes; "
             "formandos, formados = concluintes; candidatos = inscritos)")
    return f"""Você converte perguntas em português sobre a educação superior brasileira (Sinopses do INEP, 2017–2024)
em um JSON de consulta. Você NÃO responde a pergunta, NÃO inventa números e NÃO escreve SQL.

Indicadores (use o identificador):
{inds}
Se a pergunta não for sobre esses indicadores, use "indicador": null.

Tipos: valor (um número/recorte), serie (evolução no tempo), comparacao (2+ locais ou categorias ao longo do tempo),
ranking (maiores/menores municípios, estados ou cursos), crescimento (quem mais cresceu/caiu entre dois anos),
participacao (fatia/percentual de um recorte no total), compatibilidade (perguntas sobre mudanças metodológicas).
Regras:
- anos: só anos citados (intervalo "de A a B" → [A, B]); sem ano → []. "últimos N anos" → [{2024 - 0} - N + 1, 2024].
- locais: NOMES como escritos (município, estado, região, "Brasil", "Grande Vitória"). "capixaba" = "Espírito Santo".
- listar: "municipios" quando pedir municípios/cidades de um estado (ponha o estado em locais); "ufs" para estados.
- filtros: só valores permitidos no esquema; duas categorias da mesma dimensão (ex.: presencial e EaD) → quebras.
- curso: nome do curso citado (ex.: "Direito") ou null. quebras ["curso"] quando pedir lista/ranking de cursos.
- ordem "asc" para menores/perdas; so_reducao true quando pedir quem perdeu/caiu; criterio "percentual" se pedir %.
- Não invente filtros nem quebras que a pergunta não pede. "cidades/municípios do ES onde mais..." → listar "municipios".
- Sinônimos de dimensões: particular = rede Privada; pública/gratuita = rede Pública; EaD/online = A Distância;
  mulheres = sexo Feminino; homens = sexo Masculino.
"""


def _chamar(texto, cat, modelo):
    msgs = [{"role": "system", "content": _prompt(cat)}]
    for p, r in EXEMPLOS:
        msgs += [{"role": "user", "content": p}, {"role": "assistant", "content": json.dumps(r, ensure_ascii=False)}]
    msgs.append({"role": "user", "content": texto})
    corpo = json.dumps({"model": modelo, "messages": msgs, "stream": False, "format": esquema_llm(cat),
                        "options": {"temperature": 0, "num_ctx": 4096, "seed": 7}}).encode("utf-8")
    req = urllib.request.Request(URL, data=corpo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TEMPO_MAXIMO_S) as resp:
        return json.loads(json.loads(resp.read().decode("utf-8"))["message"]["content"])


def disponivel(modelo=MODELO) -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as r:
            return any(m["name"].startswith(modelo) for m in json.loads(r.read())["models"])
    except Exception:
        return False


def _resolver_local(nome, cat):
    """Nome → (id_geo | None, aviso | None, erro | None). Mesmas regras do interpretador por regras."""
    n = normalizar(nome)
    n = n.removeprefix("regiao ").removeprefix("estado do ").removeprefix("estado de ").removeprefix("municipio de ")
    if n in cat.aliases:
        alvo = cat.aliases[n]
        return ("GRUPO:" + n if isinstance(alvo, dict) else alvo), None, None
    if n in ("brasil", "pais"):
        return "BR", None, None
    if n in cat.nomes_uf and not n.startswith("sigla:"):
        return cat.nomes_uf[n].id_geo, None, None
    sg = cat.nomes_uf.get("sigla:" + nome.strip().upper())
    if sg:
        return sg.id_geo, None, None
    cands = cat.nomes_municipio.get(n, [])
    if len(cands) == 1:
        return cands[0].id_geo, None, None
    if len(cands) > 1:
        es = [l for l in cands if l.co_uf == "32"]
        if es:
            return es[0].id_geo, f"'{es[0].nome}' existe em mais de uma UF: usei o do ES", None
        return None, None, f"Há mais de um município chamado '{nome}': " + ", ".join(f"{l.nome} ({l.sg_uf})" for l in cands)
    return None, None, f"local não reconhecido no cadastro do INEP: '{nome}'"


def _resolver_curso(nome, cat):
    n = normalizar(nome)
    if n in cat.nomes_curso:
        return cat.nomes_curso[n], None
    parecidos = sorted({ref for k, ref in cat.nomes_curso.items() if n in k})
    if len(parecidos) == 1:
        return parecidos[0], None
    return None, (f"curso '{nome}' não encontrado" if not parecidos else
                  f"curso '{nome}' é ambíguo: " + ", ".join(sorted(cat.nome_curso[p] for p in parecidos)[:6]))


def para_contrato(d: dict, cat, ano_min=2017, ano_max=2024) -> tuple[dict, list, list]:
    """JSON do modelo (com nomes) → JSON do contrato (com códigos). Devolve (contrato, supostos, esclarecer)."""
    supostos, esclarecer = ["interpretação feita pelo modelo de linguagem local e validada pelo catálogo"], []
    locais, lmu, ufs = [], None, False
    for nome in d.get("locais", []) or []:
        idg, aviso, erro = _resolver_local(nome, cat)
        if erro:
            esclarecer.append(erro)
        elif idg not in locais:
            locais.append(idg)
        if aviso:
            supostos.append(aviso)
    if d.get("listar") == "municipios":
        uf = next((cat.locais[i].co_uf for i in locais if i in cat.locais and cat.locais[i].nivel == "UF"), None)
        if uf:
            lmu = uf
        else:
            esclarecer.append("De qual estado são os municípios?")
    elif d.get("listar") == "ufs":
        ufs = True
        locais = [i for i in locais if i != "BR"]
    filtros = dict(d.get("filtros") or {})
    if d.get("curso"):
        ref, erro = _resolver_curso(d["curso"], cat)
        if erro:
            esclarecer.append(erro)
        else:
            filtros["curso"] = ref
    anos = sorted(set(a for a in (d.get("anos") or []) if isinstance(a, int)))
    fora = [a for a in anos if not ano_min <= a <= ano_max]
    if fora:
        esclarecer.append(f"Os dados cobrem {ano_min}–{ano_max}; não há dados para {', '.join(map(str, fora))}.")
        anos = [a for a in anos if a not in fora]
    tipo = d.get("tipo", "valor")
    if len(anos) == 2 and tipo in ("serie", "comparacao", "participacao") and anos[1] - anos[0] > 1:
        anos = list(range(anos[0], anos[1] + 1))
    if not anos:
        if tipo in ("serie", "comparacao", "crescimento"):
            anos = list(range(ano_min, ano_max + 1))
            supostos.append(f"período não informado: usei toda a série {ano_min}–{ano_max}")
        else:
            anos = [ano_max]
            supostos.append(f"ano não informado: usei o mais recente ({ano_max})")
    if tipo == "crescimento" and len(anos) < 2:
        anos = [max(ano_min, anos[0] - 5), anos[0]]
    if not locais and not ufs and not lmu:
        locais = ["BR"]
        supostos.append("local não informado: usei o Brasil")
    if d.get("indicador") is None and tipo != "compatibilidade":
        esclarecer.append("Não identifiquei um indicador disponível (matrículas, ingressantes, concluintes, cursos, "
                          "vagas, inscritos, IES, docentes, candidatos por vaga).")
    quebras = [q for q in (d.get("quebras") or []) if q in DIMS_QUEBRA]
    contrato = {"indicador": d.get("indicador"), "tipo": tipo, "anos": anos, "locais": locais,
                "listar_municipios_uf": lmu, "listar_ufs": ufs, "filtros": filtros, "quebras": quebras,
                "ordem": d.get("ordem", "desc"), "top_n": int(d.get("top_n") or 10),
                "criterio": d.get("criterio", "absoluto"), "so_reducao": bool(d.get("so_reducao")),
                "parte_dims": [], "supostos": supostos, "esclarecer": esclarecer}
    return contrato, supostos, esclarecer


def interpretar_llm(texto, cat, modelo=MODELO) -> tuple[Consulta | None, dict]:
    """Pergunta → (Consulta validada | None, meta). meta registra o JSON bruto, o tempo e os erros."""
    from .contrato import de_json
    t0 = time.time()
    meta = {"modelo": modelo, "bruto": None, "erros": [], "segundos": None}
    try:
        bruto = _chamar(texto, cat, modelo)
        meta["bruto"] = bruto
    except Exception as e:
        meta["erros"].append(f"modelo indisponível ou sem resposta válida: {type(e).__name__}: {e}")
        meta["segundos"] = round(time.time() - t0, 1)
        return None, meta
    contrato, _, esclarecer = para_contrato(bruto, cat)
    c, erros = de_json(contrato, cat, texto)
    meta["segundos"] = round(time.time() - t0, 1)
    meta["contrato"] = contrato
    meta["erros"] += erros
    if c is None:
        return None, meta
    return c, meta
