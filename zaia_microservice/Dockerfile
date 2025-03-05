FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.zaia_agents.main:app", "--host", "0.0.0.0", "--port", "8000"]
