# https://github.com/PromptEngineer48/Sales_Agent_using_LangChain/blob/main/sales_pen_git.py

import json
import os
import random
from time import sleep
from typing import Any, Callable, Dict, List, Union
from pydantic import BaseModel, Field
from pathlib import Path
 
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, Tool, tool
from langchain.indexes import VectorstoreIndexCreator
from langchain.schema.document import Document
from langchain.chains import LLMChain, RetrievalQA
from langchain.llms import BaseLLM
from langchain.chains.base import Chain
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma, Qdrant, FAISS
from langchain_community.document_loaders import TextLoader
from tenacity import retry_unless_exception_type
from langchain_community.tools import HumanInputRun
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import UnstructuredFileLoader

from app_product_data_model import ConexaoBanco, adicionar_itens_carrinho, apagar_carrinho, carrinho_para_json, criar_carrinho, filtrar_produtos_detalhados, filtrar_produtos_detalhados_materializada, listar_categorias, object_to_dict, produtos_para_json, remover_item_carrinho


@tool
def pesquisar_produto(query:str) -> json:
    """útil para quando você precisa responder a perguntas sobre produtos."""
    #produtos = filtrar_produtos_detalhados(query_str=query)
    produtos = filtrar_produtos_detalhados_materializada(query_str=query)
    produtos_json = produtos_para_json(produtos)
    return produtos_json


@tool
def listar_categorias_de_produtos() -> json:
    """útil para quando o cliente perguntar quais produtos ou tipos de produtos estão disponíveis para ele comprar."""
    return listar_categorias()


@tool
def responder_duvida(duvida:str) -> str:
    """
    útil para quando você precisa responder a perguntas do usuário que não estão relacionadas à comprar um produto.
    Exemplos de dúvidas: Horário de funcionamento, politicas de devolução, modos de pagamento, etc.
    """

    fname = "./faq_tem_de_tudo.txt"
    loader = UnstructuredFileLoader(fname)
    index = VectorstoreIndexCreator()
    doc = index.from_loaders([loader])
    chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0,model=os.getenv("MODEL_NAME")),chain_type="stuff",retriever=doc.vectorstore.as_retriever(),input_key="question")
    response = chain.invoke({"question":duvida})

    return response["result"]


@tool
def acompanhar_pedido(numero_pedido:str) -> str:
    """
    útil para quando você precisa responder sobre o status de uma compra.
    """
    return "Não há resposta para a sua pergunta."


@tool
def metodos_de_pagamento() -> str:
    """
    útil para quando você precisa responder sobre os métodos de pagamento aceitos.
    """
    return "Aceitamos cartão de crédito, boleto bancário e PIX."


@tool
def processar_pagamento_produto(numero_do_cartao:str, nome_impresso_no_cartao:str, data_de_validade:str, codigo_de_seguranca_cvv:str) -> str:
    """
    útil para quando você precisa processar o pagamento do pedido do cliente por cartão de crétido.
    """
    return f"Pagamento realizado com sucesso. Número do pedido {random.randint(10000, 99999)}"


@tool
def registrar_item_desejo_cliente(email:str, produto_desejado:str) -> str:
    """
    Útil para quando o produto que o cliente deseja está em falta e você registrar um lembrete para o cliente ser avisado quando este produto chegar.
    Args:
        email (str): O email informado pelo cliente.
        produto_desejado (str): Descrição do produto que o cliente deseja.

    Returns:
        str: Mensagem de retorno.
    """    
    print(f"\nRegistrando pedido do cliente: {email} = {produto_desejado}\n")
    return "Lembrete registrado com sucesso!"


@tool
def registrar_reclamacao_cliente(email:str, reclamacao:str) -> str:
    """útil para quando você precisa registrar uma reclamação do cliente."""
    print(f"\nRegistrando reclamação do cliente: {email} = {reclamacao}\n")
    return "Reclamação registrada com sucesso!"


@tool
def abrir_chamado_duvida(email:str, duvida:str) -> str:
    """útil para quando você precisa abrir um chamado de atendimento para solucionar uma dúvida do cliente que você não encontrou a resposta."""
    print(f"\nAbrindo chamado do cliente: {email} = {duvida}\n")
    return f"Chamado {random.randint(10000, 99999)} aberto com com sucesso!"


@tool
def apagar_carrinho_compras(email_usuario: str) -> bool:
    """útil para quando você precisa apagar o carrinho de compras do cliente."""
    return apagar_carrinho(email_usuario)


@tool
def criar_carrinho_compras(email_usuario: str) -> bool:
    """útil para quando você precisa criar um carrinho de compras para o cliente."""
    return criar_carrinho(email_usuario)


@tool
def adicionar_itens_carrinho_compras(email_usuario: str, itens: List[Dict[str, int]]) -> bool:
    """
    Adiciona itens ao carrinho de compras de um usuário específico.

    Args:
        email_usuario (str): O email do usuário para o qual o carrinho pertence ou será criado.
        itens (List[Dict[str, int]]): Uma lista de dicionários, onde cada dicionário representa um item a ser adicionado ao carrinho.
            Cada dicionário deve ter as seguintes chaves e valores:
            - 'id_produto' (int): O identificador do produto a ser adicionado ao carrinho.
            - 'quantidade' (int): A quantidade do produto a ser adicionada.

    Exemplo de 'itens':
        [
            {'id_produto': 1, 'quantidade': 2},
            {'id_produto': 2, 'quantidade': 1},
        ]

    Retorna:
        bool. A função retorna True se conseguiu adicionar os itens 
    """
    return adicionar_itens_carrinho(email_usuario, itens)


@tool
def remover_item_carrinho_compras(email_usuario: str, id_item: int) -> bool:
    """Remove um item do carrinho de compras de um usuário."""
    return remover_item_carrinho(email_usuario, id_item)


@tool
def recuperar_carrinho_compras(email_usuario: str):
    """Recupera o carrinho de compras de um usuário."""
    return carrinho_para_json(email_usuario)


@tool
def obtem_email_cliente() -> str:
    """
    útil para quando você precisa saber qual é o email do cliente.
    """
    return os.getenv("EMAIL_USUARIO")


def get_app_tools():
    human_tool_desc = ''' 
    Você pode usar esta ferramenta para solicitar ao usuário os detalhes relacionados à solicitação, como por exemplo o seu email. 
    Sempre use esta ferramenta se tiver dúvidas de acompanhamento. 
    A entrada deve ser uma pergunta para o usuário. 
    Seja conciso, educado e profissional ao fazer as perguntas. 
    '''

    human_tool = HumanInputRun(descrição = human_tool_desc)

    tools = []
    #tools.append(human_tool)
    tools.append(pesquisar_produto)
    tools.append(listar_categorias_de_produtos)
    tools.append(responder_duvida)
    tools.append(acompanhar_pedido)
    tools.append(metodos_de_pagamento)
    tools.append(processar_pagamento_produto)
    tools.append(registrar_item_desejo_cliente)
    tools.append(registrar_reclamacao_cliente)
    tools.append(abrir_chamado_duvida)
    tools.append(apagar_carrinho_compras)
    tools.append(criar_carrinho_compras)
    tools.append(adicionar_itens_carrinho_compras)
    tools.append(remover_item_carrinho_compras)
    tools.append(recuperar_carrinho_compras)
    tools.append(obtem_email_cliente)

    return tools

