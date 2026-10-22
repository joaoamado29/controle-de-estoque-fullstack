"""
Ponto de entrada da aplicação FastAPI.

O que este módulo faz?
Ele cria a aplicação FastAPI, configura os middlewares (como CORS para permitir
a comunicação com o frontend) e registra as rotas da API de produtos.

Por que foi feito assim?
Centralizar a inicialização da API em um único arquivo facilita a execução
do servidor ASGI (uvicorn) e o compartilhamento da instância do app nos testes.
"""
import logging
from pathlib import Path
from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.routers.produto_router import router as produto_router

logger = logging.getLogger("backend.main")

app = FastAPI(
    title="Stoky - Sistema de Gestão de Estoque",
    description="API do Stoky para controle de produtos, movimentação de estoque, alertas e relatórios.",
    version="1.0.0",
)

# Configuração de CORS para permitir requisições do frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """
    O que faz: Captura falhas de conexão operacional com o banco de dados (ex: PostgreSQL fora do ar).
    Por que assim: Evita que a aplicação gere erro 500 sem tratamento e informa ao cliente o status 503 com mensagem clara.
    """
    logger.error(f"Erro operacional no banco de dados na rota {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": f"Erro de conexão com o banco de dados: {str(exc)}"},
    )


# Registra as rotas da API com o prefixo /api
app.include_router(produto_router, prefix="/api")


@app.get("/health", tags=["Healthcheck"])
async def healthcheck(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    O que faz: Retorna o status de saúde da aplicação e da conectividade com o banco de dados.
    Por que assim: Testa a conectividade real executando um ping simples no banco (SELECT 1),
    garantindo que monitoramentos recebam 503 caso o banco esteja indisponível.
    """
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "database": "connected"},
        )
    except Exception as exc:
        logger.error(f"Falha de saúde na conexão com o banco de dados: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "database": "offline",
                "detail": f"Falha de conexão com o banco de dados: {str(exc)}",
            },
        )


# O que este bloco faz?
# Monta a pasta do frontend para que a interface HTML/CSS/JS seja servida
# diretamente ao acessar a raiz do servidor web (http://localhost:8000/).
#
# Por que foi feito assim?
# Permite que qualquer pessoa abra o sistema completo simplesmente iniciando o
# servidor FastAPI com `uvicorn backend.main:app`, sem precisar de outro servidor web.
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

