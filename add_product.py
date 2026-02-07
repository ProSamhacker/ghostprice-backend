"""
Add Products to GhostPrice Database
Easy tool to add single or multiple products manually

Usage:
  python add_product.py B0D1XD1ZV3 "Dell Inspiron 15 Laptop"
  python add_product.py B0CK2FCG1K  # Auto-fetch title from Amazon
"""

import sys
import sqlite3
from datetime import datetime
from electronics_categories import detect_category
from amazon_scraper import AmazonScraperClient
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'lifecycle.db')

def add_product(asin, title=None, marketplace='IN', currency='INR'):
    """Add a product to tracked_products"""
    
    # If no title provided, try to scrape it
    if not title:
        print(f"📡 Fetching product details from Amazon...")
        scraper = AmazonScraperClient()
        data = scraper.get_current_price(asin, marketplace)
        
        if data and data.get('title'):
            title = data['title']
            print(f"✅ Found: {title[:60]}")
        else:
            print(f"❌ Could not fetch product title. Please provide manually:")
            print(f"   python add_product.py {asin} \"Product Title Here\"")
            return False
    
    # Detect category
    category = detect_category(title)
    
    if not category:
        print(f"⚠️  Warning: '{title[:50]}' doesn't match electronics categories")
        print(f"   Will add anyway, but it won't be tracked by the extension")
    
    # Add to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if exists
        cursor.execute("SELECT asin, product_title FROM tracked_products WHERE asin = ?", (asin,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  Product already exists:")
            print(f"   ASIN: {existing[0]}")
            print(f"   Title: {existing[1][:60]}")
            return False
        
        # Insert
        cursor.execute("""
            INSERT INTO tracked_products 
            (asin, product_title, category, marketplace, currency, first_seen_at, last_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asin, title, category, marketplace, currency, datetime.now(), datetime.now()))
        
        conn.commit()
        
        print(f"✅ Added product:")
        print(f"   ASIN: {asin}")
        print(f"   Title: {title[:60]}")
        print(f"   Category: {category or 'None (not electronics)'}")
        print(f"   Marketplace: {marketplace}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding product: {e}")
        return False
    finally:
        conn.close()

def add_multiple_products(products_file):
    """Add multiple products from a text file"""
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        added = 0
        skipped = 0
        
        print(f"📦 Processing {len(lines)} products from {products_file}")
        print("-" * 60)
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse line: "ASIN | Product Title"
            parts = line.split('|')
            if len(parts) >= 2:
                asin = parts[0].strip()
                title = parts[1].strip()
            else:
                asin = parts[0].strip()
                title = None
            
            if add_product(asin, title):
                added += 1
            else:
                skipped += 1
            
            print()
        
        print("-" * 60)
        print(f"✅ Complete! Added: {added} | Skipped: {skipped}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {products_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add single product:")
        print("    python add_product.py ASIN \"Product Title\"")
        print("    python add_product.py ASIN              # Auto-fetch title")
        print()
        print("  Add multiple products from file:")
        print("    python add_product.py --file products.txt")
        print()
        print("  File format (one per line):")
        print("    B0D1XD1ZV3 | Dell Inspiron 15 Laptop")
        print("    B0CK2FCG1K | Sony WH-1000XM5 Headphones")
        return
    
    # Batch mode
    if sys.argv[1] == '--file' and len(sys.argv) >= 3:
        add_multiple_products(sys.argv[2])
        return
    
    # Single product mode
    asin = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) >= 3 else None
    
    add_product(asin, title)

if __name__ == "__main__":
    main()
