#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import wraps
from flask import request, jsonify, current_app
import os
import logging

logger = logging.getLogger(__name__)

def api_key_required(f):
    """
    Middleware para validar API key
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Obter a API key configurada
            api_key = current_app.config.get('API_KEY')
            
            # Se não estiver nas configurações da aplicação, tentar variável de ambiente
            if not api_key:
                api_key = os.environ.get('API_KEY')
                
            # Se ainda não tiver API key, usar valor padrão
            if not api_key:
                api_key = 'api-key-padrao'
                logger.warning("API_KEY não configurada. Usando valor padrão (inseguro).")
            
            # Obter a API key da requisição
            request_api_key = request.headers.get('X-API-KEY')
            
            # Verificar se a API key foi fornecida
            if not request_api_key:
                logger.warning(f"Tentativa de acesso sem API Key: {request.path}")
                return jsonify({
                    'status': 'error',
                    'message': 'API Key não fornecida. Use o cabeçalho X-API-KEY.'
                }), 401
            
            # Verificar se a API key é válida
            if request_api_key != api_key:
                logger.warning(f"Tentativa de acesso com API Key inválida: {request.path}")
                return jsonify({
                    'status': 'error',
                    'message': 'API Key inválida.'
                }), 401
            
            # API Key válida, continuar
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro ao validar API Key: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Erro interno ao validar autenticação.'
            }), 500
    
    return decorated 