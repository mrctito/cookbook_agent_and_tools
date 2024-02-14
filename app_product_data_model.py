import datetime
import os
from typing import List, Dict
import json
from unidecode import unidecode
from sqlalchemy import DECIMAL, Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, func
from sqlalchemy import or_, and_
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import sessionmaker


class ConexaoBanco:
    def __init__(self, conexao_string):
        self.conexao_string = conexao_string

    @staticmethod
    def criar_sessao():
        conexao_string = os.getenv('CONEXAO_BANCO')
        engine = create_engine(conexao_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

# Exemplo de uso:
# sessao = ConexaoBanco.criar_sessao()    
# categorias = sessao.query(Categoria).all()

Base = declarative_base()


class Categoria(Base):
    __tablename__ = 'categorias'
    id_categorias = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)


class Subcategoria(Base):
    __tablename__ = 'subcategorias'
    id_subcategorias = Column(Integer, primary_key=True)
    nome = Column(String(50))


class Marca(Base):
    __tablename__ = 'marcas'
    id_marcas = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)


class Cor(Base):
    __tablename__ = 'cores'
    id_cores = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)


class Produto(Base):
    __tablename__ = 'produtos'
    id_produtos = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(String(1000))
    preco = Column(Float, nullable=False)
    preco_oferta = Column(Float, nullable=True)
    estoque = Column(Integer, nullable=False)
    id_categorias = Column(Integer, ForeignKey('categorias.id_categorias'), nullable=False)
    id_subcategorias = Column(Integer, ForeignKey('subcategorias.id_subcategorias'), nullable=False)
    id_marcas = Column(Integer, ForeignKey('marcas.id_marcas'), nullable=False)
    id_cores = Column(Integer, ForeignKey('cores.id_cores'), nullable=False)
    imagem = Column(String(1000))

    categoria = relationship("Categoria")
    subcategoria = relationship("Subcategoria")
    marca = relationship("Marca")
    cor = relationship("Cor")


class Carrinho(Base):
    __tablename__ = 'carrinho'
    id_carrinho = Column(Integer, primary_key=True, autoincrement=True)
    email_usuario = Column(String(50), nullable=False)
    data_criacao = Column(DateTime, default=func.now())
    status = Column(String(50))
    itens = relationship("ItemCarrinho", back_populates="carrinho")

class ItemCarrinho(Base):
    __tablename__ = 'itens_carrinho'
    id_item = Column(Integer, primary_key=True, autoincrement=True)
    id_carrinho = Column(Integer, ForeignKey('carrinho.id_carrinho'))
    id_produtos = Column(Integer, ForeignKey('produtos.id_produtos'))
    quantidade = Column(Integer, nullable=False)
    preco = Column(DECIMAL(10, 2), nullable=False)
    data_adicionado = Column(DateTime, default=func.now())
    carrinho = relationship("Carrinho", back_populates="itens")
    produto = relationship("Produto", backref="itens_carrinho")
    

class Venda(Base):
    __tablename__ = 'vendas'
    id_compras = Column(Integer, primary_key=True)
    id_cliente = Column(Integer, nullable=False)
    id_produtos = Column(Integer, ForeignKey('produtos.id_produtos'), nullable=False)
    id_lojas = Column(Integer, nullable=False)
    quantidade_vendida = Column(Integer, nullable=False)
    data_venda = Column(DateTime)
    preco_total = Column(Float, nullable=False)
    desconto_concedido = Column(Float)
    frete = Column(Integer)
    valor_pago = Column(Float, nullable=False)
    cupom = Column(String(50))
    parcelas = Column(Integer)
    status = Column(String(50), nullable=False)
    data_envio = Column(String(50))
    data_entrega = Column(String(50))
    id_meios_pagamento = Column(Integer, nullable=False)
    id_tipos_entrega = Column(Integer, nullable=False)

    produto = relationship("Produto")


class ProdutoDetalhado(Base):
    __tablename__ = 'produtos_detalhados'
    id_produtos = Column(Integer, primary_key=True)
    nome_produto = Column(String(150))
    descricao = Column(String(1000))
    preco = Column(Float)
    preco_oferta = Column(Float)
    estoque = Column(Integer)
    nome_categoria = Column(String(100))
    nome_subcategoria = Column(String(50))
    nome_marca = Column(String(50))
    nome_cor = Column(String(50))
    imagem = Column(String(1000))


