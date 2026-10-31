"""Configuração do motor de consultas (caminhos, tabelas autorizadas e limites)."""
from pathlib import Path

PROJETO = Path(__file__).resolve().parent.parent
BANCO = PROJETO / "dados" / "nucleo" / "ijsn.duckdb"
CATALOGO = Path(__file__).resolve().parent / "semantica" / "catalogo.yaml"
REGISTRO = PROJETO / "dados" / "consultas" / "registro_consultas.jsonl"
SAIDAS = PROJETO / "dados" / "consultas" / "saidas"

# Somente estas tabelas/visões podem aparecer em consultas do motor (somente leitura)
TABELAS_AUTORIZADAS = {
    "mart_anexos_geo", "mart_curso_geo", "mart_sinopse_geo",
    "dim_geografia", "dim_uf", "dim_curso_cine", "dim_indicador", "xw_cine",
    "qualidade_ocorrencias", "fato_sinopse", "fato_anexo_curso", "dim_recorte", "dim_recorte_sinopse",
}
LIMITE_LINHAS = 5000          # máximo de linhas devolvidas por consulta
TEMPO_MAXIMO_S = 60           # consulta interrompida após este tempo
MEMORIA_DUCKDB = "2GB"        # o PC tem 16 GB e o DuckDB divide a máquina com outros processos
