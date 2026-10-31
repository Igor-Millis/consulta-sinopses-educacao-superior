# Arquitetura de dados — Sinopses da Educação Superior (INEP), 2017–2024

**Status:** proposta para discussão. **Nada foi implementado.**
**Data:** 30/10/2026 · **Base:** diagnóstico estrutural em `_diagnostico_estrutura/` (relatórios 01–07).
**Princípios herdados do diagnóstico:** preservar o original, rastrear cada valor até a célula, não interpretar vazio como zero, não corrigir nem imputar valores sem fonte oficial, não descartar variáveis.

---

## 1. Objetivo e escopo

Montar uma base analítica que permita:
- séries históricas 2017–2024 de cursos, vagas, inscritos, ingressantes, matrículas, concluintes, docentes e IES;
- recortes por geografia (Brasil, UF, município), curso (Cine), organização acadêmica, dependência administrativa, grau, modalidade e características dos alunos e docentes;
- foco no **Espírito Santo**, comparado com Brasil e UFs (ver §8).

Fora do escopo desta versão: microdados do Censo, os arquivos ODS e as abas auxiliares, que serão apenas catalogadas.

---

## 2. Visão geral em camadas

```
 ZIPs INEP (imutáveis)
        │  manifesto de versões (MD5, data, URL)
        ▼
 [0] BRUTO ──────────── arquivos originais, nunca alterados
        │  leitura em streaming do XML (lxml), sem abrir no Excel
        ▼
 [1] STAGING ────────── uma tabela Parquet por aba e ano, "como está":
        │                linha da planilha, colunas A..ZZ, valor bruto em texto
        │  mapeamento curado (cabeçalho → dimensões), regras de qualidade
        ▼
 [2] NÚCLEO ─────────── modelo dimensional em formato longo (fatos + dimensões)
        │                + status de qualidade + linhagem até a célula
        ▼
 [3] ANALÍTICO ──────── visões prontas (ES × UF × Brasil, séries, indicadores)
```

| Camada | Conteúdo | Formato | Regra principal |
|---|---|---|---|
| 0 Bruto | 8 ZIPs + `manifesto_fontes.csv` | ZIP | Somente leitura. Cada versão nova do INEP entra como arquivo novo, com MD5 e data. |
| 1 Staging | Linhas de dados de cada aba, sem interpretar | Parquet (texto) | Nada é convertido nem descartado. A linha de origem é preservada. |
| 2 Núcleo | Fatos longos + dimensões + qualidade | DuckDB / Parquet | Cada valor tem dimensões explícitas, status e origem (arquivo, aba, célula). |
| 3 Analítico | Visões e tabelas agregadas | Visões DuckDB e exportações (CSV/XLSX) | Só lê o núcleo. Nunca soma totais publicados com detalhes. |

---

## 3. Modelo do núcleo (camada 2)

### 3.1 Fatos

Dois fatos, porque as duas famílias de planilhas têm granularidades diferentes:

**`fato_anexo_curso`** (Anexos I, II e III): um valor por ano × anexo × geografia × curso Cine × indicador × recorte.

| Campo | Descrição | Origem |
|---|---|---|
| `ano` | 2017–2024 | ZIP |
| `anexo` | I (pres. + EaD), II (pres.), III (EaD) | arquivo |
| `id_geo` | → `dim_geografia` | colunas A–E (por **código** da linha 12) |
| `id_cine` | → `dim_curso_cine` | colunas F–G |
| `id_indicador` | cursos, vagas, inscritos, ingressantes, matrículas, concluintes | prefixo do código (`NCURSO`, `VAG`, `INSCR`, `INGR`, `MAT`, `CONCL`) |
| `id_recorte` | org. acadêmica × grau × dependência × categoria privada | gramática do código (por exemplo, `NCURSOB14`) |
| `valor` | número, ou nulo quando não há valor válido | célula |
| `status_valor` | ver §5 | regras |
| `eh_agregado` | coluna de Total (soma de outras) | cabeçalho |
| `origem` | arquivo + aba + célula (por exemplo, `8.2!CA1453`) + MD5 do ZIP | staging |

**`fato_sinopse`** (Sinopse por município, tabelas 1.x a 7.x): um valor por ano × tabela × geografia × [nível acadêmico] × recorte.

