#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from app.api.auth_middleware import api_key_required
from app.services.tdlib_service import tdlib_service
import asyncio

# Criar o blueprint para chats
chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/list', methods=['GET'])
@api_key_required
def get_chats():
    """
    Obtém a lista de chats
    ---
    tags:
      - Chats
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de chats a serem retornados (padrão 100, máximo 100)
      - name: offset
        in: query
        type: string
        required: false
        description: Offset baseado no ID do último chat retornado
    responses:
      200:
        description: Lista de chats
      500:
        description: Erro interno
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 100)
        offset_order = request.args.get('offset', '9223372036854775807')  # max int64
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getChats',
                {'chat_list': None, 'limit': limit, 'offset_order': offset_order}
            ))
            
            return jsonify({
                'status': 'success',
                'chat_ids': result.get('chat_ids', []),
                'total_count': len(result.get('chat_ids', []))
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter chats: {str(e)}'
        }), 500

@chats_bp.route('/<int:chat_id>', methods=['GET'])
@api_key_required
def get_chat(chat_id):
    """
    Obtém informações de um chat pelo ID
    ---
    tags:
      - Chats
    parameters:
      - name: chat_id
        in: path
        type: integer
        required: true
        description: ID do chat
    responses:
      200:
        description: Informações do chat
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
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getChat',
                {'chat_id': chat_id}
            ))
            
            return jsonify({
                'status': 'success',
                'chat': result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter informações do chat: {str(e)}'
        }), 500

@chats_bp.route('/create_group', methods=['POST'])
@api_key_required
def create_basic_group():
    """
    Cria um novo grupo
    ---
    tags:
      - Chats
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: Título do grupo
            user_ids:
              type: array
              items:
                type: integer
              description: Lista de IDs de usuários para adicionar ao grupo
    responses:
      200:
        description: Grupo criado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'title' not in data or 'user_ids' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Título e lista de usuários são obrigatórios'
            }), 400
            
        title = data['title']
        user_ids = data['user_ids']
        
        if not isinstance(user_ids, list) or len(user_ids) == 0:
            return jsonify({
                'status': 'error',
                'message': 'A lista de usuários deve conter pelo menos um usuário'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'createNewBasicGroupChat',
                {'user_ids': user_ids, 'title': title}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Grupo criado com sucesso',
                'chat': result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao criar grupo: {str(e)}'
        }), 500

@chats_bp.route('/create_supergroup', methods=['POST'])
@api_key_required
def create_supergroup():
    """
    Cria um novo supergrupo ou canal
    ---
    tags:
      - Chats
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: Título do supergrupo/canal
            is_channel:
              type: boolean
              description: Se true, cria um canal; se false, cria um supergrupo
            description:
              type: string
              description: Descrição do supergrupo/canal
    responses:
      200:
        description: Supergrupo/canal criado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'title' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Título é obrigatório'
            }), 400
            
        title = data['title']
        is_channel = data.get('is_channel', False)
        description = data.get('description', '')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'createNewSupergroupChat',
                {'title': title, 'is_channel': is_channel, 'description': description}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Supergrupo/canal criado com sucesso',
                'chat': result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao criar supergrupo/canal: {str(e)}'
        }), 500

