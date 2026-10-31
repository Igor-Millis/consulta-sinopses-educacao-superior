# 07 — Relatório de diagnóstico estrutural

**Sinopses Estatísticas da Educação Superior (INEP), 2017–2024. Planilhas XLSX.**
Data do diagnóstico: 30/10/2026 · Escopo: só diagnóstico. Nenhum banco foi construído, nenhum dado foi padronizado e nada foi descartado.

---

## 0. Como ler este relatório

Cada afirmação é marcada com um destes selos:

| Selo | Significado |
|---|---|
| ✅ **Confirmado** | Verificado diretamente no conteúdo das células, com local de origem indicado. |
| 🔶 **Hipótese** | Inferência plausível que ainda não foi verificada contra documentação oficial. |
| ⚠️ **Ambiguidade / risco** | Ponto em que a planilha admite mais de uma leitura, ou em que há defeito na origem. Exige decisão ou revisão manual. |

**Rastreabilidade.** Todo item pode ser seguido até `arquivo › ano › aba › célula`:
- `02_catalogo_abas.xlsx`: célula do título (`celula_titulo`), linhas de cabeçalho, linha de início dos dados e notas de rodapé com célula (aba `notas_rodape`).
- `03_catalogo_colunas.xlsx`: para cada coluna, a célula de origem de cada nível do cabeçalho (`celula_nivel_1…6`) e a do código da variável (`celula_codigo`).
- `04_perfil_dados.xlsx`: exemplos de registros com o número da linha (`celula_inicial`).
- `05_comparacao_estrutural.xlsx`: pareamento de colunas entre anos, com coluna de origem e de destino.

**Como foi feito.** Os ZIPs originais foram lidos sem alteração. Cópias dos 32 XLSX foram extraídas para uma pasta temporária, fora do projeto. O XML de cada aba foi lido em *streaming* (lxml), sem carregar os arquivos inteiros na memória. São 662 abas, ~45 GB de XML descompactado e ~2,4 milhões de linhas de dados.

---

## 1. Resumo da estrutura encontrada

### 1.1 Visão geral

| Conjunto | Workbooks | Abas por ano | Abas de dados | Linhas de dados (2017 → 2024) | Colunas úteis |
|---|---|---|---|---|---|
| Sinopse por município | 8 | 79 (2017–2022) / 82 (2023–2024) | 65 → 68 por ano | 75.141 → 118.565 (soma das abas) | 19 a 603, conforme a tabela |
| Anexo I — Tabela 8.1 (presencial + EaD) | 8 | 1 | 1 | 52.513 → 213.522 | 521 (todos os anos) |
| Anexo II — Tabela 8.2 (presencial) | 8 | 1 | 1 | 18.707 → 19.078 | 521 (todos os anos) |
| Anexo III — Tabela 8.3 (EaD) | 8 | 1 | 1 | 42.171 → 209.220 | 521 (todos os anos) |

✅ As 662 abas foram perfiladas sem erro de leitura: 550 têm bloco de dados e 112 são auxiliares. As auxiliares são, por ano: 4 de documentação (`Sinopse_Estatística`, `Resumo`, `Equipe Técnica`, `Como Citar`), 1 `Sumário`, 8 capas de seção e 1 remissiva (`8.1 a 8.3`).

✅ **Todas as tabelas de dados são contagens absolutas** (os títulos começam com "Número de…"). Em 82.268 colunas de medida não há **nenhum** valor decimal ou negativo. A única exceção de título é a tabela **7.4** (2023–2024), que mistura vários indicadores numa só aba (ver §2.4).

✅ **As linhas são agregados, não microdados.** Não existe linha por aluno, docente, curso ou IES.
- Sinopse por município: linhas = Brasil, Região, UF e Município (em algumas tabelas, × Nível Acadêmico do Curso).
- Anexos: linhas = Município × Curso (rótulo Cine Brasil), mais linhas "Total Brasil" por curso.

### 1.2 Anatomia de uma aba de dados (padrão comum aos dois tipos)

| Linhas | Conteúdo | Exemplo (Anexo I 2024, aba `8.1`) |
|---|---|---|
| 1 | Link "Voltar ao Sumário" | `A1` |
| 2 | Tema da seção | `A2` = "Dados Gerais por Curso" |
| 3 | Universo / subtítulo | `A3` = "Cursos de Graduação - Presenciais e a Distância" |
| 4 | Título da tabela, com o ano | `A4` = "8.1 - Número de Cursos, Vagas Oferecidas, …" |
| 6 a 11 (variável: 3 a 7 níveis) | Cabeçalho hierárquico com células mescladas | `H7` = "Número de Cursos", `I8` = "Universidade", `J9` = "Bacharelado", … |
| 12 | **Só nos Anexos:** códigos das variáveis | `H12` = `NCURSO`, `CA12` = `VAGT` … |
| 13 em diante (variável) | Dados. A primeira linha é sempre "Total Brasil" | `A13` = "Total Brasil" |
| Final | "Fonte:" e "Notas:" numeradas | `A18721` = "Fonte: INEP - Censo da Educação Superior." (Anexo II 2017) |

✅ Os cabeçalhos **não** ficam na primeira linha. Começam na linha 6 e têm de 3 a 7 níveis (distribuição nas 550 abas: 68 com 3 níveis, 170 com 4, 128 com 5, 176 com 6 e 8 com 7).
✅ Cada aba de dados contém **uma única tabela**. Nenhuma tabela secundária foi encontrada no meio das abas.
✅ Há 52.297 células mescladas (40.393 na Sinopse e 11.904 nos Anexos), **todas na área do cabeçalho**. Nenhuma mesclagem invade a área de dados.

### 1.3 Sinopse por município

- **Tabelas por tema:** 1.x Instituições, 2.x Docentes, 3.x Cursos, 4.x Processos Seletivos (vagas, inscritos, ingressantes), 5.x Matrículas, 6.x Concluintes e 7.x Dados Gerais.
- **Colunas identificadoras** ✅: `Região Geográfica`, `Unidade da Federação`, `Município` e `Código do Município` (7 dígitos, IBGE). Em 20 tabelas também aparece `Nível Acadêmico do Curso` (Graduação / Sequencial de Formação Específica): 3.1, 4.1, 4.2, 4.6–4.8, 4.11, 5.1, 5.2, 5.5–5.7, 5.10, 6.1, 6.2, 6.5–6.7, 6.10 e 7.1.
- **Pseudo-região `Exterior`** ✅: em várias tabelas 4.x a 7.x, a coluna A traz "Exterior" (cursos de IES brasileiras ofertados fora do país). Não é região do IBGE e não tem UF nem município.
- **Níveis de agregação na mesma aba** ✅. Exemplo da aba `1.1` de 2024:
  - 1 linha "Total Brasil";
  - 5 linhas "Total <Região>";
  - 27 linhas "Total <UF>", com a UF na coluna B;
  - 698 municípios.
