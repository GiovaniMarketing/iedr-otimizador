import logging
import sys
import os
from logging.config import dictConfig
from contextlib import asynccontextmanager
from app.api import optimizer, pricing  # Importe o novo router de pricing
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import pricing
from dotenv import load_dotenv


# --- COLOQUE A CONFIGURAÇÃO DE CORS AQUI ---
# Configuração de CORS

# ... (seus imports)

# 1. Definição do Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando IEDR Motor de Cálculo...")
    yield
    logger.info("Encerrando aplicação...")

# 2. Criação do app (A VARIÁVEL 'app' NASCE AQUI)
app = FastAPI(
    title="IEDR Auth Service",
    version="1.0.0",
    lifespan=lifespan
)

# 3. CONFIGURAÇÃO DE CORS (Agora o 'app' já existe, pode usar!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return Response(status_code=200)

# 4. O resto do seu código (Rotas, print do ID, etc...)
print(">>> APP INSTANCE ID:", id(app))
# ...


# --- MÓDULOS DE BANCO DE DADOS DESATIVADOS (MODO CSV) ---
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession


# FORÇA O PATH: Garante que o Python encontre a pasta 'app' e 'api'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if os.path.join(current_dir, "app") not in sys.path:
    sys.path.insert(0, os.path.join(current_dir, "app"))

# Importações de Infraestrutura
# --- CONEXÕES DE BANCO DE DADOS DESATIVADAS (MODO CSV) ---
# from app.db.session import engine, get_db
# from app.models.base import Base

# Importações das Rotas Originais
from app.api.user_routes import router as user_router
from app.api.optimizer import router as optimizer_router

# =====================================================
# TRATAMENTO DO MÓDULO CATALOG
# =====================================================
catalog = None 

try:
    # Tenta importar o modelo/roteador
    from app.models import catalog as catalog_model
    catalog = catalog_model 
except ImportError:
    print("⚠️ Aviso: O módulo catalog em app/models não foi encontrado.")

load_dotenv()

# =====================================================
# CONFIGURAÇÃO DE LOGGING
# =====================================================
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# =====================================================
# INSTÂNCIA DO APP CORE
# =====================================================


print(">>> APP INSTANCE ID:", id(app))

# =====================================================
# REGISTRO DE TODAS AS ROTAS (ROUTERS)
# =====================================================

# Rotas base
app.include_router(user_router, prefix="/users", tags=["Users"])
# app.include_router(optimizer_router, prefix="/optimizer", tags=["Optimizer"]) # COMENTADO PARA EVITAR CONFLITO
app.include_router(pricing.router, prefix="/optimizer", tags=["Optimizer"])
app.include_router(pricing.router, prefix="/pricing", tags=["Preços e OCR"])

# TRUQUE DE ENGENHARIA: Registro espelho para garantir compatibilidade total
# Se o seu React bater em /pricing/optimizer/basket, este registro resolve:
app.include_router(pricing.router, prefix="/pricing/optimizer", tags=["Preços e OCR (Compatibilidade)"])

# Registro Seguro do Catálogo
if catalog and hasattr(catalog, 'router'):
    app.include_router(catalog.router, prefix="/catalog", tags=["Catalog"])
else:
    msg = "ℹ️ Info: Catalog importado como modelo" if catalog else "⚠️ Info: Catalog não disponível"
    print(f"{msg} - Sem rotas configuradas para o Swagger.")

# =====================================================
# ENDPOINTS DE MONITORAMENTO E DEBUG
# =====================================================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "auth-service",
        "region": "São Sebastião - SP"
    }

# --- ENDPOINT DE SAÚDE DO BANCO DE DADOS DESATIVADO ---
# @app.get("/db-health")
# async def db_health(db: AsyncSession = Depends(get_db)):
#     try:
#         result = await db.execute(text("SELECT 1"))
#         return {
#             "database": "connected",
#             "status": "ok",
#             "check": result.scalar()
#         }
#     except Exception as e:
#         logger.error("Falha Crítica no Banco: %s", e)
#         return {
#             "database": "disconnected",
#             "status": "error",
#             "detail": str(e)
#         }

@app.get("/debug/info")
async def debug_info():
    return {
        "python_version": sys.version,
        "working_dir": os.getcwd(),
        "sys_path": sys.path[:3]
    }