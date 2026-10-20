"""
Modelo da tabela 'produtos' no banco de dados.

Cada produto tem um nome único, quantidade em estoque (nunca negativa)
e um preço unitário (sempre positivo). Datas de criação e atualização
são gerenciadas automaticamente pelo banco.
"""
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Produto(Base):
    """
    Representa um produto no estoque.

    Campos:
        id          - Identificador único (auto-incremento).
        nome        - Nome do produto (máx 100 caracteres, único).
        quantidade  - Unidades em estoque (>= 0).
        preco       - Preço unitário (> 0).
        criado_em   - Data/hora da criação (preenchida pelo banco).
        atualizado_em - Data/hora da última atualização.
    """
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    nome: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    quantidade: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    preco: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Constraints garantem integridade direto no banco.
    __table_args__ = (
        CheckConstraint("quantidade >= 0", name="ck_quantidade_nao_negativa"),
        CheckConstraint("preco > 0", name="ck_preco_positivo"),
    )

    def __repr__(self) -> str:
        return f"<Produto(id={self.id}, nome='{self.nome}', qtd={self.quantidade})>"
