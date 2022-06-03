import mysql.connector
import os

from dotenv import load_dotenv

database = None
db_cursor = None


def init_db():
    global database
    global db_cursor
    if database is None:
        database = mysql.connector.connect(
            host=os.getenv("db_address"),
            user=os.getenv("db_username"),
            password=os.getenv("db_password"),
            database=os.getenv("db_name")
        )

    db_cursor = database.cursor()


def raw_query(query):
    init_db()
    db_cursor.execute(query)
    return db_cursor.fetchall()


if __name__ == "__main__":
    load_dotenv()
    print("Testing database access...")
    result = raw_query("SELECT * FROM students WHERE grad_year < 2022")
    print("For this test, should return all students gradyear 2021 or before.")
    print(result)
