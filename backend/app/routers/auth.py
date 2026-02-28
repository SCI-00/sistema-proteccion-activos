"""
Router de Autenticación - CORREGIDO
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.models.usuario import Usuario
from app.schemas import UserLogin, UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    try:
        # Verificar si email ya existe
        existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Hashear contraseña
        hashed_password = get_password_hash(user_data.password)
        
        # Crear usuario
        db_user = Usuario(
            nombre=user_data.nombre,
            email=user_data.email,
            password_hash=hashed_password,
            rol=user_data.rol,
            organizacion_id=user_data.organizacion_id,
            activo=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login de usuario"""
    try:
        # Buscar usuario
        user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar contraseña
        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.activo:
            raise HTTPException(status_code=400, detail="Usuario inactivo")
        
        # Actualizar último login
        user.ultimo_login = datetime.utcnow()
        db.commit()
        
        # Crear token
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en login: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Obtener usuario actual"""
    return current_user

@router.post("/logout")
def logout(current_user: Usuario = Depends(get_current_user)):
    """Logout (invalidar token en el cliente)"""
    return {"mensaje": "Logout exitoso"}
