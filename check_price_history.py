import sqlite3

conn = sqlite3.connect('lifecycle.db')
conn.row_factory = sqlite3.Row

# Check if price_history has data
count = conn.execute('SELECT COUNT(*) FROM price_history').fetchone()[0]
print(f'Total price history entries: {count}')

if count > 0:
    print('\nFirst 5 entries:')
    print('=' * 100)
    rows = conn.execute('SELECT * FROM price_history LIMIT 5').fetchall()
    for row in rows:
        print(f'ID: {row["id"]} | ASIN: {row["asin"]} | Price: ₹{row["price"]} | Time: {row["timestamp"]} | Source: {row["source"]}')
    
    print('\nBreakdown by source:')
    sources = conn.execute('SELECT source, COUNT(*) as cnt FROM price_history GROUP BY source').fetchall()
    for s in sources:
        print(f'  - {s["source"]}: {s["cnt"]} entries')
else:
    print('\n⚠️ Database is empty! No price data yet.')
    print('Price data will be added when:')
    print('  1. Users visit Amazon product pages (extension tracks price)')
    print('  2. Keepa API imports historical data (one-time per product)')

conn.close()