class ProdutoDetalhadoMaterializado(Base):
    __tablename__ = 'produtos_detalhados_materializada'
    id_produtos = Column(Integer, primary_key=True)
    nome_produto = Column(String(150))
    descricao = Column(String(1000))
    preco = Column(Float)
    preco_oferta = Column(Float)
    estoque = Column(Integer)
    nome_categoria = Column(String(100))
    nome_subcategoria = Column(String(50))
    nome_marca = Column(String(50))
    nome_cor = Column(String(50))
    imagem = Column(String(1000))


# ============================================================

def object_to_dict(obj):
    """Converte um objeto SQLAlchemy em um dicionário."""
    mapper = class_mapper(obj.__class__)
    columns = [column.key for column in mapper.columns]
    return {column: getattr(obj, column) for column in columns}


def listar_categorias() -> json:
    """útil para quando você precisa saber todas as categorias de produto que existem."""
    with ConexaoBanco.criar_sessao() as sessao:
        categorias = sessao.query(Categoria).all()
        categorias_dict = [object_to_dict(categoria) for categoria in categorias]
        categorias_json = json.dumps(categorias_dict)
        return categorias_json


def listar_subcategorias() -> json:
    """útil para quando você precisa saber todas as subcategorias de produto que existem."""
    with ConexaoBanco.criar_sessao() as sessao:
        subcategorias = sessao.query(Categoria).all()
        subcategorias_dict = [object_to_dict(subcategoria) for subcategoria in subcategorias]
        subcategorias_json = json.dumps(subcategorias_dict)
        return subcategorias_json


def listar_marcas() -> json:
    """útil para quando você precisa saber todas as marcas de produto que existem."""
    with ConexaoBanco.criar_sessao() as sessao:
        marcas = sessao.query(Marca).all()
        marcas_dict = [object_to_dict(marca) for marca in marcas]
        marcas_json = json.dumps(marcas_dict)
        return marcas_json


def listar_cores() -> json:
    """útil para quando você precisa saber todas as cores de produto que existem."""
    with ConexaoBanco.criar_sessao() as sessao:
        cores = sessao.query(Cor).all()
        cores_dict = [object_to_dict(cor) for cor in cores]
        cores_json = json.dumps(cores_dict)
        return cores_json


def filtrar_produtos_detalhados(query_str: str = None, max_results: int = 3, normalize_string: bool=False) -> List[ProdutoDetalhado]:
    with ConexaoBanco.criar_sessao() as session:
        query = session.query(ProdutoDetalhado)
        
        if query_str:
            # Divide a string de consulta em termos individuais
            
            if normalize_string:
                query_str = unidecode(query_str)
        
            termos_busca = query_str.split()

            # Cria uma lista de condições 'or_' para cada termo de busca
            condicoes = []
            for termo in termos_busca:
                termo_busca = f'%{termo}%'
                condicao_or = or_(
                    ProdutoDetalhado.nome_produto.ilike(termo_busca),
                    ProdutoDetalhado.descricao.ilike(termo_busca),
                    ProdutoDetalhado.nome_categoria.ilike(termo_busca),
                    ProdutoDetalhado.nome_subcategoria.ilike(termo_busca),
                    ProdutoDetalhado.nome_marca.ilike(termo_busca),
                    ProdutoDetalhado.nome_cor.ilike(termo_busca),
                )
                condicoes.append(condicao_or)
            
            # Combina todas as condições 'or_' com 'and_' para garantir que todos os termos sejam atendidos
            query = query.filter(and_(*condicoes))
            query = query.limit(max_results)
        return query.all()


'''
-- Criação da tabela materializada
CREATE TABLE produtos_detalhados_materializada AS
SELECT * FROM produtos_detalhados;

-- Adicionando índice full-text
CREATE FULLTEXT INDEX ft_index ON produtos_detalhados_materializada (nome_produto, descricao, nome_categoria, nome_subcategoria, nome_marca);
'''
def filtrar_produtos_detalhados_materializada(query_str: str = None, max_results: int = 3, normalize_string: bool = False) -> List[ProdutoDetalhadoMaterializado]:
    with ConexaoBanco.criar_sessao() as session:
        if query_str:
            if normalize_string:
                query_str = unidecode(query_str)
            
            # Prepara a string de consulta para uso no MATCH ... AGAINST
            # Adapte conforme necessário para usar o modo natural ou booleano
            match_clause = "MATCH(nome_produto, descricao, nome_categoria, nome_subcategoria, nome_marca, nome_cor) AGAINST(:query IN NATURAL LANGUAGE MODE)"
            
            # Executa a consulta usando MATCH ... AGAINST
            query = session.query(ProdutoDetalhadoMaterializado).filter(text(match_clause)).params(query=query_str)
            query = query.limit(max_results)

            return query.all()
        else:
            # Se não houver uma string de consulta, retorna os primeiros max_results produtos
            return session.query(ProdutoDetalhadoMaterializado).limit(max_results).all()



