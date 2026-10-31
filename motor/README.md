# Motor de consultas IJSN — manual e documentação técnica

Responde perguntas em português sobre as Sinopses da Educação Superior (INEP, 2017–2024), com números calculados pelo banco e por código, além das fontes e limitações.

## Como usar

```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
& $py -I perguntar.py "Quantas matrículas havia em Vila Velha em 2024?"
& $py -I perguntar.py          # modo interativo; linha vazia sai
```

Em Python: `from motor import perguntar; r = perguntar("...")`. O objeto `r` traz `r.texto` (markdown), `r.tabela` (DataFrame), `r.grafico` e `r.csv` (arquivos em `dados/consultas/saidas/`) e `r.precisa_esclarecer`.

### Perguntas que o motor entende (exemplos testados)
| Tipo | Exemplo |
|---|---|
| valor | Quantas matrículas havia em Vila Velha em 2024? |
| série | Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024? |
| comparação | Compare as matrículas presenciais e a distância no ES nos últimos 5 anos · Compare Vitória e Serra em concluintes |
| ranking | Quais os 10 municípios capixabas com mais matrículas em 2024? |
| crescimento | Quais cursos mais cresceram em ingressantes no ES entre 2019 e 2024? (acrescente "percentual" para ordenar por %) |
| participação | Qual a participação do EaD nas matrículas do Espírito Santo? · Qual a participação de Vila Velha nas matrículas do ES? |
| dimensões | por sexo, cor/raça, faixa etária (Sinopse); rede, dependência, organização acadêmica, grau, modalidade (Anexos); curso pelo nome (ex.: "Direito") |
| metodologia | Quais mudanças metodológicas prejudicam a comparação entre anos? |

Indicadores: matrículas, ingressantes, concluintes, cursos, vagas, inscritos, IES e docentes; derivados: **candidatos por vaga** e **ingressantes por vaga** (Σ numerador ÷ Σ denominador). Sexo, cor/raça e faixa etária podem ser combinados com rede, dependência, categoria privada e organização acadêmica (ex.: "matrículas de mulheres na rede pública do ES"). Em participação com mais de um filtro, o primeiro citado depois de "participação" é a parte e os demais definem o universo. Locais: município, UF (nome ou sigla em maiúsculas), região, Brasil e "Grande Vitória" (soma de 7 municípios).

Quando a pergunta é ambígua ou pede algo que a fonte não tem, o motor **pede esclarecimento** e não consulta nada. Exemplos: sem indicador; ano fora de 2017–2024; município homônimo fora do ES; vagas EaD por município (o INEP só publica no total Brasil); cruzamentos que a Sinopse não publica, como sexo × rede por município.

## Arquitetura

```
pergunta ─► interpretador ─► Consulta ─► consultas.planejar ─► SQL parametrizado
                │ (catálogo)                                        │
                └─ esclarecer? ◄────────────────────────────────────┤
                                                    seguranca.executar (somente leitura)
                                                                    │
            resposta.montar ◄── analise.analisar ◄── consultas.rotular (rótulos; soma de grupos)
```

| Módulo | Papel |
|---|---|
| `semantica/catalogo.yaml` | Indicadores (definição, sinônimos, aditividade, limitações), dimensões e sinônimos, aliases geográficos e regras de compatibilidade entre anos |
| `semantica/__init__.py` | Carrega o catálogo, mais os nomes de locais (`dim_geografia`) e de cursos (`xw_cine`) do banco |
| `interpretador.py` | Texto → `Consulta` (indicador, anos, locais, filtros, quebras, tipo, critério). Determinístico; registra suposições |
| `consultas.py` | Escolhe o mart e monta o SQL (valores só como `?`); rótulos; soma de grupos; ocorrências pertinentes |
| `seguranca.py` | Validação do SQL, conexão somente leitura, tempo e linhas máximos, registro jsonl |
| `analise.py` | Todos os cálculos |
| `resposta.py` | Texto em português, tabela, gráfico PNG (matplotlib), CSV, fontes e limitações |
| `api.py` | `perguntar()` (regras), `perguntar_estruturado(json)` (interpretador externo / LLM), `responder(consulta)` e a linha de comando |
| `contrato.py` | JSON da Consulta: `esquema(cat)`, `para_json`, `de_json` (validação estrita contra catálogo e banco). Ver `_arquitetura/03_proposta_llm.md` |

