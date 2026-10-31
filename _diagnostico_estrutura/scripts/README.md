# Scripts do diagnóstico estrutural

Requisitos: Python 3.12 com `openpyxl`, `pandas` e `lxml`.
Os scripts só leem os ZIPs originais. As cópias dos XLSX e os arquivos intermediários vão para uma pasta de trabalho (`<work>`), que deve ficar **fora** da pasta do projeto, porque ocupa cerca de 4 GB.

## Pipeline principal (nesta ordem)

| # | Script | Uso | Saída |
|---|---|---|---|
| 1 | `s1_extract_inventory.py` | `python -I s1_extract_inventory.py <pasta_zips> <work>` | Cópias dos XLSX em `<work>/xlsx/<ano>/` e `<work>/inventario_bruto.json` |
| 2 | `s2_profile.py` | `python -I s2_profile.py <work> [n_processos] [filtro]` | Um JSON por aba em `<work>/profiles/` (cerca de 35 min com 7 processos) |
| 3 | `check_profiles.py` | `python -I check_profiles.py <work>` | Verificação de integridade dos perfis |
| 4 | `s3_build.py` | `python -I s3_build.py <work> <saida>` | Entregáveis 01 a 04 e os arquivos `.pkl` intermediários em `<work>` |
| 5 | `s4_compare.py` | `python -I s4_compare.py <work> <saida>` | Entregável 05 |
| 6 | `s5_dict.py` | `python -I s5_dict.py <work> <saida>` | Entregável 06 |
| 7 | `s6_validate.py` | `python -I s6_validate.py <work> <saida>` | Validação dos entregáveis contra os perfis (`<work>/validacao.json`) |

O relatório `07_relatorio_estrutura.md` foi escrito à mão a partir das saídas da validação e dos scripts auxiliares abaixo. Ele não é gerado por script.

## Auxiliares de inspeção (somente leitura)

- `peek.py`: primeiras N linhas de uma aba.
- `show_profile.py`: resumo legível de um perfil JSON.
- `dbg_hdr.py`: uma linha de cabeçalho crua e as mesclagens que começam nela.
- `inspect_S.py`, `inspect_pkl.py`: consulta aos catálogos intermediários.
- `s1b_show_sheets.py`: abas e dimensões por ano.
- `status.py`: perfis concluídos e pendentes.
- `s6b_investigate.py`, `s6c_facts.py`, `s6d_facts.py`, `s6e_verify_claims.py`, `s6f_ead.py`: investigações pontuais usadas no relatório 07.
- `s7_ifmt.py`: verificação da correção do IFMT em 2023 (vagas e inscritos do IF em MT, 2022–2024). Resultado no relatório 07, §8.1.
- `s8_if_insc_vagas.py`, `s8b_analise.py`, `s8c_padroes.py`: investigação de inscritos = vagas no IF de MT (Anexo II, 2017–2024). Resultado no relatório 07, §8.2.
- `s9_if_ead.py`, `s9b_analise_ead.py`: padrão EaD do IF em MT (Sinopse 7.3 e Anexo III, 2017–2024). Resultado no relatório 07, §8.3.
