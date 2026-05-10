from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import jwt, JWTError

from app.core.tenant import set_tenant_id, clear_tenant_id

SECRET_KEY = "CHANGE_THIS_SECRET_KEY_123456"
ALGORITHM = "HS256"


class TenantMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        token = request.headers.get("Authorization")

        try:
            if token and token.startswith("Bearer "):

                token = token.replace("Bearer ", "")

                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

                company_id = payload.get("company_id")

                if company_id:
                    set_tenant_id(company_id)

        except JWTError:
            # não quebra request pública (login/register)
            pass

        response = await call_next(request)

        # garante limpeza do contexto entre requests
        clear_tenant_id()

        return response