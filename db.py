import mysql.connector

DB_CONFIG = {
    'host' : 'localhost',
    'database': 'photoai_db', #lalinass_photoai_db
    'user':'root', #lalinass_emon
    'password':'' #@Emon123456Emon
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"error connection : {e}")
        return None