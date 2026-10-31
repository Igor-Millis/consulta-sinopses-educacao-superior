# Relatório final de auditoria — Consulta às Sinopses da Educação Superior

**Data:** 31/10/2026 (auditoria encerrada às 12:15, depois do prazo de 12:00 indicado). Commit: `882281c`.

## 1. Estado geral
Primeira versão utilizável, auditada e testada de ponta a ponta, **recomendada para demonstração** (ver §13). Três defeitos de uso foram achados nesta auditoria e corrigidos (§6). O mais grave: o atalho `iniciar_interface.bat` **não iniciava** depois da troca de identidade.

## 2. Criador e natureza do projeto
**Igor L. Millis - Projeto Independente com Dados Públicos**

Fonte dos dados: INEP/MEC — Sinopses Estatísticas da Educação Superior (Graduação), 2017–2024. Processamento e consultas realizados localmente. Inconsistências identificadas na publicação original são preservadas e sinalizadas nas respostas.

*(31/10/2026: identificação padronizada a pedido do autor; a auditoria abaixo registra os textos da época.)*

**Auditoria de identidade** (busca por "IJSN" em todo o projeto, exceto `dados/`, ZIPs e `.git`): 74 ocorrências em 47 arquivos.

| Tipo | Arquivos | Ação |
|---|---|---|
| Identidade/apresentação | `app/pagina.html` (título, texto, rodapé), `app/servidor.py`, `iniciar_interface.bat`, `motor/api.py`, `motor/resposta.py` (**legenda impressa em todo gráfico**), `catalogo.yaml`, README, MANUAL, `motor/README`, ACOMPANHAMENTO | **substituídas** por "Consulta às Sinopses da Educação Superior" + autoria de Igor L. Millis; rodapé com aviso de não ser produto oficial; fonte INEP/MEC preservada |
| Nomes técnicos | arquivo `ijsn.duckdb`, pasta temporária `ijsn_pipeline`, pasta do projeto `IJSN` (cerca de 55 ocorrências em caminhos de código) | **mantidas**: renomear arquivos e pastas exige mover dados e refazer caminhos; documentado no README como identificador técnico, sem relação de autoria |
| Histórico | autor "IJSN projeto" nos 12 commits até `858f873` | **preservado** (o histórico não é reescrito); `git config user.name` = Igor L. Millis; o commit `882281c` já sai com esse autor |

Verificação na página servida: autoria visível, aviso de não ser oficial, fonte INEP, **nenhuma** menção a "IJSN" (`tests/e2e_usuario.py`).

## 3. Funcionalidades concluídas
- Base local DuckDB construída a partir dos 8 ZIPs do INEP (2017–2024), com rastreabilidade até a célula.
- Motor de perguntas em português:
  - tipos de pergunta: valor, série, comparação, ranking, crescimento/redução, participação, razões (candidatos por vaga);
  - cortes: curso, sexo/cor/faixa × rede, por exemplo.
- Fontes e limitações em toda resposta.
- Qualidade Q01–Q13 sinalizada (Q10 célula a célula).
- Interface web local (`iniciar_interface.bat`), com gráfico PNG e CSV.
- IA local opcional (Ollama + Qwen2.5 7B), rotulada como **experimental**.
- Backup leve validado; permissões restritas.

