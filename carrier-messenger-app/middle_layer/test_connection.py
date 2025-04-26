import pymysql
from config import Config

def test_mysql_connection():
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE
        )
        print("✅ Successfully connected to MySQL server!")

        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("📋 Tables in the database:")
            for table in tables:
                print(f" - {table[0]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    test_mysql_connection()