# Telegram API

API REST para integração com o Telegram usando TDLib, fornecendo uma interface simples e poderosa para bots e contas de usuário.

## Visão Geral

Esta API fornece endpoints para interagir com o Telegram através da biblioteca TDLib, permitindo:

- Autenticação com bots ou contas de usuário
- Envio e recebimento de mensagens
- Gerenciamento de chats e grupos
- Manipulação de mídia e arquivos
- Configuração de webhooks para notificações
- Gerenciamento de bots

## Estrutura do Projeto

```
├── app/                   # Pacote principal da aplicação
│   ├── api/               # Endpoints da API
│   ├── services/          # Serviços de integração
│   ├── utils/             # Utilitários
│   ├── webhooks/          # Manipuladores de webhooks
│   └── __init__.py        # Arquivo de inicialização da aplicação
├── main.py                # Ponto de entrada da aplicação
├── Dockerfile             # Configuração para contêinerização
├── requirements.txt       # Dependências do projeto
└── .env.example           # Exemplo de variáveis de ambiente
```

## Endpoints

A API fornece os seguintes grupos de endpoints:

- `/api/v1/auth`: Autenticação e gerenciamento de sessões
- `/api/v1/users`: Operações relacionadas a usuários
- `/api/v1/chats`: Operações relacionadas a chats e grupos
- `/api/v1/messages`: Envio e gerenciamento de mensagens
- `/api/v1/media`: Upload, download e manipulação de mídia
- `/api/v1/webhooks`: Configuração de webhooks para notificações
- `/api/v1/bots`: Gerenciamento de bots e comandos
- `/api/v1/files`: Operações com arquivos

## Requisitos

- Python 3.8+
- TDLib
- Redis (opcional, para armazenamento em cache)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/telegram-api.git
   cd telegram-api
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente copiando o arquivo `.env.example` para `.env` e editando-o:
   ```bash
   cp .env.example .env
   ```

## Uso com Docker

Para executar a API usando Docker:

```bash
docker build -t telegram-api .
docker run -p 8000:8000 -v $(pwd)/.env:/app/.env telegram-api
```

## Variáveis de Ambiente

Configure as seguintes variáveis de ambiente:

- `TELEGRAM_API_ID`: ID da API do Telegram
- `TELEGRAM_API_HASH`: Hash da API do Telegram
- `TELEGRAM_BOT_TOKEN`: Token do bot (para uso de bots)
- `TELEGRAM_PHONE`: Número de telefone (para uso de contas de usuário)
- `API_KEY`: Chave para autenticação na API
- `DEBUG`: Define o modo de depuração (true/false)
- `HOST`: Host para execução do servidor
- `PORT`: Porta para execução do servidor

## Autenticação

A API usa autenticação por chave de API. Adicione o cabeçalho `X-API-KEY` com sua chave API para todas as requisições.

## Documentação

Para visualizar a documentação completa da API, acesse `/api/v1/docs` após iniciar o servidor.

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 