## 4. Testes executados e resultados (31/10/2026)
| Tipo | Conjunto | Resultado |
|---|---|---|
| Automatizados (pytest) | 262 testes coletados: contrato/gabarito 136, segurança 24, regressão 22, LLM 21, interpretador 17, referências independentes 15, interface 12 (+1 novo = 13), qualidade 8, análise 5, backup 1, equivalência 1 | **260 aprovados, 0 reprovados**, 2 pulados que exigem opção (rodados à parte: **ambos aprovados**). Depois das correções de interface: `test_app.py` 13/13 |
| Integração com o banco | `auditar_banco.py`: 25 tabelas, **8/8 visões compilam** · `p6_validar.py`: **13/13** · `p3_validar.py`: T1 OK, T2 35.932 (Q09/Q10, explicadas), T3 106 (Q11/Q12 e duas notas, explicadas), T5 120/120, T6 16/16 no XML original | OK, idêntico às rodadas anteriores |
| Integração backup | `backup_leve.py --validar dados/backup/20261031_024107` | **VÁLIDO e ATUAL**; reconstrução: motor igual ao banco |
| Integração bancos | 61 respostas: banco atual × banco pré-compactação | **idênticas** |
| Integração IA | `test_llm.py` (inclui chamada real ao 7B) e roteiro com pergunta livre | OK; 83 s na primeira pergunta (carga do modelo) |
| Ponta a ponta (servidor iniciado por `iniciar_interface.bat`, porta 8765) | 8 verificações da página + 13 cenários (exemplos, perguntas livres, 3 recusas, CSV, PNG, fontes, limitações, IA) | **8/8 e 13/13 OK** (`dados/qualidade/e2e_usuario.md`) |
| Manual | aparência visual e JavaScript da página no navegador | **NÃO executado por mim** (sem navegador nesta sessão) — ver §7 |

## 5. Problemas encontrados nesta auditoria
1. **O `.bat` não iniciava:** os acentos da linha `rem` adicionada na troca de identidade, com quebras LF, fizeram o `cmd` ler "sulta" como comando. A janela mostrava erro.
2. **Duas versões do servidor escutavam a mesma porta** (no Windows, `SO_REUSEADDR` do `http.server`): uma instância antiga, iniciada às 02:46, seguia respondendo com a página antiga. Também é uma brecha de segurança (outro processo local poderia ocupar a porta).
3. **Abrir o `.bat` duas vezes** daria erro técnico de porta ocupada.
4. **Identidade:** a legenda "Elaboração: motor IJSN" saía em todos os gráficos.

## 6. Problemas corrigidos (todos retestados)
| # | Correção | Teste |
|---|---|---|
| 1 | `.bat` em ASCII com CRLF; `.gitattributes` fixa CRLF | `.bat` executado: servidor no ar; e2e 13/13 |
| 2 | Porta exclusiva (`SO_EXCLUSIVEADDRUSE`, sem reuso) | `test_porta_exclusiva_segunda_instancia_falha` |
| 3 | Segunda abertura avisa "A Consulta já está aberta… abrindo o navegador" | executado: mensagem correta |
| 4 | Identidade trocada (§2) | e2e: página sem "IJSN", com autoria |

Instâncias antigas e de teste do servidor foram encerradas. Fica no ar só a versão atual (porta 8765, iniciada às 12:08).

## 7. Limitações ainda existentes
- **Inspeção visual da página não feita por mim:** o servidor, a página e as respostas foram validados por HTTP, mas não vi a tela nem executei o JavaScript. Abra a página uma vez antes da demonstração.
- **Erros silenciosos de interpretação:** nenhum **conhecido** em aberto (os 2 achados no conjunto inédito foram corrigidos), mas outros podem existir em formulações não testadas. Toda resposta mostra "Como a pergunta foi entendida".
- **IA local experimental:** sozinha acerta 27/40; 20–90 s por pergunta; só entra quando as regras não entendem.
- **Temas fora do motor** (com recusa explicada): deficiência, cotas, FIES, turno, nacionalidade, titulação de docentes.
- **Q10** = "sem evidência a favor", não erro comprovado; Q11/Q12 não marcadas (tabelas fora do motor).

## 8. Banco de dados
`dados/nucleo/ijsn.duckdb` (4,48 GB, compactado e validado): 25 tabelas, 8 visões, 745 milhões de linhas; 126.758.202 valores da Sinopse com status (80.369 suspeitos, 178.644 somente_presencial). O original pré-compactação foi preservado e é equivalente.

