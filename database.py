import mysql.connector
import os
from dotenv import load_dotenv

if __name__ == "__main__":

    load_dotenv()

    mydb = mysql.connector.connect(
        host="localhost",
        user=os.getenv("db_username"),
        password=os.getenv("db_password"),
        database="cgh"
    )

    cursor = mydb.cursor()

    cursor.execute("SELECT * FROM students")
    result = cursor.fetchall()

    for r in result:
        print(r)
