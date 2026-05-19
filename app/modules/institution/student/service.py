import mysql.connector
from mysql.connector import errorcode
from argon2 import PasswordHasher, Type
from . import models
from ..exceptions import UserAlreadyExistsError, InstitutionDoesntExistError

password_hasher = PasswordHasher(
    memory_cost=65536,
    time_cost=4,
    parallelism=2,
    hash_len=32,
    type=Type.ID
)

def create_new_student(institution_id: int, data, db):
    hashed_password = password_hasher.hash(data.password)
    cursor = db.cursor()
    try:
        cursor.execute(models.STUDENT_INSERT_QUERY, (institution_id, data.email, hashed_password))
        db.commit()
        return {"id": cursor.lastrowid}
    except mysql.connector.Error as err:
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
