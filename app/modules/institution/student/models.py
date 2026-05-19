STUDENT_INSERT_QUERY = "INSERT INTO TC.users (institution_id, email, password_hash, role) VALUES (%s, %s, %s, 'student')"
STUDENT_SELECT_QUERY = "SELECT id, email FROM TC.users WHERE institution_id = %s AND role = 'student' LIMIT %s OFFSET %s"
STUDENT_COUNT_QUERY = "SELECT COUNT(*) AS count FROM TC.users WHERE institution_id = %s AND role = 'student'"
