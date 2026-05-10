from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.schemas.user_schema import UserCreate
from app.models.user import User
from app.models.company import Company
from app.core.deps import get_db

router = APIRouter()


@router.post("/register", status_code=201)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    # =========================
    # 1. VERIFICA EMAIL
    # =========================
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email já cadastrado"
        )

    try:
        # =========================
        # 2. CRIA COMPANY (TENANT)
        # =========================
        company = Company(
            name=f"{user.name}'s Company"
        )

        db.add(company)
        await db.flush()  # gera company.id sem commit ainda

        # =========================
        # 3. CRIA USER LIGADO À COMPANY
        # =========================
        new_user = User(
            name=user.name,
            email=user.email,
            password=hash_password(user.password),
            company_id=company.id,   # 👈 AQUI ESTÁ O PONTO QUE FALTAVA
            role="admin",            # primeiro usuário = admin da empresa
            is_active=True
        )

        db.add(new_user)

        # =========================
        # 4. SALVA TUDO
        # =========================
        await db.commit()
        await db.refresh(new_user)

        return {
            "message": "Empresa e usuário criados com sucesso",
            "user_id": new_user.id,
            "company_id": company.id
        }

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Erro ao criar usuário/empresa"
        )