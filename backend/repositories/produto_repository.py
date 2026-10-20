"""
Repositório de acesso a dados da entidade Produto.

O que este módulo faz?
Ele concentra todas as operações de banco de dados relacionadas a produtos
(buscar, listar, salvar, atualizar e deletar).

Por que foi feito assim?
Isolar o banco de dados em um repositório segue o padrão Repository e o
princípio de Responsabilidade Única (SOLID). Caso a tecnologia do banco mude
ou precisemos fazer consultas mais complexas, alteramos apenas este arquivo.
"""
from typing import Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.produto import Produto


class ProdutoRepository:
    """
    Classe responsável por interagir diretamente com a tabela 'produtos' no banco.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        O que faz: Recebe a sessão assíncrona do banco de dados.
        Por que assim: Usamos injeção de dependência para facilitar testes e reuso.
        """
        self.db = db

    async def get_by_id(self, produto_id: int) -> Produto | None:
        """
        O que faz: Busca um produto pelo seu identificador numérico (ID).
        Por que assim: Usado para validar se um produto existe antes de vender ou dar entrada.
        """
        query = select(Produto).where(Produto.id == produto_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_nome(self, nome: str) -> Produto | None:
        """
        O que faz: Busca um produto pelo seu nome exato.
        Por que assim: O sistema não permite cadastrar dois produtos com o mesmo nome.
        """
        query = select(Produto).where(Produto.nome == nome)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(self) -> Sequence[Produto]:
        """
        O que faz: Retorna todos os produtos cadastrados ordenados pelo ID.
        Por que assim: Permite exibir a listagem completa na tela inicial do sistema.
        """
        query = select(Produto).order_by(Produto.id.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def list_estoque_baixo(self, limite: int = 5) -> Sequence[Produto]:
        """
        O que faz: Retorna produtos cuja quantidade em estoque esteja abaixo do limite especificado.
        Por que assim: Alerta o operador sobre itens que precisam ser repostos rapidamente.
        """
        query = select(Produto).where(Produto.quantidade < limite).order_by(Produto.quantidade.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def calculate_valor_total(self) -> float:
        """
        O que faz: Calcula a soma de (quantidade * preço) de todos os itens cadastrados.
        Por que assim: Fornece o valor financeiro total do patrimônio armazenado no estoque.
        """
        query = select(func.sum(Produto.quantidade * Produto.preco))
        result = await self.db.execute(query)
        total = result.scalar()
        # Se não houver produtos no estoque, o total retornado é 0.0
        return float(total or 0.0)

    async def create(self, produto: Produto) -> Produto:
        """
        O que faz: Salva um novo produto no banco de dados e confirma a transação.
        Por que assim: Garante a persistência dos dados e preenche automaticamente o ID gerado.
        """
        self.db.add(produto)
        await self.db.commit()
        await self.db.refresh(produto)
        return produto

    async def update(self, produto: Produto) -> Produto:
        """
        O que faz: Grava no banco as alterações feitas em um produto existente.
        Por que assim: Usado ao atualizar o saldo de estoque após uma entrada ou venda.
        """
        await self.db.commit()
        await self.db.refresh(produto)
        return produto

    async def delete(self, produto: Produto) -> None:
        """
        O que faz: Remove o produto do banco de dados e confirma a exclusão.
        Por que assim: Permite limpar itens descontinuados do catálogo.
        """
        await self.db.delete(produto)
        await self.db.commit()
