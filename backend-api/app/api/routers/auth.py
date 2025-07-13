from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.security import create_access_token
from app.schemas.token import Token
from datetime import timedelta

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Genera un token JWT.
    En un sistema real, aquí verificarías el usuario y contraseña contra la BD.
    Por simplicidad, usamos un usuario y contraseña fijos.
    """
    # DEMO: Hardcoded user/password
    if not (form_data.username == "admin" and form_data.password == "string"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}