# https://python.langchain.com/docs/use_cases/question_answering/conversational_retrieval_agents

import json
import os
import pickle
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory, CombinedMemory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain.agents import AgentType, Tool, initialize_agent, create_openai_tools_agent, create_openai_functions_agent, AgentExecutor
from langchain_community.chat_models import ChatLiteLLM
from avalia_intencao import obtem_acao, obtem_acao, obtem_intencao, converte_para_singular
from app_memory import carregar_chat_history

from app_product_tools import get_app_tools

system_prompt = """
You work as a customer service representative at the company Tem de Tudo - T&T.
The company Tem de Tudo sells a variety of household and office items.

Remember: 
- Never ever use made-up or fictitious emails or any other personal data.
- Your final response should always be in PORTUGUESE.

If you're unsure about the details of the request, do not provide an answer and ask follow-up questions to gain a clear understanding.
You are very helpful and do your best to answer questions, but you NEVER make assumptions about data requests. For example, if email are not specified, you ask follow-up questions.

If you don't have enough context to answer the question, ask the user follow-up questions to obtain the necessary information. 
You do not make assumptions about data requests. For example, if email are not specified, you ask follow-up questions.
Always use the tool if you have follow-up questions about the request.
You can use Summary conversation history to help you understand the context of the conversation.

You are expected to kindly assist customers by:

1- Answering questions about the store, purchase policy, and return policy regarding the products:
   If you are unable to answer a question, inquire if they would like you to open a support ticket so that their question can be addressed by the customer support team.

2- Assisting with their complaints:
   If the customer wants to make a complaint, apologize, and record the complaint.

3- Helping them find everything they wish to buy for until they complete their purchase:
   If you cannot find the product the customer wants, do not suggest they look elsewhere.
   Ask them if they would like you to register a reminder to inform them when the product is back in stock.
   Pay attention: Do not register a reminder before asking the customer if they would like you to do so.

Here you are the data you need to use:

Este é o e-mail do cliente: {email_usuario}

Summary conversation history:
{chat_history2}

User: {input}
"""


system_prompt = """
Você trabalha como representante de atendimento ao cliente na empresa Tem de Tudo, que vende uma variedade de itens para casa e escritório.

Lembre-se:
- Nunca use e-mails ou quaisquer outros dados pessoais fictícios.
- Se não tiver certeza sobre os detalhes do pedido, faça perguntas de acompanhamento para obter um entendimento claro.
- Seja sempre útil e faça o seu melhor para responder às perguntas, mas NUNCA faça suposições sobre os pedidos de dados.

Você deve ajudar os clientes:
1- Respondendo perguntas sobre a loja, política de compra e devolução dos produtos. Se não puder responder a uma pergunta, ofereça abrir um ticket de suporte.
2- Assistindo com reclamações, registrando-as após pedir desculpas.
3- Ajudando-os a encontrar tudo o que desejam comprar até completarem sua compra. Se não encontrar o produto desejado pelo cliente, pergunte se gostariam de registra um lembrete quando o produto voltar ao estoque.

Utilize os seguintes dados em seu atendimento:
Este é o e-mail do cliente: {email_usuario}
Histórico resumido da conversa: {chat_history2}
Usuário: {input}
"""


#Previous conversation history:
#{chat_history1}


def app_agent_main():
    verbose = True

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )

    tools = get_app_tools()
    llm1 = ChatOpenAI(temperature=0.1, model=os.getenv("MODEL_NAME"))
    llm2 = ChatOpenAI(temperature=0.1, model=os.getenv("MODEL_NAME"))

    chat_memory = carregar_chat_history()
    memory_conversation = ConversationBufferWindowMemory(llm=llm2, 
                                             max_token_limit=500,
                                             input_key="input",
                                             memory_key="chat_history1",
                                             chat_memory=chat_memory)
    
    memory_summary = ConversationSummaryBufferMemory(llm=llm2, 
                                             max_token_limit=1000,
                                             input_key="input",
                                             memory_key="chat_history2",
                                             chat_memory=chat_memory)
    
    #memory = CombinedMemory(memories=[memory_conversation, memory_summary])
    memory = memory_summary

    human_input_agent = create_openai_tools_agent(llm1,
                                                tools = tools, 
                                                prompt = prompt
                                            )

    human_input_agent_executor = AgentExecutor(agent=human_input_agent, 
                                                tools=tools, 
                                                memory = memory,
                                                max_iterations=3,
                                                max_execution_time=30.0,
                                                early_stopping_method='generate',
                                                verbose=verbose, 
                                                handle_parsing_errors=True, 
                                                #return_intermediate_steps=True,
                                            )


    while True:
        print("\n\n")
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        usr = f"{user_input}"

        #intencao = obtem_intencao(usr, verbose=verbose)
        #print(f"\nIntenção: {intencao}")
        #acao = obtem_acao(intencao)
        #print(f"Ação: {acao}\n")

        #if intencao == '2':
        #    usr = converte_para_singular(usr)
        
        output = human_input_agent_executor.invoke({f"input": usr, "email_usuario": os.getenv("EMAIL_USUARIO")})
        print("\n")
        #print(output)
        #print("\n")
        print(output["output"])

