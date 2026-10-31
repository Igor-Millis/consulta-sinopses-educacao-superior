# Proposta: integração de um modelo de linguagem (LLM) ao motor de consultas

Situação em 30/10/2026: o motor funciona com um interpretador por regras. Esta proposta descreve como acrescentar um modelo de linguagem **sem abrir mão** de três garantias:
- os números vêm do banco e do código;
- toda consulta é somente leitura e validada;
- toda suposição aparece na resposta.

O ponto de integração **já está implementado e testado** (§3).

## 1. Princípio: o modelo traduz, não calcula

```
pergunta ─► [LLM] ─► JSON da Consulta ─► contrato.de_json (validação) ─► responder() ─► números do banco/código
                 ▲                                    │ inválido
                 └── esquema + exemplos do catálogo    └─► pedido de esclarecimento (nada é consultado)
```

O modelo **pode**:
1. transformar a pergunta no JSON da `Consulta` (indicador, anos, locais, filtros, quebras, tipo);
2. opcionalmente, reescrever em linguagem mais natural um texto **já calculado**.

O modelo **não pode**:
- escrever SQL;
- acessar o banco;
- produzir ou alterar números;
- decidir o que é comparável entre anos (isso está no catálogo e nas ocorrências Q01–Q13).

## 2. Por que essa divisão
| Risco do LLM | Contenção |
|---|---|
| Inventar números | Os números vêm de `analise.py`. Se o LLM reescrever o texto, um verificador confere que cada número citado existe no `Resultado` (§4.3). |
| SQL perigoso ou errado | O LLM não gera SQL. O SQL é montado por `consultas.py` com parâmetros, passa por `seguranca.validar_sql` e roda numa conexão somente leitura. |
| Indicador, local ou categoria inexistente | `contrato.de_json` recusa qualquer valor fora do catálogo e de `dim_geografia` (testado: 8 tipos de entrada inválida). |
| Interpretação plausível, mas errada | Comparação com o interpretador por regras (§4.2) e a seção "Como a pergunta foi entendida" em toda resposta. |
| Dados enviados para fora | Só modelo local (regra 10). Nenhuma API externa. |

## 3. O que já está pronto (implementado e testado)
| Peça | Arquivo | Teste |
|---|---|---|
| Esquema JSON da Consulta, com valores permitidos vindos do catálogo | `motor/contrato.py` → `esquema(cat)` | `test_esquema_e_serializavel` |
| Validação estrita do JSON (campos, indicador, anos, locais, filtros, dimensões) | `contrato.de_json` | `test_contrato_recusa_invalido` (8 casos) |
| Entrada para interpretadores externos | `motor.api.perguntar_estruturado(json)` | `test_perguntar_estruturado_recusa_sem_consultar`, `test_caminho_estruturado_da_mesma_resposta` |
| Gabarito de 61 interpretações revisadas | `tests/gold_interpretacoes.jsonl` (gerado por `tests/gerar_gold.py`) | `test_gabarito_de_interpretacao` (61) e `test_ida_e_volta` (61) |
| Bateria com registro de desfecho e tempo | `tests/bateria_perguntas.py` | relatórios `dados/qualidade/bateria_*.md/csv` |

## 4. Próximas etapas (quando autorizadas)

### 4.1 Modelo local
- **Restrição do PC:** CPU Ryzen 5 4650G, 15,3 GB de RAM, GPU integrada de 0,5 GB. O DuckDB do motor usa até 2 GB.
- **Opção gratuita e local:** um servidor `llama.cpp` (ou ollama) rodando só na CPU com um modelo instrução pequeno (3B–8B parâmetros), quantizado em 4 bits. Isso ocupa cerca de 2–6 GB de RAM. Desempenho e qualidade em português precisam ser **medidos** aqui; não há números confiáveis antes do teste.
- **Saída estruturada:** usar decodificação restrita por gramática/JSON Schema (`esquema(cat)`), que o llama.cpp suporta. Assim o modelo só consegue emitir JSON no formato do contrato.
- **Risco:** pressão de memória (o Claude Code já foi encerrado duas vezes por falta de RAM). Não rodar o LLM ao mesmo tempo que cargas do pipeline.

### 4.2 Arquitetura híbrida (recomendada)
1. O interpretador por regras roda primeiro (em menos de 0,05 s).
2. Se ele interpretar sem pedir esclarecimento, a resposta segue por ele. O LLM entra só nos casos de esclarecimento ou de baixa cobertura. Isso reduz custo e risco.
3. Quando os dois interpretam, divergências entre eles viram aviso na resposta e casos para revisão.
4. Toda interpretação do LLM é registrada (pergunta, JSON, validação) no `registro_consultas.jsonl`.

### 4.3 Redação opcional pelo LLM
- O LLM recebe o `Resultado` (tabela e fatos) e o texto determinístico, e pode só reescrever.
- Verificador: extrair todos os números do texto reescrito e exigir que cada um esteja no `Resultado`, com a mesma formatação. Se algum falhar, usar o texto determinístico.

### 4.4 Avaliação antes de adotar
- Métrica: exatidão do JSON contra o gabarito (`gold_interpretacoes.jsonl`), campo a campo, e por pergunta inteira.
- Critério de adoção sugerido: o modelo não pode errar nenhuma pergunta que as regras acertam, ou só entra no modo híbrido (§4.2).
- Ampliar o gabarito com perguntas reais dos usuários (cada erro encontrado vira caso de teste, como em `test_regressao.py`).

## 5. O que não muda
Catálogo semântico, marts, regras estatísticas, segurança, registro de consultas e testes continuam sendo a única fonte de verdade. O LLM é uma camada substituível na frente do contrato.
