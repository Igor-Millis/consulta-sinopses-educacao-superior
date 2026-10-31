# Acompanhamento do projeto IJSN — Sinopses da Educação Superior 2017–2024

Documento central: o que existe, o que foi testado, problemas, decisões e próximo passo. Atualizado em **30/10/2026, 23:00**.
Situações usadas: **validado** (executado e testado, resultado registrado) · **implementado** (executado, teste parcial) · **pendente**. Não uso percentuais de conclusão.

## 1. Etapas

| Etapa | Situação | Evidência |
|---|---|---|
| Diagnóstico das 8 Sinopses (ZIPs intactos, MD5) | validado | `_diagnostico_estrutura/01–07` |
| Arquitetura de dados | validado | `_arquitetura/01_arquitetura_dados.md` |
| P0 staging (662 abas → Parquet) | validado | `p0_validar` |
| P1/P2 Anexos no núcleo; Anexo I removido (= II + III) | validado | `p1_validar`, `p2_validar`, `dados/qualidade/` |
| P3 Sinopse por município (126,8 milhões de valores) | validado com ressalvas (Q09/Q10) | revalidação final de 30/10, 22:37: `dados/qualidade/p3_validar_log.txt` |
| P4 crosswalks (Cine, deficiência, reserva de vagas) | validado | `p4_crosswalks.py` |
| P5 visões do ES | validado | ES 5.1 = Σ municípios dos Anexos, todos os anos |
| Ocorrências de qualidade Q01–Q10 | validado (Q02/Q03/Q10 confirmadas no XML original) | `config/qualidade_ocorrencias.csv`, sincronizada no banco às 22:41 |
| P6 marts (camada de consulta) | validado | `dados/qualidade/p6_validacao.txt`: 11 testes OK |
| Camada semântica (catálogo) | implementado e testado pelo motor | `motor/semantica/catalogo.yaml` |
| Motor de consultas | validado (1ª versão) | 61 testes pytest OK: `dados/qualidade/pytest_resultado.txt` |
| Documentação | implementado | este arquivo, `README.md`, `motor/README.md`, `_arquitetura/02_decisoes.md`, `pipeline/README.md` |
| Interface (Streamlit local) | pendente (D09: só após o uso do motor) | — |
| Marcação célula a célula da Q10 | pendente | — |

## 2. Testes executados (30/10/2026)

| Conjunto | Resultado |
|---|---|
| P3 revalidação (5,3 min) | T1 OK · T2 exclusivas 35.932/39,07 milhões (0,092%, Q09/Q10) · T2 não exclusivas OK · T3 178/2,32 milhões (regiões + Exterior → Brasil em 7.4, 5.14, 6.14; 27 em 5.8 municípios → UF, 2024) · T5 120/120 · T6 16/16 |
| P6 marts (6 s) | V1–V4 (Anexos e cursos × fatos) 0 falhas · V5 Sinopse Σ categorias = total publicado: 0 falhas fora da Q10; 108 UF×ano em 6.6 (2017–2019, 2023) = Q10 · V6 Sinopse por sexo = Anexos, 648/648 · V7 IES, Σ dependências = total, 6.000/6.000 |
| pytest (10 s) | 61 aprovados: segurança 24, interpretador 17, análise 5, referências independentes 15 |

## 3. Problemas conhecidos

| Id | Problema | Situação |
|---|---|---|
| Q01 | 4.1/2023: IFMT sem a correção da Nota 02/2023 | documentado; o motor usa os Anexos (corretos) |
| Q02/Q03 | IFMT: inscritos = vagas (2018–2022); ingressantes ≈ 0 (2021–2022) | confirmado no XML; marcado como `suspeito`; sem correção possível |
| Q04 | 2022: falta a linha Distância de um curso Cine | documentado; sem imputação |
| Q05/Q06 | colunas sem rótulo (6.5 de 2017–2018; 3.2/4.4 de 2020) | preservadas só no staging |
| Q09 | 3.1: pares de colunas trocados em 2017–2019, 2021 e 2023 | marcado como `suspeito` |
| Q10 | 6.3/6.6: células inconsistentes em 2017–2019 e 2023 | confirmado no XML; **não marcado célula a célula**; o motor avisa por tabela × ano |
| T3 | 178 diferenças regiões/Exterior → Brasil, concentradas em 2023–2024 (7.4, 5.14, 6.14, 5.8) | a investigar; não afeta os marts (que somam municípios) |
| Motor | interpretador por regras: cobre os padrões documentados; fora deles, pede esclarecimento | limitação de projeto (D05) |

