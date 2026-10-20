"""
Configurações da aplicação.

Carrega variáveis de ambiente do arquivo .env para uso
em todo o sistema (ex: URL do banco de dados).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações centrais do sistema.
    O valor padrão de database_url é sobrescrito pelo .env em produção.
    """
    database_url: str = (
        "postgresql+asyncpg://estoque_user:estoque_pass@localhost:5432/estoque_db"
    )
    database_url_sync: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Instância global de configurações — importada em qualquer módulo.
settings = Settings()
