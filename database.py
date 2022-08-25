from winreg import QueryInfoKey
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


def get_teams(user_id=None, identifier=None, invert=False):
    query = ""
    if user_id:
        # return all team the selected user is not on the roster for
        if invert : query = f"SELECT team, identifier, emoji_id FROM esports_teams WHERE identifier NOT IN \
            (SELECT team_id FROM esports_players WHERE user_id = \"{user_id}\")"
        # return all team the selected user is on the roster for
        else : query = f"SELECT team, identifier, emoji_id FROM esports_teams WHERE identifier IN \
            (SELECT team_id FROM esports_players WHERE user_id = \"{user_id}\")"
    # return the team corresponding to the provided identifier
    elif identifier : query = f"SELECT team, identifier, emoji_id FROM esports_teams WHERE identifier = \"{identifier}\""
    # return all teams
    else : query = f"SELECT team, identifier, emoji_id FROM esports_teams"
    data = raw_query(query)
    if len(data) == 0 or data is None : return []
    return data


def manage_player(user_id, team_id, position_id= None):
    query = ""
    if position_id:
        query = f"INSERT INTO esports_players (user_id, team_id, position_id) VALUES ('{user_id}', '{team_id}', '{position_id}') ON DUPLICATE KEY UPDATE position_id='{position_id}'"
    else: 
        query = f"DELETE FROM esports_players WHERE user_id = {user_id} AND team_id = \"{team_id}\""
    raw_query(query)
    return


def get_positions(user_id=None, team_id=None, position_id=None, invert=False):
    query = ""
    if user_id:
        if team_id:
            # return all positions the selected user does not hold in a selected team
            if invert : query = f"SELECT position, identifier, emoji_id FROM esports_positions WHERE identifier NOT IN \
                (SELECT position_id FROM esports_players JOIN esports_teams ON esports_players.team_id = esports_teams.identifier WHERE user_id = \"{user_id}\" AND identifier = \"{team_id}\")"
            # return the position the selected user currently holds in a selected team
            else : query = f"SELECT position, identifier, emoji_id FROM esports_positions WHERE identifier IN \
                (SELECT position_id FROM esports_players JOIN esports_teams ON esports_players.team_id = esports_teams.identifier WHERE user_id = \"{user_id}\" AND identifier = \"{team_id}\")"
    # return the position corresponding to the provided identifier
    elif position_id : query = f"SELECT position, identifier, emoji_id FROM esports_positions WHERE identifier = \"{position_id}\""
    # return all positions
    else : query = f"SELECT position, identifier, emoji_id FROM esports_positions"
    data = raw_query(query)
    if len(data) == 0 or data is None : return []
    return data
    

def get_emoji_from_id(identifier):
    query = f"SELECT emoji_id FROM esports_teams WHERE identifier=\"{identifier}\" UNION \
        SELECT emoji_id FROM esports_positions WHERE identifier=\"{identifier}\""
    data = raw_query(query)
    if len(data) == 0 or data is None : return []
    return data

def get_team_from_id(team_id):
    query = f"SELECT team FROM esports_teams WHERE identifier=\"{team_id}\""
    data = raw_query(query)
    if len(data) == 0 or data is None : return []
    return data[0][0]

def get_position_from_id(position_id):
    query = f"SELECT position FROM esports_positions WHERE identifier=\"{position_id}\""
    data = raw_query(query)
    if len(data) == 0 or data is None : return []
    return data[0][0]

if __name__ == "__main__":
    load_dotenv()
    print("Testing database access...")
    random_entry("welcome_titles")
