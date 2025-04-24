import os
import sqlite3
import datetime

# Define the path to the database
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, 'pies.db')

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Set row factory to return rows as dictionaries
        conn.row_factory = self._dict_factory
        return conn
    
    @staticmethod
    def _dict_factory(cursor, row):
        """Convert row to dictionary"""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    
    def connection_status(self):
        """Check if the database connection is successful"""
        try:
            conn = self.get_connection()
            conn.close()
            return True
        except Exception as e:
            return False

    def execute_query(self, query, params=None, fetch_all=True):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
                return cursor.lastrowid
            else:
                if fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_products(self, limit=None):
        """Get all products from the database"""
        query = "SELECT * FROM products"
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query)
    
    def get_product_by_id(self, product_id):
        """Get a product by ID"""
        query = "SELECT * FROM products WHERE id = ?"
        return self.execute_query(query, (product_id,), fetch_all=False)
    
    def add_generation_log(self, product_id, prompt, engine, result):
        """Add a generation log entry"""
        query = """
        INSERT INTO generation_logs (product_id, prompt, engine, result, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        current_time = datetime.datetime.now().isoformat()
        return self.execute_query(query, (product_id, prompt, engine, result, current_time))
    
    def get_generation_logs(self, product_id=None):
        """Get generation logs, optionally filtered by product_id"""
        if product_id:
            query = "SELECT * FROM generation_logs WHERE product_id = ?"
            return self.execute_query(query, (product_id,))
        else:
            query = "SELECT * FROM generation_logs"
            return self.execute_query(query)

# Create singleton instance
db = Database() 