# Registro de decisões de arquitetura (ADR)

Cada decisão: contexto, decisão, alternativas, consequências. Data no formato dd/mm/aaaa.

## D01 — Banco local DuckDB, arquivo único (out/2026)
- **Contexto:** 8 anos de planilhas (3,8 GB de XLSX), PC com 15,3 GB de RAM, sem servidor, sem orçamento.
- **Decisão:** DuckDB (livre, embutido, colunar) em `dados/nucleo/ijsn.duckdb`; staging em Parquet.
- **Consequências:** consultas analíticas rápidas sem servidor. Um só processo pode escrever por vez. É preciso limitar a memória (3 GB nas cargas, 2 GB no motor), porque o Claude Code já foi encerrado duas vezes por falta de memória.

## D02 — Anexo I removido do núcleo (30/10/2026)
- **Contexto:** o Anexo I ocupava 3,5 GB e é a soma dos Anexos II e III.
- **Decisão:** removido depois de validar I = II + III célula a célula (2017–2022) e por agregados (2023–2024). Fica a visão `v_anexo_i`.
- **Consequências:** banco de 7,4 → 3,9 GB. A visão é lenta (agrega 610 milhões de valores): não usar no motor.

## D03 — Valores suspeitos marcados, nunca corrigidos (30/10/2026)
- **Contexto:** Q02, Q03, Q09 e Q10 foram confirmadas como problemas da publicação do INEP (o XML original é idêntico ao banco).
- **Decisão:** os valores ficam como publicados e recebem `status_valor = 'suspeito'` + `id_ocorrencia`. As respostas citam a ocorrência.
- **Consequências:** rastreabilidade preservada; nenhuma imputação. Q10 ainda não está marcada célula a célula (só por tabela × ano).

## D04 — Camada de consulta (marts) em vez de consultar os fatos (30/10/2026)
- **Contexto:** os fatos têm 610 milhões (Anexos) e 127 milhões (Sinopse) de valores. Consultas abertas sobre eles são lentas e fáceis de errar (somar Total com categorias, misturar níveis).
- **Decisão:** três marts compactos (P6), com regras de agregação explícitas e validados contra os fatos. O motor só consulta os marts e as dimensões.
- **Alternativas:** visões sobre os fatos (lentas); cubo completo (duplicaria GBs, contra a regra 9).
- **Consequências:** +0,09 GB no banco; respostas em segundos; a regra "somar só folhas" fica num único lugar.

## D05 — Interpretador determinístico primeiro; modelo de linguagem depois, substituível (30/10/2026)
- **Contexto:** sem GPU dedicada (só a integrada, de 0,5 GB), 15 GB de RAM já pressionados pelo DuckDB e sem ollama. Regra 10 (processamento local) e regra 11 (ferramentas gratuitas). Um modelo local de 7B rodaria só na CPU, devagar e com risco de memória.
- **Decisão:** um interpretador por regras e catálogo (`motor/interpretador.py` + `semantica/catalogo.yaml`) produz uma estrutura explícita `Consulta`. Um modelo de linguagem futuro deve produzir a **mesma** estrutura; nunca SQL livre nem números.
- **Consequências:** é previsível, testável e não alucina. Por outro lado, cobre só as formas de pergunta previstas: quando não entende, pede esclarecimento em vez de adivinhar. Os cálculos estão sempre em `analise.py`.

## D06 — Segurança em camadas no motor (30/10/2026)
- **Decisão:** conexão `read_only`, validação do SQL (só SELECT/WITH, lista de tabelas autorizadas, sem leitura de arquivos nem extensões), parâmetros `?`, tempo máximo de 60 s, limite de 5.000 linhas e registro de toda consulta em `dados/consultas/registro_consultas.jsonl`.
- **Consequências:** mesmo um interpretador futuro mal comportado não consegue alterar o banco nem ler arquivos.

## D07 — Ausência ≠ zero (regra permanente)
- **Decisão:** linhas ausentes nos marts (zeros de folha descartados ou células vazias) não viram zero nas respostas. Participações sem numerador ficam indefinidas ("—"). Anos sem dado são listados como ausentes.
- **Observação:** os marts descartam zeros de **folha** porque eles não alteram as somas; os totais nunca são inferidos a partir de ausências.

## D08 — Recorte ES como visão, base completa (30/10/2026)
- Ver `01_arquitetura_dados.md` §8.3. O motor responde sobre qualquer UF ou município. Para municípios homônimos, prefere o do ES e registra essa suposição na resposta.

## D10 — Contrato JSON como ponto de integração de interpretadores (30/10/2026)
- **Decisão:** qualquer interpretador (regras ou LLM) produz o JSON da `Consulta` (`motor/contrato.py`), validado contra o catálogo e o banco antes de consultar. Inválido = pedido de esclarecimento, sem correção silenciosa.
- **Consequências:** o LLM pode ser trocado ou removido sem mexer em consultas, análise e segurança. Proposta completa em `03_proposta_llm.md`.

## D11 — Indicadores derivados por razão de somas (30/10/2026)
- **Decisão:** candidatos por vaga e ingressantes por vaga = Σ numerador ÷ Σ denominador no mesmo recorte (nunca média de razões). Participação de uma razão é recusada.

