import mysql.connector
from mysql.connector import Error

def getConnection():
    try:
       return mysql.connector.connect(
            host="localhost",
            user="root",
            password ="",
            database="projectsypoint"
        )
    except Error:
        print("Database connection error.")