| Campo | Descrição |
|---|---|
| `ano`, `id_tabela` | → `dim_tabela` (por exemplo, 4.2), com título, universo e referência geográfica |
| `id_geo` | Brasil, Região, UF, Município ou Exterior, conforme a linha |
| `id_nivel_academico` | Graduação / Sequencial / Total (quando a tabela tem essa coluna) |
| `id_indicador` | vem do título ou do nível do cabeçalho (por exemplo, "Vagas Oferecidas" na 4.1) |
| `id_recorte` | → `dim_recorte` (caminho hierárquico da coluna) |
| `valor`, `status_valor`, `eh_agregado`, `origem` | como acima |

### 3.2 Dimensões

| Dimensão | Chave natural | Observações do diagnóstico |
|---|---|---|
| `dim_geografia` | código IBGE do município (7 dígitos); UF; região | Inclui os níveis Brasil, Região, UF e Município e as **pseudo-regiões** `Distância` e `Exterior` (marcadas `eh_pseudo = true`). Nomes "limpos" (sem espaços extras), com o original guardado. Na Sinopse, a UF só vem por nome: é preciso uma tabela fixa nome → código e sigla. |
| `dim_curso_cine` | código Cine **sem aspas** (`0413A01`) | Guarda o texto original com aspas. Há uma versão por ano e uma tabela de correspondência para a revisão de 2024 (18–22 códigos entram e saem). |
| `dim_recorte` | id + caminho hierárquico original | Colunas tipadas: `org_academica`, `dependencia`, `categoria_privada`, `grau`, `modalidade`, `turno`, `sexo`, `cor_raca`, `faixa_etaria`, `nacionalidade`, `deficiencia`, `forma_ingresso`, `financiamento`, `reserva_vagas`, `regime_trabalho`, `grau_formacao`. Cada coluna de planilha aponta para um recorte. "Total" é um valor explícito, nunca nulo. |
| `dim_indicador` | código | Unidade (todas são contagens), **`aditivo`** (falso para docentes: notas 3–7 das tabelas 2.x), referência geográfica (sede × oferta). |
| `dim_tabela` | conjunto + número | Título e universo por ano, notas de rodapé e `ref_geografica` (sede para 1.x e 2.x; oferta para 3.x a 7.x e Anexos). |
| `dim_fonte` | MD5 do ZIP | Data, URL e observações (por exemplo, "versão sem a correção da 4.1/2023"). |

### 3.3 Correspondências entre anos (crosswalks)

Tabelas curadas e versionadas que **não alteram o dado**, só dizem como comparar:

| Tabela | Uso |
|---|---|
| `xw_cine` | Códigos Cine de cada ano → código de referência (prioridade: revisão de 2024). |
| `xw_deficiencia` | Autismo Infantil / Asperger / Rett / … (2017–2020) → TGD (2021–22) → TEA (2023–24) → classe comparável. |
| `xw_reserva_vagas` | "Étnico" (2017–23) → 8 categorias de 2024. |
| `xw_colunas_sinopse` | Coluna (ano, aba, letra) → recorte. Gerado a partir do catálogo 03 e **revisado à mão** onde há ∅ (mesclagens desalinhadas). |

Cada linha leva a classificação de equivalência do diagnóstico (confirmada, provável, parcial, não comparável).

---

## 4. Regras de transformação (staging → núcleo)

