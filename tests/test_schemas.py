"""
Testes unitários para os schemas Pydantic de validação de dados.
"""
import pytest
from pydantic import ValidationError

from backend.schemas.produto import ProdutoCreate, QuantidadeInput, ProdutoResponse


def test_produto_create_valido():
    """Valida que dados corretos criam um schema ProdutoCreate com sucesso."""
    produto = ProdutoCreate(nome="Caderno Universitário", quantidade=10, preco=19.90)
    assert produto.nome == "Caderno Universitário"
    assert produto.quantidade == 10
    assert produto.preco == 19.90


def test_produto_create_nome_vazio_invalido():
    """Valida que nome vazio ou apenas espaços é rejeitado."""
    with pytest.raises(ValidationError):
        ProdutoCreate(nome="", quantidade=10, preco=19.90)

    with pytest.raises(ValidationError):
        ProdutoCreate(nome="   ", quantidade=10, preco=19.90)


def test_produto_create_preco_menor_ou_igual_a_zero_invalido():
    """Valida que preço zero ou negativo é rejeitado."""
    with pytest.raises(ValidationError):
        ProdutoCreate(nome="Lápis", quantidade=10, preco=0.0)

    with pytest.raises(ValidationError):
        ProdutoCreate(nome="Lápis", quantidade=10, preco=-5.0)


def test_produto_create_quantidade_negativa_invalida():
    """Valida que quantidade negativa é rejeitada no cadastro."""
    with pytest.raises(ValidationError):
        ProdutoCreate(nome="Borracha", quantidade=-1, preco=2.50)


def test_quantidade_input_menor_ou_igual_zero_invalido():
    """Valida que operações de entrada ou venda exigem quantidade maior que zero."""
    with pytest.raises(ValidationError):
        QuantidadeInput(quantidade=0)

    with pytest.raises(ValidationError):
        QuantidadeInput(quantidade=-3)
