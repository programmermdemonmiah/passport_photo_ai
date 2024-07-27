import mysql.connector

DB_CONFIG = {
    'host' : 'localhost',
    'database': 'photoai_db',
    'user':'root',
    'password':''
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"error connection : {e}")
        return None