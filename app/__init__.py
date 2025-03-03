# Pacote app 

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
import uvicorn
import os
import asyncio
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Importa os roteadores
from app.api import users, chats, messages, auth, files, auth_telegram

# Cria a aplicação FastAPI
app = FastAPI(
    title="Telegram TDLib API",
    description="""API REST para integração com o Telegram via TDLib.
    
    Esta API permite interagir com o Telegram usando a biblioteca TDLib, fornecendo
    endpoints para autenticação, gerenciamento de mensagens, chats, usuários e arquivos.
    
    ## Funcionalidades Principais
    
    * **Autenticação**: Login com número de telefone e código de verificação
    * **Mensagens**: Envio, recebimento, encaminhamento e exclusão de mensagens
    * **Chats**: Gerenciamento de conversas individuais e grupos
    * **Usuários**: Busca, informações de perfil e contatos
    * **Arquivos**: Upload e download de mídias
    
    ## Como usar
    
    1. Obtenha um token JWT através do endpoint `/auth/token`
    2. Use o token para autenticar solicitações às rotas protegidas
    3. Se necessário, configure o cliente Telegram através dos endpoints em `/auth/telegram`
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json"
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
app.include_router(auth_telegram.router, prefix="/auth/telegram", tags=["Autenticação Telegram"])
app.include_router(users.router, prefix="/users", tags=["Usuários"])
app.include_router(chats.router, prefix="/chats", tags=["Chats"])
app.include_router(messages.router, prefix="/messages", tags=["Mensagens"])
app.include_router(files.router, prefix="/files", tags=["Arquivos"])

# Rota personalizada para documentação Swagger
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png"
    )

# Rota para ReDoc
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png"
    )

# Função personalizada para o schema OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Adiciona configurações de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira o token JWT com o prefixo Bearer, exemplo: 'Bearer {token}'"
        }
    }

    # Aplica segurança global
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Rota de verificação de saúde
@app.get("/health", tags=["Sistema"])
async def health_check():
    return {"status": "ok", "message": "API está funcionando corretamente"}

# Função para inicializar o cliente TDLib
async def initialize_tdlib():
    from app.core.tdlib_wrapper import initialize_client
    print("Inicializando cliente TDLib...")
    await initialize_client()
    print("Cliente TDLib inicializado com sucesso!")

# Inicializar o cliente TDLib na inicialização do aplicativo
@app.on_event("startup")
async def startup_event():
    # Cria e inicia os diretórios necessários
    os.makedirs(os.environ.get("TD_DATABASE_DIRECTORY", "./td_db"), exist_ok=True)
    os.makedirs(os.environ.get("TD_FILES_DIRECTORY", "./td_files"), exist_ok=True)
    
    # Inicializa o cliente TDLib
    await initialize_tdlib() 