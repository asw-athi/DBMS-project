import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aswathi@123",
        database="my_database"
    )
    return connection
