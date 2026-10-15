import secrets
import mysql.connector
from mysql.connector import errorcode
from app.core.class_access import get_accessible_class
from . import models
from fastapi import HTTPException
from datetime import date, timedelta

JOIN_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
JOIN_CODE_LENGTH = 6
JOIN_CODE_ATTEMPTS = 5

def generate_join_code() -> str:
    return "".join(secrets.choice(JOIN_CODE_ALPHABET) for _ in range(JOIN_CODE_LENGTH))

def calculate_class_dates(start_date: date, end_date: date, frequency: str) -> list[date]:
    if frequency == "weekly":
        current, step = start_date, timedelta(weeks=1)
    elif frequency == "biweekly_a":
        current, step = start_date, timedelta(weeks=2)
    elif frequency == "biweekly_b":
        current, step = start_date + timedelta(weeks=1), timedelta(weeks=2)
    else:
        raise HTTPException(status_code=400, detail="Frequência inválida")

    dates = []
    while current <= end_date:
        dates.append(current)
        current += step
    return dates

def link_class_student(user_id: int, institution_id: int, code: str, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CLASS_BY_JOIN_CODE_QUERY, (code.strip().upper(), institution_id))
        existing_class = cursor.fetchone()
        if not existing_class:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        class_id = existing_class["id"]

        cursor.execute(models.VALIDATE_STUDENT_CLASS_LINK_QUERY, (user_id, class_id))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Aluno já matriculado nesta turma")

        cursor.execute(models.STUDENT_CLASS_LINK_QUERY, (user_id, class_id))
        db.commit()
        return {"id": cursor.lastrowid, "class_id": class_id, "linked": True}
    except HTTPException:
        raise
    except mysql.connector.IntegrityError as err:
        db.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise HTTPException(status_code=409, detail="Aluno já matriculado nesta turma")
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def _insert_class(cursor, data, user_id: int, institution_id: int) -> tuple[int, str]:
    for _ in range(JOIN_CODE_ATTEMPTS):
        join_code = generate_join_code()
        try:
            cursor.execute(models.CLASS_INSERT_QUERY, (data.subject, user_id, institution_id, data.class_name, join_code))
            return cursor.lastrowid, join_code
        except mysql.connector.IntegrityError as err:
            if err.errno != errorcode.ER_DUP_ENTRY:
                raise
    raise RuntimeError("Não foi possível gerar um código de turma único")

def create_new_class(data, user_id: int, institution_id: int, db):
    dates = calculate_class_dates(data.start_date, data.end_date, data.frequency)
    if not dates:
        raise HTTPException(status_code=400, detail="Nenhuma aula gerada para o período e frequência informados")

    cursor = db.cursor(dictionary=True)
    try:
        class_id, join_code = _insert_class(cursor, data, user_id, institution_id)

        titles = data.titles[:len(dates)]
        while len(titles) < len(dates):
            titles.append(f"Aula {len(titles) + 1}")

        values = [(str(d), class_id, titles[i] or f"Aula {i + 1}") for i, d in enumerate(dates)]
        cursor.executemany(models.CLASS_ITEM_INSERT_QUERY, values)

        db.commit()
        return {"id": class_id, "subject": data.subject, "join_code": join_code}
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def get_classes(payload, db):
    user_id = int(payload.get("sub"))
    role = payload.get("role")
    current_date = date.today()

    cursor = db.cursor(dictionary=True)
    try:
        if role == "student":
            cursor.execute(models.CLASS_GET_BY_STUDENT_QUERY, (current_date, current_date, user_id))
        elif role == "professor":
            cursor.execute(models.CLASS_GET_BY_PROFESSOR_QUERY, (current_date, current_date, user_id))
        else:
            raise HTTPException(status_code=403, detail="Perfil inválido")
        return cursor.fetchall()
    finally:
        cursor.close()

def get_class_items(class_id: int, payload: dict, db):
    access = get_accessible_class(class_id, payload, db)

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CLASS_INFO_QUERY, (class_id,))
        info = cursor.fetchone()
        if access["professor_id"] != int(payload["sub"]):
            info["join_code"] = None

        cursor.execute(models.CLASS_ITEMS_GET_QUERY, (int(payload["sub"]), class_id))
        return {"info": info, "dates": cursor.fetchall()}
    finally:
        cursor.close()
