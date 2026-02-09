"""
Initialize simplified electronics database
Runs the SQL schema to create tracked_products and price_history tables
"""

import sqlite3
import os

def init_database(db_path="lifecycle.db"):
    """Initialize the electronics tracking database"""
    
    # Read SQL schema
    schema_path = os.path.join(os.path.dirname(__file__), "init_electronics_db.sql")
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema (handles CREATE TABLE IF NOT EXISTS)
    cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {db_path}")
    print(f"   - tracked_products table ready")
    print(f"   - price_history table ready")
    return True


if __name__ == "__main__":
    # Run initialization
    init_database()
    
    # Verify tables exist
    conn = sqlite3.connect("lifecycle.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n📋 Available tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    conn.close()
