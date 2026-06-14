import mysql.connector
from mysql.connector import errorcode
from argon2 import PasswordHasher, Type
from . import models
from ..exceptions import UserAlreadyExistsError, InstitutionDoesntExistError, CoordinatorDoesntExistError

password_hasher = PasswordHasher(
    memory_cost=65536,
    time_cost=4,
    parallelism=2,
    hash_len=32,
    type=Type.ID
)

def create_new_professor(institution_id: int, data, db):
    cursor = db.cursor(dictionary=True)

    if data.coordinator_id:
        cursor.execute(models.CHECK_COORDINATOR_QUERY, (data.coordinator_id,))
        if not cursor.fetchone():
            cursor.close()
            raise CoordinatorDoesntExistError()

    hashed_password = password_hasher.hash(data.password)

    try:
        values = (institution_id, data.email, hashed_password)
        if data.is_coordinator:
            value = value + ("coordinator",)
        else:
            value = value + ("professor",)

        cursor.execute(models.PROFESSOR_INSERT_QUERY, values)
        db.commit()
        professor_id = cursor.lastrowid

        cursor.execute(models.PROFESSOR_PROFILE_INSERT_QUERY, (professor_id, data.name, int(data.is_coordinator)))
        db.commit()

        if data.coordinator_id:
            cursor.execute(models.COORDINATOR_PROFESSOR_INSERT_QUERY, (professor_id, data.coordinator_id))
            db.commit()

        return {"id": professor_id}
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise UserAlreadyExistsError()
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            raise InstitutionDoesntExistError()
        raise err
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