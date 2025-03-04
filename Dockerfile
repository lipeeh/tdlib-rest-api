FROM python:3.9-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    TD_DATABASE_DIRECTORY=/app/td_db \
    TD_FILES_DIRECTORY=/app/td_files \
    UPLOAD_FOLDER=/app/uploads \
    LOG_FILE=/app/logs/telegram_api.log

# Criar diretório de trabalho
WORKDIR /app

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

# Criar diretórios para dados da TDLib e logs
RUN mkdir -p /app/td_db /app/td_files /app/uploads /app/logs

# Copiar requirements.txt primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código-fonte da aplicação
COPY . .

# Verificar a existência de bibliotecas críticas
RUN pip list | grep -E "waitress|flask|python-telegram|pytdlib" || echo "AVISO: Uma ou mais bibliotecas importantes podem estar faltando"

# Porta da aplicação
EXPOSE 8000

# Informação sobre a imagem
LABEL maintainer="Desenvolvedor <dev@exemplo.com>" \
      version="1.0" \
      description="API Telegram usando TDLib"

# Verificações de saúde (para Docker Compose/Kubernetes)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando para iniciar a aplicação
CMD ["python", "main.py"] 