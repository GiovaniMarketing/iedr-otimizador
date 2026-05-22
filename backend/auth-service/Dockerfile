FROM python:3.11-slim

WORKDIR /app

# Removemos o apt-get install (já que não precisamos mais de drivers de banco)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Sem o --reload, a API fica mais estável e rápida para produção/testes externos
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]