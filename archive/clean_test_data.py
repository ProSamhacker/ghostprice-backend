import sqlite3

# Connect to database
conn = sqlite3.connect('lifecycle.db')
cursor = conn.cursor()

# Delete test entries
cursor.execute("DELETE FROM price_history WHERE asin LIKE 'B0TEST%'")
deleted = cursor.rowcount

print(f"✅ Deleted {deleted} test entries")

# Verify
cursor.execute("SELECT COUNT(*) FROM price_history")
count = cursor.fetchone()[0]
print(f"📊 Remaining entries: {count}")

# Commit and close
conn.commit()
conn.close()

print("✅ Database cleaned!")
