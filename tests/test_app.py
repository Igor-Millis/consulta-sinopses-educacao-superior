"""Interface web local (app/servidor.py): página, perguntas, arquivos e segurança."""
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from markdown_simples import para_html  # noqa: E402
import servidor  # noqa: E402


@pytest.fixture(scope="module")
def url(cat):
    srv = servidor.criar_servidor(0)                # porta livre escolhida pelo sistema
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _get(u):
    try:
        with urllib.request.urlopen(u, timeout=60) as r:
            return r.status, r.read(), r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers


def _post(u, obj):
    req = urllib.request.Request(u, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def test_so_escuta_localhost():
    srv = servidor.criar_servidor(0)
    try:
        assert srv.server_address[0] == "127.0.0.1"
    finally:
        srv.server_close()


def test_porta_exclusiva_segunda_instancia_falha():
    """Defeito de 31/10/2026: no Windows duas instâncias escutavam a mesma porta (a antiga seguia respondendo)."""
    a = servidor.criar_servidor(0)
    try:
        with pytest.raises(OSError):
            servidor.criar_servidor(a.server_address[1])
    finally:
        a.server_close()


def test_pagina(url):
    st, corpo, h = _get(url + "/")
    assert st == 200 and "Consulta às Sinopses" in corpo.decode() and "Content-Security-Policy" in h


def test_pagina_com_parametro_q(url):
    """?q=... abre a mesma página (o JavaScript lê a pergunta); antes do ajuste de 31/10/2026 dava 404."""
    st, corpo, _ = _get(url + "/?q=Quantas%20matr%C3%ADculas%20em%20Vit%C3%B3ria")
    assert st == 200 and "Consulta às Sinopses" in corpo.decode()


def test_pergunta_com_numero_correto_e_arquivos(url):
    d = _post(url + "/api/perguntar", {"pergunta": "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?"})
    assert "182.335" in d["html"] and not d["precisa_esclarecer"] and d["interpretador"] == "regras"
    st, png, h = _get(url + d["grafico"])
    assert st == 200 and png[:4] == b"\x89PNG"
    st, csv, h = _get(url + d["csv"])
    assert st == 200 and "attachment" in h["Content-Disposition"]


def test_esclarecimento(url):
    d = _post(url + "/api/perguntar", {"pergunta": "Quantos alunos com deficiência no ES?"})
    assert d["precisa_esclarecer"] and "deficiência" in d["html"]


def test_pergunta_vazia(url):
    assert "erro" in _post(url + "/api/perguntar", {"pergunta": "   "})


@pytest.mark.parametrize("caminho", ["/arquivo/../nucleo/ijsn.duckdb", "/arquivo/..%2F..%2Fnucleo%2Fijsn.duckdb",
                                     "/arquivo/ijsn.duckdb", "/arquivo/x.png", "/arquivo/../../perguntar.py"])
def test_arquivo_nao_sai_da_pasta_de_saidas(url, caminho):
    st, _, _ = _get(url + caminho)
    assert st == 404


def test_html_escapado(url):
    d = _post(url + "/api/perguntar", {"pergunta": "<script>alert(1)</script> matrículas em Vitória em 2024"})
    assert "<script>" not in d["html"]


def test_markdown_escapa_e_formata():
    h = para_html("**Total**: <b>x</b>\n\n| a | b |\n|---|---|\n| 1.234 | <i>y</i> |\n- item `c`")
    assert "<strong>Total</strong>" in h and "&lt;b&gt;" in h and "<td class=num>1.234</td>" in h
    assert "&lt;i&gt;" in h and "<li>item <code>c</code></li>" in h
