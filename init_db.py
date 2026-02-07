"""
GhostPrice Database Initialization
Clean initialization with NO hardcoded sample data
"""

import sqlite3
import os

# Paths
SCRIPT_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(SCRIPT_DIR, "lifecycle.db")
SQL_SCHEMA_PATH = os.path.join(SCRIPT_DIR, "init_database.sql")


def init_database():
    """Initialize clean database with schema only (NO sample data)"""
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Initializing GhostPrice database...")
    
    # Execute schema SQL
    with open(SQL_SCHEMA_PATH, 'r') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)
    
    print("✅ Schema created")
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ Created {len(tables)} tables: {', '.join([t[0] for t in tables])}")
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")
    print(f"📁 Database location: {DB_PATH}")
    print("\n💡 How data is populated:")
    print("  1. Price History: Imported from Keepa API + user visits")
    print("  2. AI Analysis: Generated on-demand via Groq AI")
    print("  3. NO hardcoded sample data!")


if __name__ == "__main__":
    init_database()
