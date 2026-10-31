"""Teste ponta a ponta no servidor JÁ INICIADO por iniciar_interface.bat (http://127.0.0.1:8765), como o navegador faria.

Uso: python -I tests/e2e_usuario.py [porta]
Percorre o roteiro de demonstração (exemplos da página, perguntas livres, recusa honesta, modo IA), baixa gráfico e CSV
e grava dados/qualidade/e2e_usuario.md com os resultados efetivos (números, interpretação, fontes, tempo).
Não executa o JavaScript da página (isso exige um navegador): valida o HTML servido e as mesmas chamadas que ele faz.
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
URL = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else 8765}"   # porta opcional
SAIDA = Path(__file__).resolve().parent.parent / "dados" / "qualidade" / "e2e_usuario.md"

ROTEIRO = [
    ("Consulta simples (exemplo da página)", "Quantas matrículas havia em Vila Velha em 2024?", "regras"),
    ("Evolução entre anos", "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?", "regras"),
    ("Ranking de municípios (exemplo)", "Quais os 10 municípios capixabas com mais matrículas em 2024?", "regras"),
    ("Presencial × EaD (exemplo)", "Compare as matrículas presenciais e a distância no ES nos últimos 5 anos", "regras"),
    ("Análise por curso (livre)", "Matrículas em Direito em Vitória de 2017 a 2024", "regras"),
    ("Espírito Santo × Brasil (livre)", "Qual a participação do ES nas matrículas do Brasil entre 2017 e 2024?", "regras"),
    ("Participação com universo (exemplo)", "Qual a participação das mulheres nas matrículas da rede privada do ES em 2024?", "regras"),
    ("Cursos que mais cresceram (exemplo)", "Quais cursos mais cresceram em ingressantes no ES entre 2019 e 2024?", "regras"),
    ("Razão derivada (exemplo)", "Relação candidatos por vaga no ES em 2024", "regras"),
    ("Limitação reconhecida — tema fora do motor", "Quantos alunos com deficiência no ES?", "regras"),
    ("Limitação reconhecida — dado que o INEP não publica", "Quantas vagas a distância em Vitória?", "regras"),
    ("Pergunta ambígua — sem indicador", "Como está Vitória em 2024?", "regras"),
    ("Pergunta livre com IA local (experimental)", "Quero saber a quantidade de gente estudando na Serra em 2021", "hibrido"),
]


def get(caminho):
    with urllib.request.urlopen(URL + caminho, timeout=60) as r:
        return r.status, r.read(), dict(r.headers)


def post(pergunta, modo):
    req = urllib.request.Request(URL + "/api/perguntar", data=json.dumps({"pergunta": pergunta, "modo": modo}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=400) as r:
        return json.loads(r.read())


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def main():
    linhas = [f"# Teste ponta a ponta — {datetime.now():%d/%m/%Y %H:%M}", "",
              "Servidor iniciado por `iniciar_interface.bat`; chamadas iguais às da página. "
              "O JavaScript e a aparência visual NÃO foram verificados aqui (exigem navegador): teste manual.", ""]
    ok_total = True
    st, pag, h = get("/")
    pagina = pag.decode("utf-8")
    checagens = {
        "página responde 200": st == 200,
        "autoria Igor L. Millis visível": "Igor L. Millis" in pagina,
        "aviso de não ser produto oficial": "Não é produto oficial" in pagina,
        "fonte INEP identificada": "INEP" in pagina,
        "nenhuma menção a IJSN na página": "IJSN" not in pagina,
        "modo IA rotulado como experimental": "experimental" in pagina,
        "cabeçalho Content-Security-Policy": "Content-Security-Policy" in h,
    }
    st2, est, _ = get("/api/estado")
    estado = json.loads(est)
    checagens["IA local disponível (Ollama)"] = estado.get("llm_disponivel") is True
    linhas += ["## Página", ""] + [f"- {'OK' if v else 'FALHA'} — {k}" for k, v in checagens.items()] + \
              [f"- modelo: {estado.get('modelo')}", ""]
    ok_total &= all(checagens.values())
    print(checagens, estado)
    for titulo, pergunta, modo in ROTEIRO:
        t0 = time.time()
        d = post(pergunta, modo)
        seg = time.time() - t0
        corpo = texto(d.get("html", ""))
        principal = corpo[:400]
        graf = csv = "—"
        if d.get("grafico"):
            s, png, _ = get(d["grafico"])
            graf = f"PNG {len(png):,} bytes" if s == 200 and png[:4] == b"\x89PNG" else "FALHA"
        if d.get("csv"):
            s, c, hh = get(d["csv"])
            csv = (f"CSV {len(c):,} bytes, {c.decode('utf-8-sig').count(chr(10))} linhas"
                   if s == 200 and "attachment" in hh.get("Content-Disposition", "") else "FALHA")
        tem_fonte = "Fontes" in corpo or d.get("precisa_esclarecer")
        tem_lim = "Limitações" in corpo or d.get("precisa_esclarecer")
        ok = "erro" not in d and tem_fonte and tem_lim and "FALHA" not in (graf + csv)
        ok_total &= ok
        linhas += [f"## {titulo}", f"**Pergunta:** {pergunta}  ", f"**Modo:** {modo} · **interpretador:** "
                   f"{d.get('interpretador')} · **tempo:** {seg:.1f} s · **esclarecimento:** {d.get('precisa_esclarecer')}",
                   "", f"**Início da resposta:** {principal}", "",
                   f"**Como foi entendida:** {'; '.join(d.get('supostos', [])) or '(sem suposições)'}", "",
                   f"**Gráfico:** {graf} · **CSV:** {csv} · **Fontes:** {'sim' if tem_fonte else 'NÃO'} · "
                   f"**Limitações:** {'sim' if tem_lim else 'NÃO'} · **resultado do teste:** {'OK' if ok else 'FALHA'}", ""]
        print(f"[{'OK' if ok else 'FALHA'}] {seg:5.1f}s {modo:7s} {pergunta}\n      {principal[:200]}")
    linhas.append(f"**Resultado geral: {'OK' if ok_total else 'COM FALHAS'}**")
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print("resultado geral:", "OK" if ok_total else "COM FALHAS", "→", SAIDA)
    sys.exit(0 if ok_total else 1)


if __name__ == "__main__":
    main()
