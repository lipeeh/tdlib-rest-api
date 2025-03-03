FROM python:3.9-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo \
    DEBIAN_FRONTEND=noninteractive

# Instalar pacotes básicos e dependências da TDLib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gperf \
    git \
    libssl-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de aplicação
WORKDIR /app

# Criar diretórios para dados da TDLib
RUN mkdir -p /app/td_db /app/td_files /app/uploads

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos da aplicação
COPY . .

# Porta da aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "main.py"] 