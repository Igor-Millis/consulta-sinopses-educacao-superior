# Acompanhamento do projeto — Consulta às Sinopses da Educação Superior 2017–2024

Igor L. Millis - Projeto Independente com Dados Públicos. Menções a "IJSN" que restam neste arquivo são nomes técnicos de pasta/arquivo.

> **Atualização de 31/10/2026, 12:15: auditoria final concluída.** Ver `RELATORIO_FINAL_AUDITORIA.md`.
> - Identidade trocada para Igor L. Millis.
> - 3 defeitos de uso corrigidos: `.bat` não iniciava; duas instâncias na mesma porta; segunda abertura.
> - Testes: 260/260 automatizados, e2e 13/13 pelo `.bat`, P3/P6/backup/equivalência OK.
> - Disco: 2,5 GB livres. Liberação segura de cerca de 15 GB aguarda autorização.
> - As seções abaixo são o registro da entrega anterior (03:00) e foram mantidas como histórico.
>
> **Pós-limpeza (31/10/2026, 15:01):** o usuário excluiu o banco pré-compactação (5,49 GB) e as cópias XLSX de `%TEMP%\ijsn_pipeline` (4,09 GB).
> - Verificação 23/23 OK: banco atual íntegro (25 tabelas, 8/8 visões, contagens e consultas corretas); 8 ZIPs com MD5 igual ao manifesto.
> - Disco: **14,0 GB livres** (antes: 2,5 GB).
> - Para rodar de novo o T6 da validação P3, recrie antes as cópias XLSX (`p0_staging.py`, etapa de extração).
> - Detalhes em `RELATORIO_FINAL_AUDITORIA.md` §9.1.

Documento central. Atualizado em **31/10/2026, 03:00**: entrega da **primeira versão utilizável (v1)**.
Situações: **validado** (executado, testado, resultado registrado) · **implementado** (executado, teste parcial) · **pendente**.

## 1. Situação da v1

| Componente | Situação | Evidência |
|---|---|---|
| Base: 8 Sinopses (ZIPs intactos), pipeline P0–P6 reconstruível | validado | `pipeline/README.md`; P3 final 31/10, 02:50 |
| Qualidade Q01–Q13 (Q10 célula a célula, Q13 aplicada) | validado | `config/qualidade_ocorrencias.csv`, `q10_celulas_suspeitas.csv`, `tests/test_qualidade.py` |
| Banco compactado (5,11 → 4,48 GB) | validado | `dados/qualidade/compactacao_validacao.json`; 61 respostas iguais |
| Backup leve (Parquet, 47 MB) | validado | `dados/backup/20261031_024107/` (VÁLIDO e ATUAL) |
| Motor de consultas (regras) | validado | 260 testes; bateria de 61 perguntas |
| IA local (Ollama + Qwen2.5 7B, modo híbrido opcional) | validado, como apoio | `tests/avaliar_llm.py`; decisão D17 |
| Interface web local | validado (testes automáticos) | `app/`, `tests/test_app.py` (12); **não aberta visualmente por mim** (§4) |
| Permissões restritas do Claude Code | validado | regra-sentinela negada; rotinas permitidas |
| Manual do usuário | implementado | `MANUAL_USUARIO.md` |

## 2. O que foi feito nesta fase (31/10/2026, 00:38 → 03:00)

1. **Auditoria inicial:** git limpo (`f686e4c`), 216 testes OK, sem processos no banco, 8,3 GB de RAM livres. Achados:
   - a validação do backup tinha 2 defeitos no meu script (caminho relativo e reescrita de `validacao.txt`), já corrigidos: integridade e atualidade agora são verificações separadas, e cada relatório vai para um arquivo novo;
   - o backup de 23:34 estava íntegro, mas desatualizado em `qualidade_ocorrencias` (antes de Q11–Q13).
2. **Q10** (D14): regra objetiva (`q10_detectar.py`, mesma regra T2 da validação, extraída para `regras_t2.py`).
   - 2,58 milhões de somas verificadas em 6.3/6.6; 16.101 não fecham, **todas** em 2017–2019 e 2023.
   - **26.809 células marcadas** `suspeito/Q10` (menos de 2% das células desses anos); 25.832 "relacionadas" listadas e não marcadas.
   - Valores intactos.
