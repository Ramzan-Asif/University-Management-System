import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_sql_script(filename):
    print(f"Executing {filename}...")
    try:
        # Connect to MySQL Server (without DB first) to ensure DB creates
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = connection.cursor()
        
        with open(filename, 'r') as f:
            sql_script = f.read()
            
        # Split by semicolon to execute commands individually
        commands = sql_script.split(';')
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Error as e:
                    print(f"Command skipped/failed: {e}")
                    
        connection.commit()
        cursor.close()
        connection.close()
        print("Schema execution completed.")
        
    except Error as e:
        print(f"Error reading/executing script: {e}")

if __name__ == '__main__':
    execute_sql_script('schema.sql')