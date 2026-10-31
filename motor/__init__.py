"""Motor de consultas em linguagem natural sobre as Sinopses da Educação Superior (INEP).

Camadas (separadas e substituíveis):
  semantica    — catálogo de indicadores, dimensões, sinônimos e compatibilidade (YAML + banco)
  interpretador — pergunta em português → Consulta (estrutura) — determinístico; um modelo de linguagem pode
                  substituí-lo implementando a mesma interface (interpretar(texto) -> Consulta)
  consultas    — Consulta → SQL parametrizado sobre a camada de consulta (marts)
  seguranca    — validação do SQL (só leitura, tabelas autorizadas) e execução com limites
  analise      — cálculos estatísticos em código (nunca pelo modelo de linguagem)
  resposta     — resposta em português: valor, tabela, gráfico, interpretação, fontes e limitações
"""
from .api import perguntar  # noqa: F401
