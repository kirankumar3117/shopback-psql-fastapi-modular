from psycopg2 import pool
import os

try: 
    postgreSql_pool = pool.SimpleConnectionPool(
        1, 10,
        user="admin",
        password="password123",
        host="127.0.0.1",
        port="5432",
        database="shop_db"
    )
    print("Connection pool created successfully")
except Exception as e:
    print("Error while connection pool: {e}")