| # | Situação (referência no relatório 07) | Regra |
|---|---|---|
| R1 | Cabeçalho dos Anexos com rótulo trocado em B/C (C3) | Ler **pelo código da linha 12**, nunca pela posição nem pelo rótulo da linha 6. |
| R2 | Ordem das colunas identificadoras muda (A1) | Localizar as colunas pelo rótulo normalizado, não pela letra. |
| R3 | Cabeçalhos hierárquicos e mesclados | Usar `xw_colunas_sinopse`. As 63 colunas com ∅ (C4) recebem mapeamento manual. As colunas fantasma de 2020 (A3) são ignoradas e registradas. |
| R4 | Totais intercalados (C5) | A linha recebe `nivel_geo`. A coluna recebe `eh_agregado`. Nada é somado no núcleo. |
| R5 | Pseudo-regiões `Distância` e `Exterior` (A7) | Viram geografias próprias, nunca somadas a regiões. |
| R6 | Zeros estruturais EaD (C6) | Nos Anexos I e III, linha municipal, indicadores cursos, vagas e inscritos: `valor = nulo` e `status = nao_desagregado`. O original fica no staging. |
| R7 | Célula vazia (C1) | `status = celula_vazia`, `valor = nulo`. **Nunca vira 0.** Exceção: só se uma regra validada demonstrar que, naquela tabela e ano, vazio = 0. |
| R8 | Marcador "." (C2) | `status = marcador_ponto`, `valor = nulo`. |
| R9 | Códigos Cine com aspas (A4) | Remover as aspas na dimensão e manter o original no staging. |
| R10 | Espaços extras em rótulos e nomes (M3, M7) | Aplicar `strip` e normalização para chave; o texto original é guardado. |
| R11 | Números como texto (M4) | Converter e registrar a conversão no log. |
| R12 | Totais de docentes não aditivos (C7) | `dim_indicador.aditivo = false`. A camada analítica bloqueia somas desses indicadores. |
| R13 | Dados suspeitos (§8.1–8.3 do relatório 07) | `status = suspeito`, mantendo o valor, e registro em `qualidade_ocorrencias` (tabela 4.1/2023 do IF-MT; inscritos do IF-MT 2018–2023; ingressantes do IF-MT 2021–2022). |

---

## 5. Qualidade e linhagem

**`status_valor`** (lista fechada):

| Status | Significado | `valor` |
|---|---|---|
| `informado` | Número publicado | número |
| `celula_vazia` | Célula vazia ou inexistente na planilha | nulo |
| `marcador_ponto` | "." ou ". " na célula | nulo |
| `nao_desagregado` | O INEP não distribui o indicador neste nível (EaD por município) | nulo |
| `suspeito` | Valor publicado, mas com inconsistência documentada | número |

**`qualidade_ocorrencias`**: id, ano, tabela, recorte afetado, descrição, evidência, fonte (por exemplo, "Nota Informativa 02/2023") e situação (aberta/confirmada).

**Linhagem:** todo fato guarda `arquivo`, `aba`, `célula` e `md5_zip`. A partir de qualquer número da camada analítica, é possível chegar à célula da planilha do INEP.

**Testes automáticos de reconciliação** (executados a cada carga):
1. Contagem de linhas e células do staging = perfil do diagnóstico (04).
2. Indicadores aditivos: soma dos detalhes = colunas de Total da mesma linha (tolerância 0).
3. Municípios → UF → Brasil, só para indicadores aditivos e só na Sinopse, onde a UF é publicada.
4. Anexo I = Anexo II + Anexo III (por curso e geografia).
5. Anexo II = Sinopse 7.2 e Anexo I − II = 7.3 (totais por organização acadêmica).
6. Falhas viram ocorrências de qualidade e **não interrompem** a carga.

---

## 6. Tecnologia proposta

| Item | Escolha | Por quê |
|---|---|---|
| Linguagem | Python 3.12 (já instalado) | Os scripts do diagnóstico já fazem a leitura em streaming. |
| Leitura | `lxml.iterparse` sobre o XML interno | Arquivos de até 3,8 GB de XML por aba. O `openpyxl` seria lento demais. |
| Armazenamento | **Parquet** (staging) + **DuckDB** (núcleo e analítico) | Um único arquivo, sem servidor, SQL rápido para centenas de milhões de linhas; abre no Python, no R e em ferramentas de BI. |
| Configuração | YAML/CSV versionados (mapeamentos e crosswalks) | Decisões humanas ficam em arquivos legíveis e revisáveis. |
| Orquestração | Script único por etapa (`extrair`, `transformar`, `validar`), idempotente | Reprocessar um ano não afeta os outros. |

Estrutura de pastas sugerida (a criar só na implementação):

```
IJSN/
├── *.zip                         (bruto — intocado)
├── _diagnostico_estrutura/       (já existe)
├── _arquitetura/                 (este documento)
├── config/                       mapeamentos, crosswalks, lista de UFs/municípios
├── dados/staging/<ano>/<aba>.parquet
├── dados/nucleo/ijsn.duckdb
├── dados/qualidade/
└── pipeline/                     extrair.py, transformar.py, validar.py
```

