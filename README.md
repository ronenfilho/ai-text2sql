# Gerador de Consultas DuckDB

Este repositório constrói uma aplicação Streamlit que permite aos usuários fazerem perguntas sobre seus dados do DuckDB. A aplicação utiliza a API Groq para gerar consultas SQL com base nas perguntas do usuário e executá-las em um banco de dados DuckDB.

## Recursos

- **Texto para SQL**: A aplicação utiliza processamento de linguagem natural para converter perguntas do usuário em consultas SQL, facilitando aos usuários consultar seus dados sem conhecer SQL.

- **Tratamento de Erros**: Se a IA gerar uma consulta SQL inválida, a aplicação solicita à IA que corrija sua resposta, garantindo que a saída seja uma consulta SQL válida do DuckDB.

- **Sumarização de Dados**: Após a execução de uma consulta SQL, a aplicação utiliza a IA para resumir os dados resultantes em relação à pergunta original do usuário.

- **Customização**: Os usuários podem personalizar o modelo de IA usado, o número máximo de reflexões (tentativas de corrigir uma resposta inválida) e o comprimento da memória conversacional.

## Dados

A aplicação consulta dados de dois arquivos CSV localizados na pasta `data`:

- `employees.csv`: Contém dados dos funcionários, incluindo seu ID, nome completo e endereço de e-mail.

- `purchases.csv`: Registra detalhes de compra, incluindo ID da compra, data, ID do funcionário associado, valor e nome do produto.

## Prompts

O prompt base para a IA é armazenado em um arquivo de texto na pasta `prompts`:

- `base_prompt.txt`

## Funções

- `chat_with_groq()`: Envia um prompt para a API Groq e retorna a resposta da IA.
- `execute_duckdb_query()`: Executa uma consulta SQL em um banco de dados DuckDB e retorna o resultado.
- `get_json_output()`: Extrai e formata a consulta SQL ou mensagem de erro da resposta da IA.
- `get_reflection()`: Solicita à IA que corrija uma resposta inválida.
- `get_summarization()`: Gera um prompt para a IA resumir os dados resultantes de uma consulta SQL.
- `main()`: A função principal da aplicação, que lida com a entrada do usuário e controla o fluxo da aplicação.

## Uso

Para usar esta aplicação, você precisa ter o Streamlit e as outras bibliotecas Python necessárias instaladas. Você também precisa ter uma chave da API Groq, que pode ser obtida ao se inscrever no site da Groq.

Depois de ter os requisitos necessários, você pode executar a aplicação executando o script com o Streamlit:

```shell
streamlit run app.py
```

Isso iniciará o servidor Streamlit e abrirá a aplicação em seu navegador da web. Você pode então fazer perguntas sobre seus dados do DuckDB, e a aplicação irá gerar e executar consultas SQL com base em suas perguntas.

## Personalizando com Seus Próprios Dados

Esta aplicação é projetada para ser flexível e pode ser facilmente personalizada para funcionar com seus próprios dados. Se você quiser usar seus próprios dados, siga estas etapas:

1. **Substitua os arquivos CSV**: A aplicação consulta dados de dois arquivos CSV localizados na pasta `data`: `employees.csv` e `purchases.csv`. Substitua esses arquivos pelos seus próprios arquivos CSV.

2. **Modifique o prompt base**: O prompt base para a IA, armazenado na pasta `prompts` como `base_prompt.txt`, contém informações específicas sobre os metadados dos dados. Modifique este prompt para combinar com a estrutura e conteúdo de seus próprios dados. Certifique-se de descrever com precisão as tabelas, colunas e quaisquer regras ou dicas específicas para consultar seu conjunto de dados.

Seguindo estas etapas, você pode adaptar o Gerador de Consultas DuckDB aos seus próprios dados e casos de uso. Sinta-se à vontade para experimentar e construir a partir deste repositório para criar suas próprias aplicações poderosas de consulta de dados.