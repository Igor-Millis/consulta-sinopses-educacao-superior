# Acompanhamento do projeto IJSN — Sinopses da Educação Superior 2017–2024

Documento central: o que existe, o que foi testado, problemas, decisões e próximo passo. Atualizado em **30/10/2026, 23:45**.
Situações usadas: **validado** (executado e testado, resultado registrado) · **implementado** (executado, teste parcial) · **pendente**. Não uso percentuais de conclusão.

## 1. Etapas

| Etapa | Situação | Evidência |
|---|---|---|
| Diagnóstico das 8 Sinopses (ZIPs intactos, MD5) | validado | `_diagnostico_estrutura/01–07` |
| Arquitetura de dados e decisões | validado | `_arquitetura/01`, `02_decisoes.md` (D01–D13), `03_proposta_llm.md` |
| P0 staging · P1/P2 Anexos (Anexo I = II + III, removido) | validado | `p0/p1/p2_validar` |
| P3 Sinopse por município (126,8 milhões de valores) | validado com ressalvas (Q09/Q10) | `dados/qualidade/p3_validar_log.txt` (30/10, 22:37) |
| P4 crosswalks · P5 visões do ES | validado | — |
| T3 (178 diferenças geográficas) | **explicada** (30/10, 23:36): 0 erros de carga | Q11–Q13; `dados/qualidade/t3_falhas_detalhe.csv` |
| Ocorrências de qualidade Q01–Q13 | validado | `config/qualidade_ocorrencias.csv`, sincronizada no banco |
| P6 marts | validado (13 testes) | `dados/qualidade/p6_validacao.txt` |
| Backup leve em Parquet | **validado** | `dados/backup/20261030_233404/` (manifesto + validação) |
| Motor de consultas | validado | 216 testes pytest; bateria de 61 perguntas |
| Contrato JSON para LLM | validado (implementado e testado) | `motor/contrato.py`, `tests/test_contrato.py` |
| LLM local | pendente (proposta pronta) | `_arquitetura/03_proposta_llm.md` |
| Interface (Streamlit local) | pendente (D09) | — |
| Marcação célula a célula da Q10; regra `somente_presencial` na 7.4 (Q13) | pendente | — |

## 2. Registro da operação autônoma de 30/10/2026 (23:14 → 23:45)

| Hora | Ação | Resultado |
|---|---|---|
| 23:14 | Auditoria inicial | `main` em `e48022b`, sem alterações pendentes; 61/61 testes OK; nenhum processo Python ativo |
| 23:15 | Backup leve, 1ª tentativa | Validação **INVÁLIDA** (esquema): HUGEINT dos marts virou DOUBLE no Parquet. A pasta `20261030_231538` foi mantida com `validacao.txt` = INVÁLIDO (uma pasta anterior, incompleta por erro de sintaxe, foi apagada por mim segundos depois de criada) |
| 23:17 | Correção na origem | Marts com `valor` BIGINT; o backup recusa HUGEINT; marts refeitos; P6 11/11; testes 61/61 |
| 23:18 | Backup | **VÁLIDO** `20261030_231810` (34,3 MB) |
| 23:19 | Bateria "antes" (61 perguntas) | 54 respondidas, 7 esclarecimentos, 0 erros. A leitura das respostas achou **12 problemas** (§4) |
| 23:20–23:23 | Correções R01–R09 + 17 testes de regressão | 78 testes OK; bateria "depois": todos os 12 casos certos |
| 23:24–23:33 | `mart_sinopse_geo` com folhas (sexo/cor/faixa × rede/dependência/org.) | 2,74 milhões de linhas; V8 e V9 novos OK; 80 testes |
| 23:34 | Backup | **VÁLIDO** `20261030_233404` (47,4 MB) |
| 23:35–23:36 | Investigação da T3 | 178/178 explicadas; Q11–Q13 registradas e sincronizadas |
| 23:37–23:38 | Contrato JSON + gabarito de 61 interpretações | 216 testes OK |
| 23:39–23:45 | Proposta de LLM, decisões D10–D13, documentação, bateria final | bateria final: 51 respondidas, 10 esclarecimentos, 0 erros |

