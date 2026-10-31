# 06 — Dicionário de variáveis (diagnóstico estrutural)

> Gerado automaticamente a partir das cópias dos XLSX de 2017–2024, com revisão manual dos pontos sinalizados. Os rótulos são reproduzidos **como estão nas planilhas** (inclusive com erros de grafia e chamadas de nota coladas, como `…Administrativa1-3`). Para chegar à célula de origem de cada coluna, use `03_catalogo_colunas.xlsx` (colunas `celula_nivel_*` e `celula_codigo`).

**Convenções**

- *Indicador*: aquilo que a célula conta (cursos, vagas, matrículas…). *Dimensão/categoria*: os recortes do cabeçalho (organização acadêmica, dependência administrativa…).
- *Unidade*: todas as tabelas de dados são **contagens absolutas** (os títulos começam com "Número de…"). Não há percentuais, médias nem valores monetários. Em nenhuma coluna de medida foram encontrados decimais ou negativos (ver 04).
- *Linha (unidade de observação)*: as linhas são **agregados** (Brasil, Região, UF, Município e, nos Anexos, Município × curso). Não há microdados de alunos, docentes ou instituições.
- *Totais*: colunas cujo caminho contém "Total" são agregados de outras colunas da mesma aba. Linhas com "Total Brasil", "Total <Região>" e "Total <UF>" são subtotais misturados às linhas de detalhe.
- ⚠️ *Totais não aditivos*: nas tabelas de docentes (2.x), cada docente é contado uma vez em cada nível (notas 3–7). Somar municípios ou categorias **não** reproduz os totais.
- ⚠️ *Pseudo-regiões*: a coluna "Região Geográfica" também contém `Distância` (Anexos I e III) e `Exterior` (Anexos I e III e tabelas 4.x a 7.x da Sinopse).
- ⚠️ *Zeros estruturais*: nos Anexos I e III, cursos, vagas e inscritos EaD não são computados por município (notas 2, 6 e 7). Nas linhas municipais esses valores aparecem como 0, sem ser zero real, e os valores verdadeiros estão nas linhas `Distância`.
- ⚠️ *Referência geográfica*: as tabelas 1.x e 2.x usam a sede/reitoria da IES. As tabelas 3.x a 7.x e os Anexos usam o local de oferta.

## 1. Anexos I, II e III — Tabelas 8.1, 8.2 e 8.3 (dados gerais por curso)

### 1.1 Universo de cada anexo (subtítulo, célula A3) e título (A4)

| Conjunto | Ano | Subtítulo (A3) | Título (A4) |
|---|---|---|---|
| Anexo I — Tabela 8.1 | 2017 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2017 |
| Anexo I — Tabela 8.1 | 2018 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2018 |
| Anexo I — Tabela 8.1 | 2019 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2019 |
| Anexo I — Tabela 8.1 | 2020 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2020 |
| Anexo I — Tabela 8.1 | 2021 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2021 |
| Anexo I — Tabela 8.1 | 2022 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2022 |
| Anexo I — Tabela 8.1 | 2023 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2023 |
| Anexo I — Tabela 8.1 | 2024 | Cursos de Graduação - Presenciais e a Distância | 8.1 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2024 |
| Anexo II — Tabela 8.2 | 2017 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2017 |
| Anexo II — Tabela 8.2 | 2018 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2018 |
| Anexo II — Tabela 8.2 | 2019 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2019 |
| Anexo II — Tabela 8.2 | 2020 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2020 |
| Anexo II — Tabela 8.2 | 2021 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2021 |
| Anexo II — Tabela 8.2 | 2022 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2022 |
| Anexo II — Tabela 8.2 | 2023 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2023 |
| Anexo II — Tabela 8.2 | 2024 | Cursos de Graduação - Presenciais | 8.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2024 |
| Anexo III — Tabela 8.3 | 2017 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2017 |
| Anexo III — Tabela 8.3 | 2018 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2018 |
| Anexo III — Tabela 8.3 | 2019 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2019 |
| Anexo III — Tabela 8.3 | 2020 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2020 |
| Anexo III — Tabela 8.3 | 2021 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2021 |
| Anexo III — Tabela 8.3 | 2022 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2022 |
| Anexo III — Tabela 8.3 | 2023 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2023 |
| Anexo III — Tabela 8.3 | 2024 | Cursos de Graduação a Distância (EaD) | 8.3 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas e Concluintes nos Cursos de Graduação a Distância (EaD),  por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação, Município e Curso - Cine Rótulo - 2024 |

### 1.2 Colunas identificadoras (linha 12 = código da variável)

| Conjunto | Coluna | Código (linha 12) | Rótulo (linhas 6–7) | Tipo observado | Anos |
|---|---|---|---|---|---|
| Anexo I — Tabela 8.1 | A | `NO_REGIAO` | Região Geográfica | categórico | todos (2017–2024) |
| Anexo I — Tabela 8.1 | B | `CO_UF` | Unidade da Federação | código numérico | 2023, 2024 |
| Anexo I — Tabela 8.1 | B | `NO_UF` | Unidade da Federação | categórico | 2017, 2018, 2019, 2020, 2021, 2022 |
| Anexo I — Tabela 8.1 | C | `CO_UF` | Código da UF | código numérico | 2017, 2018, 2019, 2020, 2021, 2022 |
| Anexo I — Tabela 8.1 | C | `NO_UF` | Código da UF | categórico | 2023, 2024 |
| Anexo I — Tabela 8.1 | D | `NO_MUNICIPIO` | Município | textual/alta cardinalidade | todos (2017–2024) |
| Anexo I — Tabela 8.1 | E | `CO_MUNICIPIO` | Código do Município | código numérico | todos (2017–2024) |
| Anexo I — Tabela 8.1 | F | `NO_CINE_ROTULO` | Nome e Código do Curso de Graduação4 > Nome do Curso - Cine Rótulo | textual/alta cardinalidade | todos (2017–2024) |
| Anexo I — Tabela 8.1 | G | `CO_CINE_ROTULO` | Nome e Código do Curso de Graduação4 > Código do Curso - Cine Rótulo | textual/alta cardinalidade | todos (2017–2024) |
| Anexo II — Tabela 8.2 | A | `NO_REGIAO` | Região Geográfica | categórico | todos (2017–2024) |
| Anexo II — Tabela 8.2 | B | `CO_UF` | Unidade da Federação | código numérico | 2023, 2024 |
| Anexo II — Tabela 8.2 | B | `NO_UF` | Unidade da Federação | categórico | 2017, 2018, 2019, 2020, 2021, 2022 |
| Anexo II — Tabela 8.2 | C | `CO_UF` | Código da UF | código numérico | 2017, 2018, 2019, 2020, 2021, 2022 |
| Anexo II — Tabela 8.2 | C | `NO_UF` | Código da UF | categórico | 2023, 2024 |
| Anexo II — Tabela 8.2 | D | `NO_MUNICIPIO` | Município | textual/alta cardinalidade | todos (2017–2024) |
| Anexo II — Tabela 8.2 | E | `CO_MUNICIPIO` | Código do Município | código numérico | todos (2017–2024) |
| Anexo II — Tabela 8.2 | F | `NO_CINE_ROTULO` | Nome e Código do Curso de Graduação3 > Nome do Curso - Cine Rótulo | textual/alta cardinalidade | todos (2017–2024) |
| Anexo II — Tabela 8.2 | G | `CO_CINE_ROTULO` | Nome e Código do Curso de Graduação3 > Código do Curso - Cine Rótulo | textual/alta cardinalidade | todos (2017–2024) |
| Anexo III — Tabela 8.3 | A | `NO_REGIAO` | Região Geográfica | categórico | todos (2017–2024) |
| Anexo III — Tabela 8.3 | B | `CO_UF` | Unidade da Federação | código numérico | 2023, 2024 |
| Anexo III — Tabela 8.3 | B | `NO_UF` | Unidade da Federação | categórico | 2017, 2018, 2019, 2020, 2021, 2022 |
| Anexo III — Tabela 8.3 | C | `CO_UF` | Código da UF | código numérico | 2017, 2018, 2019, 2020, 2021, 2022 |
| Anexo III — Tabela 8.3 | C | `NO_UF` | Código da UF | categórico | 2023, 2024 |
| Anexo III — Tabela 8.3 | D | `NO_MUNICIPIO` | Município | textual/alta cardinalidade | todos (2017–2024) |
| Anexo III — Tabela 8.3 | E | `CO_MUNICIPIO` | Código do Município | código numérico | todos (2017–2024) |
| Anexo III — Tabela 8.3 | F | `NO_CINE_ROTULO` | Nome e Código do Curso de Graduação1-6 > Nome do Curso - Cine Rótulo | textual/alta cardinalidade | todos (2017–2024) |
| Anexo III — Tabela 8.3 | G | `CO_CINE_ROTULO` | Nome e Código do Curso de Graduação1-6 > Código do Curso - Cine Rótulo | textual/alta cardinalidade | todos (2017–2024) |

> ⚠️ **Rótulo × código das colunas B/C:** em alguns anos o rótulo da linha 6 ("Unidade da Federação" / "Código da UF") e o código da linha 12 (`NO_UF`/`CO_UF`) estão em ordens diferentes. A tabela acima mostra os pares exatamente como aparecem. O conteúdo das células deve ser conferido em 04 (perfil: categórico × código numérico).

### 1.3 Indicadores (nível 2 do cabeçalho, linha 7) e prefixos de código

| Conjunto | Indicador (rótulo) | Código da coluna total | Faixa de colunas | Nº de colunas | Unidade | Anos |
|---|---|---|---|---|---|---|
| Anexo I — Tabela 8.1 | Número de Cursos | `NCURSO` | H–BZ (2024) | 71 | contagem | todos (2017–2024) |
| Anexo I — Tabela 8.1 | Vagas Oferecidas | `VAGT` | CA–FO (2024) | 93 | contagem | todos (2017–2024) |
| Anexo I — Tabela 8.1 | Candidatos Inscritos | `INSCRT` | FP–JD (2024) | 93 | contagem | todos (2017–2024) |
| Anexo I — Tabela 8.1 | Ingressantes | `INGR` | JE–MS (2024) | 93 | contagem | todos (2017–2024) |
| Anexo I — Tabela 8.1 | Matrículas | `MATT` | MT–QH (2024) | 93 | contagem | todos (2017–2024) |
| Anexo I — Tabela 8.1 | Concluintes | `CONCLT` | QI–TA (2024) | 71 | contagem | todos (2017–2024) |
| Anexo II — Tabela 8.2 | Número de Cursos | `NCURSO` | H–BZ (2024) | 71 | contagem | todos (2017–2024) |
| Anexo II — Tabela 8.2 | Vagas Oferecidas | `VAGT` | CA–FO (2024) | 93 | contagem | todos (2017–2024) |
| Anexo II — Tabela 8.2 | Candidatos Inscritos | `INSCRT` | FP–JD (2024) | 93 | contagem | todos (2017–2024) |
| Anexo II — Tabela 8.2 | Ingressantes | `INGR` | JE–MS (2024) | 93 | contagem | todos (2017–2024) |
| Anexo II — Tabela 8.2 | Matrículas | `MATT` | MT–QH (2024) | 93 | contagem | todos (2017–2024) |
| Anexo II — Tabela 8.2 | Concluintes | `CONCLT` | QI–TA (2024) | 71 | contagem | todos (2017–2024) |
| Anexo III — Tabela 8.3 | Número de Cursos | `NCURSO` | H–BZ (2024) | 71 | contagem | todos (2017–2024) |
| Anexo III — Tabela 8.3 | Vagas Oferecidas | `VAGT` | CA–FO (2024) | 93 | contagem | todos (2017–2024) |
| Anexo III — Tabela 8.3 | Candidatos Inscritos | `INSCRT` | FP–JD (2024) | 93 | contagem | todos (2017–2024) |
| Anexo III — Tabela 8.3 | Ingressantes | `INGR` | JE–MS (2024) | 93 | contagem | todos (2017–2024) |
| Anexo III — Tabela 8.3 | Matrículas | `MATT` | MT–QH (2024) | 93 | contagem | todos (2017–2024) |
| Anexo III — Tabela 8.3 | Concluintes | `CONCLT` | QI–TA (2024) | 71 | contagem | todos (2017–2024) |

### 1.4 Categorias das dimensões de coluna (níveis 3–6)

| Conjunto | Nível | Categoria (rótulo original) | Anos em que aparece |
|---|---|---|---|
| Anexo I — Tabela 8.1 | 3 | Centro Universitário | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 3 | Faculdade | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 3 | Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet) | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 3 | Total | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 3 | Universidade | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 4 | Bacharelado | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 4 | Federal | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 4 | Licenciatura | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 4 | Não Aplicável5 | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 4 | Tecnológico | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 4 | Total | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Bacharelado | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Estadual | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Federal | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Licenciatura | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Municipal | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Não Aplicável5 | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Privada | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Tecnológico | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 5 | Total | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 6 | Com Fins Lucrativos | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 6 | Sem Fins Lucrativos | todos (2017–2024) |
| Anexo I — Tabela 8.1 | 6 | Total | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 3 | Centro Universitário | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 3 | Faculdade | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 3 | Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet) | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 3 | Total | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 3 | Universidade | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 4 | Bacharelado | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 4 | Federal | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 4 | Licenciatura | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 4 | Não Aplicável4 | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 4 | Tecnológico | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 4 | Total | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Bacharelado | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Estadual | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Federal | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Licenciatura | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Municipal | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Não Aplicável4 | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Privada | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Tecnológico | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 5 | Total | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 6 | Com Fins Lucrativos | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 6 | Sem Fins Lucrativos | todos (2017–2024) |
| Anexo II — Tabela 8.2 | 6 | Total | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 3 | Centro Universitário | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 3 | Faculdade | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 3 | Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet) | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 3 | Total | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 3 | Universidade | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 4 | Bacharelado | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 4 | Federal | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 4 | Licenciatura | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 4 | Não Aplicável5 | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 4 | Tecnológico | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 4 | Total | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Bacharelado | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Estadual | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Federal | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Licenciatura | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Municipal | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Não Aplicável5 | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Privada | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Tecnológico | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 5 | Total | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 6 | Com Fins Lucrativos | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 6 | Sem Fins Lucrativos | todos (2017–2024) |
| Anexo III — Tabela 8.3 | 6 | Total | todos (2017–2024) |

