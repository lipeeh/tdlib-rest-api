from fastapi import APIRouter, HTTPException, Depends, status, Query, File, UploadFile, Response
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
import os
import aiofiles
import uuid
from pathlib import Path

from app.core.tdlib_wrapper import tg
from app.api.auth import verify_token

router = APIRouter()

@router.post("/upload", response_model=Dict)
async def upload_file(
    file: UploadFile = File(...),
    user_data: Dict = Depends(verify_token)
):
    """Upload de um arquivo para uso posterior no Telegram."""
    try:
        # Cria diretório para arquivos temporários se não existir
        temp_dir = os.path.join(os.environ.get("TD_FILES_DIRECTORY", "./td_files"), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Gera um nome único para o arquivo
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else f"{uuid.uuid4()}"
        file_path = os.path.join(temp_dir, unique_filename)
        
        # Salva o arquivo
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Registra o arquivo no TDLib
        result = await tg.call_method(
            method_name='uploadFile',
            params={
                'file': {
                    '@type': 'inputFileLocal',
                    'path': file_path
                },
                'file_type': {
                    '@type': 'fileTypeDocument'
                },
                'priority': 1
            }
        )
        
        return {
            "success": True,
            "file_id": result.get("id", 0),
            "temp_path": file_path,
            "original_name": file.filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload do arquivo: {str(e)}"
        )

@router.get("/{file_id}", response_model=Dict)
async def get_file_info(
    file_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Obtém informações sobre um arquivo pelo seu ID."""
    try:
        result = await tg.call_method(
            method_name='getFile',
            params={
                'file_id': file_id
            }
        )
        
        return {
            "success": True,
            "file": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter informações do arquivo: {str(e)}"
        )

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Baixa um arquivo do Telegram pelo seu ID."""
    try:
        # Obtém informações do arquivo
        file_info = await tg.call_method(
            method_name='getFile',
            params={
                'file_id': file_id
            }
        )
        
        # Verifica se o arquivo está disponível localmente
        if not file_info.get("local", {}).get("is_downloading_completed", False):
            # Solicita o download
            await tg.call_method(
                method_name='downloadFile',
                params={
                    'file_id': file_id,
                    'priority': 1,
                    'offset': 0,
                    'limit': 0,
                    'synchronous': True
                }
            )
            
            # Obtém as informações atualizadas após o download
            file_info = await tg.call_method(
                method_name='getFile',
                params={
                    'file_id': file_id
                }
            )
        
        # Verifica se o download foi concluído
        if not file_info.get("local", {}).get("is_downloading_completed", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo não disponível para download"
            )
        
        # Caminho do arquivo local
        file_path = file_info.get("local", {}).get("path", "")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo não encontrado no sistema"
            )
        
        # Determina o tipo de conteúdo com base na extensão do arquivo
        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=None  # Autodeteção do tipo de conteúdo
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao baixar arquivo: {str(e)}"
        )

@router.delete("/{file_id}", response_model=Dict)
async def delete_file(
    file_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Deleta um arquivo temporário."""
    try:
        # Obtém informações do arquivo
        file_info = await tg.call_method(
            method_name='getFile',
            params={
                'file_id': file_id
            }
        )
        
        # Caminho do arquivo local
        file_path = file_info.get("local", {}).get("path", "")
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove o arquivo do TDLib
        await tg.call_method(
            method_name='deleteFile',
            params={
                'file_id': file_id
            }
        )
        
        return {
            "success": True,
            "message": "Arquivo excluído com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir arquivo: {str(e)}"
        )

@router.post("/send_document/{chat_id}", response_model=Dict)
async def send_document(
    chat_id: int,
    file_id: int = Query(...),
    caption: str = Query(""),
    user_data: Dict = Depends(verify_token)
):
    """Envia um documento para um chat usando um arquivo previamente carregado."""
    try:
        result = await tg.call_method(
            method_name='sendMessage',
            params={
                'chat_id': chat_id,
                'input_message_content': {
                    '@type': 'inputMessageDocument',
                    'document': {
                        '@type': 'inputFileId',
                        'id': file_id
                    },
                    'caption': {
                        '@type': 'formattedText',
                        'text': caption
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
            detail=f"Erro ao enviar documento: {str(e)}"
        ) 