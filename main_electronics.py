"""
GhostPrice Electronics Tracker - Simplified Backend API
Focused on price tracking for electronics products
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import os

# Local imports
from electronics_categories import detect_category, is_electronics, get_category_display_name

# Load environment variables
load_dotenv()

app = FastAPI(
    title="GhostPrice Electronics API",
    version="2.0.0",
    description="Price tracking for electronics products"
)

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None and DATABASE_URL.startswith("postgres")

if USE_POSTGRES:
    import psycopg
    from psycopg.rows import dict_row
    print(f"✅ Using PostgreSQL database")
else:
    import sqlite3
    DB_PATH = os.path.join(os.path.dirname(__file__), "lifecycle.db")
    print(f"✅ Using SQLite database at {DB_PATH}")


def get_db_connection():
    """Create database connection (PostgreSQL or SQLite)"""
    if USE_POSTGRES:
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "GhostPrice Electronics Tracker",
        "version": "2.0.0",
        "features": {
            "electronics_categories": 14,
            "price_tracking": True,
            "fake_discount_detection": True,
            "cost": "100% Free"
        }
    }


@app.get("/check-electronics")
async def check_electronics(
    asin: str = Query(..., description="Amazon product ASIN"),
    product_title: str = Query(..., description="Product title from Amazon"),
    current_price: float = Query(..., description="Current product price"),
    currency: str = Query("INR", description="Currency code (INR/USD)"),
    marketplace: str = Query("IN", description="Marketplace (IN/US)")
):
    """
    Check if product is electronics and add to tracking
    
    This endpoint:
    1. Detects if product is in supported electronics category
    2. Adds product to tracked_products table
    3. Records current price in price_history
    4. Returns tracking status
    """
    # Detect category
    category = detect_category(product_title)
    
    if not category:
        return {
            "tracked": False,
            "reason": "not_electronics",
            "message": "This product is not in our supported electronics categories.",
            "supported_categories": [
                "Laptops", "Smartphones", "Monitors", "Headphones",
                "Tablets", "Smartwatches", "Cameras", "Gaming Consoles",
                "PC Components", "Keyboards & Mice", "Speakers",
                "Routers", "Storage", "Chargers"
            ]
        }
    
    conn = get_db_connection()
    
    try:
        # Add to tracked products (or update if exists)
        conn.execute("""
            INSERT INTO tracked_products (asin, product_title, category, marketplace, currency, last_updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(asin) DO UPDATE SET
                product_title = excluded.product_title,
                last_updated_at = CURRENT_TIMESTAMP
        """, (asin, product_title, category, marketplace, currency))
        
        # Record price
        conn.execute("""
            INSERT INTO price_history (asin, price, currency, marketplace, source, timestamp)
            VALUES (?, ?, ?, ?, 'extension', CURRENT_TIMESTAMP)
        """, (asin, current_price, currency, marketplace))
        
        conn.commit()
        
        # Get current tracking stats
        stats = conn.execute("""
            SELECT COUNT(*) as data_points,
                   MIN(price) as lowest_price,
                   MAX(price) as highest_price,
                   AVG(price) as avg_price
            FROM price_history
            WHERE asin = ?
            AND timestamp > datetime('now', '-30 days')
        """, (asin,)).fetchone()
        
        return {
            "tracked": True,
            "category": category,
            "category_display": get_category_display_name(category),
            "message": f"Tracking {get_category_display_name(category)} price!",
            "price_data": {
                "current": current_price,
                "lowest_30d": round(stats["lowest_price"], 2) if stats["data_points"] > 0 else current_price,
                "highest_30d": round(stats["highest_price"], 2) if stats["data_points"] > 0 else current_price,
                "avg_30d": round(stats["avg_price"], 2) if stats["data_points"] > 0 else current_price,
                "data_points": stats["data_points"]
            }
        }
    
    finally:
        conn.close()


@app.get("/price-intelligence")
async def price_intelligence(
    asin: str = Query(..., description="Amazon product ASIN"),
    current_price: float = Query(..., description="Current product price"),
    currency: str = Query("INR", description="Currency code")
):
    """
    🎯 Price Intelligence: Track price and provide buy recommendations
    
    Features:
    - Automatic price tracking
    - Fake discount detection
    - Buy/wait recommendations
    - 30-day price statistics
    """
    from price_tracker import PriceTracker
    
    tracker = PriceTracker()
    
    # Track this price point
    tracker.track_price(asin, current_price, currency, source="extension")
    
    # Get price statistics
    stats = tracker.get_price_stats(asin, days=30)
    
    if not stats:
        # New product - not enough data yet
        return {
            "status": "tracking_started",
            "asin": asin,
            "current_price": current_price,
            "currency": currency,
            "message": "👻 GhostPrice is now tracking this product! Check back soon for price intelligence.",
            "data_points": 1
        }
    
    # Detect fake discounts
    fake_discount_analysis = tracker.detect_fake_discount(asin, current_price)
    
    # Get buy recommendation
    buy_recommendation = tracker.get_buy_recommendation(asin, current_price)
    
    # Price trend analysis
    trend = "stable"
    if current_price < stats["avg_30d"] * 0.9:
        trend = "dropping"
    elif current_price > stats["avg_30d"] * 1.1:
        trend = "rising"
    
    return {
        "status": "success",
        "asin": asin,
        "current_price": current_price,
        "currency": currency,
        
        # Price statistics
        "price_stats": {
            "lowest_30d": round(stats["min_30d"], 2),
            "highest_30d": round(stats["max_30d"], 2),
            "average_30d": round(stats["avg_30d"], 2),
            "is_at_lowest": stats["is_lowest"],
            "is_at_highest": stats["is_highest"],
            "price_range": round(stats["price_range"], 2),
            "volatility": round(stats["volatility"], 1),
            "data_points": stats["data_points"]
        },
        
        # Fake discount detection
        "fake_discount": fake_discount_analysis,
        
        # Buy recommendation
        "recommendation": buy_recommendation,
        
        # Trend
        "trend": trend,
        
        # Metadata
        "timestamp": datetime.now().isoformat(),
        "data_source": "GhostPrice Intelligence"
    }


@app.get("/price-stats")
async def get_price_stats(
    asin: str = Query(..., description="Amazon product ASIN"),
    days: int = Query(30, description="Number of days for statistics")
):
    """
    Get price statistics for a product
    
    Returns:
    - Current price vs 30-day low/high/average
    - Buy recommendation
    - Data source
    """
    try:
        from price_tracker import PriceTracker
        
        tracker = PriceTracker()
        stats = tracker.get_price_stats(asin, days=days, use_keepa=False, country="IN")
        
        if not stats:
            return {
                "success": False,
                "message": "No price data available yet. Visit the product page to start tracking!",
                "asin": asin
            }
        
        # Add recommendation
        recommendation = "UNKNOWN"
        if stats.get("is_lowest"):
            recommendation = "BUY_NOW"
        elif stats["current"] <= stats["avg_30d"] * 0.95:
            recommendation = "GOOD_DEAL"
        elif stats["current"] >= stats["avg_30d"] * 1.10:
            recommendation = "WAIT"
        else:
            recommendation = "FAIR_PRICE"
        
        return {
            "success": True,
            "asin": asin,
            "current_price": stats["current"],
            "min_30d": stats["min_30d"],
            "max_30d": stats["max_30d"],
            "avg_30d": stats["avg_30d"],
            "is_lowest": stats.get("is_lowest", False),
            "is_highest": stats.get("is_highest", False),
            "data_points": stats.get("data_points", 0),
            "volatility": stats.get("volatility", 0),
            "source": stats.get("source", "Crowdsourced"),
            "recommendation": recommendation,
            "savings_from_high": round(stats["max_30d"] - stats["current"], 2),
            "potential_savings": round(stats["current"] - stats["min_30d"], 2)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "asin": asin
        }


@app.get("/tracked-products")
async def get_tracked_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, description="Limit results")
):
    """
    Get list of tracked electronics products
    
    Optional filters:
    - category: Filter by electronics category
    - limit: Maximum number of results
    """
    conn = get_db_connection()
    
    try:
        if category:
            products = conn.execute("""
                SELECT * FROM tracked_products
                WHERE category = ?
                ORDER BY last_updated_at DESC
                LIMIT ?
            """, (category, limit)).fetchall()
        else:
            products = conn.execute("""
                SELECT * FROM tracked_products
                ORDER BY last_updated_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
        
        return {
            "success": True,
            "count": len(products),
            "products": [dict(p) for p in products]
        }
    
    finally:
        conn.close()


@app.post("/admin/trigger-daily-scrape")
async def trigger_daily_scrape():
    """
    Admin endpoint to trigger daily price scraping
    Called by GitHub Actions cron job
    """
    import subprocess
    import sys
    
    try:
        # Run daily_price_scraper.py as a background process
        # Removed stdout/stderr PIPE so logs appear in Render dashboard
        script_path = os.path.join(os.path.dirname(__file__), "daily_price_scraper.py")
        process = subprocess.Popen([sys.executable, script_path])
        
        return {
            "status": "started",
            "task": "daily_price_scrape",
            "message": "Daily price scraping started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scraper: {str(e)}")


@app.post("/admin/trigger-discovery")
async def trigger_discovery():
    """
    Admin endpoint to trigger weekly product discovery
    Called by GitHub Actions cron job
    """
    import subprocess
    import sys
    
    try:
        # Run discover_products.py as a background process
        # Removed stdout/stderr PIPE so logs appear in Render dashboard
        script_path = os.path.join(os.path.dirname(__file__), "discover_products.py")
        process = subprocess.Popen([sys.executable, script_path])
        
        return {
            "status": "started",
            "task": "product_discovery",
            "message": "Product discovery started in background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start discovery: {str(e)}")


@app.get("/admin/status")
async def get_admin_status():
    """Check system status and database stats"""
    conn = get_db_connection()
    
    try:
        # Get product count
        result = conn.execute("SELECT COUNT(*) as count FROM tracked_products").fetchone()
        product_count = result['count'] if USE_POSTGRES else result[0]
        
        # Get price history count
        result = conn.execute("SELECT COUNT(*) as count FROM price_history").fetchone()
        price_count = result['count'] if USE_POSTGRES else result[0]
        
        # Get category breakdown
        categories = conn.execute("""
            SELECT category, COUNT(*) as count 
            FROM tracked_products 
            GROUP BY category 
            ORDER BY count DESC
        """).fetchall()
        
        # Convert to list of dicts
        category_list = []
        for cat in categories:
            if USE_POSTGRES:
                category_list.append(dict(cat))
            else:
                category_list.append({"category": cat[0], "count": cat[1]})
        
        return {
            "status": "healthy",
            "database": {
                "tracked_products": product_count,
                "price_history_entries": price_count,
                "categories": category_list
            },
            "timestamp": datetime.now().isoformat()
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/admin/init-database")
async def init_database():
    """
    Initialize database schema (PostgreSQL or SQLite)
    Creates all required tables if they don't exist
    """
    try:
        conn = get_db_connection()
        
        if USE_POSTGRES:
            # PostgreSQL schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracked_products (
                    asin TEXT PRIMARY KEY,
                    product_title TEXT NOT NULL,
                    category TEXT,
                    marketplace TEXT DEFAULT 'IN',
                    currency TEXT DEFAULT 'INR',
                    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id SERIAL PRIMARY KEY,
                    asin TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    marketplace TEXT DEFAULT 'IN',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'extension',
                    FOREIGN KEY (asin) REFERENCES tracked_products(asin)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_price_asin ON price_history(asin)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracked_category ON tracked_products(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tracked_marketplace ON tracked_products(marketplace)")
            
            conn.commit()
        else:
            # SQLite schema
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracked_products (
                    asin TEXT PRIMARY KEY,
                    product_title TEXT NOT NULL,
                    category TEXT,
                    marketplace TEXT DEFAULT 'IN',
                    currency TEXT DEFAULT 'INR',
                    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    price REAL NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    marketplace TEXT DEFAULT 'IN',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'extension',
                    FOREIGN KEY (asin) REFERENCES tracked_products(asin)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_asin ON price_history(asin)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracked_category ON tracked_products(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracked_marketplace ON tracked_products(marketplace)")
            
            conn.commit()
        
        conn.close()
        
        return {
            "status": "success",
            "message": "Database schema initialized successfully",
            "database_type": "PostgreSQL" if USE_POSTGRES else "SQLite"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")
