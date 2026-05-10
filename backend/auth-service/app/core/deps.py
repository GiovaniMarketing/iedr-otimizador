from app.db.session import AsyncSessionLocal
from app.core.tenant import clear_tenant_id

async def get_db():

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # garante que não "vaze" tenant entre requests
            clear_tenant_id()