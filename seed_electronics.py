"""
Seed Database with Popular Electronics Products
Populates tracked_products table with top electronics from Amazon India

This gives you instant price tracking for popular products
without needing users to visit them first!
"""

import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from electronics_categories import detect_category
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("⚠️ WARNING: DATABASE_URL not found. Ensure .env is set.")

# Curated list of popular electronics products (Amazon India)
# Format: (ASIN, Product Title)
POPULAR_ELECTRONICS = [
    # Laptops
    ("B0D1XD1ZV3", "Dell Inspiron 15 Laptop, Intel Core i5-1235U, 15.6 FHD, 8GB DDR4, 512GB SSD"),
    ("B0CX23V2ZK", "HP Laptop 15s, 12th Gen Intel Core i3, 15.6-inch FHD, 8GB DDR4, 512GB SSD"),
    ("B0C8T68Q6S", "Lenovo IdeaPad Slim 3 Intel Core i3 12th Gen 15.6 FHD Thin & Light Laptop"),
    ("B0CK2YLWX1", "ASUS Vivobook 15, Intel Core i3-1215U 12th Gen, 15.6 FHD, 8GB, 512GB SSD"),
    ("B09X5K6Z8R", "Apple MacBook Air Laptop M2 chip"),
    
    # Smartphones
    ("B0CXWCFDLQ", "Samsung Galaxy M14 5G (Sapphire Blue, 6GB, 128GB Storage)"),
    ("B0CX59H6YL", "Redmi 13C (Starlight Black, 6GB RAM, 128GB Storage)"),
    ("B0CHX1W1XJ", "OnePlus Nord CE 3 Lite 5G (Pastel Lime, 8GB RAM, 128GB Storage)"),
    ("B0BDK62PDX", "Apple iPhone 15 (128 GB) - Black"),
    ("B09G9F5T3Z", "Apple iPhone 13 (128GB) - Starlight"),
    
    # Headphones
    ("B0CK2FCG1K", "Sony WH-1000XM5 Wireless Noise Cancelling Headphones"),
    ("B09JQMJHXY", "JBL Tune 770NC Wireless Over Ear ANC Headphones"),
    ("B0BYYF7PQF", "boAt Rockerz 450 Bluetooth On Ear Headphones"),
    ("B0C5N4D3C4", "OnePlus Bullets Wireless Z2 ANC"),
    
    # Monitors
    ("B0BYV73MFV", "LG 24 inch Full HD IPS Monitor, AMD FreeSync, 24MR400"),
    ("B0C1JFJNKQ", "Samsung 24 inch FHD Flat Monitor, 75Hz, AMD FreeSync"),
    ("B094RDLDPF", "Acer Ek220Q 21.5 Inch (54.61 Cm) Full Hd (1920x1080) Pixels VA Panel LCD Monitor"),
    
    # Tablets
    ("B0CRW1H3JF", "OnePlus Pad Go 11.35 inch 2.4K LCD Display (8GB RAM, 128GB)"),
    ("B0BJYQ1Z8W", "Samsung Galaxy Tab S6 Lite 10.4 inch"),
    ("B09G9F1B2C", "Apple iPad (9th Generation): with A13 Bionic chip"),
    
    # Smartwatches
    ("B0C7XKS21H", "boAt Wave Call 2 Smart Watch with 1.83 inch HD Display"),
    ("B0C9Q3C7K5", "Noise ColorFit Pulse 3 Bluetooth Calling Smart Watch"),
    
    # Cameras
    ("B0CHGLWZ19", "Canon EOS 3000D 18MP Digital SLR Camera with 18-55mm Lens"),
    ("B08L5V9TVQ", "Sony Alpha ILCE-7M4 Full-Frame Hybrid Camera"),
    
    # Gaming
    ("B0CJ51MTBP", "Sony PlayStation 5 Console Slim"),
    
    # PC Components
    ("B0CK2FCG1K", "Raspberry Pi 5 8GB RAM - Latest Model"),
    ("B0BVXPS6ZK", "Crucial RAM 8GB DDR4 3200MHz Desktop Memory"),
    ("B0CR59FWY6", "Samsung 980 PRO 1TB PCIe 4.0 NVMe M.2 Internal SSD"),
    
    # Keyboards & Mice
    ("B0C1NXKH9V", "Logitech MX Master 3S Wireless Mouse"),
    ("B0CDVGCMYW", "Cosmic Byte CB-GK-27 Blaze TKL Mechanical Gaming Keyboard"),
    ("B0148NPIQK", "Logitech K380 Wireless Multi-Device Keyboard"),
    
    # Speakers
    ("B098TVBQ48", "JBL Flip 6 Portable Bluetooth Speaker"),
    ("B091J31454", "Echo Dot (4th Gen, 2020 release)| Smart speaker with Alexa"),
    
    # Routers
    ("B0BXY1KFR2", "TP-Link Archer C6 Gigabit MU-MIMO Wireless Router"),
    
    # Storage
    ("B0CHBN46WW", "SanDisk Extreme Portable 1TB NVMe SSD"),
    ("B08GYKNCCP", "Seagate Backup Plus Slim 2TB External HDD"),
    
    # Chargers
    ("B0CPPP34PY", "Anker 735 Charger GaNPrime 65W"),
    ("B09MM4W55K", "Apple 20W USB-C Power Adapter"),
]

def seed_electronics():
    """Add popular electronics to tracked_products table"""
    print("🌱 Seeding database with popular electronics...")
    print(f"📦 Adding {len(POPULAR_ELECTRONICS)} products")
    print("-" * 60)
    
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    cursor = conn.cursor()
    
    try:
        added = 0
        skipped = 0
        
        for asin, title in POPULAR_ELECTRONICS:
            # Detect category
            category = detect_category(title)
            
            if not category:
                print(f"⚠️  Skipping (not electronics): {title[:50]}")
                skipped += 1
                continue
            
            try:
                # Check if already exists
                cursor.execute("SELECT asin FROM tracked_products WHERE asin = %s", (asin,))
                if cursor.fetchone():
                    print(f"⏭️  Already exists: {title[:50]}")
                    skipped += 1
                    continue
                
                # Insert new product
                cursor.execute("""
                    INSERT INTO tracked_products 
                    (asin, product_title, category, marketplace, currency, first_seen_at, last_updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (asin, title, category, 'IN', 'INR', datetime.now(), datetime.now()))
                
                print(f"✅ Added: {title[:50]}")
                print(f"   Category: {category} | ASIN: {asin}")
                added += 1
                
            except Exception as e:
                print(f"❌ Error adding {asin}: {e}")
                # Don't fail entire seeding on one error
                continue
        
        conn.commit()
        print("-" * 60)
        print(f"✅ Seeding complete!")
        print(f"📊 Added: {added} | Skipped: {skipped}")
        print()
        print("💡 Next step: Run 'python daily_price_scraper.py' to collect prices")
    
    except Exception as e:
        print(f"❌ Critical error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_electronics()
