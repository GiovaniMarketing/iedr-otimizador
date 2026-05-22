# app/db/session.py

# Como não vamos mais usar o banco de dados SQL, 
# esta função serve apenas para manter a compatibilidade 
# caso algum import no seu código ainda a chame.

async def get_db():
    # Retorna None ou uma sessão vazia para evitar que o código quebre
    yield None 
    
# Se o seu código em algum lugar exigir 'engine' ou 'SessionLocal', 
# apenas defina-os como None ou remova o import desses objetos 
# dos arquivos optimizer.py e pricing.py.