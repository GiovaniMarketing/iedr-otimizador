from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "auth"
    }