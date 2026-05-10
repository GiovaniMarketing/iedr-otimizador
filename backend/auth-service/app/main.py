import logging
import sys
import os
from logging.config import dictConfig
from contextlib import asynccontextmanager
from app.api import optimizer, pricing  # Importe o novo router de pricing
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv


# FORÇA O PATH: Garante que o Python encontre a pasta 'app' e 'api'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if os.path.join(current_dir, "app") not in sys.path:
    sys.path.insert(0, os.path.join(current_dir, "app"))

# Importações de Infraestrutura
from app.db.session import engine, get_db
from app.models.base import Base

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
# CICLO DE VIDA (LIFESPAN)
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando IEDR Auth Service e sincronizando tabelas...")
    #async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)
    logger.info("Banco de dados pronto para operações.")
    yield
    logger.info("Encerrando aplicação...")

# =====================================================
# INSTÂNCIA DO APP CORE
# =====================================================
app = FastAPI(
    title="IEDR Auth Service",
    version="1.0.0",
    lifespan=lifespan
)

print(">>> APP INSTANCE ID:", id(app))

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# REGISTRO DE TODAS AS ROTAS (ROUTERS)
# =====================================================

# Rotas de Usuários e Otimizador (Mantidas intactas)
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(optimizer_router, prefix="/optimizer", tags=["Optimizer"])
app.include_router(pricing.router, prefix="/pricing", tags=["Preços e OCR"])
# Registro Seguro do Catálogo
# Resolve o NameError e o AttributeError de uma vez só
if catalog and hasattr(catalog, 'router'):
    app.include_router(catalog.router, prefix="/catalog", tags=["Catalog"])
else:
    # Mensagem informativa amigável no console
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

@app.get("/db-health")
async def db_health(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "status": "ok",
            "check": result.scalar()
        }
    except Exception as e:
        logger.error("Falha Crítica no Banco: %s", e)
        return {
            "database": "disconnected",
            "status": "error",
            "detail": str(e)
        }

@app.get("/debug/info")
async def debug_info():
    return {
        "python_version": sys.version,
        "working_dir": os.getcwd(),
        "sys_path": sys.path[:3]
    }