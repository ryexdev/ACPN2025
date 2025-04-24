import os
import sqlite3
import datetime

# Define the path to the database
DB_DIR = 'classes/db'
DB_PATH = os.path.join(DB_DIR, 'pies.db')
SQL_FILE = 'classes/data/db_setup.sql'

def create_database():
    """Create the SQLite database and necessary tables"""
    # Ensure the directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Check if database already exists
    if os.path.exists(DB_PATH):
        print(f"Database already exists at {DB_PATH}")
        return
    
    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()    
    
    """Load sample data from the SQL file"""
    # Read the SQL file
    with open(SQL_FILE, 'r') as f:
        sql_script = f.read()
    
    # Replace NOW() function with SQLite-compatible datetime
    current_time = f"'{datetime.datetime.now().isoformat()}'"
    sql_script = sql_script.replace('NOW()', current_time)
    
    # Execute the SQL commands
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print("Sample data loaded successfully")
    except sqlite3.Error as e:
        print(f"Error loading sample data: {e}")
        conn.rollback()
    
    conn.close()

def main():
    create_database()

if __name__ == "__main__":
    main()
