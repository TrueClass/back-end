import json
import mysql.connector
from mysql.connector import errorcode
from fastapi import HTTPException
from datetime import date
from app.core.security import password_hasher
from . import models
from ..exceptions import (
    UserAlreadyExistsError, InstitutionDoesntExistError, CoordinatorDoesntExistError,
    ProfessorHasNoRatingsError, ThemesUpToDateError
)

THEMES_GENERATION_STALE_SECONDS = 600

def create_new_professor(institution_id: int, data, coordinator_id: int | None, db):
    hashed_password = password_hasher.hash(data.password)
    cursor = db.cursor(dictionary=True)

    try:
        if coordinator_id:
            cursor.execute(models.CHECK_COORDINATOR_QUERY, (coordinator_id, institution_id))
            if not cursor.fetchone():
                raise CoordinatorDoesntExistError()

        role = "coordinator" if data.is_coordinator else "professor"
        cursor.execute(models.PROFESSOR_INSERT_QUERY, (institution_id, data.email, hashed_password, role))
        professor_id = cursor.lastrowid

        cursor.execute(models.PROFESSOR_PROFILE_INSERT_QUERY, (professor_id, data.name, int(data.is_coordinator)))

        if coordinator_id:
            cursor.execute(models.COORDINATOR_PROFESSOR_INSERT_QUERY, (professor_id, coordinator_id))

        db.commit()
        return {"id": professor_id}
    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise UserAlreadyExistsError()
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            raise InstitutionDoesntExistError()
        raise err
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def get_professor_by_institution(institution_id: int, limit: int, page: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.PROFESSOR_COUNT_QUERY, (institution_id,))
        total = cursor.fetchone()["count"]

        cursor.execute(models.PROFESSOR_GET_QUERY, (institution_id, limit, limit * (page - 1)))
        professors = cursor.fetchall()

        return (total, professors)
    finally:
        cursor.close()

def get_professors_by_coordinator(coordinator_id: int, institution_id: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.PROFESSORS_BY_COORDINATOR_QUERY, (coordinator_id, institution_id))
        return cursor.fetchall()
    finally:
        cursor.close()

def get_viewable_professor(institution_id: int, professor_id: int, payload: dict, db) -> dict:
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.PROFESSOR_PROFILE_QUERY, (professor_id, institution_id))
        professor = cursor.fetchone()
        if not professor:
            raise HTTPException(status_code=404, detail="Professor não encontrado")

        user_id = int(payload["sub"])
        if user_id != professor_id:
            cursor.execute(models.IS_SUPERVISOR_QUERY, (professor_id, user_id))
            if not payload.get("coord") or not cursor.fetchone():
                raise HTTPException(status_code=403, detail="Usuário não autorizado")
        return professor
    finally:
        cursor.close()

def get_professor_classes(institution_id: int, professor_id: int, payload: dict, db):
    professor = get_viewable_professor(institution_id, professor_id, payload, db)
    current_date = date.today()

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.PROFESSOR_CLASSES_QUERY, (current_date, current_date, professor_id))
        return {"professor": professor, "classes": cursor.fetchall()}
    finally:
        cursor.close()

def get_professor_feedbacks(institution_id: int, professor_id: int, limit: int, payload: dict, db):
    get_viewable_professor(institution_id, professor_id, payload, db)

    cursor = db.cursor(dictionary=True)
    try:
        result = {}
        for key, query in (
            ("most_boosted", models.FEEDBACKS_MOST_BOOSTED_QUERY),
            ("highest_rating", models.FEEDBACKS_HIGHEST_QUERY),
            ("lowest_rating", models.FEEDBACKS_LOWEST_QUERY),
        ):
            cursor.execute(query, (professor_id, limit))
            result[key] = cursor.fetchall()
        return result
    finally:
        cursor.close()

def _read_themes_status(professor_id: int, cursor):
    cursor.execute(models.PROFESSOR_RATINGS_COUNT, (professor_id,))
    total = cursor.fetchone()["count"]

    cursor.execute(models.PROFESSOR_THEMES, (THEMES_GENERATION_STALE_SECONDS, professor_id))
    stored = cursor.fetchone()
    generating = bool(stored and stored["generating"])
    if not stored or stored["ai_themes"] is None:
        return {"snapshot": None, "generating": generating}, total

    return {
        "snapshot": {
            **json.loads(stored["ai_themes"]),
            "rating_count": stored["ai_themes_rating_count"],
            "created_at": stored["ai_themes_created_at"],
            "up_to_date": stored["ai_themes_rating_count"] == total,
        },
        "generating": generating,
    }, total

def get_professor_themes(institution_id: int, professor_id: int, payload: dict, db):
    get_viewable_professor(institution_id, professor_id, payload, db)

    cursor = db.cursor(dictionary=True)
    try:
        status, _ = _read_themes_status(professor_id, cursor)
        return status
    finally:
        cursor.close()

def request_professor_themes(institution_id: int, professor_id: int, payload: dict, db) -> tuple[dict, bool]:
    get_viewable_professor(institution_id, professor_id, payload, db)

    cursor = db.cursor(dictionary=True)
    try:
        status, total = _read_themes_status(professor_id, cursor)
        if total == 0:
            raise ProfessorHasNoRatingsError()
        if status["snapshot"] and status["snapshot"]["up_to_date"]:
            raise ThemesUpToDateError()

        cursor.execute(models.CLAIM_THEMES_GENERATION, (professor_id, THEMES_GENERATION_STALE_SECONDS))
        claimed = cursor.rowcount == 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

    return {**status, "generating": True}, claimed
