import os
import csv
from datetime import datetime
from curl_cffi import requests

def coletar_precos_krill():
    # 1. O que vamos buscar e o que vamos IGNORAR (O Filtro de Precisão)
    buscas = {
        "arroz": ["canino", "biscoito", "pronto", "bolinho", "integral", "organico"],
        "feijao": ["pronto", "feijoada", "sazon", "macarrao", "sache", "temperado", "bordon"],
        "leite": ["fermentado", "condensado", "po", "coco", "creme", "doce"]
    }
    
    # 2. Configurando o arquivo CSV onde os dados serão salvos
    # Ele vai salvar um arquivo com a data de hoje, ex: precos_krill_19-05-2026.csv
    data_hoje = datetime.now().strftime("%d-%m-%Y")
    
    # Volta uma pasta (para sair de 'scripts') e entra na pasta 'dados'
    caminho_pasta_dados = os.path.join(os.path.dirname(__file__), 'dados')
    
    # Cria a pasta 'dados' se você esquecer de criar manualmente
    os.makedirs(caminho_pasta_dados, exist_ok=True)
    
    caminho_arquivo_csv = os.path.join(caminho_pasta_dados, f'precos_krill_{data_hoje}.csv')
    
    # 3. Preparando o CSV
    with open(caminho_arquivo_csv, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv, delimiter=';')
        # Escrevendo o cabeçalho da tabela
        escritor.writerow(['Data', 'Categoria', 'Produto', 'Preço (R$)'])
        
        # O disfarce do Chrome
        headers = {
            "accept": "application/json",
            "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJ2aXBjb21tZXJjZSIsImF1ZCI6ImFwaS1hZG1pbiIsInN1YiI6IjZiYzQ4NjdlLWRjYTktMTFlOS04NzQyLTAyMGQ3OTM1OWNhMCIsInZpcGNvbW1lcmNlQ2xpZW50ZUlkIjpudWxsLCJpYXQiOjE3Nzg0NDE0MTYsInZlciI6MSwiY2xpZW50IjpudWxsLCJvcGVyYXRvciI6bnVsbCwib3JnIjoiMjE2In0.T38rayl1gtBrvzR1a8nMB_yc98YkrEmjtLBl0M_W1cVY13Zlz9LMEJ_JCjGpaHwbhpx6P2inE6B_sWssalkfog",
            "domainkey": "lojasredekrill.com.br",
            "organizationid": "216",
            "origin": "https://www.lojasredekrill.com.br",
            "sessao-id": "a311f12e31bd8ec5b758e0f1803555ae",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        }
        
        print(f"🚀 Iniciando varredura IEDR (Data: {data_hoje})...")
        
        # 4. Rodando a busca para cada categoria (Arroz, Feijão, Leite)
        for categoria, palavras_proibidas in buscas.items():
            print(f"🔎 Vasculhando corredor de: {categoria.upper()}...")
            
            url = f"https://services.vipcommerce.com.br/api-admin/v1/org/216/filial/1/centro_distribuicao/1/loja/buscas/produtos/termo/{categoria}?page=1"
            
            try:
                response = requests.get(url, headers=headers, impersonate="chrome120", timeout=15)
                
                if response.status_code == 200:
                    dados_brutos = response.json()
                    lista_produtos = dados_brutos.get("data", {}).get("produtos", [])
                    
                    produtos_salvos = 0
                    
                    for item in lista_produtos:
                        if item.get("disponivel") == True:
                            nome_produto = item.get("descricao")
                            nome_minusculo = nome_produto.lower()
                            
                            # O FILTRO DE PRECISÃO: Verifica se tem palavra proibida no nome
                            tem_palavra_proibida = any(palavra in nome_minusculo for palavra in palavras_proibidas)
                            
                            if not tem_palavra_proibida:
                                preco = float(item.get("preco", 0))
                                
                                # Salvando a linha no CSV
                                escritor.writerow([data_hoje, categoria.upper(), nome_produto, preco])
                                produtos_salvos += 1
                                
                    print(f"   ✅ {produtos_salvos} produtos válidos salvos.")
                else:
                    print(f"   ❌ Erro ao acessar. Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   🔥 Erro de conexão: {e}")

    print("\n" + "=" * 50)
    print(f"🎉 SUCESSO! Tabela salva em: {caminho_arquivo_csv}")
    print("=" * 50)

# Inicia o robô
coletar_precos_krill()