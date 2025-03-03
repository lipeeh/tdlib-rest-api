from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, List, Optional

from app.models.schemas import ChatListResponse, Chat
from app.core.tdlib_wrapper import tg, get_chats
from app.api.auth import verify_token

router = APIRouter()

@router.get("/list", response_model=Dict)
async def list_chats(
    limit: int = Query(100, ge=1, le=1000),
    offset_order: int = Query(2**63 - 1),
    offset_chat_id: int = Query(0),
    user_data: Dict = Depends(verify_token)
):
    """Lista os chats disponíveis."""
    try:
        result = await get_chats(
            limit=limit,
            offset_order=offset_order,
            offset_chat_id=offset_chat_id
        )
        
        return {
            "success": True,
            "total_count": result.get("total_count", 0),
            "chats": result.get("chat_ids", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar chats: {str(e)}"
        )

@router.get("/{chat_id}", response_model=Dict)
async def get_chat_info(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Obtém informações detalhadas de um chat."""
    try:
        result = await tg.call_method(
            method_name='getChat',
            params={
                'chat_id': chat_id
            }
        )
        
        return {
            "success": True,
            "chat": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter informações do chat: {str(e)}"
        )

@router.post("/create_group", response_model=Dict)
async def create_group_chat(
    title: str = Query(...),
    user_ids: List[int] = Query(...),
    user_data: Dict = Depends(verify_token)
):
    """Cria um novo grupo de chat."""
    try:
        result = await tg.call_method(
            method_name='createNewBasicGroupChat',
            params={
                'user_ids': user_ids,
                'title': title
            }
        )
        
        return {
            "success": True,
            "chat_id": result.get("id", 0),
            "message": "Grupo criado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar grupo: {str(e)}"
        )

@router.post("/join/{chat_id}", response_model=Dict)
async def join_chat(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Entra em um chat público ou canal."""
    try:
        await tg.call_method(
            method_name='joinChat',
            params={
                'chat_id': chat_id
            }
        )
        
        return {
            "success": True,
            "message": "Entrou no chat com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao entrar no chat: {str(e)}"
        )

@router.post("/leave/{chat_id}", response_model=Dict)
async def leave_chat(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Sai de um chat."""
    try:
        await tg.call_method(
            method_name='leaveChat',
            params={
                'chat_id': chat_id
            }
        )
        
        return {
            "success": True,
            "message": "Saiu do chat com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao sair do chat: {str(e)}"
        )

@router.delete("/{chat_id}", response_model=Dict)
async def delete_chat(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Remove um chat da lista de chats."""
    try:
        # Primeiro obtém informações do chat para saber seu tipo
        chat_info = await tg.call_method(
            method_name='getChat',
            params={
                'chat_id': chat_id
            }
        )
        
        chat_type = chat_info.get("type", {}).get("@type", "")
        
        # Escolhe o método apropriado baseado no tipo de chat
        if chat_type == "chatTypePrivate":
            await tg.call_method(
                method_name='deleteChatHistory',
                params={
                    'chat_id': chat_id,
                    'remove_from_chat_list': True,
                    'revoke': False
                }
            )
        elif chat_type in ["chatTypeBasicGroup", "chatTypeSupergroup"]:
            # Primeiro sai do grupo
            await tg.call_method(
                method_name='leaveChat',
                params={
                    'chat_id': chat_id
                }
            )
            # Depois remove da lista
            await tg.call_method(
                method_name='deleteChatHistory',
                params={
                    'chat_id': chat_id,
                    'remove_from_chat_list': True,
                    'revoke': False
                }
            )
        
        return {
            "success": True,
            "message": "Chat removido com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover chat: {str(e)}"
        )

@router.get("/search", response_model=Dict)
async def search_chats(
    query: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    user_data: Dict = Depends(verify_token)
):
    """Pesquisa chats pelo título ou nome de usuário."""
    try:
        result = await tg.call_method(
            method_name='searchChats',
            params={
                'query': query,
                'limit': limit
            }
        )
        
        return {
            "success": True,
            "chats": result.get("chat_ids", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao pesquisar chats: {str(e)}"
        )

@router.post("/{chat_id}/pin", response_model=Dict)
async def pin_chat(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Fixa um chat no topo da lista."""
    try:
        await tg.call_method(
            method_name='toggleChatIsPinned',
            params={
                'chat_id': chat_id,
                'is_pinned': True
            }
        )
        
        return {
            "success": True,
            "message": "Chat fixado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fixar chat: {str(e)}"
        )

@router.post("/{chat_id}/unpin", response_model=Dict)
async def unpin_chat(
    chat_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Remove um chat do topo da lista."""
    try:
        await tg.call_method(
            method_name='toggleChatIsPinned',
            params={
                'chat_id': chat_id,
                'is_pinned': False
            }
        )
        
        return {
            "success": True,
            "message": "Chat removido dos fixados com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao desafixar chat: {str(e)}"
        ) 