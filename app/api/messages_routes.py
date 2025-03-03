#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from app.api.auth_middleware import api_key_required
from app.services.tdlib_service import tdlib_service
import asyncio
import os

# Criar o blueprint para mensagens
messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/<int:chat_id>/send', methods=['POST'])
@api_key_required
def send_message(chat_id):
    """
    Envia uma mensagem de texto para um chat
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: Texto da mensagem
            reply_to_message_id:
              type: integer
              description: ID da mensagem para responder
            disable_notification:
              type: boolean
              description: Se true, envia a mensagem silenciosamente
    responses:
      200:
        description: Mensagem enviada com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat é obrigatório'
            }), 400
            
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Texto da mensagem é obrigatório'
            }), 400
            
        text = data['text']
        reply_to_message_id = data.get('reply_to_message_id', 0)
        disable_notification = data.get('disable_notification', False)
        
        # Criar o conteúdo de entrada da mensagem
        input_message_content = {
            '@type': 'inputMessageText',
            'text': {
                '@type': 'formattedText',
                'text': text
            }
        }
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'sendMessage',
                {
                    'chat_id': chat_id,
                    'reply_to_message_id': reply_to_message_id,
                    'disable_notification': disable_notification,
                    'input_message_content': input_message_content
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Mensagem enviada com sucesso',
                'message_id': result.get('id', 0)
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao enviar mensagem: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/photo', methods=['POST'])
@api_key_required
def send_photo(chat_id):
    """
    Envia uma foto para um chat
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            photo_path:
              type: string
              description: Caminho do arquivo de foto no servidor
            caption:
              type: string
              description: Legenda da foto
            reply_to_message_id:
              type: integer
              description: ID da mensagem para responder
            disable_notification:
              type: boolean
              description: Se true, envia a mensagem silenciosamente
    responses:
      200:
        description: Foto enviada com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat é obrigatório'
            }), 400
            
        data = request.json
        
        if not data or 'photo_path' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Caminho da foto é obrigatório'
            }), 400
            
        photo_path = data['photo_path']
        caption = data.get('caption', '')
        reply_to_message_id = data.get('reply_to_message_id', 0)
        disable_notification = data.get('disable_notification', False)
        
        # Verificar se o arquivo existe
        if not os.path.isfile(photo_path):
            return jsonify({
                'status': 'error',
                'message': f'Arquivo não encontrado: {photo_path}'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Criar o conteúdo de entrada da mensagem
            input_message_content = {
                '@type': 'inputMessagePhoto',
                'photo': {
                    '@type': 'inputFileLocal',
                    'path': photo_path
                },
                'caption': {
                    '@type': 'formattedText',
                    'text': caption
                }
            }
            
            result = loop.run_until_complete(tdlib_service.execute(
                'sendMessage',
                {
                    'chat_id': chat_id,
                    'reply_to_message_id': reply_to_message_id,
                    'disable_notification': disable_notification,
                    'input_message_content': input_message_content
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Foto enviada com sucesso',
                'message_id': result.get('id', 0)
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao enviar foto: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/file', methods=['POST'])
@api_key_required
def send_file(chat_id):
    """
    Envia um arquivo para um chat
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            file_path:
              type: string
              description: Caminho do arquivo no servidor
            caption:
              type: string
              description: Legenda do arquivo
            reply_to_message_id:
              type: integer
              description: ID da mensagem para responder
            disable_notification:
              type: boolean
              description: Se true, envia a mensagem silenciosamente
    responses:
      200:
        description: Arquivo enviado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat é obrigatório'
            }), 400
            
        data = request.json
        
        if not data or 'file_path' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Caminho do arquivo é obrigatório'
            }), 400
            
        file_path = data['file_path']
        caption = data.get('caption', '')
        reply_to_message_id = data.get('reply_to_message_id', 0)
        disable_notification = data.get('disable_notification', False)
        
        # Verificar se o arquivo existe
        if not os.path.isfile(file_path):
            return jsonify({
                'status': 'error',
                'message': f'Arquivo não encontrado: {file_path}'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Criar o conteúdo de entrada da mensagem
            input_message_content = {
                '@type': 'inputMessageDocument',
                'document': {
                    '@type': 'inputFileLocal',
                    'path': file_path
                },
                'caption': {
                    '@type': 'formattedText',
                    'text': caption
                }
            }
            
            result = loop.run_until_complete(tdlib_service.execute(
                'sendMessage',
                {
                    'chat_id': chat_id,
                    'reply_to_message_id': reply_to_message_id,
                    'disable_notification': disable_notification,
                    'input_message_content': input_message_content
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Arquivo enviado com sucesso',
                'message_id': result.get('id', 0)
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao enviar arquivo: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/video', methods=['POST'])
@api_key_required
def send_video(chat_id):
    """
    Envia um vídeo para um chat
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            video_path:
              type: string
              description: Caminho do arquivo de vídeo no servidor
            caption:
              type: string
              description: Legenda do vídeo
            reply_to_message_id:
              type: integer
              description: ID da mensagem para responder
            disable_notification:
              type: boolean
              description: Se true, envia a mensagem silenciosamente
    responses:
      200:
        description: Vídeo enviado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat é obrigatório'
            }), 400
            
        data = request.json
        
        if not data or 'video_path' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Caminho do vídeo é obrigatório'
            }), 400
            
        video_path = data['video_path']
        caption = data.get('caption', '')
        reply_to_message_id = data.get('reply_to_message_id', 0)
        disable_notification = data.get('disable_notification', False)
        
        # Verificar se o arquivo existe
        if not os.path.isfile(video_path):
            return jsonify({
                'status': 'error',
                'message': f'Arquivo não encontrado: {video_path}'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Criar o conteúdo de entrada da mensagem
            input_message_content = {
                '@type': 'inputMessageVideo',
                'video': {
                    '@type': 'inputFileLocal',
                    'path': video_path
                },
                'caption': {
                    '@type': 'formattedText',
                    'text': caption
                }
            }
            
            result = loop.run_until_complete(tdlib_service.execute(
                'sendMessage',
                {
                    'chat_id': chat_id,
                    'reply_to_message_id': reply_to_message_id,
                    'disable_notification': disable_notification,
                    'input_message_content': input_message_content
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Vídeo enviado com sucesso',
                'message_id': result.get('id', 0)
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao enviar vídeo: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/history', methods=['GET'])
@api_key_required
def get_chat_history(chat_id):
    """
    Obtém o histórico de mensagens de um chat
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de mensagens a serem retornadas (padrão 100, máximo 100)
      - name: from_message_id
        in: query
        type: integer
        required: false
        description: ID da mensagem a partir da qual obter o histórico (0 para obter do mais recente)
    responses:
      200:
        description: Histórico de mensagens
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat é obrigatório'
            }), 400
            
        limit = min(int(request.args.get('limit', 100)), 100)
        from_message_id = int(request.args.get('from_message_id', 0))
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getChatHistory',
                {
                    'chat_id': chat_id,
                    'from_message_id': from_message_id,
                    'offset': 0,
                    'limit': limit,
                    'only_local': False
                }
            ))
            
            return jsonify({
                'status': 'success',
                'messages': result.get('messages', []),
                'total_count': len(result.get('messages', []))
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter histórico de mensagens: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/forward', methods=['POST'])
@api_key_required
def forward_messages(chat_id):
    """
    Encaminha mensagens para um chat
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat de destino
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            from_chat_id:
              type: integer
              description: ID do chat de origem
            message_ids:
              type: array
              items:
                type: integer
              description: Lista de IDs das mensagens a serem encaminhadas
            disable_notification:
              type: boolean
              description: Se true, envia as mensagens silenciosamente
    responses:
      200:
        description: Mensagens encaminhadas com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat de destino é obrigatório'
            }), 400
            
        data = request.json
        
        if not data or 'from_chat_id' not in data or 'message_ids' not in data:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat de origem e IDs das mensagens são obrigatórios'
            }), 400
            
        from_chat_id = data['from_chat_id']
        message_ids = data['message_ids']
        disable_notification = data.get('disable_notification', False)
        
        if not isinstance(message_ids, list) or len(message_ids) == 0:
            return jsonify({
                'status': 'error',
                'message': 'IDs das mensagens devem ser uma lista não vazia'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'forwardMessages',
                {
                    'chat_id': chat_id,
                    'from_chat_id': from_chat_id,
                    'message_ids': message_ids,
                    'disable_notification': disable_notification,
                    'send_copy': False,
                    'remove_caption': False
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Mensagens encaminhadas com sucesso',
                'message_ids': result.get('message_ids', [])
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao encaminhar mensagens: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/<int:message_id>', methods=['DELETE'])
@api_key_required
def delete_message(chat_id, message_id):
    """
    Exclui uma mensagem
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: message_id
        in: path
        type: integer
        required: true
        description: ID da mensagem
      - name: revoke
        in: query
        type: boolean
        required: false
        description: Se true, exclui para todos os usuários
    responses:
      200:
        description: Mensagem excluída com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id or not message_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat e ID da mensagem são obrigatórios'
            }), 400
            
        revoke = request.args.get('revoke', 'false').lower() == 'true'
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'deleteMessages',
                {
                    'chat_id': chat_id,
                    'message_ids': [message_id],
                    'revoke': revoke
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Mensagem excluída com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao excluir mensagem: {str(e)}'
        }), 500

@messages_bp.route('/<int:chat_id>/<int:message_id>/edit', methods=['PUT'])
@api_key_required
def edit_message_text(chat_id, message_id):
    """
    Edita o texto de uma mensagem
    ---
    tags:
      - Mensagens
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
      - name: message_id
        in: path
        type: integer
        required: true
        description: ID da mensagem
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: Novo texto da mensagem
    responses:
      200:
        description: Mensagem editada com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not chat_id or not message_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do chat e ID da mensagem são obrigatórios'
            }), 400
            
        data = request.json
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Texto da mensagem é obrigatório'
            }), 400
            
        text = data['text']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'editMessageText',
                {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'input_message_content': {
                        '@type': 'inputMessageText',
                        'text': {
                            '@type': 'formattedText',
                            'text': text
                        }
                    }
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Mensagem editada com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao editar mensagem: {str(e)}'
        }), 500 