#institution queries
INSTITUTION_INSERT_QUERY = "INSERT INTO TC.institution (name) VALUES (%s)"
INSTITUTION_OBTAIN_QUERY = "SELECT id, name FROM TC.institution"

#Student queries
STUDENT_INSERT_QUERY = "INSERT INTO TC.student (institution_id, email,password_hash) VALUES (%s,%s,%s)"
STUDENT_SELECT_QUERY = "SELECT id, email FROM TC.student where institution_id = %s LIMIT %s OFFSET %s"
STUDENT_COUNT_QUERY = "SELECT COUNT(*) as count FROM TC.student WHERE institution_id = %s"