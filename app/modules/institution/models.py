# --- Institution Queries ---
INSTITUTION_INSERT_QUERY = "INSERT INTO TC.institution (name) VALUES (%s)"
INSTITUTION_EMAIL_INSERT_QUERY = "INSERT INTO TC.institution_emails (institution_id, email) VALUES (%s, %s)"
INSTITUTION_OBTAIN_QUERY = "SELECT t1.id, t1.name, GROUP_CONCAT(t2.email SEPARATOR ', ') AS emails FROM TC.institution t1 JOIN TC.institution_emails t2 ON t1.id = t2.institution_id GROUP BY t1.id;"

# --- Student Queries ---
STUDENT_INSERT_QUERY = "INSERT INTO TC.student (institution_id, email, password_hash) VALUES (%s,%s,%s)"
STUDENT_SELECT_QUERY = "SELECT id, email FROM TC.student WHERE institution_id = %s LIMIT %s OFFSET %s"
STUDENT_COUNT_QUERY = "SELECT COUNT(*) AS count FROM TC.student WHERE institution_id = %s"

# --- Professor Queries ---
PROFESSOR_INSERT_QUERY = "INSERT INTO TC.professor (institution_id, name, email, password_hash, is_coordinator) VALUES (%s,%s,%s,%s,%s)"
CHECK_COORDINATOR_QUERY = "SELECT is_coordinator FROM TC.professor WHERE id = %s"
COORDINATOR_PROFESSOR_INSERT_QUERY = "INSERT INTO TC.coordinator_professor (professor_id, coordinator_id) VALUES (%s,%s)"
PROFESSOR_GET_QUERY = "SELECT id, name, rating, email, profile_picture, is_coordinator FROM TC.professor WHERE institution_id = %s LIMIT %s OFFSET %s"
PROFESSOR_COUNT_QUERY = "SELECT COUNT(*) as count FROM TC.professor WHERE institution_id = %s"