from fastapi import APIRouter, HTTPException, Depends, status, Query, File, UploadFile, Form, Body, Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import os
import aiofiles
import uuid

from app.core.tdlib_wrapper import tg
from app.api.auth import verify_token

router = APIRouter()

class MessageContent(BaseModel):
    text: str
    
class MessageOptions(BaseModel):
    disable_notification: Optional[bool] = False
    from_background: Optional[bool] = False
    scheduling_state: Optional[Dict[str, Any]] = None

@router.post("/{chat_id}/send", response_model=Dict)
async def send_message(
    chat_id: int,
    text: str = Form(...),
    reply_to_message_id: Optional[int] = Form(0),
    user_data: Dict = Depends(verify_token)
):
    """Envia uma mensagem de texto para um chat."""
    try:
        result = await tg.call_method(
            method_name='sendMessage',
            params={
                'chat_id': chat_id,
                'reply_to_message_id': reply_to_message_id,
                'input_message_content': {
                    '@type': 'inputMessageText',
                    'text': {
                        '@type': 'formattedText',
                        'text': text
                    }
                }
            }
        )
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )

@router.post("/{chat_id}/send_json", response_model=Dict)
async def send_message_json(
    chat_id: int = Path(..., description="ID do chat para enviar a mensagem"),
    content: MessageContent = Body(..., description="Conteúdo da mensagem"),
    options: Optional[MessageOptions] = Body(None, description="Opções de envio"),
    reply_to_message_id: Optional[int] = Body(0, description="ID da mensagem para responder"),
    user_data: Dict = Depends(verify_token)
):
    """Envia uma mensagem de texto para um chat usando JSON."""
    try:
        params = {
            'chat_id': chat_id,
            'reply_to_message_id': reply_to_message_id,
            'input_message_content': {
                '@type': 'inputMessageText',
                'text': {
                    '@type': 'formattedText',
                    'text': content.text
                }
            }
        }
        
        # Adiciona opções se fornecidas
        if options:
            if options.disable_notification is not None:
                params['disable_notification'] = options.disable_notification
            if options.from_background is not None:
                params['from_background'] = options.from_background
            if options.scheduling_state:
                params['scheduling_state'] = options.scheduling_state
                
        result = await tg.call_method(
            method_name='sendMessage',
            params=params
        )
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar mensagem: {str(e)}"
        )

@router.post("/{chat_id}/send_photo", response_model=Dict)
async def send_photo(
    chat_id: int,
    photo: UploadFile = File(...),
    caption: Optional[str] = Form(""),
    reply_to_message_id: Optional[int] = Form(0),
    user_data: Dict = Depends(verify_token)
):
    """Envia uma foto para um chat."""
    try:
        # Salva o arquivo temporariamente
        temp_dir = os.path.join(os.environ.get("TD_FILES_DIRECTORY", "./td_files"), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{photo.filename}")
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await photo.read()
            await out_file.write(content)
        
        # Envia a foto
        result = await tg.call_method(
            method_name='sendMessage',
            params={
                'chat_id': chat_id,
                'reply_to_message_id': reply_to_message_id,
                'input_message_content': {
                    '@type': 'inputMessagePhoto',
                    'photo': {
                        '@type': 'inputFileLocal',
                        'path': file_path
                    },
                    'caption': {
                        '@type': 'formattedText',
                        'text': caption
                    }
                }
            }
        )
        
        # Remove o arquivo temporário
        os.remove(file_path)
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar foto: {str(e)}"
        )

@router.post("/{chat_id}/send_video", response_model=Dict)
async def send_video(
    chat_id: int,
    video: UploadFile = File(...),
    caption: Optional[str] = Form(""),
    reply_to_message_id: Optional[int] = Form(0),
    user_data: Dict = Depends(verify_token)
):
    """Envia um vídeo para um chat."""
    try:
        # Salva o arquivo temporariamente
        temp_dir = os.path.join(os.environ.get("TD_FILES_DIRECTORY", "./td_files"), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{video.filename}")
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await video.read()
            await out_file.write(content)
        
        # Envia o vídeo
        result = await tg.call_method(
            method_name='sendMessage',
            params={
                'chat_id': chat_id,
                'reply_to_message_id': reply_to_message_id,
                'input_message_content': {
                    '@type': 'inputMessageVideo',
                    'video': {
                        '@type': 'inputFileLocal',
                        'path': file_path
                    },
                    'caption': {
                        '@type': 'formattedText',
                        'text': caption
                    }
                }
            }
        )
        
        # Remove o arquivo temporário
        os.remove(file_path)
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar vídeo: {str(e)}"
        )

