FROM python:3.9-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cria diretórios para os dados
RUN mkdir -p /app/td_db /app/td_files

# Copia apenas os arquivos necessários primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos
COPY . .

# Expõe a porta usada pela aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "app.py"] 