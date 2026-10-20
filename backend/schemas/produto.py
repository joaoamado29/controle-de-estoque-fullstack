"""
Schemas Pydantic para validação e serialização de dados de produtos.

O que este módulo faz?
Ele define as regras para validar os dados que entram na API (como cadastro
de produtos e movimentação de estoque) e o formato dos dados enviados de volta
para o cliente (respostas).

Por que foi feito assim?
O Pydantic garante que valores incorretos (ex: texto vazio, preços negativos ou
quantidades inválidas) sejam rejeitados antes de chegarem ao banco de dados.
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProdutoBase(BaseModel):
    """
    Campos comuns a qualquer produto.

    O que faz: Reúne nome, quantidade e preço com regras de validação e limites de tamanho.
    Por que assim: Evita duplicação de regras em outros schemas e protege o banco de dados contra overflow.
    """
    nome: str = Field(..., max_length=100, description="Nome do produto (máximo 100 caracteres)")
    quantidade: int = Field(..., ge=0, le=1000000, description="Quantidade em estoque (0 a 1.000.000)")
    preco: float = Field(..., gt=0, le=9999999.99, description="Preço unitário em reais (máximo R$ 9.999.999,99)")

    @field_validator("nome")
    @classmethod
    def validar_nome_nao_vazio(cls, valor: str) -> str:
        """
        Garante que o nome não seja apenas espaços em branco ou vazio.
        """
        texto_limpo = valor.strip()
        if not texto_limpo:
            raise ValueError("O nome do produto não pode ser vazio ou conter apenas espaços.")
        return texto_limpo


class ProdutoCreate(ProdutoBase):
    """
    Schema utilizado no cadastro de um novo produto.
    Herda todas as validações básicas de ProdutoBase.
    """
    pass


class QuantidadeInput(BaseModel):
    """
    Schema para operações de movimentação de estoque (entrada e venda).

    O que faz: Recebe a quantidade a ser adicionada ou retirada do estoque.
    Por que assim: Exige pelo menos 1 unidade e no máximo 1.000.000 por movimentação.
    """
    quantidade: int = Field(
        ..., 
        gt=0, 
        le=1000000, 
        description="Quantidade movimentada (entre 1 e 1.000.000)"
    )



class ProdutoResponse(ProdutoBase):
    """
    Schema retornado pela API com os dados completos do produto.

    O que faz: Inclui identificador único gerado pelo banco e carimbos de data/hora.
    Por que assim: Permite que o frontend receba o ID para ações como venda e exclusão.
    """
    id: int
    criado_em: datetime
    atualizado_em: datetime

    # Permite ler dados diretamente de instâncias do modelo SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class ValorTotalEstoqueResponse(BaseModel):
    """
    Schema retornado pela consulta do valor total em estoque.
    """
    valor_total: float
