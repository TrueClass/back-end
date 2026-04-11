STUDENT_INSERT_QUERY = "INSERT INTO TC.students (institution_id, email,password_hash) VALUES (%s,%s,%s)"
INSTITUTION_INSERT_QUERY = "INSERT INTO TC.institution (name) VALUES (%s)"
INSTITUTION_OBTAIN_QUERY = "SELECT id, name FROM TC.institution"