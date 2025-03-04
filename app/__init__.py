#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
import asyncio
import os
from threading import Thread

# Importar os blueprints - verificar se existem ou criar
try:
    from app.api.auth_routes import auth_bp
    from app.api.users_routes import users_bp
    from app.api.chats_routes import chats_bp
    from app.api.messages_routes import messages_bp
    from app.api.media_routes import media_bp
    from app.api.webhooks_routes import webhooks_bp
    from app.api.bots_routes import bots_bp
    from app.api.files_routes import files_bp
except ImportError as e:
    print(f"Aviso: Não foi possível importar um ou mais blueprints: {e}")
    # Criar blueprints vazios para os que não existem
    # para evitar erros de execução
    missing_bp_names = []
    if 'auth_bp' not in locals():
        auth_bp = Blueprint('auth', __name__)
        missing_bp_names.append('auth_bp')
    if 'users_bp' not in locals():
        users_bp = Blueprint('users', __name__)
        missing_bp_names.append('users_bp')
    if 'chats_bp' not in locals():
        chats_bp = Blueprint('chats', __name__)
        missing_bp_names.append('chats_bp')
    if 'messages_bp' not in locals():
        messages_bp = Blueprint('messages', __name__)
        missing_bp_names.append('messages_bp')
    if 'media_bp' not in locals():
        media_bp = Blueprint('media', __name__)
        missing_bp_names.append('media_bp')
    if 'webhooks_bp' not in locals():
        webhooks_bp = Blueprint('webhooks', __name__)
        missing_bp_names.append('webhooks_bp')
    if 'bots_bp' not in locals():
        bots_bp = Blueprint('bots', __name__)
        missing_bp_names.append('bots_bp')
    if 'files_bp' not in locals():
        files_bp = Blueprint('files', __name__)
        missing_bp_names.append('files_bp')
    
    if missing_bp_names:
        print(f"Blueprints vazios foram criados para: {', '.join(missing_bp_names)}")

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

# Certificar-se de que a pasta de uploads existe
upload_folder = app.config['UPLOAD_FOLDER']
os.makedirs(upload_folder, exist_ok=True)

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
    try:
        asyncio.run(tdlib_service.initialize())
        print("Cliente TDLib inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar o cliente TDLib: {str(e)}")
        print("A aplicação continuará funcionando, mas as funcionalidades do Telegram não estarão disponíveis.")

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