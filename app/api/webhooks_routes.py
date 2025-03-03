#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, current_app
from app.api.auth_middleware import api_key_required
from app.webhooks.webhook_service import webhook_service
import asyncio

# Criar o blueprint para webhooks
webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/config', methods=['POST'])
@api_key_required
def configure_webhook():
    """
    Configura a URL do webhook para receber notificações
    ---
    tags:
      - Webhooks
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              description: URL para enviar as notificações de webhook
            enabled:
              type: boolean
              description: Se o webhook está habilitado ou não
            events:
              type: array
              items:
                type: string
              description: Lista de eventos a serem notificados (ex. message, user, chat)
    responses:
      200:
        description: Webhook configurado com sucesso
      400:
        description: Parâmetros inválidos
      500:
        description: Erro interno
    """
    try:
        data = request.json
        
        if not data or 'url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'URL do webhook é obrigatória'
            }), 400
            
        url = data['url']
        enabled = data.get('enabled', True)
        events = data.get('events', [])
        
        # Configurar o serviço de webhook
        webhook_service.configure(
            webhook_url=url,
            events_filter=events,
            enabled=enabled
        )
        
        # Atualizar as configurações do aplicativo
        current_app.config['WEBHOOK_URL'] = url
        current_app.config['WEBHOOK_ENABLED'] = enabled
        current_app.config['WEBHOOK_EVENTS'] = events
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook configurado com sucesso',
            'config': {
                'url': url,
                'enabled': enabled,
                'events': events
            }
        })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao configurar webhook: {str(e)}'
        }), 500

@webhooks_bp.route('/status', methods=['GET'])
@api_key_required
def get_webhook_status():
    """
    Obtém o status atual do webhook
    ---
    tags:
      - Webhooks
    responses:
      200:
        description: Status do webhook
      500:
        description: Erro interno
    """
    try:
        return jsonify({
            'status': 'success',
            'webhook': {
                'url': webhook_service.webhook_url,
                'enabled': webhook_service.enabled,
                'events': list(webhook_service.events_filter) if webhook_service.events_filter else []
            }
        })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter status do webhook: {str(e)}'
        }), 500

@webhooks_bp.route('/test', methods=['POST'])
@api_key_required
def test_webhook():
    """
    Testa a conexão com a URL de webhook
    ---
    tags:
      - Webhooks
    responses:
      200:
        description: Resultado do teste
      500:
        description: Erro interno
    """
    try:
        # Testar a conexão
        success = webhook_service.test_connection()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Teste de webhook bem-sucedido'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Falha no teste de webhook. Verifique a URL e se o servidor está acessível.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao testar webhook: {str(e)}'
        }), 500

@webhooks_bp.route('/disable', methods=['POST'])
@api_key_required
def disable_webhook():
    """
    Desativa o webhook
    ---
    tags:
      - Webhooks
    responses:
      200:
        description: Webhook desativado com sucesso
      500:
        description: Erro interno
    """
    try:
        # Desativar o webhook
        webhook_service.enabled = False
        
        # Atualizar configuração do aplicativo
        current_app.config['WEBHOOK_ENABLED'] = False
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook desativado com sucesso'
        })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao desativar webhook: {str(e)}'
        }), 500 