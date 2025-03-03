from fastapi import APIRouter, HTTPException, Depends, status, Query, File, UploadFile, Form
from typing import Dict, List, Optional
import os
import aiofiles
import uuid

from app.core.tdlib_wrapper import tg
from app.api.auth import verify_token

router = APIRouter()

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

@router.delete("/{chat_id}/{message_id}", response_model=Dict)
async def delete_message(
    chat_id: int,
    message_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Deleta uma mensagem de um chat."""
    try:
        result = await tg.call_method(
            method_name='deleteMessages',
            params={
                'chat_id': chat_id,
                'message_ids': [message_id],
                'revoke': True
            }
        )
        
        return {
            "success": True
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
                'send_copy': False,
                'remove_caption': False
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