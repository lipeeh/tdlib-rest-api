#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from app.api.auth_middleware import api_key_required
from app.services.tdlib_service import tdlib_service
import asyncio
import os
import json

# Criar o blueprint para bots
bots_bp = Blueprint('bots', __name__)

@bots_bp.route('/token', methods=['POST'])
@api_key_required
def check_bot_token():
    """
    Verifica um token de bot e retorna informações sobre ele
    ---
    tags:
      - Bots
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            bot_token:
              type: string
              description: Token do bot a ser verificado
    responses:
      200:
        description: Token verificado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'bot_token' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Token do bot é obrigatório'
            }), 400
            
        bot_token = data['bot_token']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'checkAuthenticationBotToken',
                {
                    'token': bot_token
                }
            ))
            
            # Se não houver erros, a verificação foi bem-sucedida
            return jsonify({
                'status': 'success',
                'message': 'Token verificado com sucesso',
                'bot_info': result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao verificar token do bot: {str(e)}'
        }), 500

@bots_bp.route('/commands', methods=['GET'])
@api_key_required
def get_commands():
    """
    Obtém a lista de comandos do bot atual
    ---
    tags:
      - Bots
    parameters:
      - name: scope
        in: query
        type: string
        required: false
        description: Escopo dos comandos (default, all_private_chats, all_group_chats, all_chat_administrators)
      - name: language_code
        in: query
        type: string
        required: false
        description: Código do idioma para os comandos (padrão 'pt-br')
    responses:
      200:
        description: Comandos obtidos com sucesso
      500:
        description: Erro interno
    """
    try:
        scope = request.args.get('scope', 'default')
        language_code = request.args.get('language_code', 'pt-br')
        
        # Mapear o escopo para o formato esperado pela API
        scope_type = {
            'default': 'botCommandScopeDefault',
            'all_private_chats': 'botCommandScopeAllPrivateChats',
            'all_group_chats': 'botCommandScopeAllGroupChats',
            'all_chat_administrators': 'botCommandScopeAllChatAdministrators'
        }.get(scope, 'botCommandScopeDefault')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getMyCommands',
                {
                    'scope': {
                        '@type': scope_type
                    },
                    'language_code': language_code
                }
            ))
            
            return jsonify({
                'status': 'success',
                'commands': result.get('commands', [])
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter comandos do bot: {str(e)}'
        }), 500

@bots_bp.route('/commands', methods=['POST'])
@api_key_required
def set_commands():
    """
    Define os comandos do bot atual
    ---
    tags:
      - Bots
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            commands:
              type: array
              items:
                type: object
                properties:
                  command:
                    type: string
                    description: Nome do comando
                  description:
                    type: string
                    description: Descrição do comando
            scope:
              type: string
              description: Escopo dos comandos (default, all_private_chats, all_group_chats, all_chat_administrators)
            language_code:
              type: string
              description: Código do idioma para os comandos
    responses:
      200:
        description: Comandos definidos com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'commands' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Lista de comandos é obrigatória'
            }), 400
            
        commands = data['commands']
        scope = data.get('scope', 'default')
        language_code = data.get('language_code', 'pt-br')
        
        if not isinstance(commands, list):
            return jsonify({
                'status': 'error',
                'message': 'O campo commands deve ser uma lista'
            }), 400
            
        # Validar a estrutura dos comandos
        for cmd in commands:
            if not isinstance(cmd, dict) or 'command' not in cmd or 'description' not in cmd:
                return jsonify({
                    'status': 'error',
                    'message': 'Cada comando deve ter os campos command e description'
                }), 400
        
        # Mapear o escopo para o formato esperado pela API
        scope_type = {
            'default': 'botCommandScopeDefault',
            'all_private_chats': 'botCommandScopeAllPrivateChats',
            'all_group_chats': 'botCommandScopeAllGroupChats',
            'all_chat_administrators': 'botCommandScopeAllChatAdministrators'
        }.get(scope, 'botCommandScopeDefault')
        
        # Formatar comandos no formato esperado pela API
        formatted_commands = [
            {
                '@type': 'botCommand',
                'command': cmd['command'],
                'description': cmd['description']
            }
            for cmd in commands
        ]
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'setMyCommands',
                {
                    'commands': formatted_commands,
                    'scope': {
                        '@type': scope_type
                    },
                    'language_code': language_code
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Comandos definidos com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao definir comandos do bot: {str(e)}'
        }), 500

