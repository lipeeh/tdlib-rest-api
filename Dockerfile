FROM python:3.9-slim

# Instala dependências para o TDLib e outras ferramentas
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gperf \
    ccache \
    libssl-dev \
    zlib1g-dev \
    curl \
    git \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala o td
RUN git clone https://github.com/tdlib/td.git && \
    cd td && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build . -j4 && \
    make install && \
    cd ../.. && \
    rm -rf td

WORKDIR /app

# Copia apenas os arquivos necessários primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cria diretórios para os dados da TDLib
RUN mkdir -p /app/td_db /app/td_files

# Copia o restante dos arquivos
COPY . .

# Expõe a porta usada pela aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "app.py"] 