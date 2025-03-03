#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from app.api.auth_middleware import api_key_required
from app.services.tdlib_service import tdlib_service
import asyncio

# Criar o blueprint para autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/config', methods=['POST'])
@api_key_required
def configure_tdlib():
    """
    Configura os parâmetros da TDLib
    ---
    tags:
      - Autenticação
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            api_id:
              type: string
              description: API ID do Telegram
            api_hash:
              type: string
              description: API Hash do Telegram
            database_directory:
              type: string
              description: Diretório para armazenar dados da TDLib
            files_directory:
              type: string
              description: Diretório para armazenar arquivos baixados
    responses:
      200:
        description: Configuração aplicada com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Corpo da requisição vazio'
            }), 400
            
        # Obter valores do corpo ou das configurações
        config = {
            'api_id': data.get('api_id', current_app.config.get('TELEGRAM_API_ID')),
            'api_hash': data.get('api_hash', current_app.config.get('TELEGRAM_API_HASH')),
            'database_directory': data.get('database_directory', current_app.config.get('TDLIB_DATABASE_DIRECTORY')),
            'files_directory': data.get('files_directory', current_app.config.get('TDLIB_FILES_DIRECTORY')),
        }
        
        # Verificar parâmetros obrigatórios
        if not config['api_id'] or not config['api_hash']:
            return jsonify({
                'status': 'error',
                'message': 'API ID e API Hash são obrigatórios'
            }), 400
            
        # Inicializar cliente TDLib de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(tdlib_service.initialize(config))
            return jsonify({
                'status': 'success',
                'message': 'Cliente TDLib configurado com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao configurar cliente TDLib: {str(e)}'
        }), 500

@auth_bp.route('/phone', methods=['POST'])
@api_key_required
def set_phone_number():
    """
    Define o número de telefone para autenticação
    ---
    tags:
      - Autenticação
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone_number:
              type: string
              description: Número de telefone com código do país (ex. +5511999999999)
    responses:
      200:
        description: Número de telefone enviado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'phone_number' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Número de telefone é obrigatório'
            }), 400
            
        phone_number = data['phone_number']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'setAuthenticationPhoneNumber',
                {'phone_number': phone_number}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Número de telefone enviado com sucesso',
                'auth_state': tdlib_service.auth_state
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao enviar número de telefone: {str(e)}'
        }), 500

@auth_bp.route('/code', methods=['POST'])
@api_key_required
def check_authentication_code():
    """
    Verifica o código de autenticação enviado pelo Telegram
    ---
    tags:
      - Autenticação
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            code:
              type: string
              description: Código de verificação recebido por SMS ou Telegram
    responses:
      200:
        description: Código verificado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Código de verificação é obrigatório'
            }), 400
            
        code = data['code']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'checkAuthenticationCode',
                {'code': code}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Código verificado com sucesso',
                'auth_state': tdlib_service.auth_state
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao verificar código: {str(e)}'
        }), 500

@auth_bp.route('/password', methods=['POST'])
@api_key_required
def check_authentication_password():
    """
    Verifica a senha de autenticação de duas etapas
    ---
    tags:
      - Autenticação
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            password:
              type: string
              description: Senha de duas etapas
    responses:
      200:
        description: Senha verificada com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'password' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Senha é obrigatória'
            }), 400
            
        password = data['password']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'checkAuthenticationPassword',
                {'password': password}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Senha verificada com sucesso',
                'auth_state': tdlib_service.auth_state
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao verificar senha: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@api_key_required
def logout():
    """
    Encerra a sessão atual no Telegram
    ---
    tags:
      - Autenticação
    responses:
      200:
        description: Logout realizado com sucesso
      500:
        description: Erro interno
    """
    try:
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute('logOut'))
            
            return jsonify({
                'status': 'success',
                'message': 'Logout realizado com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao realizar logout: {str(e)}'
        }), 500

@auth_bp.route('/state', methods=['GET'])
@api_key_required
def get_auth_state():
    """
    Obtém o estado atual da autenticação
    ---
    tags:
      - Autenticação
    responses:
      200:
        description: Estado atual da autenticação
      500:
        description: Erro interno
    """
    try:
        return jsonify({
            'status': 'success',
            'auth_state': tdlib_service.auth_state,
            'is_authorized': tdlib_service.is_authorized
        })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter estado de autenticação: {str(e)}'
        }), 500 