### 1.5 Gramática observada dos códigos de variável (linha 12)

Padrão inferido **empiricamente** a partir do pareamento código × rótulo hierárquico. Não há documentação oficial deste esquema nos arquivos, então ele deve ser validado antes de ser usado como regra de transformação.

| Código | Indicador | Nível 3 | Nível 4 | Nível 5 | Nível 6 |
|---|---|---|---|---|---|
| `NCURSO` | Número de Cursos | Total |  |  |  |
| `NCURSO1` | Número de Cursos | Universidade | Total |  |  |
| `NCURSOB1` | Número de Cursos | Universidade | Bacharelado | Total |  |
| `NCURSOB11` | Número de Cursos | Universidade | Bacharelado | Federal |  |
| `NCURSOB12` | Número de Cursos | Universidade | Bacharelado | Estadual |  |
| `NCURSOB13` | Número de Cursos | Universidade | Bacharelado | Municipal |  |
| `NCURSOB14` | Número de Cursos | Universidade | Bacharelado | Privada | Total |
| `NCURSOB15` | Número de Cursos | Universidade | Bacharelado | Privada | Com Fins Lucrativos |
| `NCURSOB16` | Número de Cursos | Universidade | Bacharelado | Privada | Sem Fins Lucrativos |
| `NCURSOL1` | Número de Cursos | Universidade | Licenciatura | Total |  |
| `NCURSOL11` | Número de Cursos | Universidade | Licenciatura | Federal |  |
| `NCURSOL12` | Número de Cursos | Universidade | Licenciatura | Estadual |  |
| `NCURSOL13` | Número de Cursos | Universidade | Licenciatura | Municipal |  |
| `NCURSOL14` | Número de Cursos | Universidade | Licenciatura | Privada | Total |
| `NCURSOL15` | Número de Cursos | Universidade | Licenciatura | Privada | Com Fins Lucrativos |
| `NCURSOL16` | Número de Cursos | Universidade | Licenciatura | Privada | Sem Fins Lucrativos |
| `NCURSOT1` | Número de Cursos | Universidade | Tecnológico | Total |  |
| `NCURSOT11` | Número de Cursos | Universidade | Tecnológico | Federal |  |
| `NCURSOT12` | Número de Cursos | Universidade | Tecnológico | Estadual |  |
| `NCURSOT13` | Número de Cursos | Universidade | Tecnológico | Municipal |  |
| `NCURSOT14` | Número de Cursos | Universidade | Tecnológico | Privada | Total |
| `NCURSOT15` | Número de Cursos | Universidade | Tecnológico | Privada | Com Fins Lucrativos |
| `NCURSOT16` | Número de Cursos | Universidade | Tecnológico | Privada | Sem Fins Lucrativos |
| `NCURSO2` | Número de Cursos | Centro Universitário | Total |  |  |
| `NCURSOB2` | Número de Cursos | Centro Universitário | Bacharelado | Total |  |
| `NCURSOB21` | Número de Cursos | Centro Universitário | Bacharelado | Federal |  |
| `NCURSOB22` | Número de Cursos | Centro Universitário | Bacharelado | Estadual |  |
| `NCURSOB23` | Número de Cursos | Centro Universitário | Bacharelado | Municipal |  |
| `NCURSOB24` | Número de Cursos | Centro Universitário | Bacharelado | Privada | Total |
| `NCURSOB25` | Número de Cursos | Centro Universitário | Bacharelado | Privada | Com Fins Lucrativos |
| `NCURSOB26` | Número de Cursos | Centro Universitário | Bacharelado | Privada | Sem Fins Lucrativos |
| `NCURSOL2` | Número de Cursos | Centro Universitário | Licenciatura | Total |  |
| `NCURSOL21` | Número de Cursos | Centro Universitário | Licenciatura | Federal |  |
| `NCURSOL22` | Número de Cursos | Centro Universitário | Licenciatura | Estadual |  |
| `NCURSOL23` | Número de Cursos | Centro Universitário | Licenciatura | Municipal |  |
| `NCURSOL24` | Número de Cursos | Centro Universitário | Licenciatura | Privada | Total |
| `NCURSOL25` | Número de Cursos | Centro Universitário | Licenciatura | Privada | Com Fins Lucrativos |
| `NCURSOL26` | Número de Cursos | Centro Universitário | Licenciatura | Privada | Sem Fins Lucrativos |
| `NCURSOT2` | Número de Cursos | Centro Universitário | Tecnológico | Total |  |
| `NCURSOT21` | Número de Cursos | Centro Universitário | Tecnológico | Federal |  |
| `NCURSOT22` | Número de Cursos | Centro Universitário | Tecnológico | Estadual |  |
| `NCURSOT23` | Número de Cursos | Centro Universitário | Tecnológico | Municipal |  |
| `NCURSOT24` | Número de Cursos | Centro Universitário | Tecnológico | Privada | Total |
| `NCURSOT25` | Número de Cursos | Centro Universitário | Tecnológico | Privada | Com Fins Lucrativos |
| `NCURSOT26` | Número de Cursos | Centro Universitário | Tecnológico | Privada | Sem Fins Lucrativos |
| `NCURSO4` | Número de Cursos | Faculdade | Total |  |  |
| `NCURSOB4` | Número de Cursos | Faculdade | Bacharelado | Total |  |
| `NCURSOB41` | Número de Cursos | Faculdade | Bacharelado | Federal |  |
| `NCURSOB42` | Número de Cursos | Faculdade | Bacharelado | Estadual |  |
| `NCURSOB43` | Número de Cursos | Faculdade | Bacharelado | Municipal |  |
| `NCURSOB44` | Número de Cursos | Faculdade | Bacharelado | Privada | Total |
| `NCURSOB45` | Número de Cursos | Faculdade | Bacharelado | Privada | Com Fins Lucrativos |
| `NCURSOB46` | Número de Cursos | Faculdade | Bacharelado | Privada | Sem Fins Lucrativos |
| `NCURSOL4` | Número de Cursos | Faculdade | Licenciatura | Total |  |
| `NCURSOL41` | Número de Cursos | Faculdade | Licenciatura | Federal |  |
| `NCURSOL42` | Número de Cursos | Faculdade | Licenciatura | Estadual |  |
| `NCURSOL43` | Número de Cursos | Faculdade | Licenciatura | Municipal |  |
| `NCURSOL44` | Número de Cursos | Faculdade | Licenciatura | Privada | Total |
| `NCURSOL45` | Número de Cursos | Faculdade | Licenciatura | Privada | Com Fins Lucrativos |
| `NCURSOL46` | Número de Cursos | Faculdade | Licenciatura | Privada | Sem Fins Lucrativos |

*(primeiras 60 colunas de medida do anexo mais recente; a lista completa por ano está em `03_catalogo_colunas.xlsx`)*

### 1.6 Códigos de variável que mudam entre anos

Nenhum código de variável muda: o conjunto de códigos é o mesmo em todos os anos de cada anexo.

Mesmo código com rótulo hierárquico diferente entre anos (após a normalização): **0** casos. A lista está em 05 › `pareamento_colunas` (classificação "Equivalência parcial").

## 2. Sinopse por município — tabelas 1.x a 7.x

Cada aba é uma tabela de contagem em que as linhas são Brasil, Região, UF e Município (e, em algumas tabelas, também o Nível Acadêmico do Curso). As colunas cruzam categorias hierárquicas. Não existe linha de códigos de variável: a identificação das colunas depende só dos rótulos.

### Tab 1.1 — aba `'1.1'` (2024)

- **Título (A4, 2024):** 1.1 - Número de Instituições de Ensino Superior (IES), por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município da sede administrativa da Instituição - 2024
- **Tema (A2) / universo (A3):** Instituições / Sede Administrativa da Instituição
- **Anos presentes:** todos (2017–2024); nomes da aba: '1.1'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** 
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 37, 2018: 37, 2019: 37, 2020: 37, 2021: 37, 2022: 37, 2023: 37, 2024: 37
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Dependência Administrativa; Universidade
- **Categorias — nível 3:** Federal; Privada; Pública; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A743: Fonte: INEP – Censo da Educação Superior. ¦ A744: Notas:    1 - Inclui Instituições de Ensino Superior que ofertam cursos de graduação e sequencial de formação específica, presenciais e/ou a distância. ¦ A745: 2 - O número de Instituições de Ensino Superior considera somente as instituições com sede administrativa/reitoria na respectiva Região Geográfica, Unidade da Federação e Município. ¦ A746: 3 - Os campi (polos e campus) das Instituições de Ensino Superior que estão localizados fora de sua sede administrativa/reitoria não estão contabilizados.

### Tab 1.2 — aba `'1.2'` (2024)

- **Título (A4, 2024):** 1.2 - Número de Instituições de Ensino Superior (IES), Comunitárias e/ou Confessionais, por Organização Acadêmica , segundo a Região Geográfica, a Unidade da Federação e o Município da sede administrativa da Instituição - 2024
- **Tema (A2) / universo (A3):** Instituições / Sede Administrativa da Instituição - Comunitária e/ou Confessional
- **Anos presentes:** 2023, 2024; nomes da aba: '1.2'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** 
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 17; Município (código preenchido): 83
- **Colunas úteis por ano:** 2023: 19, 2024: 19
- **Categorias — nível 1:** Organização Acadêmica e Categoria Administrativa da IES1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Tipo da Instituição Privada; Universidade
- **Categorias — nível 3:** Comunitária; Confessional; Total
- **Notas de rodapé (2024):** A117: Fonte: INEP – Censo da Educação Superior. ¦ A118: Notas:    1 - Inclui Instituições de Ensino Superior que ofertam cursos de graduação e sequencial de formação específica, presenciais e/ou a distância. ¦ A119: 2 - O número de Instituições de Ensino Superior considera somente as instituições comunitárias e/ou confessionais, com sede administrativa/reitoria na respectiva Região Geográfica, Unidade da Federação e Município. ¦ A120: 3 - A mesma Instituição pode ser comunitária e Confessional.

### Tab 2.1 — aba `'2.1'` (2024)

- **Título (A4, 2024):** 2.1 - Número de Docentes em Exercício, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.1'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 37, 2018: 37, 2019: 37, 2020: 37, 2021: 37, 2022: 37, 2023: 37, 2024: 37
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-9
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Dependência Administrativa; Universidade
- **Categorias — nível 3:** Federal; Privada; Pública; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A743: Fonte: INEP – Censo da Educação Superior. ¦ A744: Notas:  1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A745: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A746: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A747: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A748: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A749: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ …

### Tab 2.2 — aba `'2.2'` (2024)

- **Título (A4, 2024):** 2.2 - Número de Docentes em Exercício, por Organização Acadêmica, Dependência Administrativa e Regime de Trabalho, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.2'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 112, 2018: 112, 2019: 112, 2020: 112, 2021: 112, 2022: 112, 2023: 112, 2024: 112
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Regime de trabalho1-10
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Regime de Trabalho; Universidade
- **Categorias — nível 3:** Estadual; Federal; Horista; Municipal; Privada; Tempo Integral; Tempo Parcial; Total
- **Categorias — nível 4:** Com Dedicação Exclusiva; Com Fins Lucrativos; Privada; Regime de Trabalho; Sem Dedicação Exclusiva; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Horista; Regime de Trabalho; Tempo Integral; Tempo Parcial; Total
- **Categorias — nível 6:** Com Dedicação Exclusiva; Horista; Sem Dedicação Exclusiva; Tempo Integral; Tempo Parcial; Total
- **Notas de rodapé (2024):** A746: Fonte: INEP – Censo da Educação Superior. ¦ A747: Notas:  1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A748: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A749: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A750: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A751: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A752: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ …

### Tab 2.3 — aba `'2.3 Características do Docente'` (2024)

- **Título (A4, 2024):** 2.3 - Número de Docentes em Exercício, por Organização Acadêmica, Dependência Administrativa, Sexo e Grau de Formação, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.3 Características do Docente'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 146, 2018: 146, 2019: 146, 2020: 146, 2021: 146, 2022: 146, 2023: 146, 2024: 146
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Sexo e Grau de Formação1-10
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Sexo e por Grau de Formação; Universidade
- **Categorias — nível 3:** Estadual; Federal; Grau de Formação9; Municipal; Privada; Sexo; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Doutorado; Especialização; Feminino; Graduação; Grau de Formação9; Masculino; Mestrado; Sem Fins Lucrativos; Sem Graduação; Sexo; Total
- **Categorias — nível 5:** Doutorado; Especialização; Feminino; Graduação; Grau de Formação9; Masculino; Mestrado; Sem Graduação; Sexo; Total
- **Categorias — nível 6:** Doutorado; Especialização; Feminino; Graduação; Masculino; Mestrado; Sem Graduação
- **Notas de rodapé (2024):** A745: Fonte: INEP – Censo da Educação Superior. ¦ A746: Notas:  1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A747: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A748: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A749: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A750: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A751: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ …

### Tab 2.4 — aba `'2.4'` (2024)

- **Título (A4, 2024):** 2.4 - Número de Docentes em Exercício, por Organização Acadêmica, Dependência Administrativa e Faixa Etária, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.4 ', '2.4'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 203, 2018: 203, 2019: 203, 2020: 203, 2021: 203, 2022: 203, 2023: 203, 2024: 203
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Faixa Etária1-9
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** 65 anos ou mais; Até 20 anos; Com Fins Lucrativos; De 21 a 24 anos; De 25 a 29 anos; De 30 a 34 anos; De 35 a 39 anos; De 40 a 44 anos; De 45 a 49 anos; De 50 a 54 anos; De 55 a 59 anos; De 60 a 64 anos; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** 65 anos ou mais; Até 20 anos; De 21 a 24 anos; De 25 a 29 anos; De 30 a 34 anos; De 35 a 39 anos; De 40 a 44 anos; De 45 a 49 anos; De 50 a 54 anos; De 55 a 59 anos; De 60 a 64 anos; Total
- **Notas de rodapé (2024):** A744: Fonte: INEP – Censo da Educação Superior. ¦ A745: Notas:  1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A746: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A747: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A748: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A749: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A750: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ …

### Tab 2.5 — aba `'2.5'` (2024)

- **Título (A4, 2024):** 2.5 - Número de Docentes em Exercício, por Sexo e Faixa Etária, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.5'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 29, 2018: 29, 2019: 29, 2020: 29, 2021: 29, 2022: 29, 2023: 29, 2024: 29
- **Categorias — nível 1:** Sexo e Faixa Etária1-8
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** 65 anos ou mais; Até 20 anos; De 21 a 24 anos; De 25 a 29 anos; De 30 a 34 anos; De 35 a 39 anos; De 40 a 44 anos; De 45 a 49 anos; De 50 a 54 anos; De 55 a 59 anos; De 60 a 64 anos; Total
- **Notas de rodapé (2024):** A742: Fonte: INEP – Censo da Educação Superior. ¦ A743: Notas:  1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A744: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A745: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A746: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A747: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A748: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ …

### Tab 2.6 — aba `'2.6'` (2024)

- **Título (A4, 2024):** 2.6 - Número de Docentes em Exercício, por Organização Acadêmica, Dependência Administrativa e Cor/Raça, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.6 ', '2.6'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 123, 2018: 123, 2019: 123, 2020: 123, 2021: 123, 2022: 123, 2023: 123, 2024: 123
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Cor/Raça1-10
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Privada - Com Fins Lucrativos; Privada - Sem Fins Lucrativos; Total
- **Categorias — nível 4:** Amarela; Branca; Indígena; Não Dispõe da Informação9; Parda; Preta; Total
- **Notas de rodapé (2024):** A743: Fonte: INEP – Censo da Educação Superior. ¦ A744: Notas:   1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A745: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A746: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente se atuam em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A747: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A748: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A749: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦  …

### Tab 2.7 — aba `'2.7'` (2024)

- **Título (A4, 2024):** 2.7 - Número de Docentes em Exercício, por Sexo e Cor/Raça, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.7 ', '2.7'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 19, 2018: 19, 2019: 19, 2020: 19, 2021: 19, 2022: 19, 2023: 19, 2024: 19
- **Categorias — nível 1:** Sexo e Cor/Raça1-9
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Amarela; Branca; Indígena; Não Dispõe da Informação8; Parda; Preta; Total
- **Notas de rodapé (2024):** A742: Fonte: INEP – Censo da Educação Superior. ¦ A743: Notas:   1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A744: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A745: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A746: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A747: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A748: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação.  …

### Tab 2.8 — aba `'2.8'` (2024)

- **Título (A4, 2024):** 2.8 - Número de Docentes em Exercício, por Organização Acadêmica, Dependência Administrativa e Nacionalidade, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.8'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 698
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Nacionalidade1-9
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Privada - Com Fins Lucrativos; Privada - Sem Fins Lucrativos; Total
- **Categorias — nível 4:** Brasileira; Brasileira - Naturalizado; Estrangeiro; Total
- **Notas de rodapé (2024):** A743: Fonte: INEP – Censo da Educação Superior. ¦ A744: Notas:   1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A745: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A746: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A747: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A748: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A749: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação.  …

### Tab 2.9 — aba `'2.9'` (2024)