## D12 — Valores dos marts em BIGINT; backup leve em Parquet (30/10/2026)
- **Contexto:** `sum()` do DuckDB devolve HUGEINT, que o Parquet não representa (viraria DOUBLE).
- **Decisão:** os marts fazem cast para BIGINT. `pipeline/backup_leve.py` exporta todas as tabelas, exceto os dois fatos (reconstruíveis a partir dos ZIPs), e recusa HUGEINT. A validação confere contagem, esquema, conteúdo (hash das linhas), sha256 e a reconstrução (o motor responde igual sobre um banco refeito só com os Parquet).

## D13 — mart_sinopse_geo guarda as folhas (30/10/2026)
- **Decisão:** para sexo, cor/raça e faixa etária, uma linha por folha org. acadêmica × dependência × categoria privada (sem as folhas de valor zero), com a coluna `rede`. Isso permite cruzar sexo/cor/faixa com rede, dependência e organização acadêmica. Validado contra os Anexos (V8, V9).

## D14 — Q10/Q13 por atualização dirigida, com equivalência provada por recarga controlada (31/10/2026)
- **Contexto:** recarregar a Sinopse inteira pede 6 GB de memória e já derrubou processos duas vezes.
- **Decisão:** as regras ficam no pipeline (`carregar_sinopse.py`, lista `config/q10_celulas_suspeitas.csv` gerada por `q10_detectar.py`, regra 7.4). No banco principal, aplica-se só o UPDATE de `status_valor`/`id_ocorrencia` (`aplicar_q10_q13.py`), com estas garantias:
  - backup do status anterior;
  - transação com contagens conferidas;
  - impressão digital de todas as outras colunas igual antes e depois.

  Uma recarga parcial (6.3/6.6/7.4) num banco separado provou que o pipeline produz exatamente o mesmo resultado (0 diferenças).
- **Regra da Q10:** "suspeita" é a célula numa soma que não fecha e sem nenhuma soma que a confirme. Isso significa ausência de evidência a favor, não prova de erro.

## D15 — Compactação por cópia nova, nunca no lugar (31/10/2026)
- `COPY FROM DATABASE` para um arquivo novo. Antes da troca, valida tabelas, visões, contagens, tipos e conteúdo (hash) e as 61 respostas do motor. O original é guardado renomeado e só é apagado com autorização.

## D16 — Permissões mínimas do Claude Code (31/10/2026)
- O allow cobre leitura, edição de código e documentação, Python só nos scripts do projeto, git de rotina e consultas.
- O ask cobre apagar, mover ou renomear, `Set-Content`, git destrutivo e a própria configuração.
- O deny cobre editar ZIPs, banco, backups e staging.
- A aplicação foi verificada com uma regra-sentinela negada.
- **Brecha conhecida:** um script Python do projeto pode apagar arquivos. A mitigação é que todo script está no git e é revisado.

## D17 — LLM local como apoio, não como interpretador principal (31/10/2026)
- **Medição** (`tests/avaliar_llm.py`; logs em `dados/qualidade/avaliacao_llm_*`):

  | Interpretador | Paráfrases (24) | Controle (16, inéditas) | Total (40) | Tempo médio |
  |---|---|---|---|---|
  | Regras | 24* | 14 | 38* | 0,2 s |
  | Modelo 3B sozinho | 13 | 8 | 21 | 11 s |
  | Modelo 7B sozinho | 14 | 13 | 27 | 21–23 s (até 96 s) |
  | Híbrido (3B ou 7B) | 24* | 14 | 38* | 0,5–1 s |

  \* As regras foram ajustadas depois de ver as falhas das paráfrases: o 24/24 não mede generalização. O conjunto de controle mede: regras 14/16, com 2 erros silenciosos, depois corrigidos (R11, R12).
- **Leitura:**
  - nenhum modelo, sozinho, é tão confiável quanto as regras;
  - o 7B erra muito menos que o 3B (27 × 21 de 40), uma diferença grande, não marginal;
  - o híbrido só chama o modelo quando as regras não reconhecem o indicador, por isso não corrige erros silenciosos das regras.
- **Decisão:**
  - padrão = regras;
  - modo híbrido opcional com o **7B**, porque, quando o modelo é acionado, ele é o único interpretador e a exatidão pesa mais que o tempo;
  - aviso obrigatório para conferir a interpretação.

  O modelo devolve nomes; códigos, SQL e números são do motor.
- **Não adotado (fora do escopo desta versão):** comparar regras × 7B em toda pergunta para detectar erros silenciosos. Na avaliação, o 7B acertou as 2 perguntas que as regras erraram, mas isso custaria cerca de 20 s por pergunta.

## D18 — Interface web local só com a biblioteca padrão (31/10/2026)
- **Alternativa descartada:** Streamlit (cerca de 100 MB de dependências).
- **Decisão:** `http.server` em 127.0.0.1, página única, HTML escapado, arquivos servidos só da pasta de saídas, um pedido por vez. Abre por `iniciar_interface.bat`.

## D09 — Interface só depois do motor validado
- **Decisão:** nenhuma interface gráfica nesta etapa. A interface atual é a linha de comando `perguntar.py`. O candidato seguinte é o Streamlit local (gratuito), sobre `motor.perguntar`, sem lógica própria.
