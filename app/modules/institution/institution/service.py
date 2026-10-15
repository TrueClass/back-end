from . import models
from ..exceptions import InstitutionDoesntExistError, EmailDomainNotAllowedError

def create_new_institution(data, db):
    cursor = db.cursor()
    try:
        cursor.execute(models.INSTITUTION_INSERT_QUERY, (data.name,))
        institution_id = cursor.lastrowid

        value_list = [(institution_id, email) for email in data.emails]
        cursor.executemany(models.INSTITUTION_EMAIL_INSERT_QUERY, value_list)
        db.commit()

        return {"id": institution_id}
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def obtain_institution(db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.INSTITUTION_OBTAIN_QUERY)
        result = cursor.fetchall()
        for institution in result:
            institution["emails"] = institution["emails"].split("|") if institution["emails"] else []
        return result
    finally:
        cursor.close()

def ensure_email_allowed(institution_id: int, email: str, db):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(models.INSTITUTION_EXISTS_QUERY, (institution_id,))
        if not cursor.fetchone():
            raise InstitutionDoesntExistError()

        cursor.execute(models.INSTITUTION_DOMAINS_QUERY, (institution_id,))
        domains = {row["email"].strip().lower() for row in cursor.fetchall()}
    finally:
        cursor.close()

    if email.rsplit("@", 1)[-1].lower() not in domains:
        raise EmailDomainNotAllowedError()
