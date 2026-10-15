from mysql.connector import pooling
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import redis.asyncio as redis
import urllib.parse
import os

load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_PORT = os.getenv("REDIS_PORT")

safe_redis_password = urllib.parse.quote_plus(REDIS_PASSWORD)

db_config = {
    "host": DATABASE_HOST,
    "port": int(MYSQL_PORT or 3306),
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": MYSQL_DATABASE
}

REDIS_URL = f"redis://:{safe_redis_password}@{DATABASE_HOST}:{REDIS_PORT}/0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mysql_pool = pooling.MySQLConnectionPool(
        pool_name = "mypool",
        pool_size = 5,
        **db_config
    )

    app.state.redis = redis.Redis.from_url(REDIS_URL, decode_responses = True)

    yield
    await app.state.redis.close()

def get_db(request: Request):
    conn = request.app.state.mysql_pool.get_connection()

    try:
        yield conn
    finally:
        conn.close()

def get_redis(request: Request):
    return request.app.state.redis