from pydantic import BaseModel, EmailStr, ConfigDict


# =========================
# ENTRADA (REGISTER)
# =========================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# =========================
# SAÍDA (USER PUBLIC DATA)
# =========================
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)