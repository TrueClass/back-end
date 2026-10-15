import mysql.connector
from mysql.connector import errorcode
from app.core.security import password_hasher
from . import models
from ..institution.service import ensure_email_allowed
from ..exceptions import UserAlreadyExistsError, InstitutionDoesntExistError

def create_new_student(institution_id: int, data, db):
    ensure_email_allowed(institution_id, data.email, db)

    hashed_password = password_hasher.hash(data.password)
    cursor = db.cursor()
    try:
        cursor.execute(models.STUDENT_INSERT_QUERY, (institution_id, data.email, hashed_password))
        db.commit()
        return {"id": cursor.lastrowid}
    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise UserAlreadyExistsError()
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            raise InstitutionDoesntExistError()
        raise err
    finally:
        cursor.close()

def get_student_by_institution(institution_id: int, limit: int, page: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.STUDENT_SELECT_QUERY, (institution_id, limit, limit * (page - 1)))
        students = cursor.fetchall()

        cursor.execute(models.STUDENT_COUNT_QUERY, (institution_id,))
        total = cursor.fetchone()["count"]

        return (total, students)
    finally:
        cursor.close()
