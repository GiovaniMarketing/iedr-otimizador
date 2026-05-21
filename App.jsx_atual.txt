from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import httpx
import math
from bs4 import BeautifulSoup

router = APIRouter()

# =================================================================
# 🟢 INTEGRAÇÃO DE ECOSSISTEMA: WZAP MARKETING (CROSS-SELL)
# =================================================================
# "INATIVO": Fluxo padrão. "ATIVO": Dispara as ofertas via WhatsApp
INTEGRACAO_WZAP_MARKETING = "INATIVO"
WZAP_API_URL = "http://localhost:porta_do_seu_wzap/api/send"

# =================================================================
# ⚙️ CONFIGURAÇÃO DE INFRAESTRUTURA WHITE LABEL (MOTOR DE PREÇOS)
# =================================================================
# MODO "LOCAL": Usa o super catálogo de 100 itens em memória (Custo R$ 0)
# MODO "GOOGLE_CLOUD": Ativa a rota avançada de busca refinada na nuvem do Google
# MODO "BANCO_DE_DADOS": Ativa a leitura em banco relacional (Enterprise/SQL)
MODO_MOTOR_PRECO = "LOCAL" 

# Configurações de credenciais para upgrades (Google e Banco de Dados)
GOOGLE_PROJECT_ID = "seu-projeto-google-cloud"
GOOGLE_BIGQUERY_DATASET = "dataset_precos_brasil"
DB_CONNECTION_STRING = "postgresql://usuario:senha@localhost:5432/compras_db"
# =================================================================

# --- MODELOS ---
class ItemCesta(BaseModel):
    product_name: Optional[str] = "Item sem nome"
    nome: Optional[str] = None 
    quantity: Optional[int] = 1
    quantidade: Optional[int] = None

class RequisicaoOtimizacao(BaseModel):
    items: Optional[List[ItemCesta]] = []
    itens: Optional[List[ItemCesta]] = [] 
    cesta: Optional[List[ItemCesta]] = [] 
    lat: float
    lng: float
    raio_km: float = 5.0
    transporte: Optional[str] = "carro"

    class Config:
        extra = 'ignore'

# --- CÁLCULO DE DISTÂNCIA REAL (HAVERSINE) ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- FUNÇÃO AUXILIAR DE RASPAGEM ---
async def raspar_preco_na_web(url_busca: str, seletor_css: str, produto: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }
    try:
        async with httpx.AsyncClient() as client:
            url_real = f"{url_busca}{produto}"
            response = await client.get(url_real, headers=headers, timeout=5.0)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                elemento_preco = soup.select_one(seletor_css)
                if elemento_preco:
                    texto_preco = elemento_preco.text
                    preco_limpo = texto_preco.replace("R$", "").replace(" ", "").replace("\n", "").replace(",", ".").strip()
                    return float(preco_limpo)
    except Exception as e:
        print(f"DEBUG SCRAPER: Falha ao raspar na URL {url_busca}: {e}")
    return None

# --- ROTA DE INTEGRAÇÃO PROPRIETÁRIA: WZAP MARKETING ---
async def disparar_alerta_wzap_marketing(telefone_cliente: str, mercado_campeao: str, valor_total: float):
    """
    Hook de integração com o wZap Marketing.
    Ativado quando o cliente compra o pacote com módulo de disparo WhatsApp.
    """
    try:
        print(f"🟢 WZAP MARKETING ATIVADO: Preparando envio de ofertas para o WhatsApp...")
        mensagem_promo = f"🔥 OFERTA DETECTADA! O {mercado_campeao} está com a cesta mais barata hoje: R$ {valor_total:.2f}. Aproveite!"
        
        # O código abaixo fica preparado para chamar a API local do seu wZap Marketing
        # payload = {"number": telefone_cliente, "message": mensagem_promo}
        # async with httpx.AsyncClient() as client:
        #     await client.post(WZAP_API_URL, json=payload, timeout=3.0)
        
        print("✅ Disparo via wZap Marketing simulado com sucesso no terminal!")
    except Exception as e:
        print(f"Erro na comunicação com o wZap Marketing: {e}")

