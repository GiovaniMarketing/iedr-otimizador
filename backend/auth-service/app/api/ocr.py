from fastapi import APIRouter, UploadFile, File, Depends
from app.services.ocr.processor import process_market_image

router = APIRouter()

@router.post("/upload-encarte")
async def upload_encarte(
    market_id: int, 
    file: UploadFile = File(...)
):
    # Salva temporariamente a foto enviada pelo cliente
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Chama a função que te passei para processar
    resultado = await process_market_image(file_location, market_id)
    
    return {"status": "Processamento iniciado", "items_identificados": len(resultado)}