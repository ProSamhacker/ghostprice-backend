"""
Automated Daily Price Scraper for GhostPrice
Scrapes prices for all tracked electronics products daily
Populates price_history automatically without needing users
"""

import sys
import time
from datetime import datetime
from amazon_scraper import AmazonScraperClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force unbuffered output for Render logs
sys.stdout.reconfigure(line_buffering=True)

# PostgreSQL database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("⚠️ WARNING: DATABASE_URL not found. Ensure .env is set.")

import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    """Create PostgreSQL database connection"""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def get_tracked_products():
    """Get all tracked products from database"""
    conn = get_db_connection()
    
    try:
        # Use simple list for fetching results to avoid cursor issues
        result = conn.execute("""
            SELECT asin, product_title, marketplace, currency
            FROM tracked_products
            ORDER BY last_updated_at ASC
        """).fetchall()
        return result
    finally:
        conn.close()

def record_price(asin, price, currency, marketplace, source='scraper'):
    """Record price in price_history table"""
    conn = get_db_connection()
    
    try:
        conn.execute("""
            INSERT INTO price_history (asin, price, currency, marketplace, timestamp, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (asin, price, currency, marketplace, datetime.now(), source))
        
        # Update last_updated_at in tracked_products
        conn.execute("""
            UPDATE tracked_products
            SET last_updated_at = %s
            WHERE asin = %s
        """, (datetime.now(), asin))
        
        conn.commit()
    finally:
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
    
    for i, product in enumerate(products, 1):
        asin = product['asin']
        title = product['product_title']
        marketplace = product['marketplace']
        currency = product['currency']
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