## 9. Armazenamento (disco C: com **2,5 GB livres**; nada foi apagado)
| Item (caminho) | Tamanho | Finalidade | Necessário para usar | Necessário para reconstruir | Cópia equivalente | Recomendação |
|---|---|---|---|---|---|---|
| `IJSN\*.zip` (8) | 2,23 GB | originais do INEP | não | **sim** | não (só no site do INEP) | **preservar sempre** |
| `IJSN\dados\nucleo\ijsn.duckdb` | 4,48 GB | banco em uso | **sim** | — | pré-compactação + ZIPs | preservar |
| `IJSN\dados\nucleo\ijsn_pre_compactacao_20261031_011217.duckdb` | 5,1 GB | banco antes da compactação | não | não | **sim**: conteúdo idêntico (hash de 25 tabelas) e 61 respostas iguais | pode apagar |
| `IJSN\dados\backup\` (6 pastas) | 0,21 GB | backups leves e status pré-Q10/Q13 | não | ajuda na recuperação | — | preservar |
| `%TEMP%\ijsn_pipeline\xlsx` | 3,8 GB | cópias extraídas dos ZIPs | não | só para revalidar o T6 | **sim**: os ZIPs (`p0_staging` recria) | pode apagar |
| `%TEMP%\claude\…\a756aa04…\scratchpad` | 4,2 GB | rascunhos da fase de diagnóstico (sessão antiga) | não | não (scripts estão em `_diagnostico_estrutura/`) | parcial | revisar e apagar |
| `%USERPROFILE%\.ollama\models` | 6,2 GB | modelos de IA (7B 4,7 GB + 3B 1,9 GB) | só o 7B, no modo IA | não | redownload | remover só o 3B (`ollama rm qwen2.5:3b`) |
| `IJSN\dados\teste_q10q13\sinopse_parcial.duckdb` | 85 MB | prova da recarga controlada | não | não | sim (o banco atual tem as mesmas marcações) | pode apagar |

**Liberação segura possível: cerca de 15 GB.** Por ordem de segurança: pré-compactação (5,1 GB), XLSX (3,8 GB), scratchpad antigo (4,2 GB, depois de olhar), modelo 3B (1,9 GB), teste (0,09 GB). Com 2,5 GB livres, a aplicação funciona (banco só leitura, saídas pequenas), mas **não há espaço para recargas ou compactações**.

## 10. Como iniciar
**Dois cliques em `C:\Users\T-Gamer\Desktop\IJSN\iniciar_interface.bat`.** O navegador abre `http://127.0.0.1:8765`. Linha de comando equivalente:
```
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -I app\servidor.py
```
(na pasta do projeto). Guia: `MANUAL_USUARIO.md`.

## 11. Roteiro de demonstração (10–15 min; resultados efetivos de 31/10/2026, 12:10)
| # | Pergunta | Demonstra | Resultado obtido | Sustentação / o que conferir |
|---|---|---|---|---|
| 1 | Quantas matrículas havia em Vila Velha em 2024? | consulta simples | **27.743** | Anexos II+III (8.2/8.3); a resposta mostra célula de origem `aba!célula` |
| 2 | Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024? | série | 153.610 → **182.335** (+18,7%); maior alta 2019→2020 (+9.145) | 182.335 = Sinopse 5.1 (teste de referência); gráfico de linha |
| 3 | Quais os 10 municípios capixabas com mais matrículas em 2024? | ranking | 1º **Vitória 50.417** (27,7%) | soma dos municípios = 182.335 |
| 4 | Compare as matrículas presenciais e a distância no ES nos últimos 5 anos | presencial × EaD | EaD 60.711 → 94.795; presencial 103.205 → 87.540; **inversão em 2023** | nota: EaD contado no município do polo |
| 5 | Matrículas em Direito em Vitória de 2017 a 2024 | curso | 5.679 → **3.179** (−44,0%), queda em todos os anos | nota sobre a revisão Cine de 2024 |
| 6 | Qual a participação do ES nas matrículas do Brasil entre 2017 e 2024? | ES × Brasil | **1,8%** em 2024 (182.335 de 10.226.873); 1,9% em 2017 | denominador = total Brasil publicado |
| 7 | Qual a participação das mulheres nas matrículas da rede privada do ES em 2024? | participação com universo | **60,6%** (91.190 de 150.402) | "Como foi entendida": universo = rede privada |
| 8 | Quantos alunos com deficiência no ES? | limitação honesta | recusa explicando que o dado existe no núcleo mas não está no motor | nenhum número inventado |
| 9 | Quantas vagas a distância em Vitória? | limitação da fonte | recusa: o INEP só publica vagas EaD no total Brasil | idem |
| 10 | (modo "Regras + IA local — experimental") Quero saber a quantidade de gente estudando na Serra em 2021 | pergunta livre com IA | **17.032** matrículas (cerca de 83 s na primeira vez) | aviso amarelo; conferir que "Como foi entendida" diz matrículas, Serra, 2021 |

