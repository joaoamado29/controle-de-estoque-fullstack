"""
Rotas da API para gerenciamento de Produtos.

O que este módulo faz?
Ele expõe os endpoints HTTP (FastAPI) para cadastrar, listar, buscar estoque baixo,
calcular o valor patrimonial, dar entrada, registrar venda e excluir produtos.

Por que foi feito assim?
Os routers apenas recebem requisições HTTP, validam parâmetros com Pydantic e
delegam a execução para o ProdutoService, mantendo a camada de controle fina e desacoplada.
"""
from typing import Sequence
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.repositories.produto_repository import ProdutoRepository
from backend.services.produto_service import ProdutoService
from backend.schemas.produto import (
    ProdutoCreate,
    ProdutoResponse,
    QuantidadeInput,
    ValorTotalEstoqueResponse,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def get_produto_service(db: AsyncSession = Depends(get_db)) -> ProdutoService:
    """
    Função de fábrica para criar uma instância do ProdutoService com o repositório configurado.
    Por que assim: Centraliza a criação das dependências para injeção limpa no FastAPI.
    """
    repository = ProdutoRepository(db)
    return ProdutoService(repository)


@router.post(
    "/",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo produto",
)
async def cadastrar_produto(
    dados: ProdutoCreate,
    service: ProdutoService = Depends(get_produto_service),
) -> ProdutoResponse:
    """
    O que faz: Recebe dados válidos e cadastra um novo produto no catálogo.
    Por que assim: Retorna status 201 (Created) e o objeto criado com seu ID atribuído.
    """
    return await service.cadastrar_produto(dados)


@router.get(
    "/",
    response_model=Sequence[ProdutoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos os produtos",
)
async def listar_produtos(
    service: ProdutoService = Depends(get_produto_service),
) -> Sequence[ProdutoResponse]:
    """
    O que faz: Retorna a lista com todos os produtos disponíveis.
    """
    return await service.listar_produtos()


@router.get(
    "/estoque-baixo",
    response_model=Sequence[ProdutoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar produtos com estoque baixo",
)
async def listar_estoque_baixo(
    limite: int = Query(5, ge=1, description="Quantidade de corte para considerar estoque baixo"),
    service: ProdutoService = Depends(get_produto_service),
) -> Sequence[ProdutoResponse]:
    """
    O que faz: Filtra produtos cuja quantidade seja menor que o limite (padrão: 5).
    Por que assim: Declarado antes de /{produto_id} para evitar conflito de roteamento.
    """
    return await service.listar_estoque_baixo(limite=limite)


@router.get(
    "/valor-estoque",
    response_model=ValorTotalEstoqueResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcular o valor total do estoque",
)
async def calcular_valor_total(
    service: ProdutoService = Depends(get_produto_service),
) -> ValorTotalEstoqueResponse:
    """
    O que faz: Retorna o somatório de (quantidade * preço) de todos os produtos cadastrados.
    """
    total = await service.calcular_valor_total()
    return ValorTotalEstoqueResponse(valor_total=total)


@router.patch(
    "/{produto_id}/entrada",
    response_model=ProdutoResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar entrada de estoque",
)
async def registrar_entrada(
    produto_id: int,
    dados: QuantidadeInput,
    service: ProdutoService = Depends(get_produto_service),
) -> ProdutoResponse:
    """
    O que faz: Adiciona a quantidade especificada ao estoque atual do produto.
    """
    return await service.registrar_entrada(produto_id=produto_id, quantidade=dados.quantidade)


@router.patch(
    "/{produto_id}/venda",
    response_model=ProdutoResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar venda (saída) de estoque",
)
async def registrar_venda(
    produto_id: int,
    dados: QuantidadeInput,
    service: ProdutoService = Depends(get_produto_service),
) -> ProdutoResponse:
    """
    O que faz: Subtrai a quantidade vendida do estoque do produto, impedindo saldo negativo.
    """
    return await service.registrar_venda(produto_id=produto_id, quantidade=dados.quantidade)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir um produto",
)
async def deletar_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service),
) -> None:
    """
    O que faz: Remove permanentemente um produto pelo ID.
    Por que assim: Retorna 204 No Content para indicar sucesso sem corpo de resposta.
    """
    await service.deletar_produto(produto_id=produto_id)
