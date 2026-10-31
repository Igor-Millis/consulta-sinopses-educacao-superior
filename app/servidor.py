"""Interface web LOCAL da Consulta às Sinopses da Educação Superior — Igor L. Millis - Projeto Independente com Dados Públicos.
Só biblioteca padrão do Python; escuta apenas em 127.0.0.1).

Uso: python -I app/servidor.py [porta]      (padrão 8765; abre o navegador)   — ou duplo clique em iniciar_interface.bat
Rotas: GET /  (página) · POST /api/perguntar {"pergunta", "modo"} · GET /api/estado · GET /arquivo/<nome> (PNG/CSV
das respostas, só da pasta de saídas). Uma pergunta por vez (o banco é aberto uma vez, somente leitura).
"""
import json
import re
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from markdown_simples import para_html  # noqa: E402
from motor.api import perguntar  # noqa: E402
from motor.config import SAIDAS  # noqa: E402

HOST = "127.0.0.1"
TRAVA = threading.Lock()
PAGINA = (Path(__file__).resolve().parent / "pagina.html").read_text(encoding="utf-8")
NOME_SEGURO = re.compile(r"^[\w.-]+\.(png|csv)$")
LINHA_ARQUIVO = re.compile(r"(?m)^(Gráfico|Tabela \(CSV\)): `.*`$")


def responder_json(pergunta: str, modo: str) -> dict:
    pergunta = (pergunta or "").strip()[:500]
    if not pergunta:
        return {"erro": "Escreva uma pergunta."}
    if modo not in ("regras", "hibrido"):
        modo = "regras"
    with TRAVA:
        r = perguntar(pergunta, modo=modo)
    texto = LINHA_ARQUIVO.sub("", r.texto)
    c = r.consulta
    return {
        "pergunta": pergunta,
        "html": para_html(texto),
        "precisa_esclarecer": r.precisa_esclarecer,
        "interpretador": r.interpretador,
        "supostos": list(getattr(c, "supostos", []) or []),
        "grafico": f"/arquivo/{r.grafico.name}" if r.grafico else None,
        "csv": f"/arquivo/{r.csv.name}" if r.csv else None,
    }


def estado() -> dict:
    from motor.llm import MODELO, disponivel
    return {"llm_disponivel": disponivel(), "modelo": MODELO}


class Handler(BaseHTTPRequestHandler):
    server_version = "ConsultaSinopses"

    def log_message(self, fmt, *args):   # sem log de acesso no console (as perguntas já vão para o registro do motor)
        pass

    def _enviar(self, codigo, corpo: bytes, tipo: str, extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                                                    "script-src 'self' 'unsafe-inline'; img-src 'self'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, codigo, obj):
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        if self.path.split("?", 1)[0] in ("/", "/index.html"):   # a página aceita ?q=... (lido pelo JavaScript)
            return self._enviar(200, PAGINA.encode("utf-8"), "text/html; charset=utf-8")
        if self.path == "/api/estado":
            return self._json(200, estado())
        if self.path.startswith("/arquivo/"):
            nome = self.path[len("/arquivo/"):]
            arq = (SAIDAS / nome).resolve()
            if not NOME_SEGURO.match(nome) or arq.parent != SAIDAS.resolve() or not arq.is_file():
                return self._json(404, {"erro": "arquivo não encontrado"})
            tipo = "image/png" if nome.endswith(".png") else "text/csv; charset=utf-8"
            extra = {"Content-Disposition": f'attachment; filename="{nome}"'} if nome.endswith(".csv") else None
            return self._enviar(200, arq.read_bytes(), tipo, extra)
        return self._json(404, {"erro": "não encontrado"})

    def do_POST(self):
        if self.path != "/api/perguntar":
            return self._json(404, {"erro": "não encontrado"})
        try:
            n = min(int(self.headers.get("Content-Length", 0)), 10_000)
            dados = json.loads(self.rfile.read(n) or b"{}")
            return self._json(200, responder_json(dados.get("pergunta", ""), dados.get("modo", "regras")))
        except Exception as e:   # erro vira mensagem; nada do sistema é exposto além do tipo do erro
            return self._json(500, {"erro": f"Não foi possível processar a pergunta ({type(e).__name__})."})


class ServidorExclusivo(ThreadingHTTPServer):
    """No Windows, SO_REUSEADDR (padrão do http.server) deixa DOIS processos escutarem a mesma porta: uma versão antiga
    aberta continuaria respondendo e outro programa local poderia sequestrar a porta. Aqui a porta é exclusiva."""
    allow_reuse_address = False

    def server_bind(self):
        import socket
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def criar_servidor(porta=8765):
    return ServidorExclusivo((HOST, porta), Handler)


def ja_aberta(porta) -> bool:
    """True se a porta já tem ESTA aplicação respondendo (ex.: o .bat foi aberto duas vezes)."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://{HOST}:{porta}/api/estado", timeout=3) as r:
            return r.status == 200 and "llm_disponivel" in r.read().decode("utf-8", "replace")
    except Exception:
        return False


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    url = f"http://{HOST}:{porta}/"
    try:
        srv = criar_servidor(porta)
    except OSError:
        if ja_aberta(porta):
            print(f"A Consulta já está aberta em {url} (outra janela preta). Abrindo o navegador nela.\n"
                  "Se a página parecer desatualizada, feche a outra janela preta e abra esta de novo.")
            webbrowser.open(url)
        else:
            print(f"A porta {porta} está ocupada por outro programa. Feche-o ou rode: "
                  f"python -I app\\servidor.py 8766")
        sys.exit(1)
    print(f"Consulta às Sinopses da Educação Superior · Igor L. Millis - Projeto Independente com Dados Públicos — em {url} (só neste computador). Feche esta janela para encerrar.")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    srv.serve_forever()
