# Pipeline — Sinopses da Educação Superior (INEP)

Implementação das fases P0 e P1 descritas em `_arquitetura/01_arquitetura_dados.md`.
Requisitos: Python 3.12 com as bibliotecas de [`requirements.txt`](../requirements.txt).
Os 8 ZIPs (`sinopse_educacao_superior_<ano>.zip`, 2017–2024) devem estar na raiz do projeto; endereços e MD5 em `config/manifesto_fontes.csv`.
Com a lista `config/q10_celulas_suspeitas.csv` e a regra da tabela 7.4 já no `carregar_sinopse.py`, uma reconstrução do zero aplica as marcações Q10/Q13 automaticamente.
Os ZIPs originais nunca são alterados. As cópias dos XLSX ficam em `%TEMP%\ijsn_pipeline\xlsx` (fora do projeto).

## Ordem de execução

| Fase | Script | O que faz | Saída |
|---|---|---|---|
| P0 | `p0_staging.py [n_proc]` | Manifesto das fontes (MD5) e cópia fiel de cada aba em Parquet (texto bruto, linha de origem) | `config/manifesto_fontes.csv`, `dados/staging/<ano>/<arquivo>/<aba>.parquet`, `dados/staging/_catalogo_staging.csv` |
| P0 | `p0_validar.py` | Confere o staging contra o diagnóstico (células por coluna) | `dados/qualidade/p0_validacao.csv` |
| P1 | `p1_mapear_anexos.py` | Gera o mapeamento coluna → indicador/recorte dos Anexos a partir do catálogo 03 | `config/xw_colunas_anexos.csv` |
| P1/P2 | `carregar_anexos.py [anexo_i anexo_ii anexo_iii]` | Carrega os Anexos (2017–2024) no núcleo; sem argumentos, carrega os três (cerca de 110 min) | `dados/nucleo/ijsn.duckdb` |
| P1 | `p1_validar.py` | Testes do Anexo II: T1, T2, T3, T5 (× Sinopse 7.2) e T6 | `dados/qualidade/p1_*.csv/txt` |
| P2 | `p2_validar.py` | Testes dos Anexos I e III: T1–T6, inclusive I = II + III e × Sinopse 7.3 | `dados/qualidade/p2_*.csv/txt` |
| P2 | `investigar_t3.py` | Diagnóstico das falhas do T3 (origem da ocorrência Q04) | tela |
| — | `remover_anexo_i.py` | Valida `v_anexo_i` (II + III) contra o Anexo I e o remove do núcleo | banco recriado |
| P3 | `p3_mapear_sinopse.py` | Mapeia as colunas da Sinopse por vocabulário (+ `config/xw_override_sinopse.csv`) | `config/xw_colunas_sinopse.csv`, `config/vocabulario_sinopse.csv` |
| P3 | `carregar_sinopse.py` | Carrega a Sinopse por município no núcleo (~8 min) | `fato_sinopse` e dimensões |
| P3 | `p3_validar.py` | Testes T1, T2, T3, T5 e T6 da Sinopse (modo leve: 3 GB, ~20 min) | `dados/qualidade/p3_*` |
| P3 | `investigar_*.py` | Investigações pontuais (linhas não classificadas, UF duplicada, colunas sem rótulo, T2/T3, Q09) | tela |
| P3 | `detectar_colunas_trocadas.py` | Detecta pares de colunas com valores trocados na publicação (Q09); rodar antes de `carregar_sinopse.py` | `config/q09_colunas_trocadas.csv` |
| P4 | `p4_crosswalks.py` | Correspondências entre anos: Cine, deficiência, reserva de vagas | `config/xw_*.csv`, tabelas `xw_*`, visões comparáveis |
| P5 | `p5_visoes_es.py` | Visões do Espírito Santo (municípios × curso; municípios × indicador; ES × UFs × Brasil) | visões `v_es_*`, `v_comparativo_uf`; `dados/analitico/*.csv` |
| P6 | `p6_marts.py [mart ...]` | Camada de consulta do motor (sem argumentos: os três marts; cerca de 1 min) | `mart_anexos_geo`, `mart_curso_geo`, `mart_sinopse_geo` |
| P6 | `p6_validar.py` | Marts × fatos por caminhos independentes (11 testes) | `dados/qualidade/p6_validacao.txt` |
| — | `backup_leve.py [--validar DIR]` | Backup leve em Parquet (todas as tabelas exceto os 2 fatos), com manifesto e validação de conteúdo e de reconstrução | `dados/backup/AAAAMMDD_HHMMSS/` |
| — | `investigar_t3.py` | Detalha as diferenças da T3 (explicadas em Q11–Q13) | `dados/qualidade/t3_falhas_detalhe.csv` |
| — | `sincronizar_qualidade.py` | Copia `config/qualidade_ocorrencias.csv` para a tabela `qualidade_ocorrencias` (só ela) | tabela `qualidade_ocorrencias` |
| — | `qualidade_confirmar_fonte.py` | Confere Q02/Q03/Q10 no XML original das planilhas | `dados/qualidade/confirmacao_fonte_Q02_Q03_Q10.csv` |
| — | `estado_banco.py` | Resumo do estado do núcleo (somente leitura) | tela |
| Q10 | `q10_detectar.py` | Identifica célula a célula as inconsistências de 6.3/6.6 (regra T2 de `regras_t2.py`) | `config/q10_celulas_suspeitas.csv` (lido por `carregar_sinopse.py`) |
| Q10/Q13 | `aplicar_q10_q13.py --comparar/--aplicar/--reverter` | Aplica as marcações num banco já carregado, sem recarga, com backup e verificação | status no `fato_sinopse` |
| — | `compactar_banco.py --copiar/--validar/--trocar/--reverter` | Compacta o banco por cópia nova e validada | `dados/nucleo/ijsn.duckdb` |
| — | `verificar_pos_limpeza.py` | Confere banco, ZIPs (MD5) e disco | `dados/qualidade/verificacao_pos_limpeza.txt` |

