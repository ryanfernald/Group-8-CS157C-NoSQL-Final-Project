import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DATABASE'),
        port=int(os.getenv('MYSQL_PORT')),
        cursorclass=pymysql.cursors.DictCursor
    )
    print("✅ Connected to MySQL server successfully.")

    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📋 Tables:", tables)

        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        print("👤 Users:", users)

except Exception as e:
    print("❌ Error connecting to MySQL:", e)

finally:
    if 'connection' in locals() and connection:
        connection.close()