## 4. Decisões
Ver `_arquitetura/02_decisoes.md` (D01–D09). Principais desta etapa:
- **D04:** o motor consulta marts validados, nunca os fatos brutos;
- **D05:** interpretador determinístico (sem GPU; RAM limitada); um modelo de linguagem futuro deve produzir a mesma estrutura `Consulta`;
- **D06:** segurança em camadas;
- **D07:** ausência ≠ zero.

## 5. Relatório de auditoria (30/10/2026)

**Implementado e validado:** pipeline P0–P6 reconstruível a partir dos ZIPs (ordem em `pipeline/README.md`); motor com 61 testes; ocorrências sincronizadas.

**Parcial:**
- Q10 marcada só por tabela × ano;
- catálogo semântico cobre 8 indicadores e 11 dimensões (as tabelas de deficiência, reserva de vagas, financiamento e docentes por formação/regime estão no núcleo, mas ainda não no motor).

**Problemas e riscos encontrados:**
1. **Permissões amplas:** `.claude/settings.local.json` libera PowerShell, Bash, Edit, Write e Read sem confirmação e não expira. **Recomendação:** depois desta fase, trocar `"PowerShell"`/`"Bash"` por regras específicas (por exemplo, `PowerShell(& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -I *)`, `Bash(git status*)`) e restringir `Edit`/`Write` a `Edit(pipeline/**)`, `Edit(motor/**)`, `Edit(tests/**)`, `Edit(*.md)`. Também há uma regra residual com o caminho de um scratchpad antigo, que pode ser apagada. Só altero isso quando você pedir.
2. **Memória:** duas quedas por falta de RAM (P3 e recarga da Sinopse). Mitigação: 3 GB/4 threads nas cargas e 2 GB no motor; executar uma carga pesada de cada vez.
3. **Disco:** banco de 5,05 GB, mais 3,81 GB de cópias XLSX em `%TEMP%\ijsn_pipeline\xlsx` (reconstruíveis a partir dos ZIPs; só são necessárias para recarregar). 20,0 GB livres. Apagar as cópias depende da sua autorização.
4. **Sem backup do banco:** a reconstrução completa leva cerca de 3 h a partir dos ZIPs. Uma cópia de 5 GB ocupa espaço (regra 9). Sugestão: exportar só os marts e as tabelas de configuração em Parquet (< 0,2 GB) como cópia leve.
5. **Scripts de investigação acumulados:** 13 arquivos `pipeline/investigar_*.py`. São evidência de decisões (citados nas ocorrências), por isso ficam; sugiro movê-los para `pipeline/investigacoes/` quando você autorizar.
6. **`v_anexo_i` lenta** (agrega 610 milhões de valores): não usar em consultas interativas.
7. **Testes automáticos** começaram nesta etapa: o pipeline P0–P6 é validado por scripts próprios (`p*_validar.py`), não por pytest.
8. **Git:** criado nesta etapa. `dados/` e os ZIPs ficam fora do versionamento (de propósito).

**Dependências:** Python 3.12, duckdb, pandas, pyarrow, lxml, openpyxl, python-calamine, pyyaml, matplotlib, pytest (todos gratuitos e locais). Nenhum serviço externo.

## 6. Próximo passo
1. Você usa o motor com as suas perguntas reais (`perguntar.py`). Cada pergunta mal entendida vira um caso de teste e um ajuste no catálogo.
2. Marcar a Q10 célula a célula (regra objetiva: célula > total da linha) e investigar as 178 diferenças da T3.
3. Ampliar o catálogo: deficiência, reserva de vagas e financiamento (já com crosswalks da P4).
4. Interface Streamlit local sobre `motor.perguntar` (D09).
5. Restringir as permissões (item 1 da auditoria), quando você autorizar.
