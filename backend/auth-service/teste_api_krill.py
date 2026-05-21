from curl_cffi import requests
import json

def buscar_produtos_krill(termo_busca):
    # A URL agora é DINÂMICA. O termo_busca entra no meio do link!
    url = f"https://services.vipcommerce.com.br/api-admin/v1/org/216/filial/1/centro_distribuicao/1/loja/buscas/produtos/termo/{termo_busca}?page=1"
    
    headers = {
        "accept": "application/json",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJ2aXBjb21tZXJjZSIsImF1ZCI6ImFwaS1hZG1pbiIsInN1YiI6IjZiYzQ4NjdlLWRjYTktMTFlOS04NzQyLTAyMGQ3OTM1OWNhMCIsInZpcGNvbW1lcmNlQ2xpZW50ZUlkIjpudWxsLCJpYXQiOjE3Nzg0NDE0MTYsInZlciI6MSwiY2xpZW50IjpudWxsLCJvcGVyYXRvciI6bnVsbCwib3JnIjoiMjE2In0.T38rayl1gtBrvzR1a8nMB_yc98YkrEmjtLBl0M_W1cVY13Zlz9LMEJ_JCjGpaHwbhpx6P2inE6B_sWssalkfog",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "domainkey": "lojasredekrill.com.br",
        "organizationid": "216",
        "origin": "https://www.lojasredekrill.com.br",
        "pragma": "no-cache",
        "referer": "https://www.lojasredekrill.com.br/",
        "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sessao-id": "a311f12e31bd8ec5b758e0f1803555ae",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    }
    
    print(f"🚀 Buscando preços ao vivo para: {termo_busca.upper()}...")
    
    try:
        response = requests.get(url, headers=headers, impersonate="chrome120", timeout=15)
        
        if response.status_code == 200:
            dados_brutos = response.json()
            
            # --- O PENTE FINO COMEÇA AQUI ---
            # Entramos em "data" e depois em "produtos". Se não existir, retorna lista vazia []
            lista_produtos = dados_brutos.get("data", {}).get("produtos", [])
            
            produtos_limpos = []
            
            for item in lista_produtos:
                # Só pegamos o produto se ele estiver em estoque (disponivel = true)
                if item.get("disponivel") == True:
                    nome = item.get("descricao")
                    # O preço vem como texto ("19.99"), transformamos em float (19.99) para cálculos
                    preco = float(item.get("preco", 0)) 
                    
                    produtos_limpos.append({
                        "nome": nome,
                        "preco": preco
                    })
                    
            return produtos_limpos
            
        else:
            print(f"❌ Acesso Negado (Status: {response.status_code})")
            return []
            
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")
        return []

# ==========================================
# TESTANDO O MOTOR DO IEDR NA PRÁTICA
# ==========================================

print("-" * 50)
print("  TABELA DE PREÇOS KRILL - IEDR  ")
print("-" * 50)

# Vamos testar com Arroz e depois com Feijão
itens_para_buscar = ["arroz", "feijao", "leite"]

for item in itens_para_buscar:
    resultados = buscar_produtos_krill(item)
    
    print(f"\n🛒 Categoria: {item.upper()}")
    for produto in resultados:
        # Imprime formatado com R$ e alinhamento
        print(f"R$ {produto['preco']:>5.2f} | {produto['nome']}")

print("\n" + "-" * 50)
print("✅ Extração concluída. Prontos para salvar no Banco de Dados!")