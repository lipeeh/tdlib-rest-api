#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, send_file, current_app
from app.api.auth_middleware import api_key_required
from app.services.tdlib_service import tdlib_service
import asyncio
import os
import tempfile

# Criar o blueprint para mídia
media_bp = Blueprint('media', __name__)

@media_bp.route('/download/<int:file_id>', methods=['GET'])
@api_key_required
def download_file(file_id):
    """
    Faz o download de um arquivo do Telegram
    ---
    tags:
      - Mídia
    parameters:
      - name: file_id
        in: path
        type: integer
        required: true
        description: ID do arquivo a ser baixado
      - name: priority
        in: query
        type: integer
        required: false
        description: Prioridade do download (1-32, padrão 1)
    responses:
      200:
        description: Arquivo baixado com sucesso
      400:
        description: Parâmetros inválidos
      404:
        description: Arquivo não encontrado
      500:
        description: Erro interno
    """
    try:
        if not file_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do arquivo é obrigatório'
            }), 400
            
        priority = min(max(int(request.args.get('priority', 1)), 1), 32)
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Obter informações do arquivo
            file_info = loop.run_until_complete(tdlib_service.execute(
                'getFile',
                {
                    'file_id': file_id
                }
            ))
            
            if not file_info:
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo não encontrado'
                }), 404
                
            # Verificar se o arquivo já foi baixado
            if file_info.get('local', {}).get('is_downloading_completed', False):
                local_path = file_info.get('local', {}).get('path', '')
                if os.path.isfile(local_path):
                    return send_file(
                        local_path,
                        as_attachment=True,
                        attachment_filename=os.path.basename(local_path)
                    )
            
            # Iniciar o download do arquivo
            result = loop.run_until_complete(tdlib_service.execute(
                'downloadFile',
                {
                    'file_id': file_id,
                    'priority': priority,
                    'offset': 0,
                    'limit': 0,
                    'synchronous': True
                }
            ))
            
            if result and result.get('local', {}).get('is_downloading_completed', False):
                local_path = result.get('local', {}).get('path', '')
                if os.path.isfile(local_path):
                    return send_file(
                        local_path,
                        as_attachment=True,
                        attachment_filename=os.path.basename(local_path)
                    )
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Arquivo não encontrado no disco'
                    }), 404
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Não foi possível baixar o arquivo',
                    'download_info': result.get('local', {})
                }), 500
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao baixar arquivo: {str(e)}'
        }), 500

@media_bp.route('/status/<int:file_id>', methods=['GET'])
@api_key_required
def get_file_status(file_id):
    """
    Obtém o status de um arquivo
    ---
    tags:
      - Mídia
    parameters:
      - name: file_id
        in: path
        type: integer
        required: true
        description: ID do arquivo
    responses:
      200:
        description: Status do arquivo
      400:
        description: Parâmetros inválidos
      404:
        description: Arquivo não encontrado
      500:
        description: Erro interno
    """
    try:
        if not file_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do arquivo é obrigatório'
            }), 400
            
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Obter informações do arquivo
            file_info = loop.run_until_complete(tdlib_service.execute(
                'getFile',
                {
                    'file_id': file_id
                }
            ))
            
            if not file_info:
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo não encontrado'
                }), 404
                
            return jsonify({
                'status': 'success',
                'file_info': file_info
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter status do arquivo: {str(e)}'
        }), 500

