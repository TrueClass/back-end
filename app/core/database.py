from mysql.connector import pooling
from dotenv import load_dotenv
import os

load_dotenv()

db_pool = pooling.MySQLConnectionPool(
    pool_name = "mypool",
    pool_size = 5,
    host = os.getenv("MYSQL_HOST"),
    port = int(os.getenv("MYSQL_PORT", 3306)),
    user = os.getenv("MYSQL_USER"),
    password = os.getenv("MYSQL_PASSWORD"),
    database = os.getenv("MYSQL_DATABASE")
)

def get_db():
    connection = db_pool.get_connection()

    try:
        yield connection
    finally:
        connection.close()