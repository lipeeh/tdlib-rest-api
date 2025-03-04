#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import time
import threading
from app import app
from waitress import serve
from app.services.tdlib_service import tdlib_service

def initialize_tdlib():
    """Inicializa o cliente TDLib em uma thread separada"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("Inicializando cliente TDLib...")
        loop.run_until_complete(tdlib_service.initialize())
        print("Cliente TDLib inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar cliente TDLib: {e}")
        print("A aplicação continuará funcionando, mas as funcionalidades do Telegram não estarão disponíveis.")
    finally:
        loop.close()

def create_directories():
    """Cria os diretórios necessários para a aplicação"""
    try:
        # Diretórios TDLib
        os.makedirs("./td_db", exist_ok=True)
        os.makedirs("./td_files", exist_ok=True)
        
        # Diretório de uploads
        upload_folder = os.environ.get("UPLOAD_FOLDER", "/tmp/uploads")
        os.makedirs(upload_folder, exist_ok=True)
        
        # Diretório de logs
        log_file = os.environ.get("LOG_FILE", "./logs/telegram_api.log")
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        print("Diretórios criados com sucesso.")
    except Exception as e:
        print(f"Erro ao criar diretórios: {e}")
        print("Verifique as permissões do sistema de arquivos.")

if __name__ == "__main__":
    # Criar diretórios necessários
    create_directories()

    # Inicializar TDLib em uma thread separada
    td_thread = threading.Thread(target=initialize_tdlib)
    td_thread.daemon = True
    td_thread.start()
    print("Thread do cliente TDLib iniciada")

    # Aguardar um pouco para que a inicialização da TDLib comece
    time.sleep(1)

    # Configurar o ambiente
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    try:
        if debug:
            # Modo de desenvolvimento
            print(f"Iniciando servidor em modo de desenvolvimento em http://{host}:{port}")
            app.run(debug=True, host=host, port=port)
        else:
            # Modo de produção usando Waitress
            threads = int(os.environ.get("WAITRESS_THREADS", 4))
            print(f"Iniciando servidor em modo de produção em http://{host}:{port} com {threads} threads")
            serve(app, host=host, port=port, threads=threads)
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo usuário")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)
    finally:
        print("Servidor encerrado") 