Dica: abra o modo IA uma vez antes da apresentação (a primeira pergunta carrega o modelo e é a mais lenta).

### 9.1 Limpeza autorizada e verificação pós-limpeza (31/10/2026)
O usuário autorizou e **executou ele mesmo** (o Claude Code foi bloqueado pela proteção de arquivos, D16) as duas exclusões:

| Item excluído | Tamanho |
|---|---|
| `dados\nucleo\ijsn_pre_compactacao_20261031_011217.duckdb`: banco antes da compactação, com cópia equivalente comprovada | 5.488.521.216 bytes |
| `%TEMP%\ijsn_pipeline`: 32 cópias XLSX, recriáveis a partir dos ZIPs | 4.088.980.562 bytes |

**Verificação às 15:01 (`pipeline/verificar_pos_limpeza.py`): 23/23 OK.**
- Os dois itens estão ausentes.
- O banco atual `ijsn.duckdb` existe, com 4.813.500.416 bytes: 25 tabelas, 8/8 visões compilam, contagens idênticas às da auditoria (fato_sinopse 126.758.202; fato_anexo_curso 609.970.482; marts 662.772 / 3.182.105 / 2.741.684), marcações de qualidade preservadas (suspeito 80.369; somente_presencial 178.644).
- Consulta de leitura: ES 2024 = 182.335. Pelo motor: Vila Velha 2024 = 27.743.
- Os **8 ZIPs estão intactos** (tamanho e MD5 iguais ao manifesto).

**Disco C: de 2,5 GB (auditoria) para 14,0 GB livres.**

**Consequência:** o teste T6 de `p1/p2/p3_validar.py` e `qualidade_confirmar_fonte.py` lia as cópias XLSX. Antes de rodá-los de novo, é preciso recriar as cópias pela etapa de extração de `p0_staging.py` (cerca de 3,8 GB). O motor e a interface não dependem delas.
## 12. Pendências que dependem de autorização
1. Liberar o restante do espaço (§9): o scratchpad antigo (4,2 GB) e o modelo 3B (1,9 GB) continuam lá. O banco pré-compactação e as cópias XLSX já foram excluídos (§9.1).
2. Manter ou ajustar as permissões atuais (restritas, D16).
3. Inspeção visual da página por uma pessoa (§7).

## 13. Recomendação
| Critério | Situação |
|---|---|
| Aplicação inicia corretamente | **sim**: `.bat` executado e testado depois da correção |
| Consultas principais funcionam | sim (e2e 13/13; bateria 51+10) |
| Resultados rastreáveis às fontes | sim (célula de origem, tabela INEP) |
| Testes críticos passam | sim (260/260 + 2 à parte + validações de integração) |
| Erros conhecidos documentados | sim |
| Sem erros silenciosos **conhecidos** | sim (os conhecidos foram corrigidos; podem existir não descobertos) |
| Utilizável sem conhecimento técnico | sim pelo fluxo testado; **aparência visual a confirmar** |
| IA marcada como experimental/opcional | sim |
| Autoria de Igor L. Millis identificada | sim (página, rodapé, gráficos, docs) |
| Sem aparência de produto oficial | sim (aviso explícito no rodapé, README e manual) |

**Recomendo fazer a demonstração**, com uma condição simples: abrir a página uma vez antes para conferir a aparência (único teste não feito por mim) e já carregar a IA.

**Estimativa de conclusão da v1 para demonstração: cerca de 90%.** Os 10% restantes são a inspeção visual pendente, a liberação de disco e o risco natural de formulações de pergunta ainda não testadas. Não é uma medida matemática.
