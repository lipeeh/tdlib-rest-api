#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

# Blueprints para os diferentes grupos de endpoints
from app.api.auth_routes import auth_bp
from app.api.users_routes import users_bp
from app.api.chats_routes import chats_bp
from app.api.messages_routes import messages_bp
from app.api.media_routes import media_bp
from app.api.bots_routes import bots_bp
from app.api.webhooks_routes import webhooks_bp
from app.api.stickers_routes import stickers_bp
from app.api.settings_routes import settings_bp

def register_routes(app: Flask):
    """
    Registra todos os blueprints das rotas da API na aplicação Flask
    
    Args:
        app: Aplicação Flask onde as rotas serão registradas
    """
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(chats_bp, url_prefix='/api/chats')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(media_bp, url_prefix='/api/media')
    app.register_blueprint(bots_bp, url_prefix='/api/bots')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
    app.register_blueprint(stickers_bp, url_prefix='/api/stickers')
    app.register_blueprint(settings_bp, url_prefix='/api/settings') 