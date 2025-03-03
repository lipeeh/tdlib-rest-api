import asyncio
import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from python_tdlib.client import Client

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tdlib")

# Carrega as variáveis de ambiente
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.environ.get("TELEGRAM_PHONE")
TD_DATABASE_DIRECTORY = os.environ.get("TD_DATABASE_DIRECTORY", "./td_db")
TD_FILES_DIRECTORY = os.environ.get("TD_FILES_DIRECTORY", "./td_files")

# Cliente TDLib global
tg = None

class TDLibWrapper:
    def __init__(self):
        self.client = None
        self.ready = asyncio.Event()
        self.is_authorized = False
        self.auth_state = None
        self.updates_queue = asyncio.Queue()
        self.logger = logger

    async def initialize(self):
        """Inicializa o cliente TDLib."""
        self.logger.info("Inicializando cliente TDLib...")
        
        # Cria direórios necessários
        Path(TD_DATABASE_DIRECTORY).mkdir(parents=True, exist_ok=True)
        Path(TD_FILES_DIRECTORY).mkdir(parents=True, exist_ok=True)
        
        # Inicializa o cliente
        self.client = Client()
        
        # Configura o TDLib
        await self.client.call_method(
            method_name='setLogVerbosityLevel',
            params={'new_verbosity_level': 2}
        )
        
        # Configura os parâmetros
        await self.setup_parameters()
        
        # Inicia o manipulador de atualizações
        asyncio.create_task(self.update_handler())
        
        # Aguarda a autorização
        await self.handle_authentication()
        
        self.logger.info("Cliente TDLib inicializado com sucesso!")
        return self

    async def setup_parameters(self):
        """Configura os parâmetros do TDLib."""
        await self.client.call_method(
            method_name='setTdlibParameters',
            params={
                'use_test_dc': False,
                'database_directory': TD_DATABASE_DIRECTORY,
                'files_directory': TD_FILES_DIRECTORY,
                'use_file_database': True,
                'use_chat_info_database': True,
                'use_message_database': True,
                'use_secret_chats': False,
                'api_id': int(TELEGRAM_API_ID),
                'api_hash': TELEGRAM_API_HASH,
                'system_language_code': 'pt-br',
                'device_model': 'API Server',
                'system_version': 'Linux',
                'application_version': '1.0.0',
                'enable_storage_optimizer': True
            }
        )

    async def update_handler(self):
        """Processa atualizações do TDLib."""
        while True:
            update = await self.client.receive()
            if update:
                await self.process_update(update)

    async def process_update(self, update):
        """Processa uma atualização específica."""
        update_type = update.get('@type')
        
        # Coloca a atualização na fila para processamento assíncrono
        await self.updates_queue.put(update)
        
        # Processa estados de autenticação
        if update_type == 'updateAuthorizationState':
            await self.process_auth_update(update)
    
    async def process_auth_update(self, update):
        """Processa atualizações relacionadas à autenticação."""
        auth_state = update['authorization_state']['@type']
        self.auth_state = auth_state
        
        if auth_state == 'authorizationStateWaitTdlibParameters':
            # Já configurado em setup_parameters()
            pass
        
        elif auth_state == 'authorizationStateWaitEncryptionKey':
            await self.client.call_method(
                method_name='checkDatabaseEncryptionKey',
                params={}
            )
        
        elif auth_state == 'authorizationStateWaitPhoneNumber':
            if not TELEGRAM_PHONE:
                self.logger.error("Número de telefone não fornecido!")
                return
                
            await self.client.call_method(
                method_name='setAuthenticationPhoneNumber',
                params={
                    'phone_number': TELEGRAM_PHONE
                }
            )
            
        elif auth_state == 'authorizationStateWaitCode':
            self.logger.info("Código de verificação necessário. Use a API para enviar o código.")
            
        elif auth_state == 'authorizationStateWaitPassword':
            self.logger.info("Senha necessária. Use a API para enviar a senha.")
            
        elif auth_state == 'authorizationStateReady':
            self.logger.info("Autorizado com sucesso!")
            self.is_authorized = True
            self.ready.set()
            
        elif auth_state == 'authorizationStateLoggingOut':
            self.logger.info("Saindo...")
            self.is_authorized = False
            self.ready.clear()
            
        elif auth_state == 'authorizationStateClosing':
            self.logger.info("Fechando...")
            self.is_authorized = False
            self.ready.clear()
            
        elif auth_state == 'authorizationStateClosed':
            self.logger.info("Fechado!")
            self.is_authorized = False
            self.ready.clear()

    async def handle_authentication(self):
        """Gerencia o processo de autenticação."""
        try:
            # Aguarda até que o cliente esteja pronto (autorizado)
            await asyncio.wait_for(self.ready.wait(), timeout=60)
        except asyncio.TimeoutError:
            self.logger.warning("Timeout durante a autenticação. Estado atual: %s", self.auth_state)
            # Não levantamos erro aqui para permitir que a API continue funcionando
            # e o usuário possa enviar o código mais tarde via API

    async def call_method(self, method_name: str, params: Dict[str, Any]):
        """Chama um método TDLib."""
        # Aguarda o cliente estar pronto para aceitar comandos
        if not self.is_authorized and method_name not in ['checkAuthenticationCode', 'checkAuthenticationPassword']:
            await self.ready.wait()
            
        return await self.client.call_method(method_name=method_name, params=params)

    async def check_authentication_code(self, code: str):
        """Verifica o código de autenticação."""
        return await self.client.call_method(
            method_name='checkAuthenticationCode',
            params={'code': code}
        )
        
    async def check_authentication_password(self, password: str):
        """Verifica a senha de autenticação."""
        return await self.client.call_method(
            method_name='checkAuthenticationPassword',
            params={'password': password}
        )

async def initialize_client():
    """Inicializa o cliente TDLib global."""
    global tg
    tg = await TDLibWrapper().initialize()
    return tg

async def get_chats(limit=100, offset_order=2**63-1, offset_chat_id=0):
    """Obtém a lista de chats."""
    if not tg:
        await initialize_client()
        
    return await tg.call_method(
        method_name='getChats',
        params={
            'chat_list': {'@type': 'chatListMain'},
            'limit': limit,
            'offset_chat_id': offset_chat_id,
            'offset_order': offset_order
        }
    )

async def search_contacts(query: str, limit: int = 50):
    """Pesquisa contatos pelo nome."""
    if not tg:
        await initialize_client()
        
    return await tg.call_method(
        method_name='searchContacts',
        params={
            'query': query,
            'limit': limit
        }
    ) 