**Ordem completa para reconstruir do zero:** `p0_staging` → `p0_validar` → `p1_mapear_anexos` → `carregar_anexos` → `p1_validar`/`p2_validar` → `p3_mapear_sinopse` → `carregar_sinopse` → `detectar_colunas_trocadas` → `carregar_sinopse` (de novo, para marcar a Q09) → `p3_validar` → `p4_crosswalks` → `p5_visoes_es` → `p6_marts` → `p6_validar` → testes do motor (`python -I -m pytest -p no:cacheprovider tests`).

Comando: `python -I pipeline\<script>.py` a partir da pasta do projeto.

## Configuração curada (`config/`)

- `manifesto_fontes.csv`: versão de cada ZIP (MD5, URL do Inep).
- `ufs.csv`: código IBGE, sigla, nome e região das 27 UFs.
- `xw_colunas_anexos.csv`: cada coluna de medida dos Anexos → indicador e recorte (gerado; revisável).
- `qualidade_ocorrencias.csv`: problemas conhecidos (Q01–Q03) e a regra aplicada.

## Núcleo (`dados/nucleo/ijsn.duckdb`)

| Tabela | Conteúdo |
|---|---|
| `fato_anexo_curso` | Um valor por ano × anexo × geografia × curso Cine × indicador × recorte, com `status_valor`, `valor_bruto` (só quando o valor é nulo) e origem em `aba`, `linha`, `coluna` |
| `v_fato_anexo_curso` | Visão do fato com a coluna `origem` reconstruída (por exemplo, `8.2!CA1453`) |
| `dim_status_valor` | Significado de cada status (informado, suspeito, somente_presencial, nao_desagregado, nao_aplicavel, celula_vazia…) e se ele tem valor |
| `dim_geografia`, `dim_geografia_nomes` | Brasil, municípios (código IBGE, UF, região) e as pseudo-regiões `DIST` (Distância) e `EXT` (Exterior); nomes por ano como na planilha |
| `dim_curso_cine` | Código Cine sem aspas, nome e original, por ano (`_TOTAL` = todos os cursos) |
| `dim_recorte` | Organização acadêmica × grau × dependência × categoria privada |
| `dim_indicador`, `dim_uf`, `dim_fonte` | Indicadores, UFs e versões das fontes |
| `qualidade_ocorrencias`, `linhas_nao_classificadas`, `stg_linhas_anexo`, `carga_log` | Qualidade e auditoria |

**Atenção ao consultar:** filtrar `eh_agregado = false`, ou escolher um único recorte, antes de somar. As linhas `nivel_geo = 'Brasil'` e `co_cine = '_TOTAL'` são totais publicados e não devem ser somadas com as linhas de detalhe.
