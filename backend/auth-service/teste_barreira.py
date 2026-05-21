from curl_cffi import requests
import json

def extrair_api_krill_ninja():
    url = "https://services.vipcommerce.com.br/ws/loja/paginas/index/1"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.lojasredekrill.com.br",
        "Referer": "https://www.lojasredekrill.com.br/",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    
    print("🚀 Injetando requisição camuflada na VIPCommerce...")
    
    try:
        # A camuflagem pesada que engana o Cloudflare
        response = requests.get(url, headers=headers, impersonate="chrome120", timeout=15)
        
        if response.status_code == 200:
            print("✅ SUCESSO ABSOLUTO! O cofre foi aberto.")
            try:
                dados = response.json()
                with open("tesouro_krill.json", 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=4)
                print("📦 DADOS CAPTURADOS! Verifique o arquivo 'tesouro_krill.json'.")
            except:
                print("⚠️ Retornou 200, mas não é JSON.")
        else:
            print(f"❌ Acesso Negado (Status: {response.status_code})")
            
    except Exception as e:
        print(f"🔥 Erro: {e}")

extrair_api_krill_ninja()