@bots_bp.route('/description', methods=['POST'])
@api_key_required
def set_description():
    """
    Define a descrição do bot atual
    ---
    tags:
      - Bots
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            description:
              type: string
              description: Nova descrição do bot
            language_code:
              type: string
              description: Código do idioma para a descrição
    responses:
      200:
        description: Descrição definida com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'description' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Descrição é obrigatória'
            }), 400
            
        description = data['description']
        language_code = data.get('language_code', 'pt-br')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'setMyDescription',
                {
                    'description': description,
                    'language_code': language_code
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Descrição definida com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao definir descrição do bot: {str(e)}'
        }), 500

@bots_bp.route('/description', methods=['GET'])
@api_key_required
def get_description():
    """
    Obtém a descrição do bot atual
    ---
    tags:
      - Bots
    parameters:
      - name: language_code
        in: query
        type: string
        required: false
        description: Código do idioma para a descrição
    responses:
      200:
        description: Descrição obtida com sucesso
      500:
        description: Erro interno
    """
    try:
        language_code = request.args.get('language_code', 'pt-br')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getMyDescription',
                {
                    'language_code': language_code
                }
            ))
            
            return jsonify({
                'status': 'success',
                'description': result.get('description', '')
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter descrição do bot: {str(e)}'
        }), 500

@bots_bp.route('/short-description', methods=['POST'])
@api_key_required
def set_short_description():
    """
    Define a descrição curta do bot atual
    ---
    tags:
      - Bots
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            short_description:
              type: string
              description: Nova descrição curta do bot
            language_code:
              type: string
              description: Código do idioma para a descrição curta
    responses:
      200:
        description: Descrição curta definida com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'short_description' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Descrição curta é obrigatória'
            }), 400
            
        short_description = data['short_description']
        language_code = data.get('language_code', 'pt-br')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'setMyShortDescription',
                {
                    'short_description': short_description,
                    'language_code': language_code
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Descrição curta definida com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao definir descrição curta do bot: {str(e)}'
        }), 500

@bots_bp.route('/short-description', methods=['GET'])
@api_key_required
def get_short_description():
    """
    Obtém a descrição curta do bot atual
    ---
    tags:
      - Bots
    parameters:
      - name: language_code
        in: query
        type: string
        required: false
        description: Código do idioma para a descrição curta
    responses:
      200:
        description: Descrição curta obtida com sucesso
      500:
        description: Erro interno
    """
    try:
        language_code = request.args.get('language_code', 'pt-br')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getMyShortDescription',
                {
                    'language_code': language_code
                }
            ))
            
            return jsonify({
                'status': 'success',
                'short_description': result.get('short_description', '')
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter descrição curta do bot: {str(e)}'
        }), 500

@bots_bp.route('/answer-callback-query', methods=['POST'])
@api_key_required
def answer_callback_query():
    """
    Responde a uma consulta de callback de um botão inline
    ---
    tags:
      - Bots
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            callback_query_id:
              type: string
              description: ID da consulta de callback
            text:
              type: string
              description: Texto a ser exibido
            show_alert:
              type: boolean
              description: Se true, mostra um alerta em vez de uma notificação
            url:
              type: string
              description: URL para abrir
            cache_time:
              type: integer
              description: Tempo em segundos para armazenar o resultado em cache
    responses:
      200:
        description: Consulta de callback respondida com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'callback_query_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'ID da consulta de callback é obrigatório'
            }), 400
            
        callback_query_id = data['callback_query_id']
        text = data.get('text', '')
        show_alert = data.get('show_alert', False)
        url = data.get('url', '')
        cache_time = data.get('cache_time', 0)
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'answerCallbackQuery',
                {
                    'callback_query_id': callback_query_id,
                    'text': text,
                    'show_alert': show_alert,
                    'url': url,
                    'cache_time': cache_time
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Consulta de callback respondida com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao responder consulta de callback: {str(e)}'
        }), 500

@bots_bp.route('/answer-inline-query', methods=['POST'])
@api_key_required
def answer_inline_query():
    """
    Responde a uma consulta inline
    ---
    tags:
      - Bots
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            inline_query_id:
              type: string
              description: ID da consulta inline
            results:
              type: array
              description: Resultados para exibir
            cache_time:
              type: integer
              description: Tempo em segundos para armazenar o resultado em cache
            is_personal:
              type: boolean
              description: Se os resultados são exclusivos para o usuário solicitante
            next_offset:
              type: string
              description: Offset a ser usado para receber mais resultados
            switch_pm_text:
              type: string
              description: Texto para o botão "Ir para o chat privado"
            switch_pm_parameter:
              type: string
              description: Parâmetro para deep-linking do chat privado
    responses:
      200:
        description: Consulta inline respondida com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'inline_query_id' not in data or 'results' not in data:
            return jsonify({
                'status': 'error',
                'message': 'ID da consulta inline e resultados são obrigatórios'
            }), 400
            
        inline_query_id = data['inline_query_id']
        results = data['results']
        
        if not isinstance(results, list):
            return jsonify({
                'status': 'error',
                'message': 'O campo results deve ser uma lista'
            }), 400
            
        cache_time = data.get('cache_time', 300)
        is_personal = data.get('is_personal', False)
        next_offset = data.get('next_offset', '')
        switch_pm_text = data.get('switch_pm_text', '')
        switch_pm_parameter = data.get('switch_pm_parameter', '')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'answerInlineQuery',
                {
                    'inline_query_id': inline_query_id,
                    'results': results,
                    'cache_time': cache_time,
                    'is_personal': is_personal,
                    'next_offset': next_offset,
                    'switch_pm_text': switch_pm_text,
                    'switch_pm_parameter': switch_pm_parameter
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Consulta inline respondida com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao responder consulta inline: {str(e)}'
        }), 500 