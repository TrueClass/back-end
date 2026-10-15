INSTITUTION_INSERT_QUERY = "INSERT INTO TC.institution (name) VALUES (%s)"
INSTITUTION_EMAIL_INSERT_QUERY = "INSERT INTO TC.institution_emails (institution_id, email) VALUES (%s, %s)"
INSTITUTION_OBTAIN_QUERY = """
    SELECT t1.id, t1.name, GROUP_CONCAT(t2.email SEPARATOR '|') AS emails
    FROM TC.institution t1 LEFT JOIN TC.institution_emails t2 ON t1.id = t2.institution_id
    GROUP BY t1.id, t1.name
"""
INSTITUTION_EXISTS_QUERY = "SELECT id FROM TC.institution WHERE id = %s"
INSTITUTION_DOMAINS_QUERY = "SELECT email FROM TC.institution_emails WHERE institution_id = %s"
