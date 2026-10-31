# Manual de uso — Consulta às Sinopses da Educação Superior

Para quem vai **fazer perguntas** aos dados. Não é preciso saber programar.

*Ferramenta criada e desenvolvida por **Igor L. Millis**: projeto independente, desenvolvido em ambiente pessoal e no tempo livre, com dados públicos do INEP. Não é produto oficial do INEP, do MEC nem de qualquer outra instituição.*

## 1. Abrir
1. Na pasta do projeto (`IJSN`, nome técnico da pasta), dê **dois cliques em `iniciar_interface.bat`**.
2. Abre-se uma janela preta (deixe-a aberta) e, em seguida, o navegador em `http://127.0.0.1:8765`.
3. Para encerrar, feche a janela preta.

A página funciona **só neste computador**: nada é enviado para a internet.

## 2. Perguntar
Escreva a pergunta e clique em **Perguntar** (ou tecle Enter). Exemplos:

| Você quer… | Pergunte assim |
|---|---|
| Um número | Quantas matrículas havia em Vila Velha em 2024? |
| A evolução | Como evoluíram as matrículas no Espírito Santo entre 2017 e 2024? |
| Comparar | Compare Vitória, Vila Velha, Serra e Cariacica em matrículas |
| Um ranking | Quais os 10 municípios capixabas com mais matrículas em 2024? |
| Quem cresceu ou caiu | Quais cursos mais cresceram em ingressantes no ES entre 2019 e 2024? · Quais municípios do ES apresentaram redução de matrículas entre 2017 e 2024? |
| Uma participação | Qual a participação do EaD nas matrículas do Espírito Santo? · Qual a participação das mulheres nas matrículas da rede privada do ES? |
| Por categoria | Matrículas por sexo / cor/raça / faixa etária / rede / organização acadêmica / grau no ES em 2024 |
| Um curso | Matrículas em Direito em Vitória de 2017 a 2024 |
| Razões | Relação candidatos por vaga no ES em 2024 |

**Indicadores disponíveis:** matrículas, ingressantes, concluintes, cursos, vagas, inscritos, instituições (IES), docentes, candidatos por vaga e ingressantes por vaga.
**Locais:** qualquer município, estado (nome ou sigla), região, Brasil e "Grande Vitória".
**Anos:** 2017 a 2024. Sem ano, a resposta usa 2024 (ou a série inteira, se a pergunta for sobre evolução) e avisa.

### Modo de interpretação
- **Regras (mais previsível):** entende as formas de pergunta dos exemplos acima e responde em menos de 1 segundo.
- **Regras + IA local:** quando as regras não entendem a pergunta, uma IA instalada neste computador tenta interpretá-la (20 a 90 segundos; a primeira pergunta do dia é a mais lenta). A resposta mostra um **aviso amarelo**: confira "Como a pergunta foi entendida" antes de usar os números.

A IA **só interpreta** a pergunta. Os números vêm sempre do banco de dados, calculados por programa.

## 3. Ler a resposta
Cada resposta traz, nesta ordem:
1. **A resposta direta** (o número ou o destaque principal), seguida da tabela.
2. **Interpretação:** tendência, maior alta e maior queda anual, anos sem dado.
3. **Como a pergunta foi entendida:** toda suposição feita (ano, local, indicador). **Leia sempre.**
4. **Fontes:** tabela de origem do INEP e exemplo da célula da planilha original (rastreabilidade).
5. **Limitações:** o que o dado não mostra e, se for o caso, valores marcados como **suspeitos** na publicação do INEP (ocorrências Q01–Q13).
6. **Gráfico** e o link **Baixar a tabela (CSV)**, que abre no Excel.

## 4. Quando a resposta pede esclarecimento
Nada foi consultado. Reformule a pergunta seguindo a mensagem. Exemplos:
- "Qual indicador?" — diga se quer matrículas, concluintes etc.
- "Há mais de um município chamado…" — inclua a UF (ex.: "Bom Jesus (PI)").
- "Os dados cobrem 2017–2024" — o ano pedido não existe na base.
- "Não há dados de vagas a distância por município" — o INEP só publica esse dado no total Brasil.
- "Ainda não disponível no motor" (deficiência, cotas, FIES, turno…) — o dado existe na base, mas ainda não pode ser consultado pela página.

## 5. Cuidados com os números
- **Ausência não é zero:** se um ano ou local não tem dado publicado, a resposta diz isso.
- **EaD:** a matrícula a distância é contada no município do **polo**. Cursos, vagas e inscritos EaD só existem no total Brasil.
- **Docentes não se somam** entre municípios (um docente pode atuar em mais de um).
- **Cursos:** a classificação Cine mudou em 2024. Os cursos foram ligados entre os anos, mas alguns só existem em parte do período.
- **Valores suspeitos:** células inconsistentes na publicação do INEP são mantidas como publicadas e sinalizadas.

## 6. Problemas
| Situação | O que fazer |
|---|---|
| A página não abre | Verifique se a janela preta está aberta; acesse `http://127.0.0.1:8765` manualmente |
| "IA local indisponível" | O Ollama não está rodando. Use o modo Regras, ou abra o Ollama pelo menu Iniciar |
| Resposta parece errada | Leia "Como a pergunta foi entendida". Se a interpretação estiver errada, reformule e avise a equipe técnica (a pergunta fica registrada em `dados/consultas/registro_consultas.jsonl`) |