3. **Q13:** 45.858 células da 7.4 (cursos/vagas/inscritos abaixo do Brasil) → `somente_presencial`. A T3 caiu de 178 para 106 falhas.
4. **Como foram aplicadas, sem recarregar a Sinopse inteira** (risco de falta de memória):
   - regras no pipeline;
   - recarga parcial em banco separado; antes da aplicação, a diferença era exatamente o esperado;
   - UPDATE dirigido, com backup do status, transação e impressão digital de 126,8 milhões de linhas igual antes e depois;
   - comparação final recarga × banco: **0 diferenças**.
5. **Compactação** (D15): cópia nova, validada (25 tabelas, 745 milhões de linhas, hash de conteúdo, visões, 61 respostas), trocada. O original foi **mantido**.
6. **Permissões** (D16): allow mínimo, ask para operações destrutivas, deny para ZIPs, banco e backups. A aplicação foi verificada.
7. **IA local** (D17): Ollama 0.40.13 (escuta só em 127.0.0.1, inicia com o Windows), Qwen2.5 3B e 7B.
   - O modelo devolve nomes, resolvidos pelo catálogo; o resultado passa pelo contrato e pela validação.
   - Avaliação em 40 perguntas (§3); o modelo escolhido foi o 7B.
8. **Regras melhoradas:**
   - indicador citado primeiro;
   - sinônimos (universitários, se formaram…);
   - maioria/domina → participação; menos → ranking crescente; encolhendo → redução;
   - "qual estado", "ranking dos estados", "qual curso tem mais";
   - dimensões citadas sem "por".
9. **Interface** (D18): página local com exemplos, modo de interpretação, aviso amarelo quando a IA interpreta, gráfico, CSV e histórico. `iniciar_interface.bat`.
10. **Documentação:** decisões D14–D18, `03_proposta_llm.md` atualizado, `MANUAL_USUARIO.md`, READMEs.

## 3. Testes e resultados

| Conjunto | Resultado |
|---|---|
| pytest completo (`tests/`, 67 s) | **260 aprovados**, 0 falhas; 2 pulados que exigem opção, ambos executados à parte e aprovados (backup: 1/1; equivalência entre bancos: 1/1) |
| P3 `p3_validar.py` (31/10, 02:50) | T1 OK (126.758.202 valores) · T2 35.932/39,07 milhões (Q09/Q10, igual a antes) · T3 106/2,32 milhões (Q11, Q12 e duas notas) · T5 120/120 · T6 16/16 |
| P6 `p6_validar.py` | 13/13 OK |
| Backup `backup_leve.py` | VÁLIDO (23 tabelas) e ATUAL; reconstrução: motor igual ao banco principal |
| Compactação | conteúdo idêntico (hash) em 25 tabelas; 61/61 respostas idênticas, antes e depois da troca |
| Q10/Q13 | recarga controlada × banco = 0 diferenças; status antes/depois = exatamente +26.809 / +45.858 |
| Bateria de 61 perguntas | 51 respondidas, 10 esclarecimentos legítimos, 0 erros; 0,3 s em média |
| Avaliação de interpretação (40 perguntas) | regras 38 (14/16 nas inéditas, antes da correção R11/R12) · 7B sozinho 27 · 3B sozinho 21 · híbrido = regras (ver D17) |
| Interface | 12 testes: página, resposta correta (182.335), PNG/CSV, travessia de pasta bloqueada (5 casos), HTML escapado, só 127.0.0.1 |
| IA local | 21 testes (20 sem o modelo, 1 integração real) |

## 4. Erros encontrados e corrigidos nesta fase
| Erro | Correção | Teste |
|---|---|---|
| `backup_leve --validar` com caminho relativo falhava na reconstrução e reescrevia `validacao.txt` do backup | caminho absoluto, pasta temporária, relatório em arquivo novo, integridade ≠ atualidade | revalidação dos backups |
| `carregar_sinopse` em modo parcial falhava no resumo final | proteção no modo parcial | recarga parcial |
| "Ranking dos estados por concluintes" respondia o total Brasil (silencioso) | "ranking dos estados", "dos estados por"… | R11 |
| "Qual curso tem mais concluintes" respondia **45.772 cursos** (silencioso) | "qual curso…" = dimensão curso | R12 |
| "alunos estudam em instituições…" virava IES; "faculdades e universidades" virava quebra | indicador citado primeiro; trecho consumido | gabarito + avaliação |
| Motor citava Q10 por tabela × ano, mesmo sem célula afetada | citação só quando a célula usada está marcada | `test_qualidade.py` |

