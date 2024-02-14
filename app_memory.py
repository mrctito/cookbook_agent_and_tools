import json
import os
import pickle
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain.agents import AgentType, Tool, initialize_agent, create_openai_tools_agent, create_openai_functions_agent, AgentExecutor
from langchain_community.chat_models import ChatLiteLLM
from langchain.memory import (ConversationBufferWindowMemory, MomentoChatMessageHistory, SQLChatMessageHistory)
from langchain.schema.chat_history import BaseChatMessageHistory


def carregar_chat_history() -> BaseChatMessageHistory:
    connection = os.getenv("DB_CACHE_URL")
    table_name = "assistente_vendas_demo1"
    cache_id = os.getenv("EMAIL_USUARIO")
    chat_history = SQLChatMessageHistory(session_id=cache_id, connection_string=connection, table_name=table_name)
    return chat_history

    #history1 = GetChatHistory(app_keys, app_params, "ConversationBufferWindowMemory")
    #conv_buf_win_memory = ConversationBufferWindowMemory(memory_key='chat_history', input_key='question', output_key='answer', chat_memory=history1, return_messages=True, k=app_keys.MEMORY_K, verbose=app_keys.DEBUG(2))

    history2 = GetChatHistory(app_keys, app_params, "ConversationSummaryBufferMemory")
    summary_memory = ConversationSummaryBufferMemory(llm=llm, memory_key='summary', input_key='question', output_key='answer', chat_memory=history2, return_messages=True, verbose=app_keys.DEBUG(2))



