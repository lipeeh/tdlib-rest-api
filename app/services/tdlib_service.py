#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import os
import logging
import time

# Tentativa de importar a biblioteca telegram-client
try:
    from telegram.client import Telegram
except ImportError:
    print("AVISO: A biblioteca 'python-telegram' não está instalada. Tentando usar pytdlib como fallback.")
    try:
        from pytdlib import Client as Telegram
        USING_PYTDLIB = True
    except ImportError:
        print("ERRO: Nem 'python-telegram' nem 'pytdlib' estão instalados.")
        print("Por favor, instale uma das bibliotecas:")
        print("  pip install python-telegram")
        print("  ou")
        print("  pip install pytdlib")
        Telegram = None
        USING_PYTDLIB = False
else:
    USING_PYTDLIB = False

# Configurar o logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.environ.get("LOG_FILE", "./logs/telegram_api.log"), mode='a')
    ]
)
logger = logging.getLogger(__name__)

class TDLibService:
    """
    Serviço para interação com a TDLib
    """
    
    def __init__(self):
        """
        Inicializa o serviço TDLib
        """
        self.client = None
        self.initialized = False
        self.api_id = os.environ.get("TELEGRAM_API_ID")
        self.api_hash = os.environ.get("TELEGRAM_API_HASH")
        self.phone = os.environ.get("TELEGRAM_PHONE")
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.database_encryption_key = os.environ.get("DATABASE_ENCRYPTION_KEY", "")
        
        # Verificar se estamos usando uma conta de bot ou usuário
        self.use_bot = bool(self.bot_token)
        
        # Diretórios para a TDLib
        self.database_directory = os.environ.get("TD_DATABASE_DIRECTORY", "./td_db")
        self.files_directory = os.environ.get("TD_FILES_DIRECTORY", "./td_files")
        
        # Criar diretórios se não existirem
        os.makedirs(self.database_directory, exist_ok=True)
        os.makedirs(self.files_directory, exist_ok=True)
        
        # Verificar se temos as credenciais necessárias
        if not self.api_id or not self.api_hash:
            logger.warning("API_ID e/ou API_HASH não configurados. O cliente TDLib não poderá ser inicializado.")
    
    async def initialize(self):
        """
        Inicializa o cliente TDLib
        """
        if Telegram is None:
            logger.error("Não foi possível inicializar o cliente TDLib: biblioteca não encontrada")
            raise ImportError("Biblioteca TDLib não encontrada. Instale 'python-telegram' ou 'pytdlib'.")
            
        if self.initialized:
            logger.info("Cliente TDLib já inicializado")
            return
        
        if not self.api_id or not self.api_hash:
            logger.error("API_ID e API_HASH são obrigatórios")
            raise ValueError("API_ID e API_HASH são obrigatórios")
        
        logger.info("Inicializando cliente TDLib...")
        
        # Configurar o cliente
        client_parameters = {
            'api_id': self.api_id,
            'api_hash': self.api_hash,
            'database_directory': self.database_directory,
            'files_directory': self.files_directory,
            'database_encryption_key': self.database_encryption_key,
            'use_message_database': True,
            'use_secret_chats': True,
            'system_language_code': 'pt-br',
            'device_model': 'Server',
            'application_version': '1.0',
            'enable_storage_optimizer': True
        }
        
        # Parâmetros adicionais para pytdlib
        if USING_PYTDLIB:
            client_parameters.update({
                'use_chat_info_database': True,
                'use_file_database': True,
            })
        
        try:
            # Criar o cliente
            self.client = Telegram(**client_parameters)
            
            # Iniciar o cliente
            await self.client.start()
            
            # Autenticar com token de bot ou número de telefone
            if self.use_bot:
                logger.info("Autenticando como bot...")
                result = await self.client.login_bot(self.bot_token)
                if not result:
                    raise Exception("Falha ao autenticar como bot")
            elif self.phone:
                logger.info(f"Autenticando como usuário com número de telefone: {self.phone}")
                result = await self.client.login(self.phone)
                if not result:
                    raise Exception("Falha ao autenticar como usuário")
            else:
                logger.warning("Nenhum método de autenticação configurado. O cliente TDLib será inicializado sem autenticação.")
            
            self.initialized = True
            logger.info("Cliente TDLib inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente TDLib: {e}")
            raise
    
    async def execute(self, method, parameters=None):
        """
        Executa um método da TDLib
        
        Args:
            method (str): Nome do método a ser executado
            parameters (dict, opcional): Parâmetros do método
            
        Returns:
            dict: Resultado da execução do método
        """
        if not self.initialized:
            try:
                await self.initialize()
            except Exception as e:
                logger.error(f"Não foi possível inicializar o cliente TDLib: {e}")
                raise Exception(f"Cliente TDLib não inicializado: {e}")
        
        if not parameters:
            parameters = {}
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                result = await self.client.call_method(method, parameters)
                return result
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Erro ao executar método {method} após {max_retries} tentativas: {e}")
                    raise
                
                logger.warning(f"Erro ao executar método {method} (tentativa {retry_count}/{max_retries}): {e}")
                # Esperar um pouco antes de tentar novamente
                await asyncio.sleep(1)

    async def close(self):
        """
        Fecha a conexão com a TDLib
        """
        if self.client:
            try:
                await self.client.stop()
                self.initialized = False
                logger.info("Cliente TDLib encerrado")
            except Exception as e:
                logger.error(f"Erro ao encerrar cliente TDLib: {e}")
                raise

# Criar a instância global do serviço
tdlib_service = TDLibService() 