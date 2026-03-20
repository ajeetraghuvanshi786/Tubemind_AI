from mysql.connector.pooling import MySQLConnectionPool
import os
from dotenv import load_dotenv

load_dotenv()

pool = MySQLConnectionPool(
    pool_name="tubemind_pool",
    pool_size=10,
    host="127.0.0.1",
    port=3306,
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
    autocommit=True
)

def get_db():
    try:
        return pool.get_connection()
    except Exception as e:
        print("DB CONNECTION ERROR:", str(e))
        raise