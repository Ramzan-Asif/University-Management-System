import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

def execute_trigger_script(filename):
    print(f"Executing {filename}...")
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        cursor = connection.cursor()
        
        # for triggers, we need to handle delimiters or just execute the create statement raw
        # simpler approach: drop if exists then create
        
        cursor.execute("DROP TRIGGER IF EXISTS before_enrollment_update")
        
        trigger_sql = """
        CREATE TRIGGER before_enrollment_update
        BEFORE UPDATE ON Enrollments
        FOR EACH ROW
        BEGIN
            SET NEW.total_marks = NEW.quiz_marks + NEW.midterm_marks + NEW.final_marks;
            
            IF NEW.total_marks >= 90 THEN
                SET NEW.grade = 'A';
            ELSEIF NEW.total_marks >= 80 THEN
                SET NEW.grade = 'B';
            ELSEIF NEW.total_marks >= 70 THEN
                SET NEW.grade = 'C';
            ELSEIF NEW.total_marks >= 60 THEN
                SET NEW.grade = 'D';
            ELSE
                SET NEW.grade = 'F';
            END IF;
        END;
        """
        cursor.execute(trigger_sql)
                    
        connection.commit()
        cursor.close()
        connection.close()
        print("Trigger created successfully.")
        
    except Error as e:
        print(f"Error creating trigger: {e}")

if __name__ == '__main__':
    execute_trigger_script('triggers.sql')