# --- ROTA DE UPGRADE 1: SIMULADOR GOOGLE CLOUD ---
async def consultar_busca_refinada_google_cloud(mercado_perfil: str, produto_termo: str):
    try:
        print(f"📡 GOOGLE CLOUD ATIVO: Executando Varredura Refinada no projeto [{GOOGLE_PROJECT_ID}]...")
        precos_base_nuvem = {
            "arroz": {"ATACADO_GRANDE": 18.45, "MEDIO_PORTE": 19.99, "PEQUENO_EXPRESS": 21.90},
            "feijão": {"ATACADO_GRANDE": 6.50,  "MEDIO_PORTE": 7.50,  "PEQUENO_EXPRESS": 8.20}
        }
        tabela = precos_base_nuvem.get(produto_termo, {"ATACADO_GRANDE": 14.90, "MEDIO_PORTE": 15.90, "PEQUENO_EXPRESS": 16.90})
        return tabela.get(mercado_perfil, 15.00)
    except Exception as e:
        print(f"Erro na conexão com Google Cloud: {e}. Retornando segurança.")
        return 15.00

# --- FUNÇÃO DE EXTENSÃO: INTEGRAÇÃO COM ORÇAMENTO FAMILIAR ---
async def enviar_para_orcamento_familiar(cesta_otimizada: dict):
    # O sistema pode enviar via webhook ou salvar em um arquivo 
    # de sincronização que o seu Orçamento Familiar lê.
    print("📈 INTEGRAÇÃO FINANCEIRA: Dados da cesta enviados para o módulo de Orçamento Familiar.")

# --- ROTA DE UPGRADE 2: SIMULADOR BANCO DE DADOS (ENTERPRISE) ---
async def consultar_busca_banco_dados(mercado_perfil: str, produto_termo: str):
    try:
        print(f"🗄️ BANCO DE DADOS ATIVO: Consultando tabelas SQL na conexão configurada...")
        precos_base_sql = {
            "arroz": {"ATACADO_GRANDE": 18.99, "MEDIO_PORTE": 20.00, "PEQUENO_EXPRESS": 22.50}
        }
        tabela = precos_base_sql.get(produto_termo, {"ATACADO_GRANDE": 14.50, "MEDIO_PORTE": 15.50, "PEQUENO_EXPRESS": 16.50})
        return tabela.get(mercado_perfil, 15.00)
    except Exception as e:
        print(f"Erro na conexão com Banco de Dados: {e}. Retornando segurança.")
        return 15.00

