STUDENT_INSERT_QUERY = "INSERT INTO HL.students (institution_id, email,password_hash) VALUES (%s,%s,%s)"
INSTITUTION_INSERT_QUERY = "INSERT INTO HL.institution (name) VALUES (%s)"
INSTITUTION_OBTAIN_QUERY = "SELECT id_name FROM HL.institution"