## 5. Problemas ainda existentes (conhecidos e documentados)
1. **Interpretação:** as regras cobrem os padrões testados. Perguntas fora deles podem gerar **erro silencioso**: 2 de 16 no conjunto inédito, já corrigidos, mas outros podem existir. Mitigação: "Como a pergunta foi entendida" em toda resposta. Os testes com usuários vão revelar novos casos.
2. **IA local:** lenta (20–90 s); sozinha acerta 27 de 40. No híbrido só entra quando as regras não entendem, então não corrige erros silenciosos das regras.
3. **Q10:** "suspeita" significa sem evidência a favor, não erro comprovado. Q11/Q12 não estão marcadas (tabelas não usadas pelo motor).
4. **Fora do motor:** deficiência, reserva de vagas, financiamento, turno, nacionalidade e titulação de docentes (o motor explica que não estão disponíveis).
5. **Interface:** testada automaticamente, mas **não inspecionei a página visualmente** (sem navegador nesta sessão). Abra antes da demonstração (§7).
6. **Disco: só 3,1 GB livres.** Suficiente para usar a aplicação, insuficiente para recargas ou compactações. Ver §6.
7. **Brecha de permissão:** scripts Python do projeto rodam sem confirmação e podem, em tese, apagar arquivos (D16).

## 6. Pendências que dependem da sua autorização (nada foi apagado)
| Item | Tamanho | Recomendação |
|---|---|---|
| `dados/nucleo/ijsn_pre_compactacao_20261031_011217.duckdb` (banco original antes da compactação) | 5,1 GB | apagar depois da demonstração; equivalência comprovada e backup Parquet atual |
| Cópias XLSX em `%TEMP%\ijsn_pipeline` | 3,8 GB | apagar; recriadas a partir dos ZIPs se for preciso revalidar o T6 |
| Scratchpad de sessão antiga do Claude Code em `%TEMP%\claude\…\a756aa04…` | 4,2 GB | revisar e apagar (é da fase de diagnóstico) |
| Modelo `qwen2.5:3b` no Ollama (não usado após D17) | 1,9 GB | remover com `ollama rm qwen2.5:3b` |
| `dados/teste_q10q13/sinopse_parcial.duckdb` (recarga controlada) | 85 MB | pode apagar |
| Permissões: manter a configuração atual ou ajustar | — | manter |

## 7. Como iniciar e usar
1. **Dois cliques em `iniciar_interface.bat`** (pasta `IJSN`). Uma janela preta abre (deixe aberta) e o navegador vai para `http://127.0.0.1:8765`.
2. Clique num exemplo ou escreva a pergunta. Modo **Regras** (instantâneo) ou **Regras + IA local** (20–90 s; aviso amarelo para conferir).
3. Leia "Como a pergunta foi entendida" e "Limitações". Baixe o CSV, se quiser.
4. Linha de comando: `python -I perguntar.py "pergunta"`. Testes: `python -I -m pytest -p no:cacheprovider tests`.
5. Guia completo: `MANUAL_USUARIO.md`. Roteiro sugerido para a demonstração: os 6 exemplos da página, mais "Quantos alunos com deficiência no ES?" (mostra a recusa honesta) e uma pergunta livre no modo IA.

## 8. Próximos passos sugeridos (fora desta entrega)
1. Teste com usuários: cada pergunta mal entendida vira teste de regressão.
2. Novo conjunto inédito de perguntas para remedir a generalização (o de controle já foi usado).
3. Liberar espaço em disco (§6).
4. Avaliar a verificação cruzada regras × 7B para detectar erros silenciosos (D17, não adotada).
5. Deficiência e reserva de vagas no motor (crosswalks prontos).
