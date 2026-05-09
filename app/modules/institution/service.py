import mysql.connector
from mysql.connector import errorcode
from argon2 import PasswordHasher, Type
from . import models
from datetime import timedelta
from fastapi import HTTPException

def create_new_institution(data: object, db) -> object:
    """
    Consume a new student info sent from a POST API request and store it on mySQL, iterate through emails recieved and insert them on database.
    Returns the created institution's code.
    """

    cursor = db.cursor()
    value = (data.name,)

    try:
        cursor.execute(models.INSTITUTION_INSERT_QUERY,value)
        db.commit()

        institution_id = cursor.lastrowid

        value_list = []

        for email in data.emails:
            value = (institution_id, email)
            value_list.append(value)
        
        print(value_list)

        cursor.executemany(models.INSTITUTION_EMAIL_INSERT_QUERY, value_list)
        db.commit()

        return { "id": institution_id }
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
        for institution in result:
            iteration = 0
            emails_as_string = institution["emails"]
            institution["emails"] = [email.strip() for email in emails_as_string.split(",")]
            result[iteration] = institution
            iteration = iteration + 1
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
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            raise InstitutionDoesntExistError()
        raise err
    finally:
        cursor.close()


def link_class_student(user_id, class_id, db):
    cursor = db.cursor(dictionary=True)

    try:

        # validate if class exist
        cursor.execute(models.VALIDATE_CLASS_ID_QUERY, (class_id,))

        existing_class = cursor.fetchone()

        if not existing_class:
            raise HTTPException(
                status_code=404,
                detail="Class not found"
            )

        # validate if student is alredy linked
        cursor.execute(models.VALIDATE_STUDENT_CLASS_LINK_QUERY, (user_id, class_id))
        existing_link = cursor.fetchone()

        if existing_link:
            raise HTTPException(
                status_code=409,
                detail="Student already linked to this class"
            )

        # create link
        values = (user_id, class_id)
        cursor.execute(models.STUDENT_CLASS_LINK_QUERY, values)
        db.commit()

        return {
            "id": cursor.lastrowid,
            "linked": True
        }

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
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

def get_student_by_institution(institution_id: int, limit: int, page: int, db):
    """
    Get students based on their institution_id. Limit the result of the query based on limit and page.
    """
    cursor = db.cursor(dictionary=True)
    values = (institution_id, limit, limit*(page-1))

    cursor.execute(models.STUDENT_SELECT_QUERY,values)
    students = cursor.fetchall()

    cursor.execute(models.STUDENT_COUNT_QUERY,(institution_id,))
    total = cursor.fetchone()['count']

    return (total, students)

def create_new_professor(institution_id: int, data: object, db):
    """
    Consume a new professor info sent from a POST API request, prepare it, store it on mySQL and return a message.
    """
    cursor = db.cursor(dictionary=True)

    #Transforms boolean to int
    if data.is_coordinator:
        tinyint_is_coordinator = 1
    else:
        tinyint_is_coordinator = 0

    #If there's an coordination_id informed
    if data.coordinator_id:
        #Check if id informed is actually an coordinator
        cursor.execute(models.CHECK_COORDINATOR_QUERY, (data.coordinator_id,))
        is_coodinator_valid = cursor.fetchone()

        if not is_coodinator_valid:
            cursor.close()
            raise CoordinatorDoesntExistError()
    
    #Sets the rest of the informations
    hashed_password = passwordHash(data.password)
    values = (institution_id, data.name, data.email, hashed_password, tinyint_is_coordinator)
    
    try:
        #Inserting professor on database
        cursor.execute(models.PROFESSOR_INSERT_QUERY, values)
        db.commit()
        professor_id = cursor.lastrowid

        if data.coordinator_id:
            #Inserting coordinator_professor relation on database 
            cursor.execute(models.COORDINATOR_PROFESSOR_INSERT_QUERY,(professor_id, data.coordinator_id))
            db.commit()

        return { "id": professor_id }
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            raise UserAlreadyExistsError()
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            raise InstitutionDoesntExistError()
        raise err
    finally:
        cursor.close()

def get_professor_by_institution(institution_id: int, limit: int, page: int, db):
    """
    Get professors based on their institution_id. Limit the result of the query based on limit and page.
    """
    cursor = db.cursor(dictionary=True)
    cursor.execute(models.PROFESSOR_COUNT_QUERY, (institution_id,))
    total = cursor.fetchone()['count']

    values = (institution_id, limit, limit*(page-1))
    cursor.execute(models.PROFESSOR_GET_QUERY, values)
    professors = cursor.fetchall()

    return (total, professors)


def calculate_dates(start_date, end_date, is_biweekly, biweekly_week=None) -> list:
    all_weeks = []

    # Weekly class
    if not is_biweekly:
        current = start_date
        while start_date <= end_date:
            all_weeks.append(current)
            current += timedelta(days=7)
        return all_weeks

    # biweekly A
    if biweekly_week == "A":
        current = start_date
    # biweekly B
    elif biweekly_week == "B":
        current = start_date + timedelta(days=7)
    else:
        raise ValueError("biweekly_week must be 'A' or 'B'")

    while current <= end_date:
        all_weeks.append(current)
        current += timedelta(days=14)

    return all_weeks


def create_new_class(data: object, user_id: int, db) -> object:
    cursor = db.cursor(dictionary=True)
    try:
        dates = calculate_dates(
            data.start_date,
            data.end_date,
            data.is_biweekly,
            data.biweekly_week
        )
        biweekly = 1 if data.is_biweekly else 0
        values = (
            data.subject,
            biweekly,
            data.biweekly_week,
            user_id
        )
        cursor.execute(models.CLASS_INSERT_QUERY, values)
        class_id = cursor.lastrowid

        values = [(str(class_date), class_id) for class_date in dates]
        cursor.executemany(models.CLASS_ITEM_INSERT_QUERY, values)

        db.commit()
        return {"id": class_id, "subject": data.subject}
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()


def get_classes(user_id: int, role: str, db):
    cursor = db.cursor(dictionary=True)
    try:
        if role == "student":
            cursor.execute(models.CLASS_GET_BY_STUDENT_QUERY, (user_id,))
        else:
            cursor.execute(models.CLASS_GET_BY_PROFESSOR_QUERY, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        cursor.close()


def get_class_items(class_id: int, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.CLASS_ITEMS_GET_QUERY, (class_id,))
        rows = cursor.fetchall()
        return [row["date"] for row in rows]
    finally:
        cursor.close()

# Personalized errors
class UserAlreadyExistsError(Exception):
    """Raised when there's already an account created with the e-mail informed"""
    pass

class CoordinatorDoesntExistError(Exception):
    """Raised when coordinator_id informed on professor creation doesn't exist or isn't a coordinator"""
    pass

class InstitutionDoesntExistError(Exception):
    """Raised when institution_id does not represent any institution"""
    pass

class UserNotFoundError(Exception):
    """Raised when user is not founded"""
    pass