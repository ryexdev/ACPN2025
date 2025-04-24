import os
import sqlite3
import datetime


class InitializeDatabase:

    def __init__(self):
        # Define the path to the database
        self.DB_DIR = 'classes/db'
        self.DB_PATH = os.path.join(self.DB_DIR, 'pies.db')
        self.SQL_FILE = 'classes/data/db_setup.sql'

    def create_database(self):
        """Create the SQLite database and necessary tables"""
        # Ensure the directory exists
        os.makedirs(self.DB_DIR, exist_ok=True)
        
        # Check if database already exists
        if os.path.exists(self.DB_PATH):
            print(f"Database already exists at {self.DB_PATH}")
            return
        
        # Connect to the database (this will create it if it doesn't exist)
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()    
        
        """Load sample data from the SQL file"""
        # Read the SQL file
        with open(self.SQL_FILE, 'r') as f:
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

initialize_database = InitializeDatabase()
