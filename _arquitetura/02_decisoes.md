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

## D09 — Interface só depois do motor validado
- **Decisão:** nenhuma interface gráfica nesta etapa. A interface atual é a linha de comando `perguntar.py`. O candidato seguinte é o Streamlit local (gratuito), sobre `motor.perguntar`, sem lógica própria.