- **Referência geográfica** ✅ (notas de rodapé de 2024): município da **sede administrativa/reitoria** da IES nas tabelas **1.x e 2.x** (por exemplo, nota 9 da `2.1`: "Os docentes são computados segundo a sede e/ou reitoria da instituição"); **local de oferta** do curso nas tabelas **3.x a 7.x** e nos Anexos. Essa diferença precisa ser respeitada na modelagem.
- **Não há código de UF nem de região.** Só nomes. A UF aparece como "Total Rondônia" nas linhas de subtotal e como "Rondônia" nas linhas de município.

### 1.4 Anexos I, II e III (Tabelas 8.1, 8.2 e 8.3)

| Coluna | Código (linha 12) | Conteúdo |
|---|---|---|
| A | `NO_REGIAO` | Nome da região |
| B / C | `NO_UF` / `CO_UF` | Nome e código da UF (**ordem varia**, ver §2.1) |
| D | `NO_MUNICIPIO` | Nome do município |
| E | `CO_MUNICIPIO` | Código IBGE de 7 dígitos |
| F | `NO_CINE_ROTULO` | Nome do curso (rótulo Cine Brasil) |
| G | `CO_CINE_ROTULO` | Código do curso Cine (ex.: `"0413A01"`) |
| H–BZ | `NCURSO…` | **Número de Cursos** (71 colunas) |
| CA–FO | `VAG…` | **Vagas Oferecidas** (93) |
| FP–JD | `INSCR…` | **Candidatos Inscritos** (93) |
| JE–MS | `INGR…` | **Ingressantes** (93) |
| MT–QH | `MAT…` | **Matrículas** (93) |
| QI–TA | `CONCL…` | **Concluintes** (71) |

- ✅ Os três Anexos têm **exatamente 521 colunas úteis em todos os anos**. As dimensões declaradas `A1:TP…` de alguns anos vêm só de formatação além da coluna TA.
- ✅ Cada indicador é cruzado por Organização Acadêmica (Universidade, Centro Universitário, Faculdade, IF/Cefet) × Grau (Bacharelado, Licenciatura, Tecnológico) × Dependência Administrativa (Federal, Estadual, Municipal, Privada → Com/Sem Fins Lucrativos), com colunas de Total em cada nível.
- ✅ **Os Anexos não têm subtotais por Região ou UF.** Os tipos de linha são:
  - "Total Brasil", geral e por curso;
  - Município × Curso;
  - nos Anexos I e III, dois blocos de **pseudo-regiões** no fim da tabela, na coluna A: **`Distância`** (128 → 229 linhas por ano, uma por curso) e **`Exterior`** (20 → 120 linhas).
  
  Exemplo do Anexo I 2024: 354 linhas Brasil, 229 Distância, 120 Exterior e o restante Município × Curso. As pseudo-regiões não entram na contagem de "níveis geográficos" do 02. Elas aparecem em 04 › `niveis_agregacao`, com os padrões `v.v..vvv` e `v....vvv`.