Commits: `8bee2be` (backup), `423c495` (correções), `447ce12` (folhas), `1151aaa` (contrato), mais o commit final de documentação.

## 3. Testes executados

| Conjunto | Resultado |
|---|---|
| pytest (42 s) | **216 aprovados**, 1 pulado (`test_backup`, que só roda via `backup_leve.py`): segurança 24 · interpretador 17 · análise 5 · referências independentes 15 · regressão 19 · contrato e gabarito 136 |
| P6 marts (`p6_validar.py`) | 13 testes OK (V1–V9, V7b; V5b = Q10 documentada) |
| Backup (`backup_leve.py --validar`) | 23 tabelas: contagem, esquema, conteúdo (hash das linhas), sha256 OK; motor sobre banco reconstruído = banco principal (8 perguntas) |
| Bateria (`tests/bateria_perguntas.py`) | 61 perguntas em 7 grupos. Antes: 12 respostas erradas ou incompletas. Final: 51 respondidas, 10 esclarecimentos legítimos, 0 erros; 0,30 s em média, 0,9 s no máximo. Detalhes em `dados/qualidade/bateria_{antes,depois,final}.md` |
| P3 (revalidação de 22:37) | T1 OK · T2 0,092% (Q09/Q10) · T3 178/2,32 milhões (todas explicadas) · T5 120/120 · T6 16/16 |

## 4. Problemas encontrados pela bateria e corrigidos (regressão em `tests/test_regressao.py`)

| # | Pergunta (exemplo) | Erro | Correção |
|---|---|---|---|
| R01 | "alunos com deficiência", "FIES", "reserva de vagas" | Respondia o total de matrículas; "reserva" virava o município Reserva/PR | Temas indisponíveis no catálogo → explicação de onde o dado está no núcleo |
| R02 | "Relação candidatos por vaga" | Respondia só os inscritos | Indicadores derivados: Σ inscritos ÷ Σ vagas (D11) |
| R03 | "participação de cada município no total estadual" | "estadual" virava filtro de dependência | "total estadual/nacional" não é dimensão; "cada" lista todos |
| R04 | "municípios que apresentaram redução", "cursos que mais perderam" | Listava os maiores | Ranking de variação, crescente, só negativos |
| R05 | "quais municípios possuem maior participação" | Calculava ES ÷ Brasil | Ranking com coluna de participação |
| R06 | "por sexo e cor/raça" | Ignorava a cor/raça em silêncio | Lê várias quebras; a Sinopse não cruza as duas → esclarecimento |
| R07 | "comparadas com 2017" | Só 2017 | De 2017 até o último ano |
| R08 | "em qual ano houve a maior redução" | Sem variação ano a ano | Maior alta e maior queda anuais em toda série |
| R09 | Texto todo em maiúsculas | "SE" podia virar Sergipe | Siglas ambíguas ignoradas em texto em caixa alta |
| R10 | "participação das mulheres na rede privada" | Denominador = total geral | 1º filtro após "participação" = parte; demais = universo |
| — | "mulheres na rede pública" | Esclarecimento (faltava dado no mart) | Mart com folhas (D13) |

## 5. Problemas conhecidos (abertos)

