LOGIN_SELECT_USER_QUERY = "SELECT id, password_hash, role FROM TC.users WHERE email = %s"
LOGIN_SELECT_USER_BY_ID_QUERY = "SELECT id, role FROM TC.users WHERE id = %s"