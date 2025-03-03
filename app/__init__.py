#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
import asyncio
import os
from threading import Thread

# Importar os blueprints
from app.api.auth_routes import auth_bp
from app.api.users_routes import users_bp
from app.api.chats_routes import chats_bp
from app.api.messages_routes import messages_bp
from app.api.media_routes import media_bp
from app.api.webhooks_routes import webhooks_bp
from app.api.bots_routes import bots_bp
from app.api.files_routes import files_bp

from app.services.tdlib_service import tdlib_service

# Criar a aplicação Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configurações da aplicação
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secreto-por-padrao')
app.config['API_KEY'] = os.environ.get('API_KEY', 'chave-api-padrao')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')

# Registrar os blueprints
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(users_bp, url_prefix='/api/v1/users')
app.register_blueprint(chats_bp, url_prefix='/api/v1/chats')
app.register_blueprint(messages_bp, url_prefix='/api/v1/messages')
app.register_blueprint(media_bp, url_prefix='/api/v1/media')
app.register_blueprint(webhooks_bp, url_prefix='/api/v1/webhooks')
app.register_blueprint(bots_bp, url_prefix='/api/v1/bots')
app.register_blueprint(files_bp, url_prefix='/api/v1/files')

# Rota para verificar o status da API
@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "API está funcionando corretamente"})

# Função para inicializar o cliente TDLib
def initialize_tdlib():
    asyncio.run(tdlib_service.initialize())
    print("Cliente TDLib inicializado com sucesso!")

# Inicializar o cliente TDLib ao iniciar a aplicação
@app.before_first_request
def startup_event():
    # Iniciar o cliente TDLib em uma thread separada para não bloquear a inicialização do Flask
    thread = Thread(target=initialize_tdlib)
    thread.daemon = True
    thread.start()
    print("Iniciando thread do cliente TDLib...")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000) 