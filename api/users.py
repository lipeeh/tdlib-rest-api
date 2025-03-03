from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, List, Optional

from app.models.schemas import User, UserResponse
from app.core.tdlib_wrapper import tg, search_contacts
from app.api.auth import verify_token

router = APIRouter()

@router.get("/me", response_model=Dict)
async def get_current_user(
    user_data: Dict = Depends(verify_token)
):
    """Obtém informações do usuário atual."""
    try:
        result = await tg.call_method(
            method_name='getMe',
            params={}
        )
        
        return {
            "success": True,
            "user": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter informações do usuário: {str(e)}"
        )

@router.get("/{user_id}", response_model=Dict)
async def get_user_info(
    user_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Obtém informações de um usuário pelo ID."""
    try:
        result = await tg.call_method(
            method_name='getUser',
            params={
                'user_id': user_id
            }
        )
        
        return {
            "success": True,
            "user": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter informações do usuário: {str(e)}"
        )

@router.get("/search", response_model=Dict)
async def search_users(
    query: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    user_data: Dict = Depends(verify_token)
):
    """Pesquisa usuários pelo nome ou número de telefone."""
    try:
        result = await search_contacts(
            query=query,
            limit=limit
        )
        
        return {
            "success": True,
            "users": result.get("user_ids", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao pesquisar usuários: {str(e)}"
        )

@router.post("/contacts/add", response_model=Dict)
async def add_contact(
    first_name: str = Query(...),
    last_name: str = Query(""),
    phone_number: str = Query(...),
    user_data: Dict = Depends(verify_token)
):
    """Adiciona um contato a lista de contatos."""
    try:
        result = await tg.call_method(
            method_name='importContacts',
            params={
                'contacts': [
                    {
                        'phone_number': phone_number,
                        'first_name': first_name,
                        'last_name': last_name
                    }
                ]
            }
        )
        
        return {
            "success": True,
            "user_ids": result.get("user_ids", []),
            "message": "Contato adicionado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar contato: {str(e)}"
        )

@router.delete("/contacts/{user_id}", response_model=Dict)
async def remove_contact(
    user_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Remove um contato da lista de contatos."""
    try:
        await tg.call_method(
            method_name='removeContacts',
            params={
                'user_ids': [user_id]
            }
        )
        
        return {
            "success": True,
            "message": "Contato removido com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover contato: {str(e)}"
        )

@router.get("/contacts/list", response_model=Dict)
async def get_contacts(
    user_data: Dict = Depends(verify_token)
):
    """Obtém a lista de contatos."""
    try:
        result = await tg.call_method(
            method_name='getContacts',
            params={}
        )
        
        return {
            "success": True,
            "total_count": len(result.get("user_ids", [])),
            "contacts": result.get("user_ids", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter lista de contatos: {str(e)}"
        )

@router.post("/block/{user_id}", response_model=Dict)
async def block_user(
    user_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Bloqueia um usuário."""
    try:
        await tg.call_method(
            method_name='blockUser',
            params={
                'user_id': user_id
            }
        )
        
        return {
            "success": True,
            "message": "Usuário bloqueado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao bloquear usuário: {str(e)}"
        )

@router.post("/unblock/{user_id}", response_model=Dict)
async def unblock_user(
    user_id: int,
    user_data: Dict = Depends(verify_token)
):
    """Desbloqueia um usuário."""
    try:
        await tg.call_method(
            method_name='unblockUser',
            params={
                'user_id': user_id
            }
        )
        
        return {
            "success": True,
            "message": "Usuário desbloqueado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao desbloquear usuário: {str(e)}"
        ) 