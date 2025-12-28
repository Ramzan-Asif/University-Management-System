import database as db

def add_columns():
    queries = [
        "ALTER TABLE Enrollments ADD COLUMN quiz_marks DECIMAL(5, 2) DEFAULT 0",
        "ALTER TABLE Enrollments ADD COLUMN midterm_marks DECIMAL(5, 2) DEFAULT 0",
        "ALTER TABLE Enrollments ADD COLUMN final_marks DECIMAL(5, 2) DEFAULT 0",
        "ALTER TABLE Enrollments ADD COLUMN total_marks DECIMAL(5, 2) DEFAULT 0"
    ]
    
    for query in queries:
        try:
            db.execute_query(query)
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Error executing {query}: {e}")

if __name__ == "__main__":
    add_columns()
