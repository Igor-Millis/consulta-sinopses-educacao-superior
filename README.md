# Consulta às Sinopses da Educação Superior (INEP), 2017–2024

**Igor L. Millis - Projeto Independente com Dados Públicos**

Explore matrículas, ingressantes, concluintes, cursos, vagas e instituições de ensino superior por município, estado e região. Consulte indicadores, compare períodos e identifique tendências com base nos dados oficiais do INEP.

Fonte dos dados: INEP/MEC — Sinopses Estatísticas da Educação Superior (Graduação), 2017–2024. Processamento e consultas realizados localmente. Inconsistências identificadas na publicação original são preservadas e sinalizadas nas respostas.

> Nota técnica: a pasta do projeto, o arquivo do banco (`ijsn.duckdb`) e a pasta temporária `ijsn_pipeline` conservam o nome técnico usado desde o início do desenvolvimento. É só um identificador de arquivo (renomear exigiria mover arquivos e refazer caminhos) e não indica autoria nem vínculo institucional. Os commits antigos do git trazem o nome de autor "IJSN projeto", que foi preservado (o histórico não é reescrito); os commits a partir de 31/10/2026 são de Igor L. Millis.

Base de dados local (DuckDB) construída a partir dos 8 ZIPs originais das Sinopses do INEP, com rastreabilidade até a célula de origem, e um motor que responde perguntas em português com fontes e limitações. O foco analítico é o Espírito Santo, mas a base é nacional.

## Para usar (sem programar)
Dois cliques em **`iniciar_interface.bat`**: o navegador abre a página local de perguntas. Guia completo em **`MANUAL_USUARIO.md`**.

## Começar (equipe técnica)
```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
& $py -I perguntar.py "Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024?"
& $py -I -m pytest -p no:cacheprovider tests      # 260 testes
```

## Onde está cada coisa
| Pasta / arquivo | Conteúdo |
|---|---|
| `*.zip` | Originais do INEP. **Nunca alterados** |
| `_diagnostico_estrutura/` | Diagnóstico da estrutura das planilhas (relatórios 01–07) |
| `_arquitetura/` | Arquitetura de dados (`01`), registro de decisões (`02`) e proposta de LLM (`03`) |
| `pipeline/` | Construção da base, P0–P6, com testes de validação. Ordem de reconstrução no `pipeline/README.md` |
| `config/` | Mapeamentos, correções manuais e ocorrências de qualidade (`qualidade_ocorrencias.csv`) |
| `motor/` | Motor de consultas: manual em `motor/README.md` |
| `app/` | Interface web local (só biblioteca padrão; `iniciar_interface.bat`) |
| `tests/` | Testes pytest (motor, interface, LLM, qualidade, contrato) e avaliações |
| `dados/` | Staging, banco (`nucleo/ijsn.duckdb`), backups leves (`backup/`), saídas analíticas, qualidade e consultas (fora do git) |
| `ACOMPANHAMENTO.md` | Situação, testes, problemas, auditoria e próximo passo |

## Princípios
Originais intocados · nada é corrigido em silêncio (valores suspeitos são marcados e explicados) · ausência ≠ zero · comparações entre anos só com compatibilidade verificada · processamento 100% local, com ferramentas gratuitas · toda funcionalidade com teste executado e registrado.
