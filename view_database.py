"""
Database Viewer for GhostPrice
View all tracked products and price history
"""

import sqlite3
from datetime import datetime
import sys

DB_PATH = 'lifecycle.db'

def view_tracked_products():
    """Show all tracked electronics products"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT asin, product_title, category, marketplace, currency, 
               first_seen_at, last_updated_at
        FROM tracked_products
        ORDER BY category, product_title
    """)
    
    products = cursor.fetchall()
    conn.close()
    
    print("=" * 80)
    print(f"📦 TRACKED PRODUCTS ({len(products)} total)")
    print("=" * 80)
    print()
    
    if not products:
        print("⚠️  No products tracked yet. Run 'python seed_electronics.py' first.")
        return
    
    current_category = None
    for asin, title, category, marketplace, currency, first_seen, last_updated in products:
        # Print category header
        if category != current_category:
            current_category = category
            print(f"\n{'─' * 80}")
            print(f"📂 {category.upper().replace('_', ' ')}")
            print(f"{'─' * 80}")
        
        # Truncate long titles
        display_title = title[:65] + "..." if len(title) > 65 else title
        
        print(f"  ASIN: {asin}")
        print(f"  📝 {display_title}")
        print(f"  🌍 {marketplace} | 💰 {currency}")
        print()

def view_price_history():
    """Show all price history entries"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ph.asin, tp.product_title, ph.price, ph.currency, 
               ph.timestamp, ph.source
        FROM price_history ph
        LEFT JOIN tracked_products tp ON ph.asin = tp.asin
        ORDER BY ph.timestamp DESC
        LIMIT 50
    """)
    
    history = cursor.fetchall()
    
    # Also get total count
    cursor.execute("SELECT COUNT(*) FROM price_history")
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print("=" * 80)
    print(f"📊 PRICE HISTORY (showing {min(50, len(history))} of {total} total entries)")
    print("=" * 80)
    print()
    
    if not history:
        print("⚠️  No price history yet.")
        print("💡 Run 'python daily_price_scraper.py' to populate prices.")
        return
    
    for asin, title, price, currency, timestamp, source in history:
        display_title = (title[:50] + "...") if title and len(title) > 50 else (title or "Unknown")
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = timestamp
        
        print(f"  {time_str} | {asin} | {currency} {price:,.0f}")
        print(f"  📝 {display_title}")
        print(f"  📡 Source: {source}")
        print()

def view_statistics():
    """Show database statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count products by category
    cursor.execute("""
        SELECT category, COUNT(*) 
        FROM tracked_products 
        GROUP BY category
        ORDER BY COUNT(*) DESC
    """)
    categories = cursor.fetchall()
    
    # Count price entries by source
    cursor.execute("""
        SELECT source, COUNT(*) 
        FROM price_history 
        GROUP BY source
    """)
    sources = cursor.fetchall()
    
    # Total stats
    cursor.execute("SELECT COUNT(*) FROM tracked_products")
    total_products = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM price_history")
    total_prices = cursor.fetchone()[0]
    
    conn.close()
    
    print("=" * 80)
    print("📈 DATABASE STATISTICS")
    print("=" * 80)
    print()
    
    print(f"📦 Total Products Tracked: {total_products}")
    print(f"📊 Total Price Entries: {total_prices}")
    print()
    
    if categories:
        print("Products by Category:")
        for category, count in categories:
            print(f"  • {category.replace('_', ' ').title()}: {count}")
        print()
    
    if sources:
        print("Price Entries by Source:")
        for source, count in sources:
            print(f"  • {source}: {count}")
        print()
    
    if total_products > 0 and total_prices > 0:
        avg_prices = total_prices / total_products
        print(f"📊 Average price entries per product: {avg_prices:.1f}")
    
    if total_prices == 0:
        print("⚠️  No price data yet!")
        print("💡 Run: python daily_price_scraper.py")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "products":
            view_tracked_products()
        elif command == "prices":
            view_price_history()
        elif command == "stats":
            view_statistics()
        else:
            print("Usage: python view_database.py [products|prices|stats|all]")
            return
    else:
        # Show all by default
        view_statistics()
        print()
        view_tracked_products()
        print()
        view_price_history()

if __name__ == "__main__":
    main()
