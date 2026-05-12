# --- Institution Queries ---
INSTITUTION_INSERT_QUERY = "INSERT INTO TC.institution (name) VALUES (%s)"
INSTITUTION_EMAIL_INSERT_QUERY = "INSERT INTO TC.institution_emails (institution_id, email) VALUES (%s, %s)"
INSTITUTION_OBTAIN_QUERY = "SELECT t1.id, t1.name, GROUP_CONCAT(t2.email SEPARATOR '|') AS emails FROM TC.institution t1 JOIN TC.institution_emails t2 ON t1.id = t2.institution_id GROUP BY t1.id;"

# --- Student Queries ---
STUDENT_INSERT_QUERY = "INSERT INTO TC.users (institution_id, email, password_hash, role) VALUES (%s, %s, %s, 'student')"
STUDENT_SELECT_QUERY = "SELECT id, email FROM TC.users WHERE institution_id = %s AND role = 'student' LIMIT %s OFFSET %s"
STUDENT_COUNT_QUERY = "SELECT COUNT(*) AS count FROM TC.users WHERE institution_id = %s AND role = 'student'"

# --- Professor Queries ---
PROFESSOR_INSERT_QUERY = "INSERT INTO TC.users (institution_id, email, password_hash, role) VALUES (%s, %s, %s, 'professor')"
PROFESSOR_PROFILE_INSERT_QUERY = "INSERT INTO TC.professor_profile (user_id, name, is_coordinator) VALUES (%s, %s, %s)"
CHECK_COORDINATOR_QUERY = "SELECT pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.id = %s AND pp.is_coordinator = 1"
COORDINATOR_PROFESSOR_INSERT_QUERY = "INSERT INTO TC.coordinator_professor (professor_id, coordinator_id) VALUES (%s, %s)"
PROFESSOR_GET_QUERY = "SELECT u.id, pp.name, pp.rating, u.email, pp.profile_picture, pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.institution_id = %s AND u.role = 'professor' LIMIT %s OFFSET %s"
PROFESSOR_COUNT_QUERY = "SELECT COUNT(*) as count FROM TC.users WHERE institution_id = %s AND role = 'professor'"