@media_bp.route('/cancel/<int:file_id>', methods=['POST'])
@api_key_required
def cancel_file_download(file_id):
    """
    Cancela o download de um arquivo
    ---
    tags:
      - Mídia
    parameters:
      - name: file_id
        in: path
        type: integer
        required: true
        description: ID do arquivo
      - name: only_if_pending
        in: query
        type: boolean
        required: false
        description: Se true, cancela apenas se estiver pendente
    responses:
      200:
        description: Download cancelado com sucesso
      400:
        description: Parâmetros inválidos
      404:
        description: Arquivo não encontrado
      500:
        description: Erro interno
    """
    try:
        if not file_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do arquivo é obrigatório'
            }), 400
            
        only_if_pending = request.args.get('only_if_pending', 'false').lower() == 'true'
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Verificar se o arquivo existe
            file_info = loop.run_until_complete(tdlib_service.execute(
                'getFile',
                {
                    'file_id': file_id
                }
            ))
            
            if not file_info:
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo não encontrado'
                }), 404
                
            # Verificar se o arquivo está sendo baixado
            if only_if_pending and not file_info.get('local', {}).get('is_downloading_active', False):
                return jsonify({
                    'status': 'success',
                    'message': 'Arquivo não está sendo baixado'
                })
                
            # Cancelar o download
            result = loop.run_until_complete(tdlib_service.execute(
                'cancelDownloadFile',
                {
                    'file_id': file_id,
                    'only_if_pending': only_if_pending
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Download cancelado com sucesso'
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao cancelar download: {str(e)}'
        }), 500

@media_bp.route('/upload', methods=['POST'])
@api_key_required
def upload_file():
    """
    Faz o upload de um arquivo para o Telegram
    ---
    tags:
      - Mídia
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Arquivo a ser enviado
      - name: priority
        in: formData
        type: integer
        required: false
        description: Prioridade do upload (1-32, padrão 1)
    responses:
      200:
        description: Arquivo enviado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Nenhum arquivo enviado'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Nome do arquivo vazio'
            }), 400
            
        priority = min(max(int(request.form.get('priority', 1)), 1), 32)
        
        # Salvar o arquivo temporariamente
        temp_dir = current_app.config.get('UPLOAD_FOLDER', tempfile.gettempdir())
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file_path = os.path.join(temp_dir, file.filename)
        file.save(temp_file_path)
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Iniciar o upload do arquivo
            result = loop.run_until_complete(tdlib_service.execute(
                'uploadFile',
                {
                    'file': {
                        '@type': 'inputFileLocal',
                        'path': temp_file_path
                    },
                    'file_type': {
                        '@type': 'fileTypeDocument'
                    },
                    'priority': priority
                }
            ))
            
            return jsonify({
                'status': 'success',
                'message': 'Arquivo enviado com sucesso',
                'file_id': result.get('id', 0),
                'file_info': result
            })
        finally:
            loop.close()
            # Remover o arquivo temporário após o upload
            try:
                os.remove(temp_file_path)
            except:
                pass
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao fazer upload do arquivo: {str(e)}'
        }), 500

@media_bp.route('/profile-photos/<int:user_id>', methods=['GET'])
@api_key_required
def get_user_profile_photos(user_id):
    """
    Obtém as fotos de perfil de um usuário
    ---
    tags:
      - Mídia
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
        description: Índice da primeira foto a ser retornada (padrão 0)
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de fotos a serem retornadas (padrão 100, máximo 100)
    responses:
      200:
        description: Fotos de perfil obtidas com sucesso
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
            
        offset = max(int(request.args.get('offset', 0)), 0)
        limit = min(max(int(request.args.get('limit', 100)), 1), 100)
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Obter as fotos de perfil
            result = loop.run_until_complete(tdlib_service.execute(
                'getUserProfilePhotos',
                {
                    'user_id': user_id,
                    'offset': offset,
                    'limit': limit
                }
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

@media_bp.route('/thumbnail/<int:file_id>', methods=['GET'])
@api_key_required
def get_file_thumbnail(file_id):
    """
    Obtém a miniatura de um arquivo
    ---
    tags:
      - Mídia
    parameters:
      - name: file_id
        in: path
        type: integer
        required: true
        description: ID do arquivo
      - name: thumbnail_type
        in: query
        type: string
        required: false
        description: Tipo de miniatura (pequena, média, grande)
    responses:
      200:
        description: Miniatura obtida com sucesso
      400:
        description: Parâmetros inválidos
      404:
        description: Miniatura não encontrada
      500:
        description: Erro interno
    """
    try:
        if not file_id:
            return jsonify({
                'status': 'error',
                'message': 'ID do arquivo é obrigatório'
            }), 400
            
        thumbnail_type = request.args.get('thumbnail_type', 's')
        
        # Mapear tipos de miniatura
        thumbnail_format = 'thumbnailFormatJpeg'
        if thumbnail_type == 's':
            thumbnail_size = 'thumbnailSizeSmall'
        elif thumbnail_type == 'm':
            thumbnail_size = 'thumbnailSizeMedium'
        elif thumbnail_type == 'l':
            thumbnail_size = 'thumbnailSizeLarge'
        else:
            thumbnail_size = 'thumbnailSizeSmall'
        
        # Executar método de forma assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Obter informações do arquivo
            file_info = loop.run_until_complete(tdlib_service.execute(
                'getFile',
                {
                    'file_id': file_id
                }
            ))
            
            if not file_info:
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo não encontrado'
                }), 404
                
            # Obter miniatura
            result = loop.run_until_complete(tdlib_service.execute(
                'getFileThumbnail',
                {
                    'file_id': file_id,
                    'thumbnail_format': {
                        '@type': thumbnail_format
                    },
                    'thumbnail_size': {
                        '@type': thumbnail_size
                    }
                }
            ))
            
            if not result or not result.get('local', {}).get('path', ''):
                return jsonify({
                    'status': 'error',
                    'message': 'Miniatura não disponível'
                }), 404
                
            # Verificar se a miniatura foi baixada
            if result.get('local', {}).get('is_downloading_completed', False):
                local_path = result.get('local', {}).get('path', '')
                if os.path.isfile(local_path):
                    return send_file(
                        local_path,
                        mimetype='image/jpeg'
                    )
                
            # Baixar a miniatura se não estiver disponível localmente
            download_result = loop.run_until_complete(tdlib_service.execute(
                'downloadFile',
                {
                    'file_id': result.get('id', 0),
                    'priority': 1,
                    'offset': 0,
                    'limit': 0,
                    'synchronous': True
                }
            ))
            
            if download_result and download_result.get('local', {}).get('is_downloading_completed', False):
                local_path = download_result.get('local', {}).get('path', '')
                if os.path.isfile(local_path):
                    return send_file(
                        local_path,
                        mimetype='image/jpeg'
                    )
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Miniatura não encontrada no disco'
                    }), 404
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Não foi possível baixar a miniatura',
                    'download_info': download_result.get('local', {})
                }), 500
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter miniatura: {str(e)}'
        }), 500 