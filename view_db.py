
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found in environment or .env file.")
    sys.exit(1)

def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def view_database():
    print("\n🔍 GhostPrice Database Viewer")
    print("============================\n")
    
    conn = get_db_connection()
    try:
        # 1. Get Tracked Products Count
        count = conn.execute("SELECT COUNT(*) as count FROM tracked_products").fetchone()['count']
        print(f"📦 Total Tracked Products: {count}")
        
        if count == 0:
            print("\n   No products found. Start tracking by visiting Amazon product pages!")
            return

        # 1.5 Get Price History Count
        price_count = conn.execute("SELECT COUNT(*) as count FROM price_history").fetchone()['count']
        print(f"💰 Total Price History Points: {price_count}")

        # 2. List Products with latest price
        print("\n📋 Product List (Latest 20):")
        print(f"{'ASIN':<12} | {'Price':<10} | {'Title':<50} | {'Last Updated'}")
        print("-" * 100)
        
        products = conn.execute("""
            SELECT 
                tp.asin, 
                tp.product_title, 
                tp.last_updated_at,
                tp.currency,
                (SELECT price FROM price_history ph WHERE ph.asin = tp.asin ORDER BY ph.timestamp DESC LIMIT 1) as latest_price
            FROM tracked_products tp
            ORDER BY tp.last_updated_at DESC
            LIMIT 20
        """).fetchall()
        
        for p in products:
            price_display = f"{p['currency']} {p['latest_price']}" if p['latest_price'] else "N/A"
            title = (p['product_title'][:47] + '...') if len(p['product_title']) > 50 else p['product_title']
            updated = p['last_updated_at'].strftime('%Y-%m-%d %H:%M') if p['last_updated_at'] else "N/A"
            
            print(f"{p['asin']:<12} | {price_display:<10} | {title:<50} | {updated}")
            
        print("\n\n💡 Tip: To see more details including price history, check the /price-stats endpoint.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        conn.close()

def test_scraper(asin):
    """Test the scraper on a specific ASIN"""
    print(f"\n🧪 Testing Scraper for ASIN: {asin}")
    from amazon_scraper import AmazonScraperClient
    
    client = AmazonScraperClient()
    result = client.get_current_price(asin, country="IN")
    
    if result:
        print(f"✅ Success! Found price: {result.get('current_price')}")
        print(result)
    else:
        print("❌ Failed to extract price.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        if len(sys.argv) > 2:
            test_scraper(sys.argv[2])
        else:
            print("Usage: python view_db.py test <ASIN>")
    else:
        view_database()
