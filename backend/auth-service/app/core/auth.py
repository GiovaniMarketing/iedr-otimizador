from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.models.user import User

# =========================
# CONFIG JWT
# =========================
SECRET_KEY = "CHANGE_THIS_SECRET_KEY_123456"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# =========================
# CONTEXTO DO USUÁRIO
# =========================
class CurrentUserContext:
    def __init__(self, user: User, company_id: int):
        self.user = user
        self.company_id = company_id


# =========================
# USUÁRIO LOGADO (COM TENANT)
# =========================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Não autenticado ou token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")
        company_id = payload.get("company_id")

        if not email or not company_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User).where(
            User.email == email,
            User.company_id == company_id
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return CurrentUserContext(
        user=user,
        company_id=company_id
    )


# =========================
# PROTEÇÃO ADMIN
# =========================
def require_admin(current: CurrentUserContext = Depends(get_current_user)):

    if current.user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: apenas administradores"
        )

    return current