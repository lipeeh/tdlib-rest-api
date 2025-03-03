#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, jsonify, current_app
import os

def api_key_required(f):
    """
    Middleware para validar API key
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obter a API key configurada
        api_key = current_app.config.get('API_KEY', os.environ.get('API_KEY', 'api-key-padrao'))
        
        # Obter a API key da requisição
        request_api_key = request.headers.get('X-API-KEY')
        
        # Verificar se a API key foi fornecida
        if not request_api_key:
            return jsonify({
                'status': 'error',
                'message': 'API Key não fornecida. Use o cabeçalho X-API-KEY.'
            }), 401
        
        # Verificar se a API key é válida
        if request_api_key != api_key:
            return jsonify({
                'status': 'error',
                'message': 'API Key inválida.'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated 