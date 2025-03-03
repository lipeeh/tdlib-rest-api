#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from app import app
from waitress import serve
from app.services.tdlib_service import tdlib_service
import threading

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
    finally:
        loop.close()

if __name__ == "__main__":
    # Criar diretórios necessários
    os.makedirs("./td_db", exist_ok=True)
    os.makedirs("./td_files", exist_ok=True)

    # Inicializar TDLib em uma thread separada
    td_thread = threading.Thread(target=initialize_tdlib)
    td_thread.daemon = True
    td_thread.start()
    print("Thread do cliente TDLib iniciada")

    # Configurar o ambiente
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    if debug:
        # Modo de desenvolvimento
        print(f"Iniciando servidor em modo de desenvolvimento em http://{host}:{port}")
        app.run(debug=True, host=host, port=port)
    else:
        # Modo de produção usando Waitress
        print(f"Iniciando servidor em modo de produção em http://{host}:{port}")
        serve(app, host=host, port=port, threads=4)
    
    print("Servidor encerrado") 