@router.get("/{chat_id}/history", response_model=Dict)
async def get_chat_history(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    from_message_id: int = Query(0),
    user_data: Dict = Depends(verify_token)
):
    """Obtém o histórico de mensagens de um chat."""
    try:
        result = await tg.call_method(
            method_name='getChatHistory',
            params={
                'chat_id': chat_id,
                'from_message_id': from_message_id,
                'offset': 0,
                'limit': limit,
                'only_local': False
            }
        )
        
        return {
            "success": True,
            "messages": result.get("messages", []),
            "total_count": result.get("total_count", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter histórico de mensagens: {str(e)}"
        )

@router.get("/{chat_id}/message/{message_id}", response_model=Dict)
async def get_message(
    chat_id: int,
    message_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Obtém informações de uma mensagem específica."""
    try:
        result = await tg.call_method(
            method_name='getMessage',
            params={
                'chat_id': chat_id,
                'message_id': message_id
            }
        )
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter mensagem: {str(e)}"
        )

@router.delete("/{chat_id}/{message_id}", response_model=Dict)
async def delete_message(
    chat_id: int,
    message_id: int,
    revoke: bool = Query(True, description="Apagar para todos os usuários, não apenas para si mesmo"),
    user_data: Dict = Depends(verify_token)
):
    """Deleta uma mensagem de um chat."""
    try:
        result = await tg.call_method(
            method_name='deleteMessages',
            params={
                'chat_id': chat_id,
                'message_ids': [message_id],
                'revoke': revoke
            }
        )
        
        return {
            "success": True,
            "message": "Mensagem excluída com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar mensagem: {str(e)}"
        )

@router.post("/{chat_id}/{message_id}/forward", response_model=Dict)
async def forward_message(
    chat_id: int,
    message_id: int,
    to_chat_id: int = Query(...),
    send_copy: bool = Query(False, description="Enviar como cópia em vez de encaminhar"),
    remove_caption: bool = Query(False, description="Remover legenda da mídia"),
    user_data: Dict = Depends(verify_token)
):
    """Encaminha uma mensagem para outro chat."""
    try:
        result = await tg.call_method(
            method_name='forwardMessages',
            params={
                'chat_id': to_chat_id,
                'from_chat_id': chat_id,
                'message_ids': [message_id],
                'send_copy': send_copy,
                'remove_caption': remove_caption
            }
        )
        
        return {
            "success": True,
            "messages": result.get("messages", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao encaminhar mensagem: {str(e)}"
        )

@router.post("/{chat_id}/{message_id}/edit", response_model=Dict)
async def edit_message(
    chat_id: int,
    message_id: int,
    text: str = Body(..., embed=True),
    user_data: Dict = Depends(verify_token)
):
    """Edita o texto de uma mensagem existente."""
    try:
        result = await tg.call_method(
            method_name='editMessageText',
            params={
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
        )
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao editar mensagem: {str(e)}"
        )

@router.post("/{chat_id}/pin/{message_id}", response_model=Dict)
async def pin_message(
    chat_id: int,
    message_id: int,
    disable_notification: bool = Query(False),
    user_data: Dict = Depends(verify_token)
):
    """Fixa uma mensagem em um chat."""
    try:
        result = await tg.call_method(
            method_name='pinChatMessage',
            params={
                'chat_id': chat_id,
                'message_id': message_id,
                'disable_notification': disable_notification
            }
        )
        
        return {
            "success": True,
            "message": "Mensagem fixada com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fixar mensagem: {str(e)}"
        )

@router.post("/{chat_id}/unpin/{message_id}", response_model=Dict)
async def unpin_message(
    chat_id: int,
    message_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Remove a fixação de uma mensagem em um chat."""
    try:
        result = await tg.call_method(
            method_name='unpinChatMessage',
            params={
                'chat_id': chat_id,
                'message_id': message_id
            }
        )
        
        return {
            "success": True,
            "message": "Fixação da mensagem removida com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover fixação da mensagem: {str(e)}"
        )

@router.get("/{chat_id}/pinned", response_model=Dict)
async def get_pinned_messages(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Obtém as mensagens fixadas em um chat."""
    try:
        result = await tg.call_method(
            method_name='getChatPinnedMessages',
            params={
                'chat_id': chat_id
            }
        )
        
        return {
            "success": True,
            "messages": result.get("messages", []),
            "total_count": result.get("total_count", 0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter mensagens fixadas: {str(e)}"
        ) 