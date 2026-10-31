"""Diagnóstico (somente leitura) do ambiente para um modelo de linguagem local: RAM, CPU, executáveis e bibliotecas
disponíveis, modelos já baixados. Não instala nem baixa nada."""
import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
print("Python", sys.version.split()[0], platform.platform())
print("CPU lógicos:", os.cpu_count())
for exe in ["ollama", "llama-server", "llama-cli", "winget", "nvidia-smi"]:
    print(f"{exe}: {shutil.which(exe) or '—'}")
for lib in ["llama_cpp", "ctransformers", "transformers", "torch", "onnxruntime", "jsonschema", "streamlit"]:
    print(f"{lib}: {'instalado' if importlib.util.find_spec(lib) else '—'}")
home = Path.home()
for pasta in [home / ".ollama" / "models", home / "models", Path(os.environ.get("LOCALAPPDATA", "")) / "llama.cpp",
              home / ".cache" / "huggingface"]:
    if pasta.exists():
        gg = list(pasta.rglob("*.gguf"))[:10]
        print(f"{pasta}: existe; gguf: {[g.name for g in gg]}")
    else:
        print(f"{pasta}: —")
try:
    out = subprocess.run(["pip", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    print("pip:", out or "—")
except Exception as e:
    print("pip: erro", e)
