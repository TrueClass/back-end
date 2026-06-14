# --- INSERT Queries ---
PROFESSOR_INSERT_QUERY = "INSERT INTO TC.users (institution_id, email, password_hash, role) VALUES (%s, %s, %s, %s)"
PROFESSOR_PROFILE_INSERT_QUERY = "INSERT INTO TC.professor_profile (user_id, name, is_coordinator) VALUES (%s, %s, %s)"
COORDINATOR_PROFESSOR_INSERT_QUERY = "INSERT INTO TC.coordinator_professor (professor_id, coordinator_id) VALUES (%s, %s)"

# --- GET Queries ---
CHECK_COORDINATOR_QUERY = "SELECT pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.id = %s AND pp.is_coordinator = 1"
PROFESSOR_GET_QUERY = "SELECT u.id, pp.name, pp.rating, u.email, pp.profile_picture, pp.is_coordinator FROM TC.users u JOIN TC.professor_profile pp ON u.id = pp.user_id WHERE u.institution_id = %s AND u.role = 'professor' LIMIT %s OFFSET %s"
PROFESSOR_COUNT_QUERY = "SELECT COUNT(*) as count FROM TC.users WHERE institution_id = %s AND role = 'professor'"