- ✅ **No EaD, cursos, vagas e inscritos não são distribuídos por município.** As notas dizem: Anexo III, nota 2 (`A209236` em 2024), "os cursos a distância são computados somente a nível Brasil"; Anexo III, nota 6, e Anexo I, notas 6 e 7, "o número de vagas e inscritos não são coletados por local de oferta". Nas linhas Município × Curso do Anexo III, as colunas de Cursos (H–BZ), Vagas (CA–FO) e Inscritos (FP–JD) aparecem como **0**. É um **zero estrutural**, não ausência real. Ingressantes, Matrículas e Concluintes vêm distribuídos por município. Exemplo: Anexo III 2024, linha 243 (Alta Floresta D'Oeste, Administração): H = 0, CA = 0, FP = 0, JE = 15, MT = 31, QI = 4. Os valores de cursos, vagas e inscritos EaD ficam nas linhas `Distância` (por exemplo, a linha 208884).
- ✅ Os rótulos dos indicadores na linha 7 vêm precedidos de mais de 140 espaços (por exemplo, `H7` = "␣␣␣…Número de Cursos").
- ✅ Os Anexos II e III **somados** reproduzem o universo do Anexo I, a julgar pelos títulos e subtítulos. 🔶 A igualdade numérica (I = II + III) **não foi testada**: isso é validação de conteúdo, fora do escopo.

---

## 2. Principais problemas de padronização

Ordem de gravidade para a modelagem.

### 2.1 Críticos

| # | Problema | Onde | Selo |
|---|---|---|---|
| C1 | **Célula vazia não significa zero de forma consistente.** Na `4.1 Vagas e Inscritos` de 2023, os zeros vêm como células inexistentes (38.427 células em 41 colunas). As vagas e inscritos **a distância só existem no Total Brasil**: `H13` = 19.180.966 e `H15` (Total Norte) vazio. Nos outros anos, a mesma tabela usa 0 explícito. | Sinopse 2023 `4.1` (colunas H, K, L, M…); também `4.3` 2021–2022 (colunas AP, CK, EF) e `5.7` 2022 (28 colunas, 6 linhas) | ✅ fato / ⚠️ significado |
| C2 | **Marcador "." em colunas numéricas.** As colunas `Privada > Total` da `4.3` têm `'.'` (2019, 2.138 células) e `'. '` (2020, 2.008 células). Em 2021–2022 as mesmas colunas aparecem vazias. O significado não está documentado nas notas (🔶 talvez "não se aplica" ou "dado omitido"). | Sinopse `4.3` 2019–2022, colunas AP, CK, EF | ✅ fato / ⚠️ significado |
| C3 | **Rótulo trocado em relação ao conteúdo nas colunas B/C dos Anexos.** Em 2023–2024, `B6` = "Unidade da Federação", mas a coluna contém o código (`B12` = `CO_UF`, valores 11–53). `C6` = "Código da UF", mas contém o nome (`C12` = `NO_UF`). Em 2017–2022 a ordem é a inversa: B = nome, C = código. **O código da linha 12 corresponde ao conteúdo, e o rótulo da linha 6 não.** | Anexos I, II e III 2023–2024 | ✅ |
| C4 | **Mesclagens desalinhadas no cabeçalho (defeito da origem).** Na `4.1`, a mesclagem "Candidatos Inscritos" começa em `AB8`, e não em `AA8`. A coluna `AA` ("Total" dos Inscritos de Universidade) fica sem rótulo de indicador, e o mesmo ocorre em `BE` e `CI`. As colunas `AP`/`AQ` (Vagas de Centro Universitário) ficam fora da mesclagem de organização acadêmica (`AR7:BS7`). Acontece também em `4.15` (`IR`), `5.1` (`AL`) e `5.2` (`AK`). O nível faltante está marcado com **∅** e a coluna foi enviada para **revisão manual** (63 colunas em 35 abas). 🔶 Pela lógica do layout, `AA` = Inscritos > Total, mas isso precisa ser confirmado visualmente ou por soma. | Sinopse 2017–2024 (`4.1` em todos os anos; `4.15` até 2023; `5.1`/`5.2` até 2023) | ✅ defeito / 🔶 leitura correta |
| C5 | **Totais misturados com detalhes nas mesmas linhas e colunas.** Na Sinopse, as linhas "Total Brasil", "Total <Região>" e "Total <UF>" ficam intercaladas com as de municípios. Nas colunas, cada nível hierárquico tem seu "Total". Sem separação, qualquer soma duplica valores. | Todas as tabelas | ✅ |
| C6 | **Zeros estruturais no EaD (Anexos I e III).** Nas linhas Município × Curso, as colunas de Cursos, Vagas e Inscritos valem 0 porque o EaD não é computado por município. Esses zeros **não podem** ser lidos como "nenhum curso" ou "nenhuma vaga". Os valores reais estão nas linhas `Distância`. Já Ingressantes, Matrículas e Concluintes são distribuídos por município do polo. No Anexo I (presencial + EaD), as linhas municipais misturam as duas lógicas. 🔶 Confirmar se o Anexo I municipal contém só a parte presencial de cursos, vagas e inscritos. | Anexos I e III, todos os anos (notas 2, 6 e 7) | ✅ fato / 🔶 extensão ao Anexo I |
| C7 | **Totais não aditivos nas tabelas de docentes.** As notas 3–6 da `2.1` (2024) dizem que cada docente é contado uma única vez em cada nível de agregação: "o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios…". A nota 7 diz o mesmo para organização acadêmica e dependência administrativa. Somar municípios **não** reproduz o total da UF. | Sinopse 2.x (verificar o mesmo nas 1.x) | ✅ |

### 2.2 Altos

| # | Problema | Onde | Selo |
|---|---|---|---|
| A1 | **Ordem das colunas identificadoras muda.** Em várias tabelas, até 2023 `C` = "Nível Acadêmico do Curso", `D` = Município e `E` = Código. Em 2024, `C` = Município, `D` = Código e `E` = Nível Acadêmico. Afeta 3.1, 4.1, 4.2, 4.6–4.8, 4.11, 5.1, 5.5–5.7, 5.10, 6.1, 6.5–6.7, 6.10 e 7.1. | Sinopse 2024 | ✅ |
| A2 | **Mudança de categorias com efeito de definição.** Deficiência: "Autismo Infantil", "Síndrome de Asperger", "Síndrome de Rett", "Transtorno Desintegrativo da Infância" e "Múltipla" (2017–2019/20) → "Transtorno Global do Desenvolvimento (TGD)" (2021–2022) → "Transtorno do Espectro Autista (TEA)" (2023–2024) e "Visão Monocular" (2024). Reserva de vagas: a categoria "Étnico" (2017–2023) é substituída em 2024 por 8 novas categorias (Preto/Pardo/Indígena, Quilombola, Idoso, Refugiado, Transgênero, Internacional, Medalhista, Comunidade Tradicional), e as tabelas 4.15, 5.14 e 6.14 passam de 267 para 603 colunas. | Sinopse 2.9, 4.9, 4.10, 5.8, 5.9, 6.8, 6.9; 4.15–4.17, 5.14–5.16, 6.14–6.16 | ✅ mudança / ⚠️ comparabilidade |
| A3 | **Colunas "fantasma" em 2020.** As abas `3.2` e `4.4` de 2020 têm cabeçalho estendido até as colunas HK e IZ (219 e 285 colunas, contra 75 e 97 nos outros anos), sem nenhum dado. Também em 2020, outras abas têm dimensão declarada muito maior que a área útil (por exemplo, `2.1` com `A1:DC758` e útil `AK`). | Sinopse 2020 | ✅ |
| A4 | **Códigos Cine com aspas literais.** Todas as células da coluna G dos Anexos guardam o código entre aspas: `"0413A01"` (por exemplo, `G14` do Anexo I 2024). As aspas fazem parte do texto. Sem as aspas, todos os códigos seguem o padrão 4 dígitos + letra + 2 dígitos. | Anexos, todos os anos | ✅ |
| A5 | **"Docentes" com definições diferentes.** As tabelas 2.1–2.9 contam "Docentes em **Exercício**", e a 2.10 (nova em 2023) conta "Docentes **das IES** Comunitárias e/ou Confessionais". 🔶 Pode ser outro universo de contagem. | Sinopse 2.10 | ✅ título / 🔶 definição |
| A6 | **Unidade geográfica de referência diferente.** As tabelas 1.x e 2.x usam o município da **sede/reitoria** da IES. As tabelas 3.x a 7.x e os Anexos usam o **local de oferta** do curso. No EaD, o local de oferta é o polo, mas só para ingressantes, matrículas e concluintes (ver C6). | Sinopse e Anexos | ✅ (notas de rodapé) |
| A7 | **Pseudo-regiões na coluna "Região Geográfica"**: `Distância` (Anexos I e III) e `Exterior` (Anexos I e III e várias tabelas 4.x a 7.x da Sinopse). Não correspondem a regiões do IBGE e não têm código. | Anexos I e III; Sinopse | ✅ |

### 2.3 Médios e baixos

| # | Problema | Onde |
|---|---|---|
| M1 | Nomes de aba variam: `'2.4 '` → `'2.4'` (também 2.6 e 2.7, a partir de 2019); `'7 Dados Gerais'` (2018–2020) ↔ `'Dados Gerais'`; Anexo II: `8.2` → `8_2` (2023) → `8.2` (2024). | Sinopse e Anexo II |
| M2 | Chamadas de nota coladas aos rótulos, mudando entre anos: "…Administrativa1-3" (2017) / "…1-7" (2024); "Nome e Código do Curso de Graduação3/4/1-6". Na comparação foram removidas por normalização; nos catálogos os rótulos originais foram preservados. | Todas |
| M3 | Espaços à esquerda ou à direita em rótulos ("Total ", "Pública ", "Vestibular ") e mais de 140 espaços antes dos rótulos de indicador nos Anexos. | Todas |
| M4 | Números como texto em poucos casos: `CO_UF` e `CO_MUNICIPIO` nos Anexos I e II de **2020**; uma célula em `6.8` 2020 (D) e duas em `2.3` 2023 (EO, EP). **Nos demais casos (99,99%), os números são valores numéricos nativos.** | Anexos 2020; casos pontuais |
| M5 | Erros de digitação nos títulos: "segundo segundo" (5.10 de 2022), espaços duplos. A célula A2 da `4.4` traz o tema "Matrículas", embora a aba esteja na seção Processos Seletivos. Na `5.12` de 2021, o cabeçalho de A é "Brasil / Regiões" e não "Região Geográfica". | Sinopse |
| M6 | Algumas capas de seção de 2023–2024 declaram dimensões grandes (`I1:V1171`), mas só têm o texto da capa (por exemplo, `I16` = "3 Cursos"). | Sinopse 2023–2024 |
| M7 | **Variações de espaço em categorias de linha.** Em 2020–2022, os nomes de região ("Norte", "Sul" etc.) e "Exterior" aparecem também com espaços extras em parte das tabelas. Uma junção por texto exato criaria categorias duplicadas. Os valores originais estão em 05 › `categorias_linhas`. | Sinopse 2020–2022 |
| M8 | **Coluna oculta**: `BI` da `6.5 Características do Aluno` em 2017 e 2018. Ela desaparece em 2019 (61 → 60 colunas) e é a única "não identificada" da 6.5. | Sinopse 2017–2018 |

### 2.4 Abas que exigem revisão manual

| Aba | Motivo |
|---|---|
| `7.4` (2023–2024) | Tabela "Dados Gerais em IES Comunitárias e/ou Confessionais", com vários indicadores na mesma aba (cursos, vagas, inscritos, ingressantes, matrículas, concluintes, matrículas trancadas e desvinculadas, transferidos e falecidos). Não é uma contagem única. Esses indicadores **também aparecem nas tabelas 7.1–7.3 desde 2017**, para todas as IES. *(Corrigido: uma versão anterior deste relatório dizia que eles só existiam na 7.4.)* |
| `4.1` (todos os anos), `4.15`, `5.1`, `5.2` (2017–2023) | Mesclagens desalinhadas (C4). |
| `3.2` e `4.4` de 2020 | Colunas fantasma (A3). |
| `4.3` 2019–2022 | Marcador "." e células ausentes (C2). |
| `4.1` 2023 | Zeros omitidos e EaD só no total nacional (C1). |

A lista completa está em `02_catalogo_abas.xlsx` (coluna `revisao_manual` = "sim": 35 abas de dados, mais todas as auxiliares) e em `03_catalogo_colunas.xlsx` (coluna `alerta_rotulo`).

---

## 3. Comparação estrutural entre os anos

### 3.1 Abas

- ✅ 82 das 85 chaves de tabela estão presentes em todos os anos.
- ✅ **Adicionadas em 2023:** `1.2` (IES Comunitárias/Confessionais), `2.10` (Docentes das IES Comunitárias/Confessionais) e `7.4` (Dados Gerais Comunitárias/Confessionais).
- ✅ Nenhuma tabela foi removida. Tabelas como 2.4, 2.6 e 2.7, que parecem ter sumido, foram apenas renomeadas (espaço final).

### 3.2 Colunas: pareamento entre anos consecutivos

São 75.009 pareamentos (`05_comparacao_estrutural.xlsx`, aba `pareamento_colunas`).

| Classificação | Anexo I | Anexo II | Anexo III | Sinopse | Total |
|---|---|---|---|---|---|
| Equivalência confirmada | 3.126 | 2.605 | 2.605 | 57.601 | 65.937 |
| Equivalência provável | 519 | 1.040 | 1.040 | 3.600 | 6.199 |
| Equivalência parcial | 2 | 2 | 2 | 0 | 6 |
| Não comparável | 0 | 0 | 0 | 0 | 0 |
| Correspondência não identificada | 0 | 0 | 0 | 2.867 | 2.867 |

**Critérios.** A aba `legenda` do 05 traz a definição completa.
- **Confirmada (estrutural)**: mesmo código (Anexos) ou mesmo caminho hierárquico completo (Sinopse), mesma posição, mesmo título e subtítulo (sem o ano) e mesmas notas de rodapé.
- **Provável**: tudo igual, mas mudou a posição ou as notas. Nos Anexos, 100% dos casos "prováveis" se devem só a notas de rodapé alteradas, em 2018 e 2023.
- **Parcial**: os 6 casos são a troca B/C dos Anexos em 2023 (C3).
- **Não identificada**: categorias novas ou removidas (A2), colunas fantasma de 2020 (A3) e reorganizações pontuais.

⚠️ **Limite desta classificação.** "Equivalência confirmada" é uma confirmação **estrutural**: mesmo lugar, mesmo rótulo, mesmas notas. **Não** prova que a definição do indicador no Censo ficou igual. Nenhum par foi classificado só por semelhança de nome: o pareamento exige o caminho hierárquico completo ou o código da variável. O rótulo final sozinho gera no máximo "parcial".

⚠️ **Por que "Não comparável" ficou zerado.** A regra automática só detecta mudança de universo no título e no subtítulo, e nenhuma tabela mudou de universo entre anos. As mudanças de **categoria** (A2) aparecem como "não identificada". Na prática, as séries de deficiência e de reserva de vagas devem ser tratadas como **não comparáveis no nível da categoria** até haver uma tabela de correspondência validada.

### 3.3 Granularidade e identificadores

- ✅ A granularidade das linhas não muda em nenhuma tabela: Município (Sinopse) e Município × Curso (Anexos). O que cresce é a **cobertura**. Exemplo: a 4.2 Ingressantes passa de ~1.700 para ~3.400 linhas, com a expansão de municípios com polos EaD. O Anexo III vai de 42 mil para 209 mil linhas.
- ✅ Códigos Cine: de 342 (2017) a 353 (2024) no Anexo I. A troca é pequena até 2023 (0–7 por ano) e grande em **2024**: 18 entram e 19 saem no Anexo I, 22 entram e 16 saem no Anexo III. 🔶 Isso sugere revisão da tabela de rótulos Cine em 2024. Antes de qualquer série histórica por curso, é preciso montar uma correspondência entre os códigos.
- ✅ Em todos os anos e anexos, o número de códigos Cine distintos é igual ao número de nomes distintos. 🔶 Isso indica, mas não prova, uma relação 1:1 entre código e nome dentro de cada ano.

---

## 4. Conjuntos mais adequados para iniciar a modelagem

| Prioridade | Conjunto | Por quê | Cuidados |
|---|---|---|---|
| **1ª** | **Anexo II (presencial)**, seguido de **Anexos I e III** | Estrutura **idêntica** nos 8 anos (521 colunas). **Códigos de variável estáveis** na linha 12, com 0 colunas não pareadas. Têm código de município IBGE e código Cine (chaves naturais). Sem subtotais regionais misturados. Seis indicadores centrais. O **Anexo II** é o mais simples: só presencial, sem pseudo-regiões e sem zeros estruturais. | Ler o cabeçalho pela linha 12 (código), não pela linha 6 (C3). Remover as aspas dos códigos Cine só na transformação, mantendo o original. Marcar as linhas "Total Brasil" como agregado. **Anexos I e III:** tratar as linhas `Distância` e `Exterior` como entidades próprias e marcar os zeros estruturais de cursos, vagas e inscritos EaD nas linhas municipais (C6). Volume grande: até 213 mil linhas × 521 colunas por ano. |
| **2ª** | **Sinopse: tabelas estáveis** (1.1, 2.1–2.8, 3.1–3.3, 4.1–4.8, 4.11–4.14, 5.1–5.7, 5.10–5.13, 6.1–6.7, 6.10–6.13, 7.1–7.3) | Quase todas as colunas são "confirmadas" entre anos. Trazem recortes que os Anexos não têm (docentes, sexo, cor/raça, idade, financiamento, turno, forma de ingresso). | Não há código de variável: as colunas dependem do caminho hierárquico. Ordem dos identificadores muda em 2024 (A1). Defeitos de mesclagem (C4) e de células vazias (C1, C2). Subtotais intercalados (C5). **Totais de docentes não aditivos (C7).** Referência geográfica sede × oferta (A6). |
| **3ª** | **Sinopse: tabelas com quebra de categoria** (2.9, 4.9, 4.10, 5.8, 5.9, 6.8, 6.9, 4.15–4.17, 5.14–5.16, 6.14–6.16) | Têm conteúdo relevante, mas a lista de categorias muda. | Exigem uma tabela de correspondência de categorias, com decisão metodológica antes da série histórica. |
| **Por último** | `7.4`, `1.2`, `2.10` (só 2023–2024) | Séries curtas. A 7.4 mistura vários indicadores. | Revisão manual antes da modelagem. |

🔶 **Sugestão para a próxima etapa** (depende da sua autorização): começar pelos Anexos com um modelo **longo**, com chave `ano × município × curso_cine × indicador × org_acadêmica × grau × dependência × categoria_privada`. Ele seria derivado da gramática dos códigos da linha 12 (ver 06 §1.5), que antes precisa ser validada.

---

## 5. Testes realizados

| Teste | Resultado |
|---|---|
| Integridade dos 662 perfis (JSON válido, campos obrigatórios, sem erro de leitura, sem colisão de nomes) | ✅ 662/662 |
| Nº de abas: inventário (01) × catálogo (02) × perfis × soma `n_abas` dos workbooks | ✅ 662 = 662 = 662 = 662 |
| Nº de colunas por aba no 03 = coluna útil máxima no perfil | ✅ 0 divergências em 550 abas |
| Linhas do bloco de dados no 02 = soma das assinaturas de linha no perfil | ✅ 0 divergências |
| Células presentes por coluna no 04 = soma das classes no perfil | ✅ 0 divergências em 84.894 colunas |
| Os 6 arquivos .xlsx/.md abrem e têm conteúdo (relidos com openpyxl/pandas) | ✅ |
| Mesclagens dentro da área de dados | ✅ 0 |
| Colunas de medida sem rótulo | ✅ 0, exceto as 63 marcadas com ∅ (defeito da origem) e as colunas fantasma de 2020 |
| Caminhos de cabeçalho duplicados na mesma aba | ✅ só nas colunas fantasma de 2020 (sem dados) |
| Códigos Cine: padrão `\d{4}[A-Z]\d{2}`, aspas literais, nº de códigos = nº de nomes | ✅ 100% no padrão, 100% com aspas, igualdade em 24/24 arquivos |
| Medidas: decimais / negativos / textos | ✅ 0 / 0 / 0 (só os marcadores "." de C2) |
| Inspeção visual de cabeçalhos crus (linhas 6–12 e mesclagens) | Feita em 1.1, 4.1, 4.2, 4.4 (2017, 2023, 2024), 3.2 (2020) e Anexo II 2017 |

**Correções feitas durante a validação**, registradas para transparência:
1. A extensão de rótulos mesclados em níveis inferiores rotulava errado as colunas da 4.1 (AA recebia "Vagas Oferecidas"). Agora só o 1º nível (legenda geral) é estendido. Lacunas viram ∅ e vão para revisão.
2. Mesclagens verticais repetiam o rótulo no caminho. Foi corrigido pela célula de origem da mesclagem.
3. O filtro de valores especiais tratava "." como número. Foi corrigido, e os marcadores agora aparecem em 04 › `valores_nao_numericos`.
4. Cada afirmação do relatório foi conferida contra os dados (notas de rodapé, contagens, MD5 dos ZIPs). Essa conferência corrigiu a referência geográfica das tabelas 2.x (sede, e não oferta) e o número de tabelas com Nível Acadêmico (20). Ela também revelou C6, C7, A7, M7 e M8.
5. **Integridade dos originais:** os MD5 dos 8 ZIPs, recalculados no fim, são idênticos aos da etapa de reconhecimento.
6. **Correção de afirmação anterior:** na etapa de reconhecimento eu disse que os números estavam "gravados como texto". **Isso estava errado**: o script de inspeção convertia os valores em texto ao imprimir. Os números são nativos (ver M4).
7. **Correção de afirmação anterior:** eu disse que os rótulos dos indicadores dos Anexos estavam "em branco". Na verdade, estão precedidos de mais de 140 espaços (M3).

---

## 6. Limitações do diagnóstico

1. **Só estrutura, sem conteúdo.** Não foram testadas somas (detalhe = total, Anexo I = II + III, município → UF → Brasil) nem a coerência dos números entre anos ou entre a Sinopse e os Anexos.
2. **Documentação oficial pouco consultada.** A `Nota Informativa 02.pdf` de 2023 foi lida depois (ver §8). As notas técnicas e o dicionário do Censo não foram consultados. Por isso as equivalências são **estruturais**, e as hipóteses marcadas com 🔶 dependem dessa documentação.
3. **Os arquivos ODS não foram analisados.** O diagnóstico vale para os XLSX. A equivalência XLSX ↔ ODS não foi verificada.
4. **Detecção automática de cabeçalhos.** A linha de início dos dados foi detectada pelo primeiro "Total Brasil" na coluna A. Os níveis do cabeçalho foram reconstruídos por mesclagens e por propagação limitada ao grupo pai. Funcionou nas 550 abas, mas casos com defeito na origem (C4) dependem de revisão humana.
5. **Formatação ignorada.** Não foram lidos estilos, cores, fontes nem formatos numéricos. Linhas e colunas ocultas foram só contadas: nenhuma linha oculta, e uma coluna oculta (M8). Rótulos que só existam em caixas de texto ou imagens (por exemplo, a capa `Sinopse_Estatística`) não foram capturados.
6. **Valores distintos com limite.** Nas colunas de medida, só os valores **não numéricos** distintos foram guardados (até 300 por coluna). Nas colunas identificadoras, até 30.000. Nenhuma coluna identificadora atingiu o limite.
7. **Exemplos limitados.** O 04 traz até 5 linhas por aba, com os identificadores e as 12 primeiras medidas. A linha completa pode ser consultada na planilha original pelo número da linha.
8. **"Unidade de medida presumida"** vem do título ("Número de…" = contagem). Não há unidade explícita nas planilhas.
9. **A classificação de equivalência é feita entre anos consecutivos.** Para pares não consecutivos (por exemplo, 2017 × 2024), é preciso encadear os pareamentos.

---

## 7. Entregáveis

| Arquivo | Conteúdo principal |
|---|---|
| `01_inventario_workbooks.xlsx` | `workbooks` (32 linhas: arquivo, ZIP, caminho no ZIP, tamanho, nº de abas, abas auxiliares) e `abas` (662 linhas: ordem, nome original e `repr` com espaços visíveis, dimensão declarada × útil, tipo, parte XML). |
| `02_catalogo_abas.xlsx` | `abas` (662: título com célula, tema, universo, linhas de cabeçalho, linha de códigos, início e fim dos dados, identificadores, nº de registros, níveis geográficos, unidade, fonte, notas, alertas, revisão manual) e `notas_rodape` (3.072 notas com célula). |
| `03_catalogo_colunas.xlsx` | 84.894 colunas: papel, código da variável e célula, níveis 1–6 do cabeçalho com a célula de origem de cada um, rótulo completo, método de reconstrução, coluna de total, tipo de dado e alerta. |
| `04_perfil_dados.xlsx` | `resumo_abas`, `niveis_agregacao` (contagem por nível geográfico e por padrão de preenchimento, com exemplo), `exemplos` (até 5 por aba), `perfil_colunas` (presentes, inexistentes, texto vazio, numéricos, como texto, códigos especiais, mín./máx.) e `valores_nao_numericos`. |
| `05_comparacao_estrutural.xlsx` | `legenda`, `abas_x_anos`, `evolucao_tabelas` (mudanças ano a ano), `resumo_pareamento`, `pareamento_colunas` (75.009 pares com classificação e evidências), `categorias_cabecalho` e `categorias_linhas`. |
| `06_dicionario_variaveis.md` | Universo e títulos dos Anexos, identificadores, indicadores e faixas de colunas, categorias, gramática observada dos códigos, ficha de cada tabela da Sinopse e evolução das categorias de linha. |
| `07_relatorio_estrutura.md` | Este documento. |

*Os scripts de diagnóstico foram copiados para `_diagnostico_estrutura/scripts/` (com README). As cópias temporárias dos XLSX ficam fora da pasta do projeto. Nenhum ZIP ou planilha original foi alterado.*

---

## 8. Nota Informativa de 2023 (`Nota Informativa 02.pdf`, ZIP de 2023)

Documento do Inep (Nota SEI nº 1713030, Processo 23036.001038/2019-14), assinado em **13/10/2025**. Uma cópia do PDF foi extraída para a pasta temporária. O ZIP não foi alterado.

✅ **Conteúdo da nota:**
- **Erro identificado:** depois da divulgação do Censo 2023 (03/10/2024), o Inep identificou um salto de **1.185 para 24.428** vagas para **programas especiais** nos Institutos Federais (+1.960%). O responsável principal foi o **IFMT**, código de IES 3164. O IFMT informou dados errados de **vagas e inscritos**.
- **Classificação:** erro "a.2 — Erro grave de conteúdo (Tipo II)", conforme o Guia de Tratamento de Erros de Divulgação do Inep.
- **Correção:** o IFMT retificou os dados, que foram atualizados na base SUP_CURSO e em todos os produtos.
- **Tabelas da Sinopse 2023 corrigidas:** `4.1` (Vagas e Inscritos), `7.2`, `7.3`, `8.1`, `8.2` e `8.3` (os três Anexos).
- **Variáveis dos microdados corrigidas:** `QT_VG_TOTAL`, `QT_VG_TOTAL_DIURNO`, `QT_VG_TOTAL_NOTURNO`, `QT_VG_TOTAL_EAD`, `QT_VG_NOVA`, `QT_VG_REMANESC`, `QT_VG_PROG_ESPECIAL`, `QT_INSCRITO_TOTAL`, `QT_INSCRITO_TOTAL_DIURNO`, `QT_INSCRITO_TOTAL_NOTURNO`, `QT_INSCRITO_TOTAL_EAD`, `QT_INSC_VG_NOVA`, `QT_INSC_VG_REMANESC` e `QT_INSC_VG_PROG_ESPECIAL`.
- **Outros produtos:** o Painel de Estatísticas (aba "Cursos") e o Resumo Técnico (Tabela 6 e Figura 1).

**Implicações para o projeto:**
- ⚠️ **Não dá para saber, pela estrutura, se as planilhas de 2023 deste ZIP são a versão corrigida.**
  - As datas internas do ZIP sugerem republicação: a maioria dos arquivos de 2023 está datada de 14/07/2026, depois da nota.
  - Porém o `anexo_I_tab_8_1_dados_gerais_por_curso_2023.xlsx` está datado de **17/09/2025**, *antes* da nota (13/10/2025). 🔶 A correção pode ter sido feita antes de a nota ser assinada, mas isso não está confirmado.
  - Uma verificação de conteúdo resolveria a dúvida: vagas e inscritos do IFMT (municípios de MT, IF Federal) em 2023 comparados a 2022 e 2024, e consistência entre 4.1, 7.2, 7.3 e os Anexos.
- ⚠️ Os dados de vagas e inscritos de 2023 baixados **antes de outubro de 2025** (por exemplo, por terceiros ou em versões antigas) podem conter o erro. Em qualquer integração com outras fontes, convém registrar a versão e a data do arquivo.
- ✅ A nota cita variáveis dos **microdados** do Censo (`QT_VG_*`, `QT_INSC*`). Isso confirma que existe uma fonte em nível de curso com nomes de variáveis oficiais e documentados, útil para validar as definições dos indicadores da Sinopse.
- A nota não trata das demais anomalias deste diagnóstico (C1, C2, C4, C6). Elas continuam em aberto.

### 8.1 Verificação: os dados do IFMT de 2023 estão corrigidos?

Script: `scripts/s7_ifmt.py`. Recorte: colunas de **Institutos Federais (IF) – Federal**, Vagas Oferecidas e Candidatos Inscritos, em Mato Grosso (o IFMT é o único IF do estado) e no Brasil, 2022–2024. A Sinopse não separa vagas por tipo, então a categoria "programas especiais" citada na nota **não pode** ser verificada diretamente. A verificação é feita pelos totais.

| Fonte (IF Federal) | Recorte | 2022 | **2023** | 2024 |
|---|---|---|---|---|
| Anexo II e Anexo I (soma dos municípios com CO_UF = 51) | MT – Vagas | 3.111 | **2.540** | 2.165 |
| Anexo II e Anexo I (soma dos municípios com CO_UF = 51) | MT – Inscritos | 3.111 | **6.500** | 3.386 |
| Sinopse 7.2 (presencial) | MT – Vagas / Inscritos | — | **2.540 / 6.500** | — |
| **Sinopse 4.1** (linha "Total Mato Grosso", Graduação, presencial) | MT – Vagas | — | **66.800** | 2.165 |
| **Sinopse 4.1** (linha "Total Mato Grosso", Graduação, presencial) | MT – Inscritos | — | **67.701** | 3.386 |
| Anexo II / Sinopse 7.2 | Brasil – Vagas presenciais | 107.089 | **105.018** | 107.192 |
| **Sinopse 4.1** | Brasil – Vagas presenciais | 107.089 | **169.278** | 107.192 |
| Anexo II / Sinopse 7.2 | Brasil – Inscritos presenciais | 407.388 | **411.086** | 368.093 |
| **Sinopse 4.1** | Brasil – Inscritos presenciais | 407.388 | **472.287** | 368.093 |
| Anexo I − Anexo II = Sinopse 7.3 | Brasil – Vagas / Inscritos EaD | 13.729 / 57.738 | **15.249 / 34.905** | 10.927 / 35.935 |
| **Sinopse 4.1** | Brasil – Vagas / Inscritos EaD | 13.729 / 57.738 | **16.154 / 35.605** | 10.927 / 35.935 |

*(Na 4.1 de 2024, o script somou as linhas "Total Brasil" e "Total Brasil – Graduação". Os valores mostrados para 2024 estão divididos por 2 e conferem com os Anexos. Os traços indicam que o script não localizou a linha de MT naquela tabela ou ano, por diferença de layout.)*

**Conclusões:**
- ✅ **Anexos I, II e III e tabelas 7.2 e 7.3 de 2023: consistentes com dados corrigidos.** As vagas do IF em MT (2.540) estão em linha com 2022 (3.111) e 2024 (2.165). Os totais nacionais não mostram salto. Os Anexos, a 7.2 e a 7.3 batem entre si: Anexo II = 7.2 e Anexo I − Anexo II = 7.3.
- ⚠️ **Tabela 4.1 de 2023: NÃO está corrigida neste ZIP.** Ela traz 66.800 vagas e 67.701 inscritos para o IF em MT, contra 2.540 e 6.500 nas demais tabelas do mesmo ano. A diferença no Brasil é exatamente a mesma de MT: vagas 169.278 − 105.018 = **64.260** = 66.800 − 2.540; inscritos 472.287 − 411.086 = **61.201** = 67.701 − 6.500. O excesso está todo em Mato Grosso/IF, o que é compatível com o erro do IFMT descrito na nota. A 4.1 de 2023 também diverge levemente no EaD do IF (+905 vagas e +700 inscritos em relação à 7.3).
- 🔶 O excesso da 4.1 (+64 mil vagas) é maior que o salto citado na nota (+23 mil vagas de programas especiais). A nota cita apenas o salto mais visível; a correção abrangeu todas as variáveis de vagas e inscritos (item 4.2 da nota). Isso explicaria a diferença, mas não pode ser confirmado com a Sinopse.
- 🔶 Indício compatível: a 4.1 de 2023 é também a aba com estrutura atípica (zeros omitidos e EaD só no total Brasil, ver C1). Isso sugere que ela veio de um processamento ou versão diferente das demais.
- Observação lateral: nos Anexos de 2022, os inscritos do IF em MT são idênticos às vagas em cada grau (1.195, 660 e 1.256). É um padrão incomum, que não foi investigado.

**Recomendação:** não usar vagas e inscritos da `4.1` de 2023 para Mato Grosso e para os agregados de IF, Região Centro-Oeste e Brasil. Usar a 7.2, a 7.3 ou os Anexos.

**Conferência com o site do Inep (30/10/2026)** ✅
- A página oficial de Sinopses da Educação Superior (gov.br/inep, atualizada em 14/07/2026) aponta para `https://download.inep.gov.br/informacoes_estatisticas/sinopses_estatisticas/sinopses_educacao_superior/sinopse_educacao_superior_2023.zip`. A página não traz aviso de retificação para 2023.
- Metadados do servidor: 381.866.951 bytes, Last-Modified 14/07/2026 18:09:05 GMT.
- Uma cópia foi baixada para a pasta temporária. O **MD5 é idêntico** ao do ZIP local (`3A6485A63B867E37B091075B3EC3F190`).
- **Conclusão:** a versão hoje publicada pelo Inep é exatamente a que foi analisada. **Não existe no site uma versão da `4.1` de 2023 diferente desta**, e a inconsistência descrita acima continua na publicação oficial, apesar de a nota informativa afirmar que a 4.1 foi corrigida.
- 🔶 A inferência de que a 4.1 é a tabela errada, e não as demais, se apoia em quatro pontos: (a) a nota descreve um aumento indevido; (b) a 4.1 é a única fora da série de 2022 e 2024; (c) Anexo II = 7.2 e Anexo I − II = 7.3 batem entre si; (d) a nota lista a 4.1 entre as tabelas corrigidas, o que é compatível com uma correção que não chegou ao arquivo publicado.
- Sugestão: relatar a divergência ao Inep (dadosabertos.deed@inep.gov.br, contato indicado na nota). Não foi enviado nenhum contato.

### 8.2 Investigação: inscritos iguais às vagas no IF de Mato Grosso

Scripts: `scripts/s8_if_insc_vagas.py`, `s8b_analise.py` e `s8c_padroes.py`. Fonte: Anexo II (presencial), 2017–2024. São 151.128 linhas município × curso, das quais foram usadas as colunas de total do IF: `VAG6`, `INSCR6`, `INGR6` e `MAT6` (os códigos são os mesmos em todos os anos). Universo analisado: linhas com vagas > 0.

| IF em Mato Grosso | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| Linhas (município × curso) | 49 | 51 | 53 | 48 | 57 | 58 | 51 | 53 |
| % de linhas com inscritos = vagas | 29% | **100%** | **100%** | **100%** | **100%** | **100%** | 0% | 0% |
| Vagas | 2.094 | 2.186 | 2.372 | 1.777 | 3.011 | 3.111 | 2.540 | 2.165 |
| Inscritos | 4.975 | 2.186 | 2.372 | 1.777 | 3.011 | 3.111 | 6.500 | 3.386 |
| Inscritos por vaga | 2,38 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 2,56 | 1,56 |
| Ingressantes | 1.725 | 2.164 | 2.371 | 1.733 | 1.128 | **6** | 1.725 | 1.404 |
| Matrículas | 6.038 | 6.234 | 7.293 | 6.640 | 7.607 | 7.410 | 8.126 | 6.666 |
| % de linhas com inscritos múltiplo de 100 | 0% | 0% | 0% | 0% | 5% | 3% | **100%** | 0% |

**Fatos verificados (✅):**
1. **Não é só 2022.** Em **2018–2022, 100% das linhas** do IF em MT têm inscritos exatamente iguais às vagas, curso a curso (por exemplo, Alta Floresta – Administração: 35 vagas e 35 inscritos em 2021 e 2022; linhas 17847 e 17903 do Anexo II). Nos demais IFs do país, a igualdade ocorre em 3,6%–9,2% das linhas. Nenhuma outra UF tem 100% em mais de um ano. Os únicos outros casos acima de 80% são Amapá 2020 (82%) e Roraima 2023 (100%, só 11 linhas).
2. **Em 2018–2020, os ingressantes também ficam praticamente iguais às vagas** (0,98–1,00 por vaga), um padrão de preenchimento total incomum. Nas demais UFs, a razão fica entre 0,72 e 0,79.
3. **2022: apenas 6 ingressantes** em 3.111 vagas (0,002 por vaga), distribuídos em 3 cursos (Cuiabá e Sorriso), enquanto as matrículas se mantêm (7.410). É o **único UF-ano de toda a série** com menos de 0,05 ingressante por vaga. Em 2021 a razão já é baixa (0,37).
4. **2023, dado já corrigido segundo a nota:** os inscritos são **100% múltiplos de 100** (38 cursos com 100, 12 com 200 e 1 com 300). Nos demais IFs, isso ocorre em ~1% das linhas. Mesmo corrigido, o valor tem aparência de estimativa arredondada.
5. **2024:** a distribuição volta a ser típica (valores irregulares; 23 linhas com inscritos menores que as vagas).

**Interpretação (🔶 hipóteses, não confirmadas):**
- Em 2018–2022, o IFMT provavelmente preencheu o campo de inscritos com o número de vagas, por falta do dado ou por algum procedimento próprio. A relação inscritos/vaga calculada para MT nesses anos **não é informativa**.
- Os 6 ingressantes de 2022 podem refletir um erro de declaração ou um calendário de seleção deslocado (ingresso registrado em outro ano). As matrículas estáveis tornam improvável a ausência real de ingresso.
- A nota informativa de 2023 corrigiu vagas e inscritos de **2023** apenas. Ela não menciona os anos anteriores, e os padrões de 2018–2022 seguem nas planilhas.

⚠️ **Recomendação:** marcar como **suspeitos** os inscritos do IF em MT de 2018–2022, os ingressantes de 2021–2022 e os inscritos de 2023. Isso afeta indicadores de concorrência (inscritos/vaga) e de ocupação (ingressantes/vaga) do IF, de Mato Grosso e do Centro-Oeste. Não corrigir nem imputar valores sem fonte oficial. A verificação pode ser aprofundada nos microdados do Censo, que trazem os dados por curso e por IES.

*Limitações: só o Anexo II (presencial) foi analisado. "IF em Mato Grosso" é a coluna de IF/Cefet Federal nas linhas com código de UF 51, que se presume ser o IFMT (único IF do estado); o código de IES não está nas planilhas.*

### 8.3 Investigação: o padrão aparece nos cursos a distância (EaD)?

Scripts: `scripts/s9_if_ead.py` e `s9b_analise_ead.py`. Fontes: Sinopse `7.3` (EaD; linhas "Total Mato Grosso" e "Total Brasil") e Anexo III (EaD; 1.030.624 linhas município × curso e `Distância`), 2017–2024.

**1. O padrão "inscritos = vagas" não pode ser testado para o IFMT no EaD.** ✅ Por desenho da publicação, cursos, vagas e inscritos EaD **não são distribuídos por UF nem por município**: valem 0 em **todas** as linhas municipais de todas as UFs, em todos os anos, e 0 na linha de MT da 7.3. Esses números só existem no total Brasil e nas linhas `Distância`, que são nacionais por curso e misturam todos os IFs.

**2. Linhas `Distância` (IF, nacional):** inscritos = vagas em 0%–29% dos cursos por ano (por exemplo, 2022: Segurança pública 1.000 = 1.000; Química formação de professor 250 = 250). Inscritos por vaga entre 2,2 e 7,6. 🔶 Há valores redondos e iguais em alguns cursos, mas **não é possível atribuí-los ao IFMT**.

**3. Ingressantes e matrículas EaD do IF em polos de MT** (Anexo III, que confere exatamente com a 7.3):

| IF – EaD em MT | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| Polos (7.3) | 6 | 9 | 7 | 7 | 19 | 19 | 22 | — |
| Ingressantes | 647 | 203 | 147 | **4** | **0** | **0** | 205 | 602 |
| Matrículas | 2.756 | 2.476 | 2.192 | 2.239 | 1.899 | 1.846 | 1.731 | 1.577 |
| Concluintes | 170 | 94 | 57 | 215 | 53 | 298 | **0** | 1 |

- ✅ No EaD, **anos sem ingresso são comuns**: 39 dos 160 pares UF-ano com matrículas EaD de IF têm 0 ingressantes, concentrados em 2018–2022 (por exemplo, Amazonas 2018–2022, Amapá 2020–2023, Goiás 2020–2022 e Maranhão 2021–2022). O ingresso EaD costuma ocorrer por turmas pontuais. Por exemplo, Matemática (formação de professor) teve 203 ingressantes em 2018 e nenhum até 2024.
- **Conclusão:** os zeros de ingresso EaD em MT (2020–2022) **não destoam** dos demais estados e, sozinhos, não indicam erro, ao contrário do presencial (§8.2), em que 2022 é um caso único na série. Ficam como pontos de atenção, sem confirmação de problema: concluintes = 0 em 2023 e matrículas desvinculadas = 0 em 2022 (7.3).

⚠️ **Limitação de atribuição:** no EaD, "IF em MT" são os polos localizados em MT de **qualquer** IF. Podem incluir polos de IFs de outros estados e excluem polos do IFMT fora de MT. Por isso, os números da tabela acima **não são o IFMT** propriamente. A verificação por instituição exige os microdados do Censo (código de IES 3164).