---

## 7. Ordem de implementação (quando autorizada)

| Fase | Entrega | Critério de aceite |
|---|---|---|
| P0 | Manifesto de fontes + staging de **todas** as abas (8 anos) | Contagens = diagnóstico 04 |
| P1 | **Piloto Anexo II** → `fato_anexo_curso` + dimensões geografia, Cine e recorte | Testes 1, 2 e 5 passam; 10 valores conferidos à mão na planilha |
| P2 | Anexos III e I (pseudo-regiões, zeros estruturais) | Teste 4 passa ou as divergências são documentadas |
| P3 | Sinopse: tabelas estáveis (relatório 07, §4, 2ª prioridade) | Testes 2 e 3 passam; ∅ mapeados à mão |
| P4 | Crosswalks (Cine 2024, deficiência, reserva de vagas) + tabelas com quebra | Revisão humana das equivalências |
| P5 | Camada analítica ES (§8) | Indicadores validados com você |

---

## 8. Recorte Espírito Santo: Brasil + UFs + municípios do ES

### 8.1 O que significa em cada base

| Base | Brasil | UFs | Municípios do ES |
|---|---|---|---|
| Sinopse por município | Linha "Total Brasil" (publicada) | Linhas "Total <UF>" (publicadas, as 27) | Linhas com código IBGE `32xxxxx` |
| Anexos I, II e III | Linhas "Total Brasil" (geral e por curso) | ⚠️ **Não existem linhas de UF.** Precisam ser **somadas** a partir dos municípios de cada UF, o que exige ler os municípios de **todas** as UFs, somar e só então descartá-los | Linhas com `CO_UF = 32` |

Consequências:
- Nos Anexos, o total da UF fica como **valor derivado** (`status = derivado_soma`), não publicado, e só vale para indicadores aditivos.
- No EaD, a UF continua sem cursos, vagas e inscritos (eles só existem no Brasil).
- As pseudo-regiões `Distância` e `Exterior` entram no nível Brasil.

### 8.2 Desempenho: filtrar não acelera a etapa lenta

- A etapa mais lenta é a **leitura do XML**: cerca de 45 GB nos 8 anos, de 35 a 45 minutos com processamento paralelo. Para encontrar as linhas do ES, o arquivo inteiro precisa ser lido de qualquer forma.
- Nos Anexos, os totais por UF exigem somar os municípios de **todas** as UFs. Portanto, nem a leitura nem a soma podem pular os outros estados.
- O filtro só reduziria o volume armazenado e o tempo das consultas. Com DuckDB e Parquet, as consultas sobre a base completa já são rápidas (segundos), então esse ganho é irrelevante.
- A leitura é um **custo único** por ano: depois do staging, nada precisa ser relido.

### 8.3 Decisão

✅ **Não filtrar na ingestão.** A base completa (todas as UFs e municípios) é carregada no staging e no núcleo. O recorte **Brasil + UFs + municípios do ES** passa a ser uma **visão da camada analítica**. Assim se preserva a possibilidade de comparar o ES com qualquer outro estado sem reprocessar. A medição proposta foi cancelada.

---

## 9. Situação da implementação (30/10/2026)

