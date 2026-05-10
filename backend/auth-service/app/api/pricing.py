from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.pricing_service import update_national_pricing_base
# Supondo que você tenha o serviço de OCR pronto
from app.services.ocr_service import process_image_to_data 

router = APIRouter()

@router.post("/upload-encarte")
async def upload_encarte(
    market_id: int, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    # 1. Processa a imagem (OCR + IA Semântica)
    # Transforma a foto em uma lista de dicionários com universal_id e price
    items_extraidos = await process_image_to_data(file) 
    
    # 2. Alimenta a Base Nacional usando a função que criamos
    await update_national_pricing_base(items_extraidos, db)
    
    return {"message": "Base regional atualizada com sucesso!", "itens": len(items_extraidos)}