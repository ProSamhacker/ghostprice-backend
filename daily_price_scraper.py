"""
Automated Daily Price Scraper for GhostPrice
Scrapes prices for all tracked electronics products daily
Populates price_history automatically without needing users
"""

import sqlite3
import time
from datetime import datetime
from amazon_scraper import AmazonScraperClient
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'lifecycle.db')

def get_tracked_products():
    """Get all tracked products from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT asin, product_title, marketplace, currency
        FROM tracked_products
        ORDER BY last_updated_at ASC
    """)
    
    products = cursor.fetchall()
    conn.close()
    
    return products

def record_price(asin, price, currency, marketplace, source='scraper'):
    """Record price in price_history table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO price_history (asin, price, currency, marketplace, timestamp, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (asin, price, currency, marketplace, datetime.now(), source))
    
    # Update last_updated_at in tracked_products
    cursor.execute("""
        UPDATE tracked_products
        SET last_updated_at = ?
        WHERE asin = ?
    """, (datetime.now(), asin))
    
    conn.commit()
    conn.close()

def scrape_all_tracked_products():
    """Scrape prices for all tracked products"""
    print("🚀 Starting automated price scraper...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    products = get_tracked_products()
    
    if not products:
        print("⚠️  No tracked products found in database")
        print("💡 Run seed_electronics.py first to populate database")
        return
    
    print(f"📦 Found {len(products)} tracked products")
    print()
    
    scraper = AmazonScraperClient()
    success_count = 0
    error_count = 0
    
    for i, (asin, title, marketplace, currency) in enumerate(products, 1):
        print(f"[{i}/{len(products)}] Scraping: {title[:50]}...")
        print(f"           ASIN: {asin} | Market: {marketplace}")
        
        try:
            # Scrape current price
            data = scraper.get_current_price(asin, marketplace)
            
            if data and data.get('current_price'):
                price = data['current_price']
                
                # Record in database
                record_price(asin, price, currency, marketplace)
                
                print(f"           ✅ Price: {currency} {price:,.0f} - Recorded!")
                success_count += 1
            else:
                print(f"           ⚠️  Could not extract price")
                error_count += 1
                
        except Exception as e:
            print(f"           ❌ Error: {e}")
            error_count += 1
        
        print()
        
        # Rate limiting: Wait 2-5 seconds between requests
        if i < len(products):
            wait_time = 3  # Be conservative to avoid blocks
            print(f"           ⏳ Waiting {wait_time}s before next request...")
            time.sleep(wait_time)
            print()
    
    print("-" * 60)
    print("✅ Scraping complete!")
    print(f"📊 Success: {success_count} | Errors: {error_count}")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    scrape_all_tracked_products()