| Fase | Situação | Resultado |
|---|---|---|
| **P0** | ✅ Concluída e validada | 662 abas → Parquet (3,07 milhões de linhas; 1,31 bilhão de células; 0,21 GB) em 30 min. As 84.894 colunas conferem com o diagnóstico, sem divergências. |
| **P1** | ✅ Concluída e validada | Anexo II 2017–2024 no núcleo: 79,1 milhões de valores (1,6 min). T1 completude OK; T2 24,0 milhões de comparações de totais internos OK; T3 1,4 milhão de comparações Brasil = Σ municípios OK; T5 48 totais = Sinopse 7.2 OK; T6 16/16 valores conferidos na planilha original com outro leitor (8 deles em municípios do ES). |
| **P2** | ✅ Concluída e validada | Anexos I e III 2017–2024 no núcleo. Total dos três Anexos: 1,17 bilhão de valores; 7,44 GB; 108 min de carga. Status aplicados: `somente_presencial` (277 milhões), `nao_desagregado` (265 milhões), `nao_aplicavel` (784 mil), `suspeito` (72 mil). Testes: T1 OK (e as regras de status só pegaram zeros publicados); T2 250 milhões de comparações OK; **T3 falhou em 22 células por anexo, todas em 2022, por omissão na publicação** (falta a linha Distância do curso Cine 0011A09; ocorrência **Q04**, sem imputação); T4 I = II + III em 557 milhões de comparações OK; T5 96 totais = Sinopse 7.2/7.3 OK; T6 16/16 valores conferidos no XML original (8 em municípios do ES). |
| **Remoção do Anexo I** | ✅ Concluída | O Anexo I é idêntico a II + III: validado célula a célula em 2017–2022 (343 milhões de valores) e por agregados em 2023–2024, sem diferenças. Fica disponível como visão `v_anexo_i`. Banco: 7,4 → 3,9 GB. |
| **P3** | ✅ Concluída e validada, com 1 item aberto | Sinopse por município: 69.806 colunas mapeadas por vocabulário (14 indicadores, 18 dimensões; 40 correções manuais; 126 colunas só no staging, ocorrências Q05/Q06); 126,8 milhões de valores. Regras: EaD não desagregado em 3.1/4.1/7.3 (`nao_desagregado`, 2,27 milhões), "Total" subnacional só presencial (`somente_presencial`), subtotais de UF com rótulo errado corrigidos pelo código IBGE (Q07/Q08), categorias não exclusivas documentadas nas notas (`config/categorias_nao_exclusivas.csv`). Testes: T1 OK; T2 0,092% de falhas nas categorias exclusivas (restante: **Q09**, a investigar); T3 0,008% de falhas; T5 120/120 = Anexos; T6 16/16 no XML original. |
| **Q09 (3.1)** | ✅ Identificada | Em 2017–2019, 2021 e 2023 a tabela 3.1 traz os valores de três pares de colunas trocados (X/Y, AO/AP, BF/BG: total presencial × total público de Universidade, Centro Universitário e Faculdade). Detectado automaticamente e marcado como `suspeito` (cerca de 7 mil valores por ano), com os valores mantidos como publicados. |
| **Q10 (6.3/6.6)** | ⚠️ Aberta | Células isoladas inconsistentes em 2017–2019 e 2023 (por exemplo, 6.6/2023: Masculino = 159.798 num total de 4.568). Sem padrão de troca; só uma fonte oficial pode dizer qual célula está certa. |
| **P4** | ✅ Concluída | `xw_cine` (322 códigos estáveis; 13 que mudaram de código com o mesmo nome, ligados; 1 que mudou de nome; 40 presentes só em parte dos anos), `xw_deficiencia` (18 → 11 classes), `xw_reserva_vagas` (14 → 6 classes), com o grau de equivalência; visões `v_sinopse_deficiencia_comparavel` e `v_anexo_curso_cine_ref`. |
| **P5** | ✅ Concluída | Visões `v_es_municipio_curso`, `v_es_municipio_indicador` e `v_comparativo_uf`, exportadas em `dados/analitico/*.csv` (separador `;`). Conferência: matrículas de graduação do ES na Sinopse 5.1 = Σ municípios do ES nos Anexos II + III em todos os anos (ex.: 2024: 87.540 + 94.795 = 182.335). |

Código em `pipeline/` (com README), configuração em `config/`, dados em `dados/`. Resultados dos testes em `dados/qualidade/`.

## 10. Decisões pendentes (suas)

1. ~~**Recorte geográfico**~~ → **decidido (30/10/2026):** a base é completa, e o ES é uma visão analítica (§8.3).
2. **Anexo I:** carregar o Anexo I ou só os Anexos II + III, se o teste 4 mostrar que I = II + III? Isso economiza cerca de 45% do tempo de leitura.
3. **Tabelas da Sinopse com quebra de categoria** (deficiência, reserva de vagas): entram na P3 sem crosswalk (só por ano) ou esperam a P4?
4. **Valores suspeitos do IF-MT:** apenas marcar (recomendado) ou excluir das visões analíticas por padrão?
5. **Microdados do Censo:** avaliar como fonte complementar de validação?
