# Telegram TDLib API REST

Uma API REST para integração com o Telegram usando a biblioteca TDLib, projetada para ser facilmente implantada com Docker e EasyPanel.

## Recursos

- Autenticação via JWT para segurança da API
- Endpoints para gerenciar usuários, chats e mensagens
- Compatível com Docker e EasyPanel
- Documentação automática com Swagger UI

## Requisitos

- Docker e Docker Compose
- Credenciais de API do Telegram (api_id e api_hash)

## Configuração

1. Clone este repositório
2. Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

3. Edite o arquivo `.env` com suas credenciais do Telegram:

```
# Configurações do Telegram
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=+5511999999999

# Diretórios para dados
TD_DATABASE_DIRECTORY=./td_db
TD_FILES_DIRECTORY=./td_files

# Configurações de segurança
API_SECRET_KEY=seu_secret_key_muito_seguro
JWT_SECRET=seu_jwt_secret_muito_seguro
JWT_EXPIRE_MINUTES=1440

# Modo DEBUG
DEBUG=False
```

## Execução

### Com Docker Compose

```bash
docker-compose up -d
```

### Importando no EasyPanel

1. Faça upload dos arquivos para seu servidor
2. No EasyPanel, vá para "Apps" > "Custom App" > "Import from Docker Compose"
3. Selecione o arquivo docker-compose.yml
4. Configure as variáveis de ambiente

## Endpoints da API

A documentação completa dos endpoints está disponível em:

- Swagger UI: `http://seu-servidor:8000/docs`
- ReDoc: `http://seu-servidor:8000/redoc`

### Principais Endpoints

- `/auth/token` - Obter token JWT para autenticação
- `/users/me` - Obter informações do usuário atual
- `/chats/list` - Listar chats disponíveis
- `/messages/{chat_id}/send` - Enviar mensagem para um chat
- `/messages/{chat_id}/history` - Obter histórico de mensagens

## Primeiro Acesso

1. Inicie a API
2. Faça uma solicitação POST para `/auth/token` com o user "admin" e o password definido como `API_SECRET_KEY`
3. Use o token JWT retornado para autenticar todas as outras solicitações

## Licença

MIT 