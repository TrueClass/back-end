from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from . import service, schemas

# Criando uma instância do APIRouter, prefix diz que a todas as rotas começam com students e tags 
router = APIRouter(prefix="/login", tags=["Alunos"])

@router.post("/", response_model=schemas.StudentCreateResponse, status_code=200)
async def login(login_in: schemas.Login, db = Depends(get_db)):
    try:
        login_data = service.authenticate_user(login_in,db)
        return {"access_token" : login_data, "token_type" : "bearer" }
    except service.UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")