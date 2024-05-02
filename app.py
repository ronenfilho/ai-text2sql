import streamlit as st
import os
from groq import Groq
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import duckdb
import sqlparse
from dotenv import load_dotenv


def chat_with_groq(client,prompt,model):
    """
    Esta função envia um prompt para a API Groq e recupera a resposta do IA.

    Parâmetros:
    client (Groq): O cliente da API Groq.
    prompt (str): O prompt a ser enviado para o IA.
    model (str): O modelo de IA a ser usado para a resposta.

    Retorna:
    str: O conteúdo da resposta do IA.
    """

    completion = client.chat.completions.create(
    model=model,
    messages=[
      {
            "role": "user",
            "content": prompt
        }
        ]
    )
  
    return completion.choices[0].message.content

def execute_duckdb_query(query):
    """
    Esta função executa uma consulta SQL em um banco de dados DuckDB e retorna o resultado.

    Parâmetros:
    query (str): A consulta SQL a ser executada.

    Retorna:
    DataFrame: O resultado da consulta como um DataFrame do pandas.
    """
    # Salva o diretório de trabalho atual
    original_cwd = os.getcwd()
    # Altera o diretório de trabalho para 'data'
    os.chdir('data')
    
    try:
        # Conecta ao banco de dados DuckDB
        conn = duckdb.connect(database=':memory:', read_only=False)
        # Executa a consulta SQL e recupera o resultado como DataFrame
        query_result = conn.execute(query).fetchdf().reset_index(drop=True)
    finally:
        # Restaura o diretório de trabalho original
        os.chdir(original_cwd)

    return query_result

def get_json_output(llm_response):
    """
    Esta função limpa a resposta do IA, extrai o conteúdo JSON e verifica se contém uma consulta SQL ou uma mensagem de erro.

    Parâmetros:
    llm_response (str): A resposta do IA.

    Retorna:
    tuple: Uma tupla onde o primeiro elemento é um booleano indicando se a resposta contém uma consulta SQL (True) ou uma mensagem de erro (False), 
           e o segundo elemento é a consulta SQL ou a mensagem de erro.
    """

    # Remove caracteres inválidos e espaços em branco
    llm_response_no_escape = llm_response.replace('\\n', ' ').replace('\n', ' ').replace('\\', '').replace('\\', '').strip() 
    
    # Apenas no caso - obtém apenas o conteúdo entre colchetes
    open_idx = llm_response_no_escape.find('{')
    close_idx = llm_response_no_escape.rindex('}') + 1
    cleaned_result = llm_response_no_escape[open_idx : close_idx]

    # Carrega o resultado como JSON
    json_result = json.loads(cleaned_result)
    # Verifica se o JSON contém uma consulta SQL
    if 'sql' in json_result:
        query = json_result['sql']
        # Retorna a consulta SQL formatada
        return True, sqlparse.format(query, reindent=True, keyword_case='upper')
    # Verifica se o JSON contém uma mensagem de erro
    elif 'error' in json_result:
        # Retorna a mensagem de erro
        return False, json_result['error']

def get_reflection(client,full_prompt,llm_response,model):
    """
    Esta função gera um prompt de reflexão quando há um erro na resposta da IA.
    Em seguida, envia este prompt de reflexão para a API Groq e recupera a resposta da IA.

    Parâmetros:
    client (Groq): O cliente da API Groq.
    full_prompt (str): O prompt original que foi enviado a IA.
    llm_response (str): A resposta da IA ao prompt original.
    model (str): O modelo de IA a ser usado para a resposta.

    Retorna:
    str: O conteúdo da resposta do IA ao prompt de reflexão.
    """

    reflection_prompt = '''
    Você recebeu o seguinte prompt:

    {full_prompt}

    Esta foi a sua resposta:

    {llm_response}

    Houve um erro com a resposta, seja no formato de saída ou na consulta em si.

    Garanta que as seguintes regras sejam cumpridas ao corrigir sua resposta:
    1. SQL é válido DuckDB SQL, dadas as metainformações fornecidas e as regras de consulta do DuckDB
    2. A consulta REFERENCIA ESPECIFICAMENTE as tabelas corretas: employees.csv e purchases.csv, e essas tabelas estão devidamente alinhadas? (esta é a causa mais provável de falha)
    3. A resposta está no formato correto ({{sql: <sql_aqui>}} ou {{"error": <explicação aqui>}}) sem texto adicional?
    4. Todos os campos estão devidamente nomeados
    5. Não há subconsultas desnecessárias
    6. TODAS AS TABELAS estão alinhadas (extremamente importante)

    Reescreva a resposta e responda APENAS com o formato de saída válido, sem comentários adicionais

    '''.format(full_prompt = full_prompt, llm_response=llm_response)

    return chat_with_groq(client,reflection_prompt,model)

