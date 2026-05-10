from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.core.auth import get_current_user, CurrentUserContext
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import User
from app.models.company import Company

router = APIRouter()


# =========================
# REGISTER
# =========================
@router.post("/register", status_code=201)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="Email já cadastrado")

    company = Company(name=f"{user.name}'s Space")

    db.add(company)
    await db.flush()

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        company_id=company.id,
        role="admin",
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "Usuário criado com sucesso",
        "user_id": new_user.id,
        "company_id": company.id
    }


# =========================
# LOGIN
# =========================
@router.post("/login")
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_access_token({
        "sub": db_user.email,
        "company_id": db_user.company_id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================
# ME
# =========================
@router.get("/me")
async def read_me(
    current: CurrentUserContext = Depends(get_current_user)
):

    return {
        "id": current.user.id,
        "name": current.user.name,
        "email": current.user.email,
        "role": current.user.role,
        "company_id": current.company_id,
        "is_active": current.user.is_active
    }