@chats_bp.route('/<int:chat_id>/title', methods=['PUT'])
@api_key_required
def set_chat_title(chat_id):
    """
    Atualiza o título de um chat
    ---
    tags:
      - Chats
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
            title:
              type: string
              description: Novo título para o chat
    responses:
      200:
        description: Título atualizado com sucesso
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
        
        if not data or 'title' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Título é obrigatório'
            }), 400
            
        title = data['title']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'setChatTitle',
                {'chat_id': chat_id, 'title': title}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Título atualizado com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao atualizar título: {str(e)}'
        }), 500

@chats_bp.route('/<int:chat_id>/description', methods=['PUT'])
@api_key_required
def set_chat_description(chat_id):
    """
    Atualiza a descrição de um supergrupo ou canal
    ---
    tags:
      - Chats
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
            description:
              type: string
              description: Nova descrição para o supergrupo/canal
    responses:
      200:
        description: Descrição atualizada com sucesso
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
        
        if not data or 'description' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Descrição é obrigatória'
            }), 400
            
        description = data['description']
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Primeiro, precisamos obter o ID do supergrupo
            chat = loop.run_until_complete(tdlib_service.execute(
                'getChat',
                {'chat_id': chat_id}
            ))
            
            if chat.get('type', {}).get('@type') != 'chatTypeSupergroup':
                return jsonify({
                    'status': 'error',
                    'message': 'O chat não é um supergrupo ou canal'
                }), 400
                
            supergroup_id = chat.get('type', {}).get('supergroup_id')
            
            # Agora podemos atualizar a descrição
            result = loop.run_until_complete(tdlib_service.execute(
                'setSupergroupDescription',
                {'supergroup_id': supergroup_id, 'description': description}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Descrição atualizada com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao atualizar descrição: {str(e)}'
        }), 500

@chats_bp.route('/<int:chat_id>/photo', methods=['PUT'])
@api_key_required
def set_chat_photo(chat_id):
    """
    Atualiza a foto de um chat
    ---
    tags:
      - Chats
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
            photo_id:
              type: integer
              description: ID de uma foto já enviada no Telegram
    responses:
      200:
        description: Foto atualizada com sucesso
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
        
        if not data or ('photo_path' not in data and 'photo_id' not in data):
            return jsonify({
                'status': 'error',
                'message': 'photo_path ou photo_id é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if 'photo_path' in data:
                # Primeiro, precisamos carregar o arquivo
                file_result = loop.run_until_complete(tdlib_service.execute(
                    'uploadFile',
                    {
                        'file': {
                            '@type': 'inputFileLocal',
                            'path': data['photo_path']
                        },
                        'file_type': {
                            '@type': 'fileTypePhoto'
                        },
                        'priority': 1
                    }
                ))
                
                # Agora podemos definir a foto do chat
                photo = {
                    '@type': 'inputChatPhotoStatic',
                    'photo': {
                        '@type': 'inputFileId',
                        'id': file_result.get('id')
                    }
                }
            else:  # 'photo_id' in data
                photo = {
                    '@type': 'inputChatPhotoStatic',
                    'photo': {
                        '@type': 'inputFileId',
                        'id': data['photo_id']
                    }
                }
                
            # Definir a foto do chat
            result = loop.run_until_complete(tdlib_service.execute(
                'setChatPhoto',
                {'chat_id': chat_id, 'photo': photo}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Foto atualizada com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao atualizar foto: {str(e)}'
        }), 500

@chats_bp.route('/<int:chat_id>/members', methods=['GET'])
@api_key_required
def get_chat_members(chat_id):
    """
    Obtém a lista de membros de um supergrupo ou canal
    ---
    tags:
      - Chats
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
        description: Limite de membros a serem retornados (padrão 200, máximo 200)
      - name: offset
        in: query
        type: integer
        required: false
        description: Offset para paginação (padrão 0)
    responses:
      200:
        description: Lista de membros
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
            
        limit = min(int(request.args.get('limit', 200)), 200)
        offset = int(request.args.get('offset', 0))
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Primeiro, precisamos obter o ID do supergrupo
            chat = loop.run_until_complete(tdlib_service.execute(
                'getChat',
                {'chat_id': chat_id}
            ))
            
            if chat.get('type', {}).get('@type') != 'chatTypeSupergroup':
                return jsonify({
                    'status': 'error',
                    'message': 'O chat não é um supergrupo ou canal'
                }), 400
                
            supergroup_id = chat.get('type', {}).get('supergroup_id')
            
            # Agora podemos obter os membros
            result = loop.run_until_complete(tdlib_service.execute(
                'getSupergroupMembers',
                {
                    'supergroup_id': supergroup_id,
                    'offset': offset,
                    'limit': limit,
                    'filter': {'@type': 'supergroupMembersFilterRecent'}
                }
            ))
            
            return jsonify({
                'status': 'success',
                'members': result.get('members', []),
                'total_count': result.get('total_count', 0)
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter membros: {str(e)}'
        }), 500 