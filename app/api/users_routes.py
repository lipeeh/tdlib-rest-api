#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from app.api.auth_middleware import api_key_required
from app.services.tdlib_service import tdlib_service
import asyncio

# Criar o blueprint para usuários
users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@api_key_required
def get_current_user():
    """
    Obtém informações do usuário atual
    ---
    tags:
      - Usuários
    responses:
      200:
        description: Informações do usuário atual
      500:
        description: Erro interno
    """
    try:
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute('getMe'))
            
            return jsonify({
                'status': 'success',
                'user': result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter informações do usuário: {str(e)}'
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@api_key_required
def get_user_info(user_id):
    """
    Obtém informações de um usuário pelo ID
    ---
    tags:
      - Usuários
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID do usuário
    responses:
      200:
        description: Informações do usuário
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do usuário é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getUser',
                {'user_id': user_id}
            ))
            
            return jsonify({
                'status': 'success',
                'user': result
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter informações do usuário: {str(e)}'
        }), 500

@users_bp.route('/search', methods=['GET'])
@api_key_required
def search_users():
    """
    Pesquisa usuários pelo nome ou número de telefone
    ---
    tags:
      - Usuários
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: Termo de busca (nome ou número de telefone)
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de resultados (padrão 50, máximo 100)
    responses:
      200:
        description: Resultados da pesquisa
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        query = request.args.get('query')
        limit = min(int(request.args.get('limit', 50)), 100)
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Termo de busca é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'searchContacts',
                {'query': query, 'limit': limit}
            ))
            
            return jsonify({
                'status': 'success',
                'users': result.get('user_ids', [])
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao pesquisar usuários: {str(e)}'
        }), 500

@users_bp.route('/contacts', methods=['GET'])
@api_key_required
def get_contacts():
    """
    Obtém a lista de contatos salvos
    ---
    tags:
      - Usuários
    responses:
      200:
        description: Lista de contatos
      500:
        description: Erro interno
    """
    try:
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute('getContacts'))
            
            return jsonify({
                'status': 'success',
                'contacts': result.get('user_ids', [])
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter contatos: {str(e)}'
        }), 500

@users_bp.route('/contacts', methods=['POST'])
@api_key_required
def add_contact():
    """
    Adiciona um contato
    ---
    tags:
      - Usuários
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            phone_number:
              type: string
              description: Número de telefone com código do país
            first_name:
              type: string
              description: Primeiro nome
            last_name:
              type: string
              description: Sobrenome (opcional)
    responses:
      200:
        description: Contato adicionado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'phone_number' not in data or 'first_name' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Número de telefone e primeiro nome são obrigatórios'
            }), 400
            
        phone_number = data['phone_number']
        first_name = data['first_name']
        last_name = data.get('last_name', '')
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'importContacts',
                {
                    'contacts': [
                        {
                            'phone_number': phone_number,
                            'first_name': first_name,
                            'last_name': last_name
                        }
                    ]
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Contato adicionado com sucesso',
                'user_ids': result.get('user_ids', [])
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao adicionar contato: {str(e)}'
        }), 500

@users_bp.route('/contacts/<string:phone_number>', methods=['DELETE'])
@api_key_required
def remove_contact(phone_number):
    """
    Remove um contato pelo número de telefone
    ---
    tags:
      - Usuários
    parameters:
      - name: phone_number
        in: path
        type: string
        required: true
        description: Número de telefone do contato
    responses:
      200:
        description: Contato removido com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not phone_number:
            return jsonify({
                'status': 'error',
                'message': 'Número de telefone é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Primeiro, precisamos encontrar o usuário pelo número de telefone
            search_result = loop.run_until_complete(tdlib_service.execute(
                'searchContacts',
                {'query': phone_number, 'limit': 1}
            ))
            
            user_ids = search_result.get('user_ids', [])
            if not user_ids:
                return jsonify({
                    'status': 'error',
                    'message': 'Contato não encontrado'
                }), 404
                
            user_id = user_ids[0]
            
            # Agora podemos remover o contato
            result = loop.run_until_complete(tdlib_service.execute(
                'removeContacts',
                {'user_ids': [user_id]}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Contato removido com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao remover contato: {str(e)}'
        }), 500

@users_bp.route('/block/<int:user_id>', methods=['POST'])
@api_key_required
def block_user(user_id):
    """
    Bloqueia um usuário
    ---
    tags:
      - Usuários
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID do usuário a ser bloqueado
    responses:
      200:
        description: Usuário bloqueado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do usuário é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'blockUser',
                {'user_id': user_id}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Usuário bloqueado com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao bloquear usuário: {str(e)}'
        }), 500

@users_bp.route('/unblock/<int:user_id>', methods=['POST'])
@api_key_required
def unblock_user(user_id):
    """
    Desbloqueia um usuário
    ---
    tags:
      - Usuários
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID do usuário a ser desbloqueado
    responses:
      200:
        description: Usuário desbloqueado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do usuário é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'unblockUser',
                {'user_id': user_id}
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Usuário desbloqueado com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao desbloquear usuário: {str(e)}'
        }), 500

@users_bp.route('/profile_photos/<int:user_id>', methods=['GET'])
@api_key_required
def get_user_profile_photos(user_id):
    """
    Obtém as fotos de perfil de um usuário
    ---
    tags:
      - Usuários
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID do usuário
      - name: offset
        in: query
        type: integer
        required: false
        description: Offset para paginação (padrão 0)
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de resultados (padrão 100, máximo 100)
    responses:
      200:
        description: Fotos de perfil do usuário
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do usuário é obrigatório'
            }), 400
            
        offset = int(request.args.get('offset', 0))
        limit = min(int(request.args.get('limit', 100)), 100)
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(tdlib_service.execute(
                'getUserProfilePhotos',
                {'user_id': user_id, 'offset': offset, 'limit': limit}
            ))
            
            return jsonify({
                'status': 'success',
                'photos': result.get('photos', []),
                'total_count': result.get('total_count', 0)
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter fotos de perfil: {str(e)}'
        }), 500 