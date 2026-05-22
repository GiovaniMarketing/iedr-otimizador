# app/core/deps.py
from app.core.tenant import clear_tenant_id

# Como você removeu o banco de dados SQL, 
# a dependência 'get_db' agora apenas garante que o contexto do tenant
# seja limpo após cada requisição, sem tentar abrir conexão com banco.

async def get_db():
    try:
        # Retornamos None pois não há mais conexão SQL
        yield None
    finally:
        # Garante que não "vaze" tenant entre requests, mesmo sem banco
        clear_tenant_id()