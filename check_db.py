import sqlite3

conn = sqlite3.connect('lifecycle.db')
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
    
# Get schema for products table if it exists
try:
    cursor.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    print("\nProducts table schema:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        
    # Get sample data
    cursor.execute("SELECT * FROM products LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        print("\nSample row:")
        print(sample)
except:
    print("\nNo products table found")

conn.close()