### Fontes de dados (marts, gerados por `pipeline/p6_marts.py`)
- `mart_anexos_geo`: Anexos II/III, recortes-folha (org. acadêmica × grau × dependência × categoria privada). Município = Σ cursos; UF/Região = Σ municípios; Brasil = linha publicada. Qualquer marginal = soma das folhas.
- `mart_curso_geo`: por curso Cine (Município, UF, Brasil); cursos agrupados pelo código de 2024 (`xw_cine.co_cine_ref`).
- `mart_sinopse_geo`: IES e docentes (valor publicado, tabelas 1.1/2.1/2.5); sexo, cor/raça e faixa etária (soma das folhas, tabelas 4.6–4.8, 5.5–5.7, 6.5–6.7, nível Graduação).

## Regras estatísticas
- Variação absoluta = último − primeiro. Variação % = (último − primeiro) / primeiro, indefinida com base 0.
- Taxa média anual = (último/primeiro)^(1/anos) − 1, só com valores positivos.
- Participação = parte / todo do mesmo ano, local e fonte. Município → UF; UF/Região → Brasil (linha publicada, que inclui EaD não localizado e Exterior).
- Ranking de crescimento: por variação absoluta (padrão) ou por % com base mínima de 100 no ano inicial. Itens sem valor no ano inicial ficam fora, e a resposta informa quantos.
- Ano de ultrapassagem: primeiro ano em que a ordem entre duas séries se inverte.
- **Ausência ≠ zero.** **Docentes não são aditivos:** grupos de municípios não são somados.
- Categorias agregadas publicadas ("Pública" em 1.1/2.1) nunca entram em somas com as suas partes.

## Segurança
Ver `_arquitetura/02_decisoes.md` (D06). As tabelas autorizadas estão em `config.py` (`TABELAS_AUTORIZADAS`). Para auditoria, toda consulta fica em `dados/consultas/registro_consultas.jsonl`, com pergunta, SQL, parâmetros, linhas, tempo e erro.

## Testes
`python -I -m pytest -p no:cacheprovider tests` (216 testes, cerca de 45 s):
- `test_seguranca.py`: 4 SQLs aceitos e 17 recusados, escrita bloqueada pela conexão, injeção via parâmetro;
- `test_interpretador.py`: 17 formas de pergunta;
- `test_analise.py`: fórmulas e formatação;
- `test_referencias.py`: respostas comparadas com consultas **independentes** nas tabelas de fato;
- `test_regressao.py`: um teste por erro encontrado pela bateria (R01–R10);
- `test_contrato.py`: contrato JSON, entradas inválidas e **gabarito** de 61 interpretações revisadas (`gold_interpretacoes.jsonl`; regenerar com `tests/gerar_gold.py` só depois de revisar a bateria);
- `test_backup.py`: usado por `pipeline/backup_leve.py` (o motor responde igual sobre o banco reconstruído).

`tests/bateria_perguntas.py [rótulo]` roda 61 perguntas (7 grupos) e grava `dados/qualidade/bateria_<rótulo>.md/csv` com interpretação, desfecho e tempo de cada uma.

`tests/fumaca_motor.py` roda perguntas de exemplo e imprime as respostas (inspeção manual).

## Limitações conhecidas do motor
- O interpretador é por regras. Perguntas fora dos padrões acima recebem um pedido de esclarecimento ou podem ser mal entendidas: confira sempre a seção "Como a pergunta foi entendida".
- Não há cruzamento de duas dimensões da Sinopse (por exemplo, sexo × cor) nem de sexo/cor/faixa com modalidade, grau ou curso.
- Deficiência, reserva de vagas, financiamento, turno, nacionalidade e titulação de docentes estão no núcleo, mas não no motor: a pergunta recebe essa explicação.
- Por curso, não há região nem as dimensões org./grau/dependência.
- Nomes de município muito curtos (menos de 4 letras) não são reconhecidos.
- Sem interface gráfica (D09).