def produtos_para_json_str(produtos):
    produtos_json = []
    for produto in produtos:  # Itera sobre cada produto na lista
        produto_dict = object_to_dict(produto)  # Converte cada produto para dicionário
        produtos_json.append(produto_dict)
    return json.dumps(produtos_json) 


def produtos_para_json(produtos: List[ProdutoDetalhado | ProdutoDetalhadoMaterializado]) -> json:
    produtos_json = produtos_para_json_str(produtos)
    return json.loads(produtos_json)


def apagar_carrinho(email_usuario: str) -> bool:
    with ConexaoBanco.criar_sessao() as session:
        try:
            # Primeiro, encontre o carrinho com base no email do usuário
            carrinho = session.query(Carrinho).filter_by(email_usuario=email_usuario, status='ativo').first()
            if carrinho:
                # Remova todos os itens associados ao carrinho
                itens_carrinho = session.query(ItemCarrinho).filter_by(id_carrinho=carrinho.id_carrinho).all()
                for item in itens_carrinho:
                    session.delete(item)
                
                # Após remover todos os itens, remova o próprio carrinho
                session.delete(carrinho)
                session.commit()
                return True
        except Exception as e:
            print(f"Erro ao apagar carrinho: {e}")
            return False
        

def criar_carrinho(email_usuario: str) -> bool:
    with ConexaoBanco.criar_sessao() as session:
        try:
            novo_carrinho = Carrinho(email_usuario=email_usuario, data_criacao=datetime.datetime.now(), status='ativo')
            session.add(novo_carrinho)
            session.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar carrinho: {e}")
            return False


def adicionar_itens_carrinho(email_usuario: str, itens: List[Dict[str, int]]) -> bool:
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
    with ConexaoBanco.criar_sessao() as session:
        try:
            carrinho_localizado = session.query(Carrinho).filter_by(email_usuario=email_usuario, status='ativo').first()
            if not carrinho_localizado:
                carrinho_localizado = Carrinho(email_usuario=email_usuario, data_criacao=datetime.datetime.now(), status='ativo')
                session.add(carrinho_localizado)
            carrinho = carrinho_localizado
            for item in itens:
                id_produto = item['id_produto']
                quantidade = item['quantidade']
                produto = session.query(Produto).filter_by(id_produtos=id_produto).first()
                if produto:
                    novo_item = ItemCarrinho(id_carrinho=carrinho.id_carrinho, id_produtos=id_produto, quantidade=quantidade, preco=produto.preco, data_adicionado=datetime.datetime.now())
                    session.add(novo_item)
            session.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar carrinho: {e}")
            return False


def remover_item_carrinho(email_usuario: str, id_item: int) -> bool:
    with ConexaoBanco.criar_sessao() as session:
        try:
            item = session.query(ItemCarrinho).join(Carrinho).filter(Carrinho.email_usuario == email_usuario, ItemCarrinho.id_item == id_item).first()
            if item:
                session.delete(item)
                session.commit()
                return True
        except Exception as e:
            print(f"Erro ao criar carrinho: {e}")
            return False


def recuperar_carrinho(email_usuario: str):
    with ConexaoBanco.criar_sessao() as session:
        try:
            carrinho = session.query(Carrinho).filter_by(email_usuario=email_usuario, status='ativo').first()
            if not carrinho:
                return None
            itens_carrinho = session.query(ItemCarrinho).filter_by(id_carrinho=carrinho.id_carrinho).all()
            return carrinho, itens_carrinho
        except Exception as e:
            print(f"Erro ao criar carrinho: {e}")
            return False


def carrinho_para_json(email_usuario: str) -> json:
    try:
        resultado = recuperar_carrinho(email_usuario)
        if not resultado:
            return json.dumps({'error': 'Carrinho não encontrado'})

        carrinho, itens_carrinho = resultado

        carrinho_json = {
            'id_carrinho': carrinho.id_carrinho,
            'email_usuario': carrinho.email_usuario,
            'data_criacao': carrinho.data_criacao.isoformat(),
            'status': carrinho.status,
            'itens': [
                {
                    'id_item': item.id_item,
                    'id_produtos': item.id_produtos,
                    'quantidade': item.quantidade,
                    'preco': float(item.preco),
                    'data_adicionado': item.data_adicionado.isoformat()
                } for item in itens_carrinho
            ]
        }
        
        return carrinho_json
    except Exception as e:
        print(f"Erro ao recuperar carrinho: {e}")
        return json.dumps({'error': 'Erro ao recuperar carrinho'})
