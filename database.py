import mysql.connector
import os

from dotenv import load_dotenv

database = None


def init_db():
    load_dotenv()
    global database

    database = mysql.connector.connect(
        host=os.getenv("db_address"),
        user=os.getenv("db_username"),
        password=os.getenv("db_password"),
        database=os.getenv("db_name")
    )


def raw_query(query):
    global database
    init_db()

    db_cursor = database.cursor()
    db_cursor.execute(query)
    data = db_cursor.fetchall()
    database.commit()
    db_cursor.close()
    database.close()

    return data


def count_table(table_name):
    data = raw_query(f"SELECT COUNT(*) FROM {table_name}")
    data = data[0][0]
    return int(data)


def random_entry(table_name):
    data = raw_query(f"SELECT * FROM {table_name} ORDER BY RAND() LIMIT 1")
    data = data[0][1]
    return data


def identify_user(user_id):
    query = f"SELECT * FROM users WHERE user_id = \"{user_id}\""
    print(query)
    data = raw_query(query)
    if len(data) == 0 or data is None:
        return None
    data = data[0]
    print(data)
    """
        Data now contains a 5-tuple with the following values:
        - User ID
        - User full name
        - User grad year
        - User email stub
        - Username#Discriminator
        """
    return data


if __name__ == "__main__":
    load_dotenv()
    print("Testing database access...")
    random_entry("welcome_titles")
