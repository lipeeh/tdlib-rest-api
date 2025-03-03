from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, Optional
import os
import jwt
from datetime import datetime, timedelta
import secrets

router = APIRouter()

# Sistema simples de autenticação baseado em token para a API
API_SECRET_KEY = os.environ.get("API_SECRET_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "1440"))  # 24 horas por padrão

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token JWT."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Verifica e decodifica o token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise credentials_exception

@router.post("/token", response_model=Dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint para obter um token de acesso usando API_SECRET_KEY."""
    if form_data.username != "admin" or form_data.password != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria o token JWT
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "admin"}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_MINUTES * 60  # em segundos
    }

@router.get("/verify", response_model=Dict)
async def verify_token_endpoint(token_data: Dict = Depends(verify_token)):
    """Verifica se o token é válido."""
    return {
        "valid": True,
        "user": token_data.get("sub", "")
    } 