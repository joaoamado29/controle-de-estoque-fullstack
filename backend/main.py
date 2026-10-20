"""
Ponto de entrada da aplicação FastAPI.

O que este módulo faz?
Ele cria a aplicação FastAPI, configura os middlewares (como CORS para permitir
a comunicação com o frontend) e registra as rotas da API de produtos.

Por que foi feito assim?
Centralizar a inicialização da API em um único arquivo facilita a execução
do servidor ASGI (uvicorn) e o compartilhamento da instância do app nos testes.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers.produto_router import router as produto_router

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

# Registra as rotas da API com o prefixo /api
app.include_router(produto_router, prefix="/api")


@app.get("/health", tags=["Healthcheck"])
async def healthcheck() -> dict[str, str]:
    """
    O que faz: Retorna o status de saúde da aplicação.
    Por que assim: Útil para checar se a API está no ar em monitoramentos ou contêineres.
    """
    return {"status": "ok"}


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

