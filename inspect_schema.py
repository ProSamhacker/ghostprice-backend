import sqlite3

conn = sqlite3.connect('lifecycle.db')
cursor = conn.cursor()

# Get complete schema
cursor.execute("PRAGMA table_info(products)")
columns = cursor.fetchall()

print("Products table columns:")
print("="* 60)
for col in columns:
    cid, name, ctype, notnull, default, pk = col
    print(f"{cid}: {name:25} {ctype:15} {'PK' if pk else ''}")

print("\n" + "=" * 60)
print("Sample data (first row):")
print("=" * 60)

cursor.execute("SELECT * FROM products LIMIT 1")
row = cursor.fetchone()

if row:
    for i, val in enumerate(row):
        col_name = columns[i][1]
        val_str = str(val)[:50] if val else "NULL"
        print(f"{col_name}: {val_str}")

conn.close()