def get_summarization(client,user_question,df,model,additional_context):
    """
    Esta função gera um prompt de sumarização com base na pergunta do usuário e nos dados resultantes. 
    Em seguida, envia este prompt de sumarização para a API Groq e recupera a resposta da IA.

    Parâmetros:
    client (Groqcloud): O cliente da API Groq.
    user_question (str): A pergunta do usuário.
    df (DataFrame): O DataFrame resultante da consulta SQL.
    model (str): O modelo de IA a ser usado para a resposta.
    additional_context (str): Qualquer contexto adicional fornecido pelo usuário.

    Retorna:
    str: O conteúdo da resposta do IA ao prompt de sumarização.
    """

    prompt = '''
    Um usuário fez a seguinte pergunta relacionada às tabelas do banco de dados local:
    
    {user_question}
    
    Para responder à pergunta, um dataframe foi retornado:

    Dataframe:
    {df}

    Em algumas frases, resuma os dados na tabela conforme eles se relacionam com a pergunta original do usuário. Evite qualificadores como "baseado nos dados" e não comente sobre a estrutura ou metadados da própria tabela
    '''.format(user_question = user_question, df = df)

    if additional_context != '':
        prompt += '''\n
        O usuário forneceu este contexto adicional:
        {additional_context}
        '''.format(additional_context=additional_context)

    return chat_with_groq(client,prompt,model)

def main():
    """
    Função principal do aplicativo. Lida com a entrada do usuário, controla o fluxo do aplicativo e 
    exibe os resultados na interface do Streamlit.
    """

    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Obtém o valor da variável de ambiente GROQ_API_KEY
    groq_api_key = os.getenv("GROQ_API_KEY")         
    client = Groq(
        api_key=groq_api_key
    )

    # Configura a interface do Streamlit
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')

    st.title("Gerador de Query")
    st.write('Bem-vindo! Sinta-se à vontade para fazer perguntas sobre os dados contidos nos arquivos `employees.csv` e `purchases.csv`. Você pode perguntar sobre detalhes específicos de funcionários ou sobre registros de compra. Por exemplo, você poderia perguntar "Quem são os funcionários?" ou "Quais são as compras mais recentes?". O aplicativo associa sua pergunta a consultas SQL para fornecer resultados precisos e relevantes. Aproveite para explorar os dados!')

    # Configurações de personalização
    st.sidebar.title('Personalização')
    additional_context = st.sidebar.text_input('Insira aqui o contexto adicional de sumarização para o LLM (por exemplo, escreva em português):')
    model = st.sidebar.selectbox(
        'Escolha um modelo',
        ['llama3-8b-8192', 'llama3-70b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it']
    )
    max_num_reflections = st.sidebar.slider('Máx. reflexões:', 0, 10, value=5)

    # Carrega o prompt base
    with open('prompts/base_prompt.txt', 'r') as file:
        base_prompt = file.read()

    # Obtém a pergunta do usuário
    user_question = st.text_input("Faça uma pergunta:")

    # Se o usuário fez uma pergunta, processa-a
    if user_question:
        # Gera o prompt completo para a IA
        full_prompt = base_prompt.format(user_question=user_question)
        
        # Obtém a resposta da IA
        llm_response = chat_with_groq(client,full_prompt,model)

        # Tenta processar a resposta da IA
        valid_response = False
        i=0
        while valid_response is False and i < max_num_reflections:
            try:
                # Verifica se a resposta da IA contém uma consulta SQL ou uma mensagem de erro
                is_sql,result = get_json_output(llm_response)
                if is_sql:
                    # Se a resposta contiver uma consulta SQL, executa-a
                    results_df = execute_duckdb_query(result)
                    valid_response = True
                else:
                    # Se a resposta contiver uma mensagem de erro, é considerada válida
                    valid_response = True
            except:
                # Se houve um erro ao processar a resposta da IA, obtém uma reflexão
                llm_response = get_reflection(client,full_prompt,llm_response,model)
                i+=1

        # Exibe o resultado
        try:
            if is_sql:
                # Se o resultado for uma consulta SQL, exibe a consulta e os dados resultantes
                st.markdown("```sql\n" + result + "\n```")
                st.markdown(results_df.to_html(index=False), unsafe_allow_html=True)

                # Obtém uma sumarização dos dados e a exibe
                summarization = get_summarization(client,user_question,results_df,model,additional_context)
                st.write(summarization.replace('$','\\$'))
            else:
                # Se o resultado for uma mensagem de erro, exibe-a
                st.write(result)
        except:
            # Se houve um erro ao exibir o resultado, exibe uma mensagem de erro
            st.write("ERRO:", 'Não foi possível gerar uma consulta SQL válida para esta pergunta')
            st.write(llm_response)
            
if __name__ == "__main__":
    main()

