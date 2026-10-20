"""
Serviço de regras de negócio para a gestão de Produtos.

O que este módulo faz?
Ele concentra toda a lógica e validações de negócio do sistema (ex: checar se
já existe produto com o mesmo nome, impedir venda quando não há estoque suficiente,
e coordenar chamadas ao repositório).

Por que foi feito assim?
Separar a regra de negócio dos endpoints HTTP (routers) mantém o código testável,
reutilizável e fácil de manter (princípio SOLID).
"""
from typing import Sequence
from fastapi import HTTPException, status

from backend.models.produto import Produto
from backend.repositories.produto_repository import ProdutoRepository
from backend.schemas.produto import ProdutoCreate


class ProdutoService:
    """
    Camada de serviço que executa as ações de negócio sobre produtos.
    """

    def __init__(self, repository: ProdutoRepository) -> None:
        """
        O que faz: Recebe a instância do repositório de produtos.
        Por que assim: Depender de abstração/injeção facilita a troca de componentes e testes.
        """
        self.repository = repository

    async def cadastrar_produto(self, dados: ProdutoCreate) -> Produto:
        """
        O que faz: Valida se o produto já existe e o cadastra no sistema.
        Por que assim: Garante a unicidade do nome do produto no catálogo.
        """
        produto_existente = await self.repository.get_by_nome(dados.nome)
        if produto_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto com o nome '{dados.nome}' já cadastrado no sistema."
            )

        novo_produto = Produto(
            nome=dados.nome,
            quantidade=dados.quantidade,
            preco=dados.preco,
        )
        return await self.repository.create(novo_produto)

    async def listar_produtos(self) -> Sequence[Produto]:
        """
        O que faz: Retorna a lista completa de produtos cadastrados.
        Por que assim: Atende a exibição da tabela principal de produtos.
        """
        return await self.repository.list_all()

    async def listar_estoque_baixo(self, limite: int = 5) -> Sequence[Produto]:
        """
        O que faz: Busca produtos com quantidade inferior ao limite informado (padrão 5).
        Por que assim: Permite identificar itens com risco de esgotamento.
        """
        return await self.repository.list_estoque_baixo(limite=limite)

    async def calcular_valor_total(self) -> float:
        """
        O que faz: Retorna o valor financeiro acumulado de todo o estoque.
        Por que assim: Mostra em tempo real quanto dinheiro está investido em mercadorias.
        """
        return await self.repository.calculate_valor_total()

    async def registrar_entrada(self, produto_id: int, quantidade: int) -> Produto:
        """
        O que faz: Aumenta o estoque de um produto existente.
        Por que assim: Usado quando chegam novas remessas de mercadorias de fornecedores.
        """
        produto = await self.repository.get_by_id(produto_id)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {produto_id} não encontrado."
            )

        produto.quantidade += quantidade
        return await self.repository.update(produto)

    async def registrar_venda(self, produto_id: int, quantidade: int) -> Produto:
        """
        O que faz: Dá baixa no estoque ao registrar uma venda.
        Por que assim: Não podemos permitir que o estoque fique negativo se o cliente tentar vender mais do que tem.
        """
        produto = await self.repository.get_by_id(produto_id)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {produto_id} não encontrado."
            )

        if produto.quantidade < quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantidade insuficiente em estoque. Disponível: {produto.quantidade}, solicitado: {quantidade}."
            )

        produto.quantidade -= quantidade
        return await self.repository.update(produto)

    async def deletar_produto(self, produto_id: int) -> None:
        """
        O que faz: Exclui permanentemente um produto do catálogo.
        Por que assim: Usado para limpar itens cadastrados por engano ou descontinuados.
        """
        produto = await self.repository.get_by_id(produto_id)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {produto_id} não encontrado."
            )

        await self.repository.delete(produto)