- **Título (A4, 2024):** 2.9 - Número de Docentes em Exercício, por Organização Acadêmica, Dependência Administrativa e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício
- **Anos presentes:** todos (2017–2024); nomes da aba: '2.9'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de docentes em
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 295
- **Colunas úteis por ano:** 2017: 155, 2018: 155, 2019: 155, 2020: 155, 2021: 155, 2022: 187, 2023: 187, 2024: 203
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Tipo de Deficiência1-9
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Privada - Com Fins Lucrativos; Privada - Sem Fins Lucrativos; Total
- **Categorias — nível 4:** Altas habilidades/superdotação; Auditiva; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Surdez; Surdocegueira; Total; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista; Visão Monocular
  - *variam entre anos:* Altas habilidades/superdotação (2022,2023,2024); Transtorno Global do Desenvolvimento (TGD) (2022); Transtorno do Espectro Autista (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A340: Fonte: INEP – Censo da Educação Superior. ¦ A341: Notas:   1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A342: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A343: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A344: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A345: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A346: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação.  …

### Tab 2.10 — aba `'2.10'` (2024)

- **Título (A4, 2024):** 2.10 - Número de Docentes das Instituições de Ensino Superior (IES), Comunitárias e/ou Confessionais, por Organização Acadêmica, segundo a Região Geográfica, a Unidade da Federação e o Município da sede administrativa da Instituição - 2024
- **Tema (A2) / universo (A3):** Docentes / Em Exercício - Instituições de Ensino Comunitárias e/ou Confessionais
- **Anos presentes:** 2023, 2024; nomes da aba: '2.10'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** 
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 17; Município (código preenchido): 83
- **Colunas úteis por ano:** 2023: 19, 2024: 19
- **Categorias — nível 1:** Organização Acadêmica e Categoria Administrativa da IES1-10
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Tipo da Instituição Privada; Universidade
- **Categorias — nível 3:** Comunitária; Confessional; Total
- **Notas de rodapé (2024):** A117: Fonte: INEP – Censo da Educação Superior. ¦ A118: Notas:  1 - Os docentes referem-se aos indivíduos que atuaram nas Instituições de Ensino Superior no período de referência do Censo. ¦ A119: 2 - Inclui somente os docentes em exercício nos cursos de graduação e/ou sequenciais de formação específica em Instituições Comunitárias e/ou Confessionais. O docente em exercício engloba os indivíduos que atuaram na instituição por um período mínimo de 60 dias no ano de referência do Censo. ¦ A120: 3 - No total do Brasil, os docentes são contados uma única vez, independentemente de atuarem em mais de uma Região Geográfica, Unidade da Federação, Município ou Instituição de Ensino Superior. ¦ A121: 4 - No total da Região Geográfica, os docentes são contados uma única vez em cada Região, portanto, o total não representa a soma das Regiões, das Unidades da Federação, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A122: 5 - No total da Unidade da Federação (UF), os docentes são contados uma única vez em cada Unidade da Federação, portanto, o total não representa a soma das 27 UFs, dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente pode atuar em mais de uma unidade de agregação. ¦ A123: 6 - No total do Município, os docentes são contados uma única vez em cada Município, portanto, o total não representa a soma dos Municípios ou das Instituições de Ensino Superior, pois o mesmo docente p …

### Tab 3.1 — aba `'3.1'` (2024)

- **Título (A4, 2024):** 3.1 - Número de Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Modalidade de Ensino e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Cursos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '3.1'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** idade de ensino e dependencia administrativa
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 1123
- **Colunas úteis por ano:** 2017: 76, 2018: 76, 2019: 76, 2020: 76, 2021: 76, 2022: 76, 2023: 76, 2024: 76
- **Categorias — nível 1:** Organização Acadêmica, Modalidade de Ensino e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Modalidade de Ensino e Dependência Administrativa; Universidade
- **Categorias — nível 3:** A Distância; Federal; Presencial; Total
- **Categorias — nível 4:** A Distância; Presencial; Privada; Pública; Total
- **Categorias — nível 5:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A1175: Fonte: INEP – Censo da Educação Superior. ¦ A1176: Notas:   1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância, com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. ¦ A1177: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1178: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 3.2 — aba `'3.2'` (2024)

- **Título (A4, 2024):** 3.2 - Número de Cursos de Graduação - Presenciais, por Organização Acadêmica, Grau Acadêmico do Curso e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Cursos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '3.2'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** 
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1121
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 219, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-2
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Bacharelado; Federal; Licenciatura; Tecnológico; Total
- **Categorias — nível 4:** Bacharelado; Estadual; Federal; Licenciatura; Municipal; Privada; Tecnológico; Total
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A1167: Fonte: INEP – Censo da Educação Superior. ¦ A1168: Notas:   1 -  Inclui somente os cursos de graduação presenciais e com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. ¦ A1169: 2 -  As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 3.3 — aba `'3.3'` (2024)

- **Título (A4, 2024):** 3.3 - Número de Cursos de Graduação - Presenciais, por Organização Acadêmica, Dependência Administrativa e Turno, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Cursos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '3.3'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** 
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1121
- **Colunas úteis por ano:** 2017: 59, 2018: 59, 2019: 59, 2020: 59, 2021: 59, 2022: 59, 2023: 59, 2024: 59
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Turno1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Diurno; Noturno; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Diurno; Noturno; Total
- **Notas de rodapé (2024):** A1167: Fonte: INEP – Censo da Educação Superior. ¦ A1168: Notas: 1 - Inclui somente os cursos de graduação presenciais e com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. ¦ A1169: 2 - O mesmo curso pode ser oferecido em mais de um turno. ¦ A1170: 3 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 4.1 — aba `'4.1 Vagas e Inscritos'` (2024)

- **Título (A4, 2024):** 4.1 - Número de Vagas Oferecidas e Candidatos Inscritos nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Modalidade de Ensino e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.1 Vagas e Inscritos'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de vagas oferecidas e candidatos inscritos nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 1063
- **Colunas úteis por ano:** 2017: 107, 2018: 107, 2019: 107, 2020: 107, 2021: 107, 2022: 107, 2023: 107, 2024: 107
- **Categorias — nível 1:** Organização Acadêmica, Modalidade de Ensino e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Candidatos Inscritos; Federal; Vagas Oferecidas
- **Categorias — nível 4:** A Distância; Candidatos Inscritos; Presencial; Total; Vagas Oferecidas
- **Categorias — nível 5:** A Distância; Estadual; Federal; Municipal; Presencial; Privada; Total
- **Categorias — nível 6:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A1116: Fonte: INEP – Censo da Educação Superior. ¦ A1117: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A1118: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1119: 3 - Número de Vagas e Inscritos na modalidade a distância (EaD) não são coletados por local de oferta.

### Tab 4.2 — aba `'4.2 Ingressantes'` (2024)

- **Título (A4, 2024):** 4.2 - Número de Ingressantes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa e Forma de Ingresso, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.2 Ingressantes'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3319
- **Colunas úteis por ano:** 2017: 164, 2018: 164, 2019: 164, 2020: 164, 2021: 164, 2022: 164, 2023: 164, 2024: 164
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Forma de Ingresso1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Forma de Ingresso; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Outras Formas de Ingresso; Privada; Seleção para Vagas Novas; Seleção para vagas de programas especiais; Seleção para vagas remanescentes; Total
- **Categorias — nível 4:** Avaliação Seriada; Com Fins Lucrativos; Enem; Outras Formas de Ingresso; Seleção Simplificada; Seleção para Vagas Novas; Seleção para vagas de programas especiais; Seleção para vagas remanescentes; Sem Fins Lucrativos; Total; Vestibular
- **Categorias — nível 5:** Avaliação Seriada; Enem; Outras Formas de Ingresso; Seleção Simplificada; Seleção para Vagas Novas; Seleção para vagas de programas especiais; Seleção para vagas remanescentes; Total; Vestibular
- **Categorias — nível 6:** Avaliação Seriada; Enem; Seleção Simplificada; Total; Vestibular
- **Notas de rodapé (2024):** A3373: Fonte: INEP – Censo da Educação Superior. ¦ A3374: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A3375: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3376: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A3377: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.3 — aba `'4.3'` (2024)

- **Título (A4, 2024):** 4.3 - Número de Ingressantes nos Cursos de Graduação Presenciais, por Organização Acadêmica, Dependência Administrativa e Forma de Ingresso, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.3'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1030
- **Colunas úteis por ano:** 2017: 163, 2018: 163, 2019: 163, 2020: 163, 2021: 163, 2022: 163, 2023: 163, 2024: 163
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Forma de Ingresso1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Forma de Ingresso; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Outras Formas de Ingresso; Privada; Seleção para Vagas Novas; Seleção para vagas de programas especiais; Seleção para vagas remanescentes; Total
- **Categorias — nível 4:** Avaliação Seriada; Com Fins Lucrativos; Enem; Outras Formas de Ingresso; Seleção Simplificada; Seleção para Vagas Novas; Seleção para vagas de programas especiais; Seleção para vagas remanescentes; Sem Fins Lucrativos; Total; Vestibular
- **Categorias — nível 5:** Avaliação Seriada; Enem; Outras Formas de Ingresso; Seleção Simplificada; Seleção para Vagas Novas; Seleção para vagas de programas especiais; Seleção para vagas remanescentes; Total; Vestibular
- **Categorias — nível 6:** Avaliação Seriada; Enem; Seleção Simplificada; Total; Vestibular
- **Notas de rodapé (2024):** A1077: Fonte: INEP – Censo da Educação Superior. ¦ A1078: Notas:   1 - Inclui cursos de graduação presenciais. ¦ A1079: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1080: 3 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.4 — aba `'4.4'` (2024)

- **Título (A4, 2024):** 4.4 - Número de Ingressantes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.4'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 3317
- **Colunas úteis por ano:** 2017: 97, 2018: 97, 2019: 97, 2020: 285, 2021: 97, 2022: 97, 2023: 97, 2024: 97
- **Categorias — nível 1:** Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-3; Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-4
  - *variam entre anos:* Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-3 (2023,2024); Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-4 (2017,2018,2019,2020,2021,2022)
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Bacharelado; Federal; Licenciatura; Não Aplicável4; Não Aplicável5; Tecnológico; Total
  - *variam entre anos:* Não Aplicável4 (2023,2024); Não Aplicável5 (2017,2018,2019,2020,2021,2022)
- **Categorias — nível 4:** Bacharelado; Estadual; Federal; Licenciatura; Municipal; Não Aplicável4; Não Aplicável5; Privada; Tecnológico; Total
  - *variam entre anos:* Não Aplicável4 (2023,2024); Não Aplicável5 (2017,2018,2019,2020,2021,2022)
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A3364: Fonte: INEP – Censo da Educação Superior. ¦ A3365: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A3366: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3367: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A3368: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.5 — aba `'4.5'` (2024)

- **Título (A4, 2024):** 4.5 - Número de Ingressantes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Dependência Administrativa e Turno, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.5'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1030
- **Colunas úteis por ano:** 2017: 59, 2018: 59, 2019: 59, 2020: 59, 2021: 59, 2022: 59, 2023: 59, 2024: 59
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Turno1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Diurno; Noturno; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Diurno; Noturno; Total
- **Notas de rodapé (2024):** A1076: Fonte: INEP – Censo da Educação Superior. ¦ A1077: Notas:   1 - Inclui cursos de graduação presenciais. ¦ A1078: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1079: 3 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.6 — aba `'4.6 Características do Aluno'` (2024)

- **Título (A4, 2024):** 4.6 - Número de Ingressantes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.6 Características do Aluno'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3319
- **Colunas úteis por ano:** 2017: 60, 2018: 60, 2019: 60, 2020: 60, 2021: 60, 2022: 60, 2023: 60, 2024: 60
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Feminino; Masculino; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3372: Fonte: INEP – Censo da Educação Superior. ¦ A3373: Notas:   1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3374: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3375: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A3376: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.7 — aba `'4.7'` (2024)

- **Título (A4, 2024):** 4.7 - Número de Ingressantes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Cor/Raça e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.7'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3319
- **Colunas úteis por ano:** 2017: 316, 2018: 316, 2019: 316, 2020: 316, 2021: 316, 2022: 316, 2023: 316, 2024: 316
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Cor/Raça e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Amarela; Branca; Com Fins Lucrativos; Indígena; Não Dispõe da Informação5; Parda; Preta; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Amarela; Branca; Feminino; Indígena; Masculino; Não Dispõe da Informação5; Parda; Preta; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3373: Fonte: INEP – Censo da Educação Superior. ¦ A3374: Notas:   1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3375: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3376: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A3377: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.8 — aba `'4.8'` (2024)

- **Título (A4, 2024):** 4.8 - Número de Ingressantes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa,  Faixa Etária e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.8'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3319
- **Colunas úteis por ano:** 2017: 556, 2018: 556, 2019: 556, 2020: 556, 2021: 556, 2022: 556, 2023: 556, 2024: 556
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Faixa Etária e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** 65 Anos ou mais; Até 18 Anos; Com Fins Lucrativos; De 19 a 24 Anos; De 25 a 29 Anos; De 30 a 34 Anos; De 35 a 39 Anos; De 40 a 44 Anos; De 45 a 49 Anos; De 50 a 54 Anos; De 55 a 59 Anos; De 60 a 64 Anos; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** 65 Anos ou mais; Até 18 Anos; De 19 a 24 Anos; De 25 a 29 Anos; De 30 a 34 Anos; De 35 a 39 Anos; De 40 a 44 Anos; De 45 a 49 Anos; De 50 a 54 Anos; De 55 a 59 Anos; De 60 a 64 Anos; Feminino; Masculino; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3373: Fonte: INEP – Censo da Educação Superior. ¦ A3374: Notas:   1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3375: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3376: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A3377: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.9 — aba `'4.9'` (2024)

- **Título (A4, 2024):** 4.9 - Número de Ingressantes nos Cursos de Graduação - Presenciais e a Distância, por Sexo e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.9'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1847
- **Colunas úteis por ano:** 2017: 33, 2018: 33, 2019: 33, 2020: 25, 2021: 25, 2022: 25, 2023: 25, 2024: 27
- **Categorias — nível 1:** Sexo e Tipo de Deficiência1-5
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Auditiva; Autismo Infantil; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Superdotação; Surdez; Surdocegueira; Síndrome de Asperger; Síndrome de Rett; Total; Transtorno Desintegrativo da Infância; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista (TEA); Visão Monocular
  - *variam entre anos:* Autismo Infantil (2017,2018,2019,2020); Múltipla (2017,2018,2019); Síndrome de Asperger (2017,2018,2019); Síndrome de Rett (2017,2018,2019); Transtorno Desintegrativo da Infância (2017,2018,2019); Transtorno Global do Desenvolvimento (TGD) (2021,2022); Transtorno do Espectro Autista (TEA) (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A1892: Fonte: INEP – Censo da Educação Superior. ¦ A1893: Notas:   1 - Inclui cursos de graduação, presenciais e a distância (EaD). ¦ A1894: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1895: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A1896: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A1897: 5 - O mesmo aluno pode ter mais de um tipo de deficiência. ¦ A1898: 6 - Até o ano de 2023, as condições de baixa visão e visão monocular eram reportadas de forma agregada nos registros oficiais, sem distinção entre os dois tipos de deficiência visual. A partir de 2024, passou-se a adotar a segregação dessas categorias, permitindo que cada condição seja informada individualmente nos sistemas de coleta e análise de dados.

### Tab 4.10 — aba `'4.10'` (2024)

- **Título (A4, 2024):** 4.10 - Número de Ingressantes nos Cursos de Graduação - Presenciais, por Sexo e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.10'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 721
- **Colunas úteis por ano:** 2017: 33, 2018: 33, 2019: 33, 2020: 25, 2021: 25, 2022: 25, 2023: 25, 2024: 27
- **Categorias — nível 1:** Sexo e Tipo de Deficiência1-4
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Auditiva; Autismo Infantil; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Superdotação; Surdez; Surdocegueira; Síndrome de Asperger; Síndrome de Rett; Total; Transtorno Desintegrativo da Infância; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista (TEA); Visão Monocular
  - *variam entre anos:* Autismo Infantil (2017,2018,2019,2020); Múltipla (2017,2018,2019); Síndrome de Asperger (2017,2018,2019); Síndrome de Rett (2017,2018,2019); Transtorno Desintegrativo da Infância (2017,2018,2019); Transtorno Global do Desenvolvimento (TGD) (2021,2022); Transtorno do Espectro Autista (TEA) (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A765: Fonte: INEP – Censo da Educação Superior. ¦ A766: Notas:   1 - Inclui cursos de graduação presenciais. ¦ A767: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A768: 3 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A769: 4 - O mesmo aluno pode ter mais de um tipo de deficiência. ¦ A770: 5 - Até o ano de 2023, as condições de baixa visão e visão monocular eram reportadas de forma agregada nos registros oficiais, sem distinção entre os dois tipos de deficiência visual. A partir de 2024, passou-se a adotar a segregação dessas categorias, permitindo que cada condição seja informada individualmente nos sistemas de coleta e análise de dados.

### Tab 4.11 — aba `'4.11'` (2024)

- **Título (A4, 2024):** 4.11 - Número de Ingressantes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Nacionalidade e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.11'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3319
- **Colunas úteis por ano:** 2017: 172, 2018: 172, 2019: 172, 2020: 172, 2021: 172, 2022: 172, 2023: 172, 2024: 172
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Nacionalidade e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Brasileira; Brasileira  - Naturalizado; Com Fins Lucrativos; Estrangeira; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Brasileira; Brasileira  - Naturalizado; Estrangeira; Feminino; Masculino; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3373: Fonte: INEP – Censo da Educação Superior. ¦ A3374: Notas:   1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3375: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3376: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A3377: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso.

### Tab 4.12 — aba `'4.12 Financiamento'` (2024)

- **Título (A4, 2024):** 4.12 - Número de Ingressantes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Tipo de Financiamento Estudantil e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Cursos de Graduação - Presenciais e a Distância / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.12 Financiamento'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 2634
- **Colunas úteis por ano:** 2017: 219, 2018: 219, 2019: 219, 2020: 219, 2021: 219, 2022: 219, 2023: 219, 2024: 219
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Tipo de Financiamento Estudantil e Sexo1-5
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; FIES; Outros Financiamentos6; ProUni Integral; ProUni Parcial; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** FIES; Feminino; Masculino; Outros Financiamentos6; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2682: Fonte: INEP – Censo da Educação Superior. ¦ A2683: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2684: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2685: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A2686: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A2687: 5 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A2688: 6 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades.

### Tab 4.13 — aba `'4.13'` (2024)

- **Título (A4, 2024):** 4.13 - Número de Ingressantes nos Cursos de Graduação - Presenciais e a Distância, por Cor/Raça, Sexo e Tipo de Financiamento Estudantil, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.13'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 2634
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Financiamento Estudantil1-5
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação7; Parda; Preta; Total; Total por Tipo de Financiamento Estudantil
- **Categorias — nível 3:** FIES; Feminino; Masculino; Outros Financiamentos6; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 4:** FIES; Outros Financiamentos6; ProUni Integral; ProUni Parcial; Total
- **Notas de rodapé (2024):** A2680: Fonte: INEP – Censo da Educação Superior. ¦ A2681: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2682: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2683: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A2684: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A2685: 5 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A2686: 6 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades. ¦ A2687: 7 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 4.14 — aba `'4.14'` (2024)

- **Título (A4, 2024):** 4.14 - Número de Ingressantes nos Cursos de Graduação - Presenciais, por Cor/Raça, Sexo e Tipo de Financiamento Estudantil, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.14'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 615
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Financiamento Estudantil1-4
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação6; Parda; Preta; Total; Total por Tipo de Financiamento Estudantil
- **Categorias — nível 3:** FIES; Feminino; Masculino; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 4:** FIES; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Notas de rodapé (2024):** A660: Fonte: INEP – Censo da Educação Superior. ¦ A661: Notas:   1 - Inclui cursos de graduação presenciais. ¦ A662: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A663: 3 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A664: 4 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A665: 5 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades. ¦ A666: 6 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 4.15 — aba `'4.15 Reserva de Vagas'` (2024)

- **Título (A4, 2024):** 4.15 - Número de Ingressantes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Programa de Reserva de Vagas e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.15 Reserva de Vagas'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1095
- **Colunas úteis por ano:** 2017: 267, 2018: 267, 2019: 267, 2020: 267, 2021: 267, 2022: 267, 2023: 267, 2024: 603
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Programa de Reserva de Vagas e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros Programas; Pessoas com Deficiência; Sem Fins Lucrativos; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 5:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros Programas; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A1143: Fonte: INEP – Censo da Educação Superior. ¦ A1144: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A1145: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1146: 3 - Pode incluir também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A1147: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A1148: 5 - O mesmo aluno pode ter mais de um tipo de Programa de Reserva de Vagas. ¦ A1149: 6 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 4.16 — aba `'4.16'` (2024)

- **Título (A4, 2024):** 4.16 - Número de Ingressantes nos Cursos de Graduação - Presenciais e a Distância, por Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.16'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1095
- **Colunas úteis por ano:** 2017: 88, 2018: 88, 2019: 88, 2020: 88, 2021: 88, 2022: 88, 2023: 88, 2024: 179
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas1-4
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Programa de Reserva de Vagas
- **Categorias — nível 3:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 4:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Notas de rodapé (2024):** A1141: Fonte: INEP – Censo da Educação Superior. ¦ A1142: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A1143: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1144: 3 - Pode incluir também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A1145: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A1146: 5 - O mesmo aluno pode ter mais de um tipo de Programa de Reserva de Vagas. ¦ A1147: 6 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça. ¦ A1148: 7 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 4.17 — aba `'4.17'` (2024)

- **Título (A4, 2024):** 4.17 - Número de Ingressantes nos Cursos de Graduação - Presenciais, por Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Processos Seletivos / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '4.17'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 679
- **Colunas úteis por ano:** 2017: 88, 2018: 88, 2019: 88, 2020: 88, 2021: 88, 2022: 88, 2023: 88, 2024: 179
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas1-3
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação4; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Programa de Reserva de Vagas
  - *variam entre anos:* Não Dispõe da Informação4 (2017,2018,2019,2020,2021,2022,2023); Não Dispõe da Informação5 (2024)
- **Categorias — nível 3:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 4:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Notas de rodapé (2024):** A724: Fonte: INEP – Censo da Educação Superior. ¦ A725: Notas:   1 - Inclui cursos de graduação presenciais. ¦ A726: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A727: 3 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A728: 4 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça. ¦ A729: 5 - O mesmo aluno pode ter mais de um tipo de Programa de Reserva de Vagas. ¦ A730: 6 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 5.1 — aba `'5.1'` (2024)

- **Título (A4, 2024):** 5.1 - Número de Matrículas nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.1'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3418
- **Colunas úteis por ano:** 2017: 38, 2018: 38, 2019: 38, 2020: 38, 2021: 38, 2022: 38, 2023: 38, 2024: 38
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Total; Total por Dependência Administrativa; Universidade
- **Categorias — nível 3:** Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Privada; Pública; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A3470: Fonte: INEP – Censo da Educação Superior. ¦ A3471: Notas:   1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3472: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3473: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior.

### Tab 5.2 — aba `'5.2'` (2024)

- **Título (A4, 2024):** 5.2 - Número de Matrículas nos Cursos de Graduação - Presenciais, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.2'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1116
- **Colunas úteis por ano:** 2017: 37, 2018: 37, 2019: 37, 2020: 37, 2021: 37, 2022: 37, 2023: 37, 2024: 38
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-2
- **Categorias — nível 2:** Centro Universitário; Faculdade; Total; Total por Dependência Administrativa; Universidade
- **Categorias — nível 3:** Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Privada; Pública; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A1161: Fonte: INEP – Censo da Educação Superior. ¦ A1162: Notas:   1 - Inclui cursos de graduação presenciais. ¦ A1163: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 5.3 — aba `'5.3'` (2024)

- **Título (A4, 2024):** 5.3 - Número de Matrículas nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso  e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.3'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 3416
- **Colunas úteis por ano:** 2017: 97, 2018: 97, 2019: 97, 2020: 97, 2021: 97, 2022: 97, 2023: 97, 2024: 97
- **Categorias — nível 1:** Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Bacharelado; Federal; Licenciatura; Não Aplicável4; Tecnológico; Total
- **Categorias — nível 4:** Bacharelado; Estadual; Federal; Licenciatura; Municipal; Não Aplicável4; Privada; Tecnológico; Total
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A3463: Fonte: INEP – Censo da Educação Superior. ¦ A3464: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A3465: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3466: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior.

### Tab 5.4 — aba `'5.4'` (2024)

- **Título (A4, 2024):** 5.4 - Número de Matrículas nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Dependência Administrativa e Turno, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.4'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1116
- **Colunas úteis por ano:** 2017: 59, 2018: 59, 2019: 59, 2020: 59, 2021: 59, 2022: 59, 2023: 59, 2024: 59
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Turno1-2
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Diurno; Noturno; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Diurno; Noturno; Total
- **Notas de rodapé (2024):** A1162: Fonte: INEP – Censo da Educação Superior. ¦ A1163: Notas:   1 -  Inclui cursos de graduação presenciais. ¦ A1164: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 5.5 — aba `'5.5 Características do Aluno'` (2024)

- **Título (A4, 2024):** 5.5 - Número de Matrículas nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.5 Características do Aluno'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3418
- **Colunas úteis por ano:** 2017: 60, 2018: 60, 2019: 60, 2020: 60, 2021: 60, 2022: 60, 2023: 60, 2024: 60
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Feminino; Masculino; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3471: Fonte: INEP – Censo da Educação Superior. ¦ A3472: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3473: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3474: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior.

### Tab 5.6 — aba `'5.6'` (2024)

- **Título (A4, 2024):** 5.6 - Número de Matrículas nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Cor/Raça e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.6'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3418
- **Colunas úteis por ano:** 2017: 316, 2018: 316, 2019: 316, 2020: 316, 2021: 316, 2022: 316, 2023: 316, 2024: 316
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Cor/Raça e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Amarela; Branca; Com Fins Lucrativos; Indígena; Não Dispõe da Informação4; Parda; Preta; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Amarela; Branca; Feminino; Indígena; Masculino; Não Dispõe da Informação4; Parda; Preta; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3472: Fonte: INEP – Censo da Educação Superior. ¦ A3473: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3474: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3475: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior. ¦ A3476: 4 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 5.7 — aba `'5.7'` (2024)

- **Título (A4, 2024):** 5.7 - Número de Matrículas nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Faixa Etária e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.7'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3418
- **Colunas úteis por ano:** 2017: 556, 2018: 556, 2019: 556, 2020: 556, 2021: 556, 2022: 556, 2023: 556, 2024: 556
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Faixa Etária e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** 65 Anos ou mais; Até 18 Anos; Com Fins Lucrativos; De 19 a 24 Anos; De 25 a 29 Anos; De 30 a 34 Anos; De 35 a 39 Anos; De 40 a 44 Anos; De 45 a 49 Anos; De 50 a 54 Anos; De 55 a 59 Anos; De 60 a 64 Anos; Privada; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** 65 Anos ou mais; Até 18 Anos; De 19 a 24 Anos; De 25 a 29 Anos; De 30 a 34 Anos; De 35 a 39 Anos; De 40 a 44 Anos; De 45 a 49 Anos; De 50 a 54 Anos; De 55 a 59 Anos; De 60 a 64 Anos; Feminino; Masculino; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3472: Fonte: INEP – Censo da Educação Superior. ¦ A3473: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3474: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3475: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior.

### Tab 5.8 — aba `'5.8'` (2024)

- **Título (A4, 2024):** 5.8 - Número de Matrículas nos Cursos de Graduação - Presenciais e a Distância, por Sexo e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.8'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 2130
- **Colunas úteis por ano:** 2017: 33, 2018: 33, 2019: 33, 2020: 25, 2021: 25, 2022: 25, 2023: 25, 2024: 27
- **Categorias — nível 1:** Sexo e Tipo de Deficiência1-4
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Auditiva; Autismo Infantil; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Superdotação; Surdez; Surdocegueira; Síndrome de Asperger; Síndrome de Rett; Total; Transtorno Desintegrativo da Infância; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista (TEA); Visão Monocular
  - *variam entre anos:* Autismo Infantil (2017,2018,2019,2020); Múltipla (2017,2018,2019); Síndrome de Asperger (2017,2018,2019); Síndrome de Rett (2017,2018,2019); Transtorno Desintegrativo da Infância (2017,2018,2019); Transtorno Global do Desenvolvimento (TGD) (2021,2022); Transtorno do Espectro Autista (TEA) (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A2175: Fonte: INEP – Censo da Educação Superior. ¦ A2176: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2177: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2178: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior. ¦ A2179: 4 - O mesmo aluno pode ter mais de um tipo de deficiência. ¦ A2180: 5 - Até o ano de 2023, as condições de baixa visão e visão monocular eram reportadas de forma agregada nos registros oficiais, sem distinção entre os dois tipos de deficiência visual. A partir de 2024, passou-se a adotar a segregação dessas categorias, permitindo que cada condição seja informada individualmente nos sistemas de coleta e análise de dados.

### Tab 5.9 — aba `'5.9'` (2024)

- **Título (A4, 2024):** 5.9 - Número de Matrículas nos Cursos de Graduação - Presenciais, por Sexo e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.9'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 865
- **Colunas úteis por ano:** 2017: 33, 2018: 33, 2019: 33, 2020: 25, 2021: 25, 2022: 25, 2023: 25, 2024: 27
- **Categorias — nível 1:** Sexo e Tipo de Deficiência1-3
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Auditiva; Autismo Infantil; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Superdotação; Surdez; Surdocegueira; Síndrome de Asperger; Síndrome de Rett; Total; Transtorno Desintegrativo da Infância; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista (TEA); Visão Monocular
  - *variam entre anos:* Autismo Infantil (2017,2018,2019,2020); Múltipla (2017,2018,2019); Síndrome de Asperger (2017,2018,2019); Síndrome de Rett (2017,2018,2019); Transtorno Desintegrativo da Infância (2017,2018,2019); Transtorno Global do Desenvolvimento (TGD) (2021,2022); Transtorno do Espectro Autista (TEA) (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A909: Fonte: INEP – Censo da Educação Superior. ¦ A910: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A911: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A912: 3 - O mesmo aluno pode ter mais de um tipo de deficiência. ¦ A913: 4 - Até o ano de 2023, as condições de baixa visão e visão monocular eram reportadas de forma agregada nos registros oficiais, sem distinção entre os dois tipos de deficiência visual. A partir de 2024, passou-se a adotar a segregação dessas categorias, permitindo que cada condição seja informada individualmente nos sistemas de coleta e análise de dados.

### Tab 5.10 — aba `'5.10'` (2024)

- **Título (A4, 2024):** 5.10 - Número de Matrículas nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Nacionalidade e Sexo, segundo  a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.10'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 29; Município (código preenchido): 3418
- **Colunas úteis por ano:** 2017: 172, 2018: 172, 2019: 172, 2020: 172, 2021: 172, 2022: 172, 2023: 172, 2024: 172
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Nacionalidade e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Brasileira; Brasileira  - Naturalizado; Com Fins Lucrativos; Estrangeira; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Brasileira; Brasileira  - Naturalizado; Estrangeira; Feminino; Masculino; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A3472: Fonte: INEP – Censo da Educação Superior. ¦ A3473: Notas: 1- Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3474: 2- As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3475: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior.

### Tab 5.11 — aba `'5.11 Financiamento'` (2024)

- **Título (A4, 2024):** 5.11 - Número de Matrículas nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Tipo de Financiamento Estudantil e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.11 Financiamento'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 2670
- **Colunas úteis por ano:** 2017: 219, 2018: 219, 2019: 219, 2020: 219, 2021: 219, 2022: 219, 2023: 219, 2024: 219
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Tipo de Financiamento Estudantil e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; FIES; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** FIES; Feminino; Masculino; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2718: Fonte: INEP – Censo da Educação Superior. ¦ A2719: Notas:  1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2720: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2721: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior. ¦ A2722: 4 - O mesmo aluno pode ter mais de um tipo de financiamento estudantil. ¦ A2723: 5 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades.

### Tab 5.12 — aba `'5.12'` (2024)

- **Título (A4, 2024):** 5.12 - Número de Matrículas nos Cursos de Graduação - Presenciais e a Distância, por Cor/Raça, Sexo e Tipo de Financiamento Estudantil, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.12'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 2670
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Financiamento Estudantil1-4
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação6; Parda; Preta; Total; Total por Tipo de Financiamento Estudantil
- **Categorias — nível 3:** FIES; Feminino; Masculino; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 4:** FIES; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Notas de rodapé (2024):** A2716: Fonte: INEP – Censo da Educação Superior. ¦ A2717: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2718: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2719: 3 - Inclui também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior. ¦ A2720: 4 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A2721: 5 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades. ¦ A2722: 6 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 5.13 — aba `'5.13'` (2024)

- **Título (A4, 2024):** 5.13  - Número de Matrículas nos Cursos de Graduação - Presenciais, por Cor/Raça, Sexo e Tipo de Financiamento Estudantil, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.13'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 644
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Financiamento Estudantil1-3
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Financiamento Estudantil
- **Categorias — nível 3:** FIES; Feminino; Masculino; Outros Financiamentos4; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 4:** FIES; Outros Financiamentos4; ProUni Integral; ProUni Parcial; Total
- **Notas de rodapé (2024):** A689: Fonte: INEP – Censo da Educação Superior. ¦ A690: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A691: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A692: 3 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A693: 4 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades. ¦ A694: 5 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 5.14 — aba `'5.14 Reserva de Vagas'` (2024)

- **Título (A4, 2024):** 5.14 - Número de Matrículas nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Programa de Reserva de Vagas e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.14 Reserva de Vagas'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1224
- **Colunas úteis por ano:** 2017: 267, 2018: 267, 2019: 267, 2020: 267, 2021: 267, 2022: 267, 2023: 267, 2024: 603
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Programa de Reserva de Vagas e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros Programas; Pessoas com Deficiência; Sem Fins Lucrativos; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 5:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros Programas; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A1272: Fonte: INEP – Censo da Educação Superior. ¦ A1273: Notas:   1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A1274: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1275: 3 - Pode incluir também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior. ¦ A1276: 4 - O mesmo aluno pode ter mais de um tipo de Forma de Ingresso. ¦ A1277: 5 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 5.15 — aba `'5.15'` (2024)

- **Título (A4, 2024):** 5.15 - Número de Matrículas nos Cursos de Graduação - Presenciais e a Distância, por Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.15'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 1224
- **Colunas úteis por ano:** 2017: 88, 2018: 88, 2019: 88, 2020: 88, 2021: 88, 2022: 88, 2023: 88, 2024: 179
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas1-3
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação4; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Programa de Reserva de Vagas
  - *variam entre anos:* Não Dispõe da Informação4 (2017,2018,2019,2020,2021,2022,2023); Não Dispõe da Informação5 (2024)
- **Categorias — nível 3:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 4:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Notas de rodapé (2024):** A1270: Fonte: INEP – Censo da Educação Superior. ¦ A1271: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A1272: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1273: 3 - Pode incluir também as matrículas na modalidade a distância (EaD) ofertadas por instituições brasileiras no exterior. ¦ A1274: 4 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça. ¦ A1275: 5 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 5.16 — aba `'5.16'` (2024)

- **Título (A4, 2024):** 5.16 - Número de Matrículas nos Cursos de Graduação - Presenciais, por Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Matrículas / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '5.16'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de matriculas nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 27; Município (código preenchido): 733
- **Colunas úteis por ano:** 2017: 88, 2018: 88, 2019: 88, 2020: 88, 2021: 88, 2022: 88, 2023: 88, 2024: 179
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas1-2
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação3; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Programa de Reserva de Vagas
  - *variam entre anos:* Não Dispõe da Informação3 (2017,2018,2019,2020,2021,2022,2023); Não Dispõe da Informação5 (2024)
- **Categorias — nível 3:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 4:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Notas de rodapé (2024):** A778: Fonte: INEP – Censo da Educação Superior. ¦ A779: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A780: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A781: 3 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça. ¦ A782: 4 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 6.1 — aba `'6.1'` (2024)

- **Título (A4, 2024):** 6.1 - Número de Concluintes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.1'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 26; Município (código preenchido): 2912
- **Colunas úteis por ano:** 2017: 38, 2018: 38, 2019: 38, 2020: 38, 2021: 38, 2022: 38, 2023: 38, 2024: 38
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Dependência Administrativa; Universidade
- **Categorias — nível 3:** Federal; Privada; Pública; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A2964: Fonte: INEP – Censo da Educação Superior. ¦ A2965: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A2966: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2967: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 6.2 — aba `'6.2'` (2024)

- **Título (A4, 2024):** 6.2 - Número de Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.2'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 1029
- **Colunas úteis por ano:** 2017: 37, 2018: 37, 2019: 37, 2020: 37, 2021: 37, 2022: 37, 2023: 37, 2024: 38
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-2
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Total por Dependência Administrativa; Universidade
- **Categorias — nível 3:** Federal; Privada; Pública; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estadual; Federal; Municipal; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A1074: Fonte: INEP – Censo da Educação Superior. ¦ A1075: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A1076: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 6.3 — aba `'6.3'` (2024)

- **Título (A4, 2024):** 6.3  - Número de Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Grau Acadêmico do Curso e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.3'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 2910
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Organização Acadêmica, Grau Acadêmico e Dependência Administrativa1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Bacharelado; Federal; Licenciatura; Tecnológico; Total
- **Categorias — nível 4:** Bacharelado; Estadual; Federal; Licenciatura; Municipal; Privada; Tecnológico; Total
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A2957: Fonte: INEP – Censo da Educação Superior. ¦ A2958: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2959: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2960: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 6.4 — aba `'6.4'` (2024)

- **Título (A4, 2024):** 6.4 - Número de Concluintes nos Cursos de Graduação - Presenciais, por Organização Acadêmica, Dependência Administrativa e Turno, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.4'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 1029
- **Colunas úteis por ano:** 2017: 59, 2018: 59, 2019: 59, 2020: 59, 2021: 59, 2022: 59, 2023: 59, 2024: 59
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Turno1-2
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Diurno; Noturno; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Diurno; Noturno; Total
- **Notas de rodapé (2024):** A1075: Fonte: INEP – Censo da Educação Superior. ¦ A1076: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A1077: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 6.5 — aba `'6.5 Características do Aluno'` (2024)

- **Título (A4, 2024):** 6.5 - Número de Concluintes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.5 Características do Aluno'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 26; Município (código preenchido): 2912
- **Colunas úteis por ano:** 2017: 61, 2018: 61, 2019: 60, 2020: 60, 2021: 60, 2022: 60, 2023: 60, 2024: 60
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Feminino; Masculino; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2965: Fonte: INEP – Censo da Educação Superior. ¦ A2966: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A2967: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2968: 3 - Inclui também os cursos na modalidade a distância (EAD) ofertados por instituições brasileiras no exterior.

### Tab 6.6 — aba `'6.6'` (2024)

- **Título (A4, 2024):** 6.6 - Número de Concluintes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Cor/Raça e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.6'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 26; Município (código preenchido): 2912
- **Colunas úteis por ano:** 2017: 316, 2018: 316, 2019: 316, 2020: 316, 2021: 316, 2022: 316, 2023: 316, 2024: 316
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Cor/Raça e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Amarela; Branca; Com Fins Lucrativos; Indígena; Não Dispõe da Informação4; Parda; Preta; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Amarela; Branca; Feminino; Indígena; Masculino; Não Dispõe da Informação4; Parda; Preta; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2966: Fonte: INEP – Censo da Educação Superior. ¦ A2967: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A2968: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2969: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A2970: 4 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 6.7 — aba `'6.7'` (2024)

- **Título (A4, 2024):** 6.7 - Número de Concluintes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Faixa Etária e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.7'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 26; Município (código preenchido): 2912
- **Colunas úteis por ano:** 2017: 556, 2018: 556, 2019: 556, 2020: 556, 2021: 556, 2022: 556, 2023: 556, 2024: 556
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Faixa Etária e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** 65 Anos ou mais; Até 18 Anos; Com Fins Lucrativos; De 19 a 24 Anos; De 25 a 29 Anos; De 30 a 34 Anos; De 35 a 39 Anos; De 40 a 44 Anos; De 45 a 49 Anos; De 50 a 54 Anos; De 55 a 59 Anos; De 60 a 64 Anos; Privada; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** 65 Anos ou mais; Até 18 Anos; De 19 a 24 Anos; De 25 a 29 Anos; De 30 a 34 Anos; De 35 a 39 Anos; De 40 a 44 Anos; De 45 a 49 Anos; De 50 a 54 Anos; De 55 a 59 Anos; De 60 a 64 Anos; Feminino; Masculino; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2966: Fonte: INEP – Censo da Educação Superior. ¦ A2967: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A2968: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2969: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 6.8 — aba `'6.8'` (2024)

- **Título (A4, 2024):** 6.8 - Número de Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Sexo e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.8'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 1140
- **Colunas úteis por ano:** 2017: 33, 2018: 33, 2019: 33, 2020: 25, 2021: 25, 2022: 25, 2023: 25, 2024: 27
- **Categorias — nível 1:** Sexo e Tipo de Deficiência1-4
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Auditiva; Autismo Infantil; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Superdotação; Surdez; Surdocegueira; Síndrome de Asperger; Síndrome de Rett; Total; Transtorno Desintegrativo da Infância; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista (TEA); Visão Monocular
  - *variam entre anos:* Autismo Infantil (2017,2018,2019,2020); Múltipla (2017,2018,2019); Síndrome de Asperger (2017,2018,2019); Síndrome de Rett (2017,2018,2019); Transtorno Desintegrativo da Infância (2017,2018,2019); Transtorno Global do Desenvolvimento (TGD) (2021,2022); Transtorno do Espectro Autista (TEA) (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A1185: Fonte: INEP – Censo da Educação Superior. ¦ A1186: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A1187: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A1188: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A1189: 4 - O mesmo aluno pode ter mais de um tipo de deficiência. ¦ A1190: 5 - Até o ano de 2023, as condições de baixa visão e visão monocular eram reportadas de forma agregada nos registros oficiais, sem distinção entre os dois tipos de deficiência visual. A partir de 2024, passou-se a adotar a segregação dessas categorias, permitindo que cada condição seja informada individualmente nos sistemas de coleta e análise de dados.

### Tab 6.9 — aba `'6.9'` (2024)

- **Título (A4, 2024):** 6.9  - Número de Concluintes nos Cursos de Graduação - Presenciais, por Sexo e Tipo de Deficiência, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.9'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 528
- **Colunas úteis por ano:** 2017: 33, 2018: 33, 2019: 33, 2020: 25, 2021: 25, 2022: 25, 2023: 25, 2024: 27
- **Categorias — nível 1:** Sexo e Tipo de Deficiência1-3
- **Categorias — nível 2:** Feminino; Masculino; Total
- **Categorias — nível 3:** Auditiva; Autismo Infantil; Baixa Visão; Cegueira; Física; Intelectual; Múltipla; Superdotação; Surdez; Surdocegueira; Síndrome de Asperger; Síndrome de Rett; Total; Transtorno Desintegrativo da Infância; Transtorno Global do Desenvolvimento (TGD); Transtorno do Espectro Autista (TEA); Visão Monocular
  - *variam entre anos:* Autismo Infantil (2017,2018,2019,2020); Múltipla (2017,2018,2019); Síndrome de Asperger (2017,2018,2019); Síndrome de Rett (2017,2018,2019); Transtorno Desintegrativo da Infância (2017,2018,2019); Transtorno Global do Desenvolvimento (TGD) (2021,2022); Transtorno do Espectro Autista (TEA) (2023,2024); Visão Monocular (2024)
- **Notas de rodapé (2024):** A572: Fonte: INEP – Censo da Educação Superior. ¦ A573: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A574: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A575: 3 - O mesmo aluno pode ter mais de um tipo de deficiência. ¦ A576: 4 - Até o ano de 2023, as condições de baixa visão e visão monocular eram reportadas de forma agregada nos registros oficiais, sem distinção entre os dois tipos de deficiência visual. A partir de 2024, passou-se a adotar a segregação dessas categorias, permitindo que cada condição seja informada individualmente nos sistemas de coleta e análise de dados.

### Tab 6.10 — aba `'6.10'` (2024)

- **Título (A4, 2024):** 6.10 - Número de Concluintes nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Nacionalidade e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.10'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 26; Município (código preenchido): 2912
- **Colunas úteis por ano:** 2017: 172, 2018: 172, 2019: 172, 2020: 172, 2021: 172, 2022: 172, 2023: 172, 2024: 172
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Nacionalidade e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Brasileira; Brasileira  - Naturalizado; Com Fins Lucrativos; Estrangeira; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** Brasileira; Brasileira  - Naturalizado; Estrangeira; Feminino; Masculino; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2966: Fonte: INEP – Censo da Educação Superior. ¦ A2967: Notas: 1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A2968: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2969: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 6.11 — aba `'6.11 Financiamento'` (2024)

- **Título (A4, 2024):** 6.11 - Número de Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica,  Dependência Administrativa, Tipo de Financiamento Estudantil e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.11 Financiamento'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 2071
- **Colunas úteis por ano:** 2017: 219, 2018: 219, 2019: 219, 2020: 219, 2021: 219, 2022: 219, 2023: 219, 2024: 219
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Tipo de Financiamento Estudantil e Sexo1-4
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; FIES; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Sem Fins Lucrativos; Total
- **Categorias — nível 5:** FIES; Feminino; Masculino; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A2119: Fonte: INEP – Censo da Educação Superior. ¦ A2120: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2121: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2122: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A2123: 4 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A2124: 5 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades.

### Tab 6.12 — aba `'6.12'` (2024)

- **Título (A4, 2024):** 6.12  - Número de Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Cor/Raça, Sexo e Tipo de Financiamento Estudantil, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.12'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 2071
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Financiamento Estudantil1-4
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação6; Parda; Preta; Total; Total por Tipo de Financiamento Estudantil
- **Categorias — nível 3:** FIES; Feminino; Masculino; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 4:** FIES; Outros Financiamentos5; ProUni Integral; ProUni Parcial; Total
- **Notas de rodapé (2024):** A2117: Fonte: INEP – Censo da Educação Superior. ¦ A2118: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A2119: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A2120: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A2121: 4 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A2122: 5 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades. ¦ A2123: 6 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 6.13 — aba `'6.13'` (2024)

- **Título (A4, 2024):** 6.13  - Número de Concluintes nos Cursos de Graduação - Presenciais, por Cor/Raça, Sexo e Tipo de Financiamento Estudantil, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.13'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 585
- **Colunas úteis por ano:** 2017: 75, 2018: 75, 2019: 75, 2020: 75, 2021: 75, 2022: 75, 2023: 75, 2024: 75
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Financiamento Estudantil1-3
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Financiamento Estudantil
- **Categorias — nível 3:** FIES; Feminino; Masculino; Outros Financiamentos4; ProUni Integral; ProUni Parcial; Total
- **Categorias — nível 4:** FIES; Outros Financiamentos4; ProUni Integral; ProUni Parcial; Total
- **Notas de rodapé (2024):** A630: Fonte: INEP – Censo da Educação Superior. ¦ A631: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A632: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A633: 3 - O mesmo aluno pode ter mais de um tipo de Financiamento Estudantil. ¦ A634: 4 - Outros financiamentos incluem alunos que utilizam financiamento estudantil reembolsável e não reembolsável do governo estadual, municipal, administrado pela IES, administrado por entidades externas à IES e por outras entidades. ¦ A635: 5 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça.

### Tab 6.14 — aba `'6.14 Reserva de Vagas'` (2024)

- **Título (A4, 2024):** 6.14 - Número de Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Organização Acadêmica, Dependência Administrativa, Programa de Reserva de Vagas  e Sexo, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.14 Reserva de Vagas'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 814
- **Colunas úteis por ano:** 2017: 267, 2018: 267, 2019: 267, 2020: 267, 2021: 267, 2022: 267, 2023: 267, 2024: 603
- **Categorias — nível 1:** Organização Acadêmica, Dependência Administrativa, Programa de Reserva de Vagas e Sexo1-3
- **Categorias — nível 2:** Centro Universitário; Faculdade; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Total; Universidade
- **Categorias — nível 3:** Estadual; Federal; Municipal; Privada; Total
- **Categorias — nível 4:** Com Fins Lucrativos; Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros Programas; Pessoas com Deficiência; Sem Fins Lucrativos; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 5:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros Programas; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 6:** Feminino; Masculino; Total
- **Notas de rodapé (2024):** A861: Fonte: INEP – Censo da Educação Superior. ¦ A862: Notas:  1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A863: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A864: 3 - Pode incluir também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A865: 4 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 6.15 — aba `'6.15'` (2024)

- **Título (A4, 2024):** 6.15 - Número de Concluintes nos Cursos de Graduação - Presenciais e a Distância, por Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.15'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 814
- **Colunas úteis por ano:** 2017: 88, 2018: 88, 2019: 88, 2020: 88, 2021: 88, 2022: 88, 2023: 88, 2024: 179
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas1-3
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação4; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Programa de Reserva de Vagas
  - *variam entre anos:* Não Dispõe da Informação4 (2017,2018,2019,2020,2021,2022,2023); Não Dispõe da Informação5 (2024)
- **Categorias — nível 3:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 4:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Notas de rodapé (2024):** A859: Fonte: INEP – Censo da Educação Superior. ¦ A860: Notas: 1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD). ¦ A861: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A862: 3 - Pode incluir também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A863: 4 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça. ¦ A864: 5 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 6.16 — aba `'6.16'` (2024)

- **Título (A4, 2024):** 6.16 - Número de Concluintes nos Cursos de Graduação - Presenciais, por Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Concluintes / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '6.16'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de concluintes nos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 611
- **Colunas úteis por ano:** 2017: 88, 2018: 88, 2019: 88, 2020: 88, 2021: 88, 2022: 88, 2023: 88, 2024: 179
- **Categorias — nível 1:** Cor/Raça, Sexo e Tipo de Programa de Reserva de Vagas1-2
- **Categorias — nível 2:** Amarela; Branca; Indígena; Não Dispõe da Informação3; Não Dispõe da Informação5; Parda; Preta; Total; Total por Tipo de Programa de Reserva de Vagas
  - *variam entre anos:* Não Dispõe da Informação3 (2017,2018,2019,2020,2021,2022,2023); Não Dispõe da Informação5 (2024)
- **Categorias — nível 3:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Feminino; Masculino; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Categorias — nível 4:** Estudante Idoso; Estudante Internacional; Estudante Medalhista; Estudante Preto, Pardo ou Indígena; Estudante Procedente de Escola Pública; Estudante Quilombola; Estudante Refugiado; Estudante Transgênero; Estudante de Comunidade Tradicional; Outros; Pessoas com Deficiência; Social / Renda Familiar; Total; Étnico
  - *variam entre anos:* Estudante Idoso (2024); Estudante Internacional (2024); Estudante Medalhista (2024); Estudante Preto, Pardo ou Indígena (2024); Estudante Quilombola (2024); Estudante Refugiado (2024); Estudante Transgênero (2024); Estudante de Comunidade Tradicional (2024); Étnico (2017,2018,2019,2020,2021,2022,2023)
- **Notas de rodapé (2024):** A656: Fonte: INEP – Censo da Educação Superior. ¦ A657: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A658: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A659: 3 - A coluna denominada "Não Dispõe da Informação" agrega tanto os casos em que de fato não se dispõe da informação, quanto os alunos que não quiseram declarar cor/raça. ¦ A660: 4 - Inclui alunos que ingressaram por meio de política de ação afirmativa ou por programa diferenciado de destinação de vagas.

### Tab 7.1 — aba `'7.1'` (2024)

- **Título (A4, 2024):** 7.1 - Número de Ingressantes, Matrículas, Concluintes, Matrículas Trancadas, Matrículas Desvinculadas, Alunos Transferidos para outros cursos na mesma IES e Alunos Falecidos, nos Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Dados Gerais / Cursos de Graduação e Sequenciais de Formação Específica - Presenciais e a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '7.1'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de ingressantes
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município, E=Nível Acadêmico do Curso
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 3; Região (A='Total <região>'): 7; UF (B='Total <UF>'): 26; Município (código preenchido): 3553
- **Colunas úteis por ano:** 2017: 166, 2018: 166, 2019: 166, 2020: 166, 2021: 166, 2022: 166, 2023: 166, 2024: 166
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-3; Total Geral
- **Categorias — nível 2:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Centro Universitário; Concluintes; Faculdade; Ingressantes; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Universidade
- **Categorias — nível 3:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Concluintes; Federal; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas
- **Categorias — nível 4:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Concluintes; Estadual; Federal; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Municipal; Privada; Total
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A3606: Fonte: INEP – Censo da Educação Superior. ¦ A3607: Notas:     1 - Inclui cursos de graduação e sequenciais de formação específica, presenciais e/ou a distância (EaD). ¦ A3608: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3609: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 7.2 — aba `'7.2'` (2024)

- **Título (A4, 2024):** 7.2 - Número de Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas, Concluintes, Matrículas Trancadas, Matrículas Desvinculadas, Alunos Transferidos para outros cursos na mesma IES e Alunos Falecidos, nos Cursos de Graduação - Presenciais, por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Dados Gerais / Cursos de Graduação - Presenciais
- **Anos presentes:** todos (2017–2024); nomes da aba: '7.2'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de cursos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 1121
- **Colunas úteis por ano:** 2017: 234, 2018: 234, 2019: 234, 2020: 234, 2021: 234, 2022: 234, 2023: 234, 2024: 234
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-2; Total Geral
- **Categorias — nível 2:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Centro Universitário; Concluintes; Faculdade; Ingressantes; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Número de Cursos; Universidade; Vagas Oferecidas
- **Categorias — nível 3:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Concluintes; Federal; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Número de Cursos; Vagas Oferecidas
- **Categorias — nível 4:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Concluintes; Estadual; Federal; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Municipal; Número de Cursos; Privada; Total; Vagas Oferecidas
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A1167: Fonte: Censo da Educação Superior - INEP. ¦ A1168: Notas: 1 - Inclui cursos de graduação presenciais. ¦ A1169: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso.

### Tab 7.3 — aba `'7.3'` (2024)

- **Título (A4, 2024):** 7.3 -  Número de Polos, Cursos, Vagas Oferecidas, Candidatos Inscritos,  Ingressantes, Matrículas, Concluintes, Matrículas Trancadas, Matrículas Desvinculadas, Alunos Transferidos para outros cursos na mesma IES e Alunos Falecidos, nos Cursos de Graduação a Distância (EaD), por Organização Acadêmica e Dependência Administrativa, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Dados Gerais / Cursos de Graduação - a Distância
- **Anos presentes:** todos (2017–2024); nomes da aba: '7.3'
- **Unidade:** contagem (número absoluto) · **Indicador (título):** numero de polos
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 3524
- **Colunas úteis por ano:** 2017: 257, 2018: 257, 2019: 257, 2020: 257, 2021: 257, 2022: 257, 2023: 257, 2024: 257
- **Categorias — nível 1:** Organização Acadêmica e Dependência Administrativa1-3; Total Geral
- **Categorias — nível 2:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Centro Universitário; Concluintes; Faculdade; Ingressantes; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Número de Cursos; Número de Polos; Universidade; Vagas Oferecidas
- **Categorias — nível 3:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Concluintes; Federal; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Número de Cursos; Número de Polos; Vagas Oferecidas
- **Categorias — nível 4:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Concluintes; Estadual; Federal; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Municipal; Número de Cursos; Número de Polos; Privada; Total; Vagas Oferecidas
- **Categorias — nível 5:** Com Fins Lucrativos; Sem Fins Lucrativos; Total
- **Notas de rodapé (2024):** A3571: Fonte: Censo da Educação Superior - INEP. ¦ A3572: Notas:    1 - Inclui cursos de graduação a distância (EaD). ¦ A3573: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A3574: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.

### Tab 7.4 — aba `'7.4'` (2024)

- **Título (A4, 2024):** 7.4 -  Dados Gerais em Instituições de Ensino Comunitárias e/ou Confessionais, tais como: Número Cursos, Vagas Oferecidas, Candidatos Inscritos, Ingressantes, Matrículas, Concluintes, Matrículas Trancadas, Matrículas Desvinculadas, Alunos Transferidos para outros cursos na mesma IES e Alunos Falecidos, nos Cursos de Graduação  - Presenciais e a Distância, por Organização Acadêmica, segundo a Região Geográfica, a Unidade da Federação e o Município - 2024
- **Tema (A2) / universo (A3):** Dados Gerais / Cursos de Graduação  -  Presenciais e a Distância - Instituições Comunitárias e/ou Confessionais
- **Anos presentes:** 2023, 2024; nomes da aba: '7.4'
- **Unidade:** verificar — título não indica contagem · **Indicador (título):** 
- **Dimensões de linha (identificadores):** A=Região Geográfica, B=Unidade da Federação, C=Município, D=Código do Município
- **Níveis geográficos (2024):** Brasil (A='Total Brasil'): 1; Região (A='Total <região>'): 5; UF (B='Total <UF>'): 25; Município (código preenchido): 478
- **Colunas úteis por ano:** 2023: 154, 2024: 154
- **Categorias — nível 1:** Organização Acadêmica1-3; Total Geral - Instituições Privadas - Comunitárias e/ou Confessionais1-5
- **Categorias — nível 2:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Centro Universitário; Concluintes; Faculdade; Ingressantes; Instituto Federal de Educação, Ciência e Tecnologia (IF) e Centro Federal de Educação Tecnológica (Cefet); Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Número de Cursos; Universidade; Vagas Oferecidas
- **Categorias — nível 3:** Alunos Falecidos; Alunos Transferidos para outros cursos na mesma IES; Candidatos Inscritos; Comunitária; Concluintes; Confessional; Ingressantes; Matrículas; Matrículas Desvinculadas; Matrículas Trancadas; Número de Cursos; Total; Vagas Oferecidas
- **Categorias — nível 4:** Comunitária; Confessional; Total
- **Notas de rodapé (2024):** A524: Fonte: INEP – Censo da Educação Superior. ¦ A525: Notas:      1 - Inclui cursos de graduação, presenciais e/ou a distância (EaD) em Instituições Comunitárias e/ou Confessionais. ¦ A526: 2 - As Regiões Geográficas, Unidades da Federação e Municípios correspondem ao local de oferta do Curso. ¦ A527: 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. ¦ A528: 4 - No Total Brasil foram incluídos o. número de cursos, vagas oferecidas e candidatos inscritos dos cursos EAD. ¦ A529: 5 - O mesmo curso EAD pode ser oferecido em mais de um local de oferta. ¦ A530: 6 - O INEP não coleta o número de vagas oferecidas e o número de candidatos inscritos dos cursos EAD por local de oferta do curso. ¦ A531: 7 - A mesma Instituição pode ser comunitária e Confessional.

## 3. Categorias das colunas identificadoras (linhas)

| Conjunto | Tabela | Coluna | Ano | Nº distintos | Adicionados vs ano anterior | Removidos vs ano anterior |
|---|---|---|---|---|---|---|
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2017 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2018 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2019 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2020 | 29 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2021 | 29 | 0 |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2022 | 29 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2023 | 28 | \| Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins | 0 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26 \| 27 \| 28 \| 29 \| 31 \| 32 \| 33 \| 35 \| 41 \| 42 \| 43 \| 50 \| 51 \| 52 \| 53 \| 61 |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Código da UF | 2024 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2017 | 685 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2018 | 681 | "0612D01" \| Defesa cibernética | "0114E01" \| "0722C01" \| "0732E04" \| Cerâmica \| Economia doméstica formação de professor \| Engenharia portuária |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2019 | 685 | "0411G01" \| "0413G10" \| "0421S01" \| "0721P04" \| Gestão estratégica \| Gestão fiscal e tributária \| Produção de cerveja \| Serviços jurídicos e cartoriais | "0716A01" \| "0811F01" \| Aeroespacial \| Fruticultura |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2020 | 699 | "0614I01" \| "0616I01" \| "0617A01" \| "0617C01" \| "0617C02" \| "0617C03" \| "0712G02" \| Agrocomputação \| Ciência de dados \| Computação e Tecnologias da Informação e Comunicação (TIC) em biociências e saúde \| Criação digital \| Gestão de resíduos \| Inteligência artificial \| Internet das coisas |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2021 | 699 | "1088P01" \| Programas interdisciplinares abrangendo serviços | "0713E03" \| Engenharia bioenergética |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2022 | 703 | "0421M01" \| "0811F01" \| Fruticultura \| Mediação |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2023 | 709 | "0199P01" \| "0399P01" \| "0732M01" \| "0914A01" \| Análises clínicas e toxicológicas \| Material de construção \| Programas abrangendo ciências sociais, comunicação e informação em processo de definição da classificação \| Programas abrangendo educação em processo de definição da classificação | "0722P01" \| Papel e celulose |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Nome e Código do Curso de Graduação4 | 2024 | 707 | "0119P01" \| "0499P01" \| "0612S01" \| "0613C01" \| "0613I01" \| "0613I02" \| "0613S01" \| "0613S02" \| "0619P01" \| "0681A01" \| "0681C01" \| "0681C02" \| "0681C03" \| "0681J01" \| "0714S03" \| "0722C01" \| "0722P01" \| "0914P01" \| Cerâmica \| Engenharia de computação \| Papel e celulose \| Programas abrangendo Computação e Tecnologias da Informação e Comunicação (TIC) em processo de definição d | "0199P01" \| "0613J01" \| "0614C01" \| "0614I01" \| "0615S01" \| "0615S02" \| "0615S03" \| "0616E01" \| "0616I01" \| "0616S01" \| "0617A01" \| "0617C01" \| "0617C02" \| "0617C03" \| "0714G01" \| "0724E03" \| "0725P02" \| "0811A03" \| "1011E01" \| Agronegócio \| Economia doméstica \| Engenharia de computação (DCN Computação) \| Engenharia de computação (DCN Engenharia) \| Engenharia geológica \| Ge |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2017 | 16 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2018 | 16 | 6 - Nos cursos a distância (EaD), o número de vagas e inscritos não são coletados por polo. Por tanto, esses dados só São computados a nível Brasil. | 6 - Nos cursos a distância (EaD), o número de vagas e inscritos não são coletados por polo. Por tanto, esses dados só são computados a nível Brasil. |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2019 | 16 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2020 | 16 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2021 | 16 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2022 | 16 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2023 | 16 | 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior.   \| Fonte: INEP - Censo da Educação Superior. | 3 - Inclui também os cursos na modalidade a distância (Ead) ofertados por instituições brasileiras no exterior.   \| Fonte: Censo da Educação Superior - INEP. |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Região Geográfica | 2024 | 16 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2017 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2018 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2019 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2020 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2021 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2022 | 28 |  |  |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2023 | 28 | 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26 \| 27 \| 28 \| 29 \| 31 \| 32 \| 33 \| 35 \| 41 \| 42 \| 43 \| 50 \| 51 \| 52 \| 53 \| 61 | \| Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins |
| Anexo I — Tabela 8.1 | Anexo I — Tabela 8.1 | Unidade da Federação | 2024 | 27 |  | 61 |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2017 | 27 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2018 | 27 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2019 | 27 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2020 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2021 | 27 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2022 | 27 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2023 | 27 | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins | 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26 \| 27 \| 28 \| 29 \| 31 \| 32 \| 33 \| 35 \| 41 \| 42 \| 43 \| 50 \| 51 \| 52 \| 53 |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Código da UF | 2024 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2017 | 683 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2018 | 679 | "0612D01" \| Defesa cibernética | "0114E01" \| "0722C01" \| "0732E04" \| Cerâmica \| Economia doméstica formação de professor \| Engenharia portuária |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2019 | 679 | "0411G01" \| "0421S01" \| Gestão fiscal e tributária \| Serviços jurídicos e cartoriais | "0716A01" \| "0811F01" \| Aeroespacial \| Fruticultura |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2020 | 689 | "0614I01" \| "0617A01" \| "0617C01" \| "0617C02" \| "0617C03" \| Agrocomputação \| Ciência de dados \| Computação e Tecnologias da Informação e Comunicação (TIC) em biociências e saúde \| Criação digital \| Inteligência artificial |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2021 | 685 |  | "0211C02" \| "0713E03" \| Comunicação assistiva \| Engenharia bioenergética |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2022 | 687 | "0811F01" \| Fruticultura |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2023 | 688 | "0399P01" \| "0413G10" \| Gestão estratégica \| Programas abrangendo ciências sociais, comunicação e informação em processo de definição da classificação | \| "0722P01" \| Papel e celulose |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Nome e Código do Curso de Graduação3 | 2024 | 683 | \| "0119P01" \| "0499P01" \| "0612S01" \| "0613C01" \| "0613I01" \| "0613S01" \| "0613S02" \| "0681A01" \| "0681C01" \| "0681C02" \| "0681C03" \| "0681J01" \| "0714S03" \| "0722C01" \| "0722P01" \| Cerâmica \| Engenharia de computação \| Papel e celulose \| Programas abrangendo educação em processo de definição da classificação \| Programas abrangendo negócios, administração e direito em processo  | "0613J01" \| "0614C01" \| "0614I01" \| "0615S01" \| "0615S02" \| "0615S03" \| "0616E01" \| "0616S01" \| "0617A01" \| "0617C01" \| "0617C02" \| "0617C03" \| "0714G01" \| "0724E03" \| "0725P02" \| "0811A03" \| "1011E01" \| "1032S01" \| Agronegócio \| Economia doméstica \| Engenharia de computação (DCN Computação) \| Engenharia de computação (DCN Engenharia) \| Engenharia geológica \| Gestão de telec |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2017 | 11 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2018 | 11 | Fonte: Censo da Educação Superior - INEP. | Fonte: INEP - Censo da Educação Superior. |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2019 | 11 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2020 | 11 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2021 | 11 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2022 | 11 | Notas:  1 - Inclui cursos de graduação, presenciais com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. | Notas: 1 - Inclui cursos de graduação, presenciais com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2023 | 11 | Fonte: INEP - Censo da Educação Superior. | Fonte: Censo da Educação Superior - INEP. |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Região Geográfica | 2024 | 11 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2017 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2018 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2019 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2020 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2021 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2022 | 28 |  |  |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2023 | 27 | 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26 \| 27 \| 28 \| 29 \| 31 \| 32 \| 33 \| 35 \| 41 \| 42 \| 43 \| 50 \| 51 \| 52 \| 53 | \| Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins |
| Anexo II — Tabela 8.2 | Anexo II — Tabela 8.2 | Unidade da Federação | 2024 | 27 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2017 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2018 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2019 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2020 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2021 | 29 | 0 |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2022 | 29 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2023 | 28 | \| Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins | 0 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26 \| 27 \| 28 \| 29 \| 31 \| 32 \| 33 \| 35 \| 41 \| 42 \| 43 \| 50 \| 51 \| 52 \| 53 \| 61 |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Código da UF | 2024 | 27 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2017 | 257 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2018 | 309 | "0111P02" \| "0115L05" \| "0211F01" \| "0211P01" \| "0211P03" \| "0212D02" \| "0213A03" \| "0222H01" \| "0231L05" \| "0231L12" \| "0312S01" \| "0511B01" \| "0531Q01" \| "0531Q02" \| "0612D01" \| "0688P01" \| "0711E05" \| "0712S01" \| "0713S01" \| "0714E09" \| "0724E02" \| "0731A01" \| "0915F02" \| "0915T01" \| "0921G01" \| "1014G01" \| Agrimensura \| Artes visuais \| Biologia \| Defesa cibernética |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2019 | 347 | "0111P01" \| "0113E03" \| "0115L06" \| "0115L17" \| "0211A01" \| "0321R01" \| "0322M01" \| "0388P01" \| "0413G10" \| "0421S01" \| "0533F01" \| "0542E01" \| "0714A01" \| "0715E03" \| "0721E01" \| "0721P04" \| "0917P01" \| "0918S01" \| "1041T01" \| "1041T02" \| Animação \| Automação industrial \| Educação indígena formação de professor \| Engenharia de alimentos \| Engenharia metalúrgica \| Estatíst | "0715M01" \| Manutenção industrial |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2020 | 393 | "0011A09" \| "0313P01" \| "0321C01" \| "0322A01" \| "0411G01" \| "0532G03" \| "0614I01" \| "0616I01" \| "0617C01" \| "0617C02" \| "0710E01" \| "0712G02" \| "0714E03" \| "0714M01" \| "0715F01" \| "0715M01" \| "0716E03" \| "0716S01" \| "0724E01" \| "0731E03" \| "0732C02" \| "0811Z01" \| "0988P01" \| "1014F01" \| ABI Saúde e bem-estar \| Arquivologia \| Ciência de dados \| Computação e Tecnologias da | "0721P03" \| Produção sucroalcooleira |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2021 | 419 | "0114E02" \| "0115L01" \| "0211C02" \| "0231L02" \| "0231L16" \| "0312A01" \| "0312C02" \| "0413G06" \| "0617A01" \| "0713E01" \| "0713E02" \| "0714E08" \| "0714S01" \| "0721P03" \| "0724M01" \| "0912M01" \| "1088P01" \| Agrocomputação \| Antropologia \| Ciências sociais \| Comunicação assistiva \| Educação do campo em áreas de conhecimento da educação básica formação de professor \| Eletrotécnica | "0231L05" \| "0715E03" \| "0716E03" \| "0724E02" \| Engenharia automotiva \| Engenharia de petróleo \| Engenharia metalúrgica \| Letras inglês |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2022 | 429 | "0421M01" \| "0713R01" \| "0714E01" \| "0714S02" \| "0715P01" \| "0811E01" \| Eletrônica industrial \| Engenharia agrícola \| Mediação \| Processos metalúrgicos \| Refrigeração e climatização \| Sistemas de telecomunicações | "0321C01" \| Comunicação social |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2023 | 447 | "0199P01" \| "0211C01" \| "0222A01" \| "0399P01" \| "0532M01" \| "0716M01" \| "0732M01" \| "0811V01" \| "0914A01" \| "0914O01" \| "0918S02" \| Análises clínicas e toxicológicas \| Arqueologia \| Cinema e audiovisual \| Manutenção de aeronaves \| Material de construção \| Meteorologia \| Oftálmica \| Programas abrangendo ciências sociais, comunicação e informação em processo de definição da classif | "0114E02" \| "0912M01" \| Educação do campo em áreas de conhecimento da educação básica formação de professor \| Medicina |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Nome e Código do Curso de Graduação1-6 | 2024 | 458 | "0115L14" \| "0119P01" \| "0288P01" \| "0499P01" \| "0512B02" \| "0612S01" \| "0613C01" \| "0613I01" \| "0613I02" \| "0613S01" \| "0613S02" \| "0619P01" \| "0681A01" \| "0681C01" \| "0681C02" \| "0681J01" \| "0711E02" \| "0721L01" \| "0722E01" \| "0788P01" \| "0888P01" \| "0914P01" \| Biotecnologia \| Engenharia de bioprocessos \| Engenharia de computação \| Engenharia de materiais \| Laticínios \ | \| "0199P01" \| "0613J01" \| "0614C01" \| "0614I01" \| "0615S01" \| "0615S02" \| "0615S03" \| "0616E01" \| "0616I01" \| "0617A01" \| "0617C01" \| "0617C02" \| "0710E01" \| "0721P03" \| "0725P02" \| "0811A03" \| Agronegócio \| Engenharia \| Engenharia de computação (DCN Computação) \| Engenharia de computação (DCN Engenharia) \| Produção industrial \| Produção sucroalcooleira |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2017 | 15 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2018 | 15 | Fonte: Censo da Educação Superior - INEP. | Fonte: INEP - Censo da Educação Superior. |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2019 | 15 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2020 | 15 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2021 | 15 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2022 | 15 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2023 | 15 | 3 - Inclui também os cursos na modalidade a distância (EaD) ofertados por instituições brasileiras no exterior. \| Fonte: INEP - Censo da Educação Superior. \| Notas: 1 - Inclui somente os cursos de graduação a distância (EaD) com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. | 3 - Inclui também os cursos na modalidade a distância (Ead) ofertados por instituições brasileiras no exterior. \| Fonte: Censo da Educação Superior - INEP. \| Notas: 1 - Inclui somente os cursos de graduação a distância (Ead) com pelo menos um aluno matriculado na data de referência do Censo da Educação Superior. |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Região Geográfica | 2024 | 15 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2017 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2018 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2019 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2020 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2021 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2022 | 28 |  |  |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2023 | 28 | 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 21 \| 22 \| 23 \| 24 \| 25 \| 26 \| 27 \| 28 \| 29 \| 31 \| 32 \| 33 \| 35 \| 41 \| 42 \| 43 \| 50 \| 51 \| 52 \| 53 \| 61 | \| Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins |
| Anexo III — Tabela 8.3 | Anexo III — Tabela 8.3 | Unidade da Federação | 2024 | 27 |  | 61 |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2017 | 15 |  |  |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2018 | 15 | Total Brasil | Total Brasil |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2019 | 15 | Total Brasil | Total Brasil |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2020 | 15 | Centro-Oeste  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul | Centro-Oeste \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2021 | 15 | Centro-Oeste \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul | Centro-Oeste  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2022 | 15 | Centro-Oeste  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul | Centro-Oeste \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2023 | 15 | Centro-Oeste \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul | Centro-Oeste  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul |
| Sinopse por município | Tab 1.1 | Região Geográfica | 2024 | 15 |  |  |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2017 | 54 |  |  |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2018 | 54 |  |  |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2019 | 54 |  |  |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2020 | 55 | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total Ac | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2021 | 54 | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total  Acre \| Total  Alagoas \| Total | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total Ac |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2022 | 55 | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total  A | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total  Acre \| Total  Alagoas \| Total |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2023 | 54 | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total  A |
| Sinopse por município | Tab 1.1 | Unidade da Federação | 2024 | 53 |  | Total Acre |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2017 | 2 |  |  |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2018 | 2 |  |  |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2019 | 2 |  |  |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2020 | 3 | \| Graduação  \| Sequencial de Formação Específica | Graduação \| Sequencial de Formação Específica |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2021 | 2 | Graduação \| Sequencial de Formação Específica | \| Graduação  \| Sequencial de Formação Específica |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2022 | 3 | \| Graduação  \| Sequencial de Formação Específica | Graduação \| Sequencial de Formação Específica |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2023 | 2 | Graduação \| Sequencial de Formação Específica | \| Graduação  \| Sequencial de Formação Específica |
| Sinopse por município | Tab 4.2 | Nível Acadêmico do Curso | 2024 | 2 | Sequencial em Formação Específica | Sequencial de Formação Específica |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2017 | 17 |  |  |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2018 | 17 |  |  |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2019 | 17 |  |  |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2020 | 17 | Centro-Oeste  \| Exterior  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul | Centro-Oeste \| Exterior \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2021 | 17 | Centro-Oeste \| Exterior \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul | Centro-Oeste  \| Exterior  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2022 | 17 | Centro-Oeste  \| Exterior  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul | Centro-Oeste \| Exterior \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2023 | 17 | Centro-Oeste \| Exterior \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul | Centro-Oeste  \| Exterior  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul |
| Sinopse por município | Tab 4.2 | Região Geográfica | 2024 | 17 |  |  |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2017 | 54 |  |  |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2018 | 54 |  |  |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2019 | 54 |  |  |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2020 | 55 | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total Ac | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2021 | 54 | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total Ac |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2022 | 55 | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total  A | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2023 | 54 | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total  A |
| Sinopse por município | Tab 4.2 | Unidade da Federação | 2024 | 54 |  |  |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2017 | 2 |  |  |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2018 | 2 |  |  |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2019 | 2 |  |  |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2020 | 3 | \| Graduação  \| Sequencial de Formação Específica | Graduação \| Sequencial de Formação Específica |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2021 | 3 |  |  |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2022 | 3 |  |  |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2023 | 2 | Graduação \| Sequencial de Formação Específica | \| Graduação  \| Sequencial de Formação Específica |
| Sinopse por município | Tab 5.1 | Nível Acadêmico do Curso | 2024 | 2 | Sequencial em Formação Específica | Sequencial de Formação Específica |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2017 | 16 |  |  |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2018 | 16 |  |  |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2019 | 16 |  |  |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2020 | 16 | Centro-Oeste  \| Exterior  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul | Centro-Oeste \| Exterior \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2021 | 16 |  |  |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2022 | 16 |  |  |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2023 | 16 | Centro-Oeste \| Exterior \| Nordeste \| Norte \| Sudeste \| Sul \| Total Brasil \| Total Centro-Oeste \| Total Nordeste \| Total Norte \| Total Sudeste \| Total Sul | Centro-Oeste  \| Exterior  \| Nordeste  \| Norte  \| Sudeste  \| Sul  \| Total Brasil  \| Total Centro-Oeste  \| Total Nordeste  \| Total Norte  \| Total Sudeste  \| Total Sul |
| Sinopse por município | Tab 5.1 | Região Geográfica | 2024 | 16 |  |  |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2017 | 54 |  |  |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2018 | 54 |  |  |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2019 | 54 |  |  |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2020 | 55 | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total Ac | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2021 | 55 |  |  |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2022 | 55 | Total  Acre  \| Total  Alagoas  \| Total  Amapá  \| Total  Amazonas  \| Total  Bahia  \| Total  Ceará  \| Total  Distrito Federal  \| Total  Espírito Santo  \| Total  Goiás  \| Total  Maranhão  \| Total  Mato Grosso  \| Total  Mato Grosso do Sul  \| Total  Minas Gerais  \| Total  Paraná  \| Total  Paraíba  \| Total  Pará  \| Total  Pernambuco  \| Total  Piauí  \| Total  Rio Grande do Norte  \| Tot | Total Acre  \| Total Alagoas  \| Total Amapá  \| Total Amazonas  \| Total Bahia  \| Total Ceará  \| Total Distrito Federal  \| Total Espírito Santo  \| Total Goiás  \| Total Maranhão  \| Total Mato Grosso  \| Total Mato Grosso do Sul  \| Total Minas Gerais  \| Total Paraná  \| Total Paraíba  \| Total Pará  \| Total Pernambuco  \| Total Piauí  \| Total Rio Grande do Norte  \| Total Rio Grande do Su |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2023 | 54 | Acre \| Alagoas \| Amapá \| Amazonas \| Bahia \| Ceará \| Distrito Federal \| Espírito Santo \| Goiás \| Maranhão \| Mato Grosso \| Mato Grosso do Sul \| Minas Gerais \| Paraná \| Paraíba \| Pará \| Pernambuco \| Piauí \| Rio Grande do Norte \| Rio Grande do Sul \| Rio de Janeiro \| Rondônia \| Roraima \| Santa Catarina \| Sergipe \| São Paulo \| Tocantins \| Total Acre \| Total Alagoas \| Total A | \| Acre  \| Alagoas  \| Amapá  \| Amazonas  \| Bahia  \| Ceará  \| Distrito Federal  \| Espírito Santo  \| Goiás  \| Maranhão  \| Mato Grosso  \| Mato Grosso do Sul  \| Minas Gerais  \| Paraná  \| Paraíba  \| Pará  \| Pernambuco  \| Piauí  \| Rio Grande do Norte  \| Rio Grande do Sul  \| Rio de Janeiro  \| Rondônia  \| Roraima  \| Santa Catarina  \| Sergipe  \| São Paulo  \| Tocantins  \| Total  A |
| Sinopse por município | Tab 5.1 | Unidade da Federação | 2024 | 54 |  |  |

*(recorte de tabelas representativas; todas as tabelas estão em 05 › `categorias_linhas`)*
