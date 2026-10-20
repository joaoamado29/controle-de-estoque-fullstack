"""
Conexão com o banco de dados.

Cria o engine assíncrono, a fábrica de sessões e a classe
base para os modelos SQLAlchemy. Também expõe a função
get_db() usada como dependência do FastAPI.
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

# Engine assíncrono — gerencia o pool de conexões com o PostgreSQL.
engine = create_async_engine(settings.database_url, echo=False)

# Fábrica de sessões — cada chamada cria uma sessão independente.
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy do projeto."""
    pass


async def get_db() -> AsyncSession:
    """
    Gera uma sessão do banco para uso como dependência do FastAPI.
    A sessão é fechada automaticamente ao final da requisição.
    """
    async with async_session() as session:
        yield session
