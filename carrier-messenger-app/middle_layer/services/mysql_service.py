# Handles persistent storage ops

import pymysql
from config import Config
import mysql.connector

def get_db_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        db=Config.MYSQL_DATABASE,
        port=Config.MYSQL_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_user(username):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username=%s"
            cursor.execute(sql, (username,))
            return cursor.fetchone()
    finally:
        conn.close()

def create_user(username, email, password_hash):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="medic26861311()",
        database="carrier_messenger"
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
    """, (username, email, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id