| Id | Problema | Situação |
|---|---|---|
| Q01–Q03 | IFMT (4.1/2023; inscritos = vagas; ingressantes ≈ 0) | confirmados no XML; Q02/Q03 marcados como `suspeito`; sem correção possível |
| Q04–Q09 | ver `config/qualidade_ocorrencias.csv` | documentados ou marcados |
| Q10 | 6.3/6.6: células inconsistentes (2017–2019, 2023) | confirmada no XML; o motor avisa por tabela × ano; **marcação célula a célula pendente** |
| Q11 | 5.8/2024: Masculino × Superdotação = 0 nas UFs/Brasil | publicação INEP; não usado pelo motor |
| Q12 | 5.14/6.14/2024: Universidade Municipal só no Brasil | publicação INEP; não usado pelo motor |
| Q13 | 7.4 (2023–2024): regiões só presencial, sem a marcação | correção pendente na regra de status de `carregar_sinopse` (exige recarga da Sinopse, pesada em memória); não afeta o motor |
| Motor | Interpretador por regras: cobre os padrões da bateria; fora deles, pede esclarecimento | limitação de projeto (D05); LLM proposto em `03_proposta_llm.md` |
| Motor | Deficiência, reserva de vagas, financiamento, turno, nacionalidade, titulação de docentes | dados no núcleo; o motor explica que ainda não estão disponíveis |
| Banco | 5,35 GB: o DuckDB não devolve ao disco o espaço liberado ao refazer marts | recuperável com uma cópia compacta (`EXPORT/IMPORT` ou `COPY FROM DATABASE`) quando você autorizar |

## 6. Segurança — permissões (proposta; **não alterada**)

`.claude/settings.local.json` hoje libera **sem confirmação**: `PowerShell` e `Bash` (qualquer comando), `Edit`, `Write` e `Read` (qualquer arquivo), além de uma regra residual com o caminho de um scratchpad antigo. Isso é amplo: um comando destrutivo, por exemplo apagar os ZIPs, não pediria confirmação.

Proposta de substituição (só com sua aprovação):
```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit(pipeline/**)", "Edit(motor/**)", "Edit(tests/**)", "Edit(config/**)", "Edit(_arquitetura/**)",
      "Edit(*.md)", "Edit(perguntar.py)",
      "PowerShell(& \"$env:LOCALAPPDATA\\Programs\\Python\\Python312\\python.exe\" -I *)",
      "PowerShell(git status*)", "PowerShell(git diff*)", "PowerShell(git log*)", "PowerShell(git add*)", "PowerShell(git commit*)",
      "PowerShell(Get-ChildItem*)", "PowerShell(Get-Content*)", "PowerShell(Get-Date*)"
    ],
    "deny": [
      "Edit(*.zip)", "PowerShell(Remove-Item*.zip*)", "PowerShell(git push*)", "PowerShell(git reset --hard*)"
    ]
  }
}
```
Com isso, apagar ou mover arquivos, comandos fora do Python do projeto e edições fora das pastas de código voltam a pedir confirmação.

## 7. Arquivos temporários (avaliados; **nada apagado**)
- `%TEMP%\ijsn_pipeline\xlsx`: 32 arquivos, 3,81 GB, de 30/10, 01:54. São cópias extraídas dos ZIPs por `p0_staging.py`, que as recria se faltarem.
- Os 8 ZIPs originais estão presentes na raiz. Nenhum processo Python está ativo.
- **Dependências:** os testes T6 de `p1/p2/p3_validar.py` e `qualidade_confirmar_fonte.py` leem essas cópias. Depois de uma limpeza, é preciso rodar a extração (parte inicial de `p0_staging.py`) antes de revalidar.
- **Conclusão:** a limpeza é segura para o motor e para o banco; libera 3,8 GB (hoje há 19,5 GB livres). Depende da sua autorização.

## 8. Decisões
D01–D13 em `_arquitetura/02_decisoes.md`. Desta operação:
- D10: contrato JSON;
- D11: razões derivadas;
- D12: BIGINT e backup;
- D13: folhas na Sinopse.

## 9. Próximo passo (sugestão de ordem)
1. Você aprova (ou ajusta) a restrição de permissões (§6) e decide sobre as cópias XLSX (§7).
2. Usar o motor com perguntas reais. Cada erro vira linha em `test_regressao.py` e no gabarito (`tests/gerar_gold.py`, depois de revisar).
3. Q13 (status da 7.4) e Q10 (célula a célula), com recarga controlada da Sinopse e backup antes.
4. Deficiência e reserva de vagas no motor (crosswalks da P4 prontos).
5. Piloto de LLM local no modo híbrido (`03_proposta_llm.md` §4), avaliado contra o gabarito.
6. Interface Streamlit sobre `motor.perguntar`.
