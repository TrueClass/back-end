from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from . import service, schemas

# Criando uma instância do APIRouter, prefix diz que a todas as rotas começam com students e tags 
router = APIRouter(prefix="/institution", tags=["Alunos"])

@router.post("/{institution_id}/student", response_model=schemas.StudentCreateResponse, status_code=201)
async def create_student(institution_id: int,student_in: schemas.StudentCreate, db = Depends(get_db)):
    try:
        new_student = service.create_new_student(institution_id, student_in, db)
        return new_student
    except service.UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")