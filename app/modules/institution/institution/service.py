from . import models

def create_new_institution(data, db):
    cursor = db.cursor()
    try:
        cursor.execute(models.INSTITUTION_INSERT_QUERY, (data.name,))
        db.commit()
        institution_id = cursor.lastrowid

        value_list = [(institution_id, email) for email in data.emails]
        cursor.executemany(models.INSTITUTION_EMAIL_INSERT_QUERY, value_list)
        db.commit()

        return {"id": institution_id}
    finally:
        cursor.close()

def obtain_institution(db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.INSTITUTION_OBTAIN_QUERY)
        result = cursor.fetchall()
        for institution in result:
            institution["emails"] = institution["emails"].split("|")
        return result
    finally:
        cursor.close()
