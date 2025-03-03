from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import uvicorn
import os
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Importa os roteadores
from app.api import users, chats, messages, auth

# Cria a aplicação FastAPI
app = FastAPI(
    title="Telegram TDLib API",
    description="API REST para integração com o Telegram via TDLib",
    version="1.0.0"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona os roteadores
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(users.router, prefix="/users", tags=["Usuários"])
app.include_router(chats.router, prefix="/chats", tags=["Chats"])
app.include_router(messages.router, prefix="/messages", tags=["Mensagens"])

# Rota de verificação de saúde
@app.get("/health", tags=["Sistema"])
async def health_check():
    return {"status": "ok", "message": "API está funcionando corretamente"}

# Rota inicial
@app.get("/", tags=["Sistema"])
async def root():
    return {
        "message": "Bem-vindo à API Telegram TDLib",
        "documentation": "/docs",
        "redoc": "/redoc"
    }

# Função para inicializar o cliente TDLib
async def initialize_tdlib():
    from app.core.tdlib_wrapper import initialize_client
    print("Inicializando cliente TDLib...")
    await initialize_client()
    print("Cliente TDLib inicializado com sucesso!")

# Função principal
if __name__ == "__main__":
    # Cria e inicia os diretórios necessários
    os.makedirs(os.environ.get("TD_DATABASE_DIRECTORY", "./td_db"), exist_ok=True)
    os.makedirs(os.environ.get("TD_FILES_DIRECTORY", "./td_files"), exist_ok=True)
    
    # Inicializa o cliente TDLib em um novo evento de loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_tdlib())
    
    # Inicia o servidor Uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=bool(os.environ.get("DEBUG", "False") == "True")) 