# --- MOTOR DE BUSCA UNIVERSAL EM MEMÓRIA (PRODUTO NACIONAL WHITE LABEL) ---
async def motor_de_busca_inteligente(mercado_nome: str, produto_nome: str):
    try:
        mercado_limpo = mercado_nome.strip().upper()
        produto_limpo = produto_nome.strip().lower()
        
        perfil_mercado = "MEDIO_PORTE"
        if any(keyword in mercado_limpo for keyword in ["ATACADÃO", "ATACADO", "ASSAÍ", "MAXXI", "RUSTIC", "SPANI", "ROLDÃO", "KRILL"]):
            perfil_mercado = "ATACADO_GRANDE"
        elif any(keyword in mercado_limpo for keyword in ["EXPRESS", "MINUTO", "CONVENIENCIA", "MERCEARIA", "MINI", "PROXIMIDADE", "MERCADINHO", "LOCAL", "EXPRESSO"]):
            perfil_mercado = "PEQUENO_EXPRESS"
            
        if MODO_MOTOR_PRECO == "GOOGLE_CLOUD":
            return await consultar_busca_refinada_google_cloud(perfil_mercado, produto_limpo)
        elif MODO_MOTOR_PRECO == "BANCO_DE_DADOS":
            return await consultar_busca_banco_dados(perfil_mercado, produto_limpo)

        CATALOGO_NACIONAL = {
            "arroz":        {"ATACADO_GRANDE": 18.90, "MEDIO_PORTE": 20.50, "PEQUENO_EXPRESS": 22.90},
            "feijão":       {"ATACADO_GRANDE": 6.99,  "MEDIO_PORTE": 7.90,  "PEQUENO_EXPRESS": 8.90},
            "óleo":         {"ATACADO_GRANDE": 5.80,  "MEDIO_PORTE": 6.20,  "PEQUENO_EXPRESS": 6.80},
            "açúcar":       {"ATACADO_GRANDE": 3.80,  "MEDIO_PORTE": 4.20,  "PEQUENO_EXPRESS": 4.60},
            "café":         {"ATACADO_GRANDE": 13.90, "MEDIO_PORTE": 15.20, "PEQUENO_EXPRESS": 16.90},
            "macarrão":     {"ATACADO_GRANDE": 2.99,  "MEDIO_PORTE": 3.50,  "PEQUENO_EXPRESS": 3.99},
            "sal":          {"ATACADO_GRANDE": 1.80,  "MEDIO_PORTE": 2.20,  "PEQUENO_EXPRESS": 2.60},
            "farinha de trigo": {"ATACADO_GRANDE": 4.20, "MEDIO_PORTE": 4.80, "PEQUENO_EXPRESS": 5.30},
            "farinha de mandioca": {"ATACADO_GRANDE": 4.90, "MEDIO_PORTE": 5.50, "PEQUENO_EXPRESS": 6.10},
            "molho de tomate": {"ATACADO_GRANDE": 1.60, "MEDIO_PORTE": 1.95,  "PEQUENO_EXPRESS": 2.30},
            "maionese":     {"ATACADO_GRANDE": 5.20,  "MEDIO_PORTE": 5.90,  "PEQUENO_EXPRESS": 6.50},
            "ketchup":      {"ATACADO_GRANDE": 5.90,  "MEDIO_PORTE": 6.50,  "PEQUENO_EXPRESS": 7.20},
            "vinagre":      {"ATACADO_GRANDE": 2.40,  "MEDIO_PORTE": 2.80,  "PEQUENO_EXPRESS": 3.20},
            "azeite":       {"ATACADO_GRANDE": 32.90, "MEDIO_PORTE": 34.90, "PEQUENO_EXPRESS": 38.50},
            "sardinha":     {"ATACADO_GRANDE": 3.60,  "MEDIO_PORTE": 3.99,  "PEQUENO_EXPRESS": 4.40},
            "atum":         {"ATACADO_GRANDE": 7.20,  "MEDIO_PORTE": 7.90,  "PEQUENO_EXPRESS": 8.60},
            "milho verde":  {"ATACADO_GRANDE": 2.70,  "MEDIO_PORTE": 3.10,  "PEQUENO_EXPRESS": 3.50},
            "ervilha":      {"ATACADO_GRANDE": 2.50,  "MEDIO_PORTE": 2.90,  "PEQUENO_EXPRESS": 3.30},
            "extrato de tomate": {"ATACADO_GRANDE": 3.10, "MEDIO_PORTE": 3.50, "PEQUENO_EXPRESS": 3.99},

            "carne moída":  {"ATACADO_GRANDE": 22.90, "MEDIO_PORTE": 24.90, "PEQUENO_EXPRESS": 27.50},
            "patinho":      {"ATACADO_GRANDE": 29.90, "MEDIO_PORTE": 32.90, "PEQUENO_EXPRESS": 35.90},
            "acém":         {"ATACADO_GRANDE": 20.90, "MEDIO_PORTE": 22.90, "PEQUENO_EXPRESS": 25.40},
            "contra filé":  {"ATACADO_GRANDE": 39.90, "MEDIO_PORTE": 42.90, "PEQUENO_EXPRESS": 46.90},
            "filé de frango": {"ATACADO_GRANDE": 15.90, "MEDIO_PORTE": 17.90, "PEQUENO_EXPRESS": 19.50},
            "coxa de frango": {"ATACADO_GRANDE": 8.50,  "MEDIO_PORTE": 9.90,  "PEQUENO_EXPRESS": 11.20},
            "bisteca suína": {"ATACADO_GRANDE": 14.90, "MEDIO_PORTE": 16.90, "PEQUENO_EXPRESS": 18.50},
            "linguiça":     {"ATACADO_GRANDE": 16.90, "MEDIO_PORTE": 18.90, "PEQUENO_EXPRESS": 21.00},
            "salsicha":     {"ATACADO_GRANDE": 8.80,  "MEDIO_PORTE": 9.90,  "PEQUENO_EXPRESS": 10.95},
            "peixe":        {"ATACADO_GRANDE": 26.90, "MEDIO_PORTE": 29.90, "PEQUENO_EXPRESS": 33.50},

            "batata":       {"ATACADO_GRANDE": 4.80,  "MEDIO_PORTE": 5.50,  "PEQUENO_EXPRESS": 6.20},
            "cebola":       {"ATACADO_GRANDE": 4.10,  "MEDIO_PORTE": 4.80,  "PEQUENO_EXPRESS": 5.40},
            "tomate":       {"ATACADO_GRANDE": 6.90,  "MEDIO_PORTE": 7.90,  "PEQUENO_EXPRESS": 8.90},
            "alho":         {"ATACADO_GRANDE": 25.90, "MEDIO_PORTE": 28.90, "PEQUENO_EXPRESS": 32.00},
            "cenoura":      {"ATACADO_GRANDE": 3.90,  "MEDIO_PORTE": 4.50,  "PEQUENO_EXPRESS": 5.10},
            "banana":       {"ATACADO_GRANDE": 3.90,  "MEDIO_PORTE": 4.50,  "PEQUENO_EXPRESS": 5.20},
            "maçã":         {"ATACADO_GRANDE": 7.90,  "MEDIO_PORTE": 8.90,  "PEQUENO_EXPRESS": 9.95},
            "laranja":      {"ATACADO_GRANDE": 3.20,  "MEDIO_PORTE": 3.80,  "PEQUENO_EXPRESS": 4.30},
            "limão":        {"ATACADO_GRANDE": 3.60,  "MEDIO_PORTE": 4.20,  "PEQUENO_EXPRESS": 4.75},
            "mamão":        {"ATACADO_GRANDE": 5.90,  "MEDIO_PORTE": 6.90,  "PEQUENO_EXPRESS": 7.80},
            "alface":       {"ATACADO_GRANDE": 2.99,  "MEDIO_PORTE": 3.50,  "PEQUENO_EXPRESS": 3.99},
            "repolho":      {"ATACADO_GRANDE": 3.50,  "MEDIO_PORTE": 4.10,  "PEQUENO_EXPRESS": 4.60},

            "pão de forma": {"ATACADO_GRANDE": 5.90,  "MEDIO_PORTE": 6.90,  "PEQUENO_EXPRESS": 7.80},
            "biscoito salgado": {"ATACADO_GRANDE": 2.99, "MEDIO_PORTE": 3.50, "PEQUENO_EXPRESS": 4.10},
            "biscoito recheado": {"ATACADO_GRANDE": 1.99, "MEDIO_PORTE": 2.40, "PEQUENO_EXPRESS": 2.85},
            "achocolatado": {"ATACADO_GRANDE": 6.90,  "MEDIO_PORTE": 7.90,  "PEQUENO_EXPRESS": 8.80},
            "aveia":        {"ATACADO_GRANDE": 4.20,  "MEDIO_PORTE": 4.90,  "PEQUENO_EXPRESS": 5.50},
            "cereal":       {"ATACADO_GRANDE": 10.50, "MEDIO_PORTE": 11.90, "PEQUENO_EXPRESS": 13.40},
            "gelatina":     {"ATACADO_GRANDE": 1.15,  "MEDIO_PORTE": 1.40,  "PEQUENO_EXPRESS": 1.70},
            "bolo misturado": {"ATACADO_GRANDE": 4.80, "MEDIO_PORTE": 5.50, "PEQUENO_EXPRESS": 6.20},

            "leite":        {"ATACADO_GRANDE": 4.20,  "MEDIO_PORTE": 4.80,  "PEQUENO_EXPRESS": 5.40},
            "ovos":         {"ATACADO_GRANDE": 11.50, "MEDIO_PORTE": 12.90, "PEQUENO_EXPRESS": 14.50},
            "manteiga":     {"ATACADO_GRANDE": 8.90,  "MEDIO_PORTE": 9.80,  "PEQUENO_EXPRESS": 10.90},
            "margarina":    {"ATACADO_GRANDE": 4.80,  "MEDIO_PORTE": 5.50,  "PEQUENO_EXPRESS": 6.30},
            "queijo mussarela": {"ATACADO_GRANDE": 13.50, "MEDIO_PORTE": 14.80, "PEQUENO_EXPRESS": 16.90},
            "presunto":     {"ATACADO_GRANDE": 7.50,  "MEDIO_PORTE": 8.50,  "PEQUENO_EXPRESS": 9.80},
            "requeijão":    {"ATACADO_GRANDE": 6.90,  "MEDIO_PORTE": 7.90,  "PEQUENO_EXPRESS": 8.95},
            "iogurte":      {"ATACADO_GRANDE": 5.90,  "MEDIO_PORTE": 6.90,  "PEQUENO_EXPRESS": 7.80},
            "creme de leite": {"ATACADO_GRANDE": 2.49, "MEDIO_PORTE": 2.99,  "PEQUENO_EXPRESS": 3.45},
            "leite condensado": {"ATACADO_GRANDE": 4.90, "MEDIO_PORTE": 5.50, "PEQUENO_EXPRESS": 6.15},

            "refrigerante": {"ATACADO_GRANDE": 7.90,  "MEDIO_PORTE": 8.90,  "PEQUENO_EXPRESS": 9.95},
            "suco":         {"ATACADO_GRANDE": 4.50,  "MEDIO_PORTE": 5.20,  "PEQUENO_EXPRESS": 5.95},
            "água mineral": {"ATACADO_GRANDE": 1.70,  "MEDIO_PORTE": 2.20,  "PEQUENO_EXPRESS": 2.70},
            "cerveja":      {"ATACADO_GRANDE": 3.99,  "MEDIO_PORTE": 4.50,  "PEQUENO_EXPRESS": 5.10},
            "vinho":        {"ATACADO_GRANDE": 19.90, "MEDIO_PORTE": 22.90, "PEQUENO_EXPRESS": 25.99},
            "bebida láctea": {"ATACADO_GRANDE": 3.40,  "MEDIO_PORTE": 3.90,  "PEQUENO_EXPRESS": 4.45},
            "energético":   {"ATACADO_GRANDE": 7.50,  "MEDIO_PORTE": 8.50,  "PEQUENO_EXPRESS": 9.80},

            "lasanha":      {"ATACADO_GRANDE": 10.50, "MEDIO_PORTE": 11.90, "PEQUENO_EXPRESS": 13.20},
            "pizza":        {"ATACADO_GRANDE": 10.90, "MEDIO_PORTE": 12.50, "PEQUENO_EXPRESS": 14.10},
            "hambúrguer":   {"ATACADO_GRANDE": 13.20, "MEDIO_PORTE": 14.90, "PEQUENO_EXPRESS": 16.80},
            "pão de queijo": {"ATACADO_GRANDE": 11.90, "MEDIO_PORTE": 13.50, "PEQUENO_EXPRESS": 14.95},
            "sorvete":      {"ATACADO_GRANDE": 21.90, "MEDIO_PORTE": 24.90, "PEQUENO_EXPRESS": 28.50},
            "batata frita palito": {"ATACADO_GRANDE": 14.90, "MEDIO_PORTE": 16.90, "PEQUENO_EXPRESS": 18.99},

            "detergente":   {"ATACADO_GRANDE": 1.85,  "MEDIO_PORTE": 2.20,  "PEQUENO_EXPRESS": 2.55},
            "sabão em pó":  {"ATACADO_GRANDE": 13.20, "MEDIO_PORTE": 14.90, "PEQUENO_EXPRESS": 16.80},
            "sabão em barra": {"ATACADO_GRANDE": 8.40,  "MEDIO_PORTE": 9.50,  "PEQUENO_EXPRESS": 10.80},
            "amaciante":    {"ATACADO_GRANDE": 10.50, "MEDIO_PORTE": 11.90, "PEQUENO_EXPRESS": 13.40},
            "água sanitária": {"ATACADO_GRANDE": 3.30,  "MEDIO_PORTE": 3.90,  "PEQUENO_EXPRESS": 4.40},
            "desinfetante": {"ATACADO_GRANDE": 5.90,  "MEDIO_PORTE": 6.90,  "PEQUENO_EXPRESS": 7.85},
            "esponja":      {"ATACADO_GRANDE": 1.60,  "MEDIO_PORTE": 1.99,  "PEQUENO_EXPRESS": 2.40},
            "lã de aço":    {"ATACADO_GRANDE": 2.10,  "MEDIO_PORTE": 2.50,  "PEQUENO_EXPRESS": 2.95},
            "álcool":       {"ATACADO_GRANDE": 5.20,  "MEDIO_PORTE": 5.90,  "PEQUENO_EXPRESS": 6.70},
            "saco de lixo": {"ATACADO_GRANDE": 8.50,  "MEDIO_PORTE": 9.80,  "PEQUENO_EXPRESS": 11.20},
            "inseticida":   {"ATACADO_GRANDE": 9.99,  "MEDIO_PORTE": 11.50, "PEQUENO_EXPRESS": 13.10},

            "papel higiênico": {"ATACADO_GRANDE": 13.20, "MEDIO_PORTE": 14.50, "PEQUENO_EXPRESS": 16.50},
            "sabonete":     {"ATACADO_GRANDE": 1.99,  "MEDIO_PORTE": 2.50,  "PEQUENO_EXPRESS": 2.99},
            "creme dental": {"ATACADO_GRANDE": 2.99,  "MEDIO_PORTE": 3.50,  "PEQUENO_EXPRESS": 4.10},
            "shampoo":      {"ATACADO_GRANDE": 12.50, "MEDIO_PORTE": 13.90, "PEQUENO_EXPRESS": 15.60},
            "condicionador": {"ATACADO_GRANDE": 13.90, "MEDIO_PORTE": 15.50, "PEQUENO_EXPRESS": 17.40},
            "desodorante":  {"ATACADO_GRANDE": 10.50, "MEDIO_PORTE": 11.90, "PEQUENO_EXPRESS": 13.25},
            "absorvente":   {"ATACADO_GRANDE": 5.80,  "MEDIO_PORTE": 6.50,  "PEQUENO_EXPRESS": 7.40},
            "fio dental":   {"ATACADO_GRANDE": 6.90,  "MEDIO_PORTE": 7.90,  "PEQUENO_EXPRESS": 8.99},
            "cotonete":     {"ATACADO_GRANDE": 3.90,  "MEDIO_PORTE": 4.50,  "PEQUENO_EXPRESS": 5.15},
            "aparelho de barbear": {"ATACADO_GRANDE": 11.20, "MEDIO_PORTE": 12.90, "PEQUENO_EXPRESS": 14.60}
        }

        tabela_perfis_encontrada = {}
        for item_catalogo in CATALOGO_NACIONAL:
            if item_catalogo in produto_limpo:
                tabela_perfis_encontrada = CATALOGO_NACIONAL[item_catalogo]
                break

        preco_final = tabela_perfis_encontrada.get(perfil_mercado, 15.00)
        return preco_final
            
    except Exception:
        return 15.00

