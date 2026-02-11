"""
Automated Product Discovery for GhostPrice
Scrapes Amazon Best Seller lists and automatically adds top electronics

This script:
1. Scrapes Amazon Best Seller lists for electronics categories
2. Finds Amazon's Choice products
3. Automatically adds new products to database
4. Respects rate limits to avoid bans
5. Runs daily to keep database fresh

Target: 100-500 products across all categories
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from electronics_categories import detect_category
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback for local testing if .env not loaded, but ideally should just fail if strict
    print("⚠️ WARNING: DATABASE_URL not found. Ensure .env is set.")

import psycopg
from psycopg.rows import dict_row

print(f"✅ Using PostgreSQL database")

def get_db_connection():
    """Create PostgreSQL database connection"""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# Multiple Amazon discovery sources for broader coverage
DISCOVERY_SOURCES = {
    # Best Sellers
    'laptops_bestsellers': 'https://www.amazon.in/gp/bestsellers/computers/1375424031',
    'smartphones_bestsellers': 'https://www.amazon.in/gp/bestsellers/electronics/1389401031',
    'headphones_bestsellers': 'https://www.amazon.in/gp/bestsellers/electronics/1388921031',
    'monitors_bestsellers': 'https://www.amazon.in/gp/bestsellers/computers/1375390031',
    'tablets_bestsellers': 'https://www.amazon.in/gp/bestsellers/electronics/1389432031',
    'smartwatches_bestsellers': 'https://www.amazon.in/gp/bestsellers/electronics/9316867031',
    'cameras_bestsellers': 'https://www.amazon.in/gp/bestsellers/electronics/1388977031',
    'gaming_bestsellers': 'https://www.amazon.in/gp/bestsellers/videogames/4092042031',
    
    # New Releases (fresh products)
    'laptops_new': 'https://www.amazon.in/gp/new-releases/computers/1375424031',
    'smartphones_new': 'https://www.amazon.in/gp/new-releases/electronics/1389401031',
    'headphones_new': 'https://www.amazon.in/gp/new-releases/electronics/1388921031',
    'monitors_new': 'https://www.amazon.in/gp/new-releases/computers/1375390031',
    
    # Movers & Shakers (trending products)
    'laptops_trending': 'https://www.amazon.in/gp/movers-and-shakers/computers/1375424031',
    'smartphones_trending': 'https://www.amazon.in/gp/movers-and-shakers/electronics/1389401031',
    'headphones_trending': 'https://www.amazon.in/gp/movers-and-shakers/electronics/1388921031',
}

# Search queries for broader electronics discovery
SEARCH_QUERIES = [
    # Laptops & Computers
    'laptop i5', 'laptop i7', 'gaming laptop rtx', 'macbook air',
    'monitor 27 inch', 'gaming monitor 144hz', '4k monitor',
    'mechanical keyboard', 'wireless mouse', 'external ssd 1tb',
    
    # Mobile & Tablets
    'smartphone 5g', 'samsung phone', 'oneplus phone', 'iphone 15',
    'ipad', 'android tablet', 'power bank 20000mah',
    
    # Audio
    'wireless headphones noise cancelling', 'sony headphones', 'jbl speakers',
    'soundbar for tv', 'bluetooth speaker', 'tws earbuds',
    
    # Cameras & Others
    'dslr camera', 'action camera', 'security camera wifi',
    'smartwatch for men', 'smartwatch for women', 'wifi 6 router'
]

class ProductDiscoveryBot:
    """Automated product discovery from Amazon"""
    
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
    def scrape_best_sellers(self, category_url, max_products=50):
        """Scrape ASINs from Amazon Best Seller list"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Add delay to be polite
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(category_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all product ASINs
            asins = []
            
            # Method 1: Look for data-asin attributes
            products = soup.find_all('div', {'data-asin': True})
            for product in products[:max_products]:
                asin = product.get('data-asin')
                if asin and len(asin) == 10:  # Valid ASIN length
                    asins.append(asin)
            
            # Method 2: Look in href links
            if len(asins) < 10:
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if '/dp/' in href:
                        # Extract ASIN from URL
                        parts = href.split('/dp/')
                        if len(parts) > 1:
                            asin = parts[1].split('/')[0].split('?')[0]
                            if len(asin) == 10 and asin not in asins:
                                asins.append(asin)
            
            return list(set(asins[:max_products]))  # Remove duplicates
            
        except Exception as e:
            print(f"❌ Error scraping {category_url}: {e}")
            return []
    
    def get_product_info(self, asin):
        """Get product title from Amazon product page"""
        try:
            url = f"https://www.amazon.in/dp/{asin}"
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Check if Amazon's Choice
            is_amazons_choice = bool(soup.find('span', {'id': 'amazonChoice_feature_div'}))
            
            return {
                'asin': asin,
                'title': title,
                'amazons_choice': is_amazons_choice
            }
            
        except Exception as e:
            print(f"⚠️  Error fetching {asin}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract product title from Amazon product page"""
        try:
            title_element = soup.find('span', {'id': 'productTitle'})
            if title_element:
                return title_element.get_text().strip()
        except:
            pass
        return None
    
    def scrape_search_results(self, query, page=1, max_products=30):
        """Scrape ASINs from Amazon search results"""
        try:
            search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}&page={page}"
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            time.sleep(random.uniform(3, 5))
            
            response = self.session.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            asins = []
            
            # Find product cards
            products = soup.find_all('div', {'data-asin': True})
            for product in products[:max_products]:
                asin = product.get('data-asin')
                if asin and len(asin) == 10 and asin not in asins:
                    asins.append(asin)
            
            return asins
            
        except Exception as e:
            print(f"❌ Error scraping search '{query}': {e}")
            return []
    
    def add_to_database(self, asin, title, category):
        """Add product to tracked_products if not exists"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if exists
            cursor.execute("SELECT asin FROM tracked_products WHERE asin = %s", (asin,))
            if cursor.fetchone():
                return False  # Already exists
            
            # Insert
            cursor.execute("""
                INSERT INTO tracked_products 
                (asin, product_title, category, marketplace, currency, first_seen_at, last_updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (asin, title, category, 'IN', 'INR', datetime.now(), datetime.now()))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        finally:
            conn.close()

def discover_products(max_per_source=20, max_total=500, include_search=True):
    """
    Main discovery function - scrapes from ALL sources
    
    Sources:
    1. Best Sellers (top products)
    2. New Releases (latest products)
    3. Movers & Shakers (trending products)
    4. Search results (broader coverage)
    
    Duplicate prevention: Automatically checks database before adding
    """
    print("🤖 AUTOMATED PRODUCT DISCOVERY BOT v2.0")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Strategy: Multi-source discovery (Best Sellers + New + Trending + Search)")
    print(f"🎯 Target: {max_per_source} products per source, max {max_total} total")
    print("=" * 70)
    print()
    
    bot = ProductDiscoveryBot()
    
    # Pre-load existing ASINs to avoid duplicates
    print("⏳ Loading existing products from database...")
    conn = get_db_connection()
    existing = conn.execute("SELECT asin FROM tracked_products").fetchall()
    conn.close()
    
    discovered_asins = set(row['asin'] for row in existing)
    print(f"✅ Loaded {len(discovered_asins)} existing products. Will skip these.")
    
    total_discovered = 0
    total_added = 0
    total_skipped = 0
    
    # Phase 1: Scrape from curated lists (Best Sellers, New Releases, Trending)
    print("📋 PHASE 1: Curated Lists (Best Sellers, New Releases, Trending)")
    print("-" * 70)
    
    for source_name, source_url in list(DISCOVERY_SOURCES.items()):
        if total_discovered >= max_total:
            print(f"⚠️  Reached maximum {max_total} products, stopping")
            break
        
        print(f"\n📂 Source: {source_name.upper().replace('_', ' ')}")
        print(f"🔗 URL: {source_url[:60]}...")
        
        # Scrape ASINs from list
        asins = bot.scrape_best_sellers(source_url, max_per_source)
        
        if not asins:
            print(f"⚠️  No ASINs found, skipping")
            continue
        
        # Remove already discovered ASINs
        new_asins = [a for a in asins if a not in discovered_asins]
        print(f"✅ Found {len(asins)} ASINs ({len(new_asins)} new)")
        
        source_added = 0
        
        # Process each new ASIN
        for i, asin in enumerate(new_asins[:max_per_source], 1):
            if total_discovered >= max_total:
                break
            
            discovered_asins.add(asin)
            total_discovered += 1
            
            print(f"  [{i}/{len(new_asins)}] {asin}: ", end='')
            
            # Get product info
            info = bot.get_product_info(asin)
            
            if not info or not info.get('title'):
                print("❌ No title")
                total_skipped += 1
                continue
            
            title = info['title']
            
            # Detect category
            detected_category = detect_category(title)
            
            if not detected_category:
                print(f"⏭️  Not electronics: {title[:40]}")
                total_skipped += 1
                continue
            
            # Add to database
            added = bot.add_to_database(asin, title, detected_category)
            
            if added:
                amazons_choice_badge = "🏆" if info.get('amazons_choice') else ""
                print(f"✅ {amazons_choice_badge} {title[:50]}")
                total_added += 1
                source_added += 1
            else:
                print(f"⏭️  Already tracked")
                total_skipped += 1
            
            # Longer delay every 10 products to avoid rate limiting
            if i % 10 == 0:
                wait = random.uniform(10, 15)
                print(f"  ⏳ Cooling down {wait:.0f}s to avoid rate limits...")
                time.sleep(wait)
        
        print(f"  📊 Source Summary: {source_added} new products added")
    
    # Phase 2: Search results (if enabled and not at limit)
    if include_search and total_discovered < max_total:
        print(f"\n\n{'='*70}")
        print("🔍 PHASE 2: Search Results (Broader Coverage)")
        print("-" * 70)
        
        for query in SEARCH_QUERIES:
            if total_discovered >= max_total:
                break
            
            # Randomize page to find new products (deep search)
            page = random.randint(1, 4)
            print(f"\n🔍 Searching: '{query}' (Page {page})")
            
            # Scrape search results
            asins = bot.scrape_search_results(query, page=page, max_products=15)
            
            if not asins:
                print(f"⚠️  No results")
                continue
            
            # Remove duplicates
            new_asins = [a for a in asins if a not in discovered_asins]
            print(f"✅ Found {len(asins)} ASINs ({len(new_asins)} new)")
            
            # Process new ASINs
            for i, asin in enumerate(new_asins[:10], 1):  # Limit per search
                if total_discovered >= max_total:
                    break
                
                discovered_asins.add(asin)
                total_discovered += 1
                
                print(f"  [{i}] {asin}: ", end='')
                
                info = bot.get_product_info(asin)
                
                if not info or not info.get('title'):
                    print("❌ No title")
                    total_skipped += 1
                    continue
                
                title = info['title']
                detected_category = detect_category(title)
                
                if not detected_category:
                    print(f"⏭️  Not electronics")
                    total_skipped += 1
                    continue
                
                # Add to database (automatically checks for duplicates)
                added = bot.add_to_database(asin, title, detected_category)
                
                if added:
                    print(f"✅ {title[:45]}")
                    total_added += 1
                else:
                    print(f"⏭️  Already in DB")
                    total_skipped += 1
                
                # Rate limiting
                if total_discovered % 10 == 0:
                    wait = random.uniform(8, 12)
                    print(f"  ⏳ Cooling down {wait:.0f}s...")
                    time.sleep(wait)
    
    print(f"\n\n{'='*70}")
    print("🎉 MULTI-SOURCE DISCOVERY COMPLETE!")
    print(f"📊 Total Scanned: {total_discovered} unique ASINs")
    print(f"✅ Added to Database: {total_added} new products")
    print(f"⏭️  Skipped: {total_skipped} (duplicates or non-electronics)")
    print(f"🎯 Success Rate: {(total_added/total_discovered*100):.1f}%")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    # Multi-source discovery settings
    # Sources: Best Sellers + New Releases + Trending + Search
    # Expected: 400-600 unique products on first run
    # Runtime: ~30-45 minutes (includes cooling periods)
    # Duplicates automatically prevented!
    
    discover_products(
        max_per_source=15,      # 15 products per source/category
        max_total=500,          # Stop at 500 total products
        include_search=True     # Include search results (Phase 2)
    )
