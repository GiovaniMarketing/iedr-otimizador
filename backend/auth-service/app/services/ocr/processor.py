import cv2
import paddleocr
from app.services.ai.semantic_matcher import normalize_product_name

# Inicializa a Engine Nacional de OCR
ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='pt')

async def process_market_image(image_path, market_id):
    """
    Transforma imagem de encarte em dados de preços para o IEDR.
    """
    # 1. Extração Textual
    result = ocr.ocr(image_path, cls=True)
    
    extracted_items = []
    for line in result[0]:
        text = line[1][0]  # Ex: "Arroz Agulhinha T1 5kg R$ 25,90"
        
        # 2. Inteligência Semântica (Seção 9 do Blueprint)
        # Normaliza o texto bruto para o Catálogo Universal
        product_data = await normalize_product_name(text)
        
        if product_data:
            extracted_items.append({
                "market_id": market_id,
                "universal_id": product_data.master_id,
                "price": product_data.price,
                "timestamp": datetime.now()
            })
            
    # 3. Atualização do Pricing Service em Lote
    await update_national_pricing_base(extracted_items)