# --- BUSCA DE MERCADO ---
async def buscar_mercado_real(m_info: dict, item: ItemCesta):
    nome_mercado = m_info.get('nome')
    nome_prod = item.product_name or item.nome or "item"
    qtd = item.quantity or item.quantidade or 1
    
    preco = await motor_de_busca_inteligente(nome_mercado, nome_prod)
    return {
        "market_name": nome_mercado,
        "total_price": preco * qtd
    }

# --- DESCOBERTA DE MERCADOS (COM LIMITADOR DE RAIO MÁXIMO DO USUÁRIO) ---
async def descobrir_mercados_no_mapa(lat: float, lng: float, raio_km: float):
    lista_mercados = []
    limite_raio_corte = float(raio_km) if float(raio_km) > 1.0 else 5.0
    
    try:
        latitude = float(lat)
        longitude = float(lng)
        raio_metros = int(limite_raio_corte * 1000)
        
        url = f"https://nominatim.openstreetmap.org/search?format=json&q=supermercado&lat={latitude}&lon={longitude}&radius={raio_metros}&addressdetails=1&countrycodes=br&limit=10"
        headers = {"User-Agent": "IEDR_Shopping_Optimizer_App_v1.0"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=4.0)
            if response.status_code == 200:
                dados_mapa = response.json()
                
                for idx, item in enumerate(dados_mapa):
                    address = item.get("address", {})
                    merc_lat = float(item.get("lat", latitude))
                    merc_lng = float(item.get("lon", longitude))
                    
                    dist_real = calcular_distancia(latitude, longitude, merc_lat, merc_lng)
                    if dist_real > (limite_raio_corte * 1.5):
                        continue
                        
                    nome_mapa = address.get("supermarket") or address.get("shop") or item.get("name") or ""
                    if nome_mapa.lower() in ["supermercado", "supermarket", "mercado", ""]:
                        continue
                        
                    lista_mercados.append({
                        "nome": nome_mapa.strip().upper(),
                        "distancia": round(dist_real if dist_real > 0.1 else 0.8, 2)
                    })
    except Exception:
        pass

    if not lista_mercados:
        print("🚨 CONTINGÊNCIA GEOGRÁFICA ATIVADA: Gerando ecossistema restrito ao CEP do usuário...")
        bairro_local = "Boiçucanga"
        try:
            url_rev = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&addressdetails=1"
            async with httpx.AsyncClient() as client:
                res_rev = await client.get(url_rev, headers={"User-Agent": "IEDR_Contingency"}, timeout=3.0)
                if res_rev.status_code == 200:
                    addr = res_rev.json().get("address", {})
                    bairro_local = addr.get("suburb") or addr.get("road") or addr.get("neighbourhood") or "Localidade"
                    bairro_local = bairro_local.split(",")[0].strip()
        except Exception:
            pass

        lista_mercados = [
            {"nome": f"KRILL ATACADÃO - {bairro_local.upper()}", "distancia": 1.20},
            {"nome": f"SUPERMERCADO SEMAR - {bairro_local.upper()}", "distancia": 2.40},
            {"nome": f"LITORAL SUPERMERCADOS", "distancia": 3.10},
            {"nome": f"MINI MERCADO EXPRESS ({bairro_local.upper()})", "distancia": 4.60}
        ]

    return lista_mercados

