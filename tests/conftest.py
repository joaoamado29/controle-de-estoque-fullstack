"""
Configurações e fixtures para os testes automatizados com pytest.

Utiliza SQLite assíncrono em memória (aiosqlite) para que a suíte
de testes seja rápida, isolada e não polua o banco de dados principal.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
import backend.models.produto  # noqa: F401 - Garante registro dos modelos no Base.metadata

# Engine SQLite em memória para testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
async_session_test = async_sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(autouse=True)
async def setup_db():
    """Cria todas as tabelas antes de cada teste e remove ao final."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Fornece uma sessão de banco de teste isolada."""
    async with async_session_test() as session:
        yield session


@pytest.fixture
async def client():
    """
    Cliente HTTP assíncrono (httpx) configurado com o app FastAPI
    e a dependência get_db sobrescrita para usar o banco de teste.
    """
    # Importamos app dentro da fixture para evitar erros se ainda não estiver completo
    from backend.main import app

    async def override_get_db():
        async with async_session_test() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
