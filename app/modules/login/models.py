LOGIN_SELECT_STUDENT_QUERY = "SELECT id, email, password_hash FROM TC.student WHERE email = %s"
LOGIN_SELECT_PROFESSOR_QUERY = "SELECT id, email, password_hash FROM TC.professor WHERE email = %s"