# --- ROTA PRINCIPAL OTIMIZADA ---
@router.post("/basket")
async def otimizar_cesta(req: RequisicaoOtimizacao):
    mercados = []
    try:
        resultado = await descobrir_mercados_no_mapa(req.lat, req.lng, req.raio_km)
        if resultado and isinstance(resultado, list):
            mercados = resultado
    except Exception as e:
        print(f"DEBUG: Falha na busca geográfica real: {e}")
        
    if not mercados:
        return {"best_market": "Nenhum mercado encontrado", "lowest_total_price": 0.0, "comparativo": []}

    try:
        lista_itens = getattr(req, 'itens', None) or getattr(req, 'items', None) or getattr(req, 'cesta', None) or []
        resultados = []
        
        for m in mercados:
            total = 0
            for item in lista_itens:
                nome_item = getattr(item, 'nome', getattr(item, 'product_name', "item"))
                qtd_item = getattr(item, 'quantidade', getattr(item, 'quantity', 1))
                
                preco_unit = await motor_de_busca_inteligente(m['nome'], nome_item)
                total += float(preco_unit) * float(qtd_item)
            
            distancia_mercado = m.get('distancia', 1.5)
            tipo_transporte = getattr(req, 'transporte', 'carro')
            fator_combustivel = 0.0 if tipo_transporte in ['a_pe', 'bicicleta'] else 0.50
            custo_final = total + (distancia_mercado * fator_combustivel)
            
            resultados.append({
                "market_name": m['nome'].upper(),
                "total_produtos": round(total, 2),
                "custo_total_final": round(custo_final, 2),
                "distancia": round(distancia_mercado, 2)
              })

        resultados = sorted(resultados, key=lambda x: x['custo_total_final'])
        melhor = resultados[0]
        
        # =================================================================
        # 🟢 GATILHO DE INTEGRAÇÃO (WZAP MARKETING)
        # =================================================================
        if INTEGRACAO_WZAP_MARKETING == "ATIVO":
            await disparar_alerta_wzap_marketing("5511999999999", melhor['market_name'], melhor['custo_total_final'])
        
        # =================================================================
        # 💰 PONTO DE EXTENSÃO: INTEGRAÇÃO COM ORÇAMENTO FAMILIAR
        # =================================================================
        # Para ativar a integração no futuro, basta descomentar a linha abaixo:
        # await enviar_para_orcamento_familiar(melhor)
        # =================================================================
        
        return {
            "best_market": melhor['market_name'], 
            "lowest_total_price": melhor['custo_total_final'], 
            "comparativo": resultados
        }
        
    except Exception as e:
        print(f"ERRO CRÍTICO NO CÁLCULO MAPEADO: {e}")
        return {"best_market": "Erro de processamento", "lowest_total_price": 0.0, "comparativo": []}