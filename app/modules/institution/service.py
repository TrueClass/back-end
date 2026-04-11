import mysql.connector
from mysql.connector import errorcode
from argon2 import PasswordHasher, Type
from . import models

def create_new_institution(name: str, db) -> object:
    """
    Consume a new student info sent from a POST API request and store it on mySQL. Returns the created institution's code.
    """
    cursor = db.cursor()
    values = (name,)

    try:
        cursor.execute(models.INSTITUTION_INSERT_QUERY,values)
        db.commit()
        return { "id": cursor.lastrowid }
    
    finally:
        cursor.close()

def obtain_institution(db) -> list:
    """
    Returns a list of institution, containing id and name for each of them
    """
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(models.INSTITUTION_OBTAIN_QUERY)
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()

def create_new_student(institution_id: int, data: object, db) -> object:
    """
    Consume a new student info sent from a POST API request, prepare it, store it on mySQL and return a message.
    """
    hashed_password = passwordHash(data.password)

    cursor = db.cursor()
    values = (institution_id, data.email, hashed_password)

    try:
        cursor.execute(models.STUDENT_INSERT_QUERY,values)
        db.commit()
        return { "id": cursor.lastrowid }

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise UserAlreadyExistsError()
        raise err
    finally:
        cursor.close()

def passwordHash(password):
    """
    Hash the password provided by the student by using argon2.
    """
    ph = PasswordHasher(
        memory_cost=65536,
        time_cost=4,
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )

    return ph.hash(password)

# Personalized errors
class UserAlreadyExistsError(Exception):
    """Raised when there's already an account created with the e-mail informed"""
    pass