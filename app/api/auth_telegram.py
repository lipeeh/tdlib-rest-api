from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel
from typing import Dict, Optional

from app.core.tdlib_wrapper import tg
from app.api.auth import verify_token

router = APIRouter()

class PhoneNumberRequest(BaseModel):
    phone_number: str
    
class AuthCodeRequest(BaseModel):
    code: str
    
class PasswordRequest(BaseModel):
    password: str

class TelegramConfigRequest(BaseModel):
    api_id: str
    api_hash: str

@router.post("/set_phone", response_model=Dict)
async def set_phone_number(
    request: PhoneNumberRequest,
    user_data: Dict = Depends(verify_token)
):
    """Inicia o processo de autenticação no Telegram enviando o número de telefone."""
    try:
        result = await tg.call_method(
            method_name='setAuthenticationPhoneNumber',
            params={
                'phone_number': request.phone_number
            }
        )
        
        return {
            "success": True,
            "next_step": "code_verification",
            "auth_state": result.get("@type", "unknown")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao configurar número de telefone: {str(e)}"
        )

@router.post("/verify_code", response_model=Dict)
async def verify_auth_code(
    request: AuthCodeRequest,
    user_data: Dict = Depends(verify_token)
):
    """Verifica o código de autenticação enviado por SMS ou Telegram."""
    try:
        result = await tg.check_authentication_code(request.code)
        
        return {
            "success": True,
            "auth_state": result.get("@type", "unknown"),
            "message": "Código verificado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar código: {str(e)}"
        )

@router.post("/verify_password", response_model=Dict)
async def verify_password(
    request: PasswordRequest,
    user_data: Dict = Depends(verify_token)
):
    """Verifica a senha de autenticação de duas etapas, se necessário."""
    try:
        result = await tg.check_authentication_password(request.password)
        
        return {
            "success": True,
            "auth_state": result.get("@type", "unknown"),
            "message": "Senha verificada com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar senha: {str(e)}"
        )

@router.get("/status", response_model=Dict)
async def get_auth_status(
    user_data: Dict = Depends(verify_token)
):
    """Verifica o estado atual da autenticação do Telegram."""
    try:
        is_ready = getattr(tg, 'is_authorized', False)
        auth_state = getattr(tg, 'auth_state', None)
        
        return {
            "is_authorized": is_ready,
            "auth_state": auth_state
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar status de autenticação: {str(e)}"
        )

@router.post("/logout", response_model=Dict)
async def logout(
    user_data: Dict = Depends(verify_token)
):
    """Faz logout da sessão atual do Telegram."""
    try:
        result = await tg.call_method(
            method_name='logOut',
            params={}
        )
        
        return {
            "success": True,
            "message": "Logout realizado com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer logout: {str(e)}"
        )

@router.post("/configure", response_model=Dict)
async def configure_telegram(
    config: TelegramConfigRequest,
    user_data: Dict = Depends(verify_token)
):
    """Configura as credenciais API do Telegram (API ID e Hash)."""
    try:
        # Atualiza as configurações do cliente TDLib
        result = await tg.call_method(
            method_name='setTdlibParameters',
            params={
                'api_id': config.api_id,
                'api_hash': config.api_hash,
                'database_directory': tg.database_directory,
                'files_directory': tg.files_directory,
                'use_message_database': True,
                'use_secret_chats': True,
                'system_language_code': 'pt-br',
                'device_model': 'API Server',
                'application_version': '1.0.0',
                'enable_storage_optimizer': True
            }
        )
        
        return {
            "success": True,
            "message": "Configuração atualizada com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao configurar cliente Telegram: {str(e)}"
        ) 