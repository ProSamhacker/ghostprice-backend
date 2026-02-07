"""
LifeCycle Backend API - FastAPI Server
Serves TCO data to the Chrome extension + Bridge Page
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import os
import json # Added import

# Load environment variables
load_dotenv()

app = FastAPI(title="LifeCycle API", version="1.0.0")

# Template configuration
BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL URL for production
USE_POSTGRES = DATABASE_URL is not None and DATABASE_URL.startswith("postgres")

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    print(f"✅ Using PostgreSQL database")
else:
    import sqlite3
    DB_PATH = os.path.join(os.path.dirname(__file__), "lifecycle.db")
    print(f"✅ Using SQLite database at {DB_PATH}")

# Amazon Associates Tag (REPLACE WITH YOUR ACTUAL TAG)
AMAZON_TAG = os.getenv("AMAZON_ASSOCIATES_TAG", "lifecycle-20")


def get_db_connection():
    """Create database connection (PostgreSQL or SQLite)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def calculate_tco_for_product(product, consumable):
    """Calculate TCO data for a product"""
    sticker_price = float(product["base_price"])
    
    if consumable:
        consumable_price = float(consumable["consumable_price"])
        lifespan_months = int(consumable["replacement_frequency_months"])
        annual_maintenance = consumable_price * (12 / lifespan_months)
    else:
        consumable_price = 0
        lifespan_months = 0
        annual_maintenance = 0
    
    total_year_1 = sticker_price + annual_maintenance
    
    return {
        "sticker_price": sticker_price,
        "consumable_price": consumable_price,
        "replacement_months": lifespan_months,
        "annual_maintenance": round(annual_maintenance, 2),
        "total_year_1": round(total_year_1, 2)
    }


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "message": "LifeCycle API is running",
        "features": {
            "database_products": 960,
            "ai_powered": True,
            "model": "Llama 3.1 8B (Groq)"
        }
    }


@app.get("/analyze")
async def analyze_page(request: Request, asin: str = Query(..., description="Product ASIN to analyze")):
    """
    Bridge Page - Head-to-head comparison
    This is where the user lands from the Chrome extension
    This page shows the TCO comparison and contains the affiliate link
    """
    
    conn = get_db_connection()
    
    try:
        # Get trap product
        trap_product = conn.execute("""
            SELECT * FROM products WHERE parent_asin = ?
        """, (asin,)).fetchone()
        
        if not trap_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get consumable
        trap_consumable = conn.execute("""
            SELECT * FROM consumables WHERE parent_asin = ?
        """, (asin,)).fetchone()
        
        # Get BIFL alternative
        alternative_data = conn.execute("""
            SELECT * FROM bifl_alternatives WHERE trap_asin = ?
        """, (asin,)).fetchone()
        
        if not alternative_data:
            raise HTTPException(status_code=404, detail="No alternative found")
        
        # Get BIFL product details
        bifl_product = conn.execute("""
            SELECT * FROM products WHERE parent_asin = ?
        """, (alternative_data["bifl_asin"],)).fetchone()
        
        bifl_consumable = conn.execute("""
            SELECT * FROM consumables WHERE parent_asin = ?
        """, (alternative_data["bifl_asin"],)).fetchone()
        
        # Calculate TCOs
        trap_tco = calculate_tco_for_product(trap_product, trap_consumable)
        bifl_tco = calculate_tco_for_product(bifl_product, bifl_consumable)
        
        # Calculate savings
        savings_year_1 = trap_tco["total_year_1"] - bifl_tco["total_year_1"]
        
        # Calculate break-even months
        if bifl_tco["sticker_price"] > trap_tco["sticker_price"]:
            upfront_diff = bifl_tco["sticker_price"] - trap_tco["sticker_price"]
            monthly_savings = (trap_tco["annual_maintenance"] - bifl_tco["annual_maintenance"]) / 12
            
            if monthly_savings > 0:
                break_even_months = int(upfront_diff / monthly_savings)
            else:
                break_even_months = None
        else:
            break_even_months = 0  # Already cheaper upfront
        
        # Build template context
        context = {
            "request": request,
            "trap": {
                "product_name": trap_product["product_name"],
                "sticker_price": trap_tco["sticker_price"],
                "annual_maintenance": trap_tco["annual_maintenance"],
                "total_year_1": trap_tco["total_year_1"],
                "consumable_name": trap_consumable["consumable_name"] if trap_consumable else "maintenance",
                "consumable_price": trap_tco["consumable_price"],
                "replacement_months": trap_tco["replacement_months"]
            },
            "bifl": {
                "product_name": bifl_product["product_name"],
                "short_name": bifl_product["product_name"].split()[0],  # First word
                "sticker_price": bifl_tco["sticker_price"],
                "annual_maintenance": bifl_tco["annual_maintenance"],
                "total_year_1": bifl_tco["total_year_1"],
                "reasoning": alternative_data["reasoning"],
                "amazon_link": f"https://www.amazon.com/dp/{alternative_data['bifl_asin']}?tag={AMAZON_TAG}"
            },
            "savings": {
                "year_1": round(savings_year_1, 2),
                "break_even_months": break_even_months
            },
            "trap_asin": asin,
            "max_cost": max(trap_tco["total_year_1"], bifl_tco["total_year_1"]),
            "last_updated": datetime.now().strftime("%B %d, %Y")
        }
        
        return templates.TemplateResponse("analyze.html", context)
    
    finally:
        conn.close()

"""
New FastAPI JSON endpoint for React frontend
Add this endpoint to your main.py file after the /analyze endpoint
"""

@app.get("/analyze-json")
async def analyze_json(asin: str = Query(..., description="Amazon product ASIN")):
    """
    Returns full comparison data as JSON for React frontend
    Compatible with React app's ComparisonData interface
    """
    conn = get_db_connection()
    
    try:
        # Get trap product
        trap_product = conn.execute("""
            SELECT * FROM products WHERE parent_asin = ?
        """, (asin,)).fetchone()
        
        if not trap_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get consumable for trap product
        trap_consumable = conn.execute("""
            SELECT * FROM consumables WHERE parent_asin = ?
        """, (asin,)).fetchone()
        
        # Get BIFL alternative
        alternative_data = conn.execute("""
            SELECT * FROM bifl_alternatives WHERE trap_asin = ?
        """, (asin,)).fetchone()
        
        if not alternative_data:
            raise HTTPException(status_code=404, detail="No BIFL alternative found for this product")
        
        # Get BIFL product details
        bifl_product = conn.execute("""
            SELECT * FROM products WHERE parent_asin = ?
        """, (alternative_data["bifl_asin"],)).fetchone()
        
        bifl_consumable = conn.execute("""
            SELECT * FROM consumables WHERE parent_asin = ?
        """, (alternative_data["bifl_asin"],)).fetchone()
        
        # Calculate TCOs
        trap_tco = calculate_tco_for_product(trap_product, trap_consumable)
        bifl_tco = calculate_tco_for_product(bifl_product, bifl_consumable)
        
        # Calculate break-even months
        if bifl_tco["sticker_price"] > trap_tco["sticker_price"]:
            upfront_diff = bifl_tco["sticker_price"] - trap_tco["sticker_price"]
            monthly_savings = (trap_tco["annual_maintenance"] - bifl_tco["annual_maintenance"]) / 12
            
            if monthly_savings > 0:
                break_even_months = int(upfront_diff / monthly_savings)
            else:
                break_even_months = 999  # Never breaks even
        else:
            break_even_months = 0  # Already cheaper upfront
        
        # Calculate 5-year savings
        trap_five_year = trap_tco["sticker_price"] + (trap_tco["annual_maintenance"] * 5)
        bifl_five_year = bifl_tco["sticker_price"] + (bifl_tco["annual_maintenance"] * 5)
        five_year_savings = int(trap_five_year - bifl_five_year)
        
        # Return data matching React frontend's ComparisonData interface
        return {
            "trap": {
                "name": trap_product["product_name"],
                "price": float(trap_product["base_price"]),
                "consumableCost": float(trap_consumable["consumable_price"]) if trap_consumable else 0,
                "consumableFrequencyMonths": int(trap_consumable["replacement_frequency_months"]) if trap_consumable else 0,
            },
            "winner": {
                "name": bifl_product["product_name"],
                "price": float(bifl_product["base_price"]),
                "consumableCost": float(bifl_consumable["consumable_price"]) if bifl_consumable else 0,
                "consumableFrequencyMonths": int(bifl_consumable["replacement_frequency_months"]) if bifl_consumable else 0,
            },
            "breakEvenMonths": break_even_months,
            "fiveYearSavings": five_year_savings,
            "trap_asin": asin,
            "winner_asin": alternative_data["bifl_asin"],
        }
    
    finally:
        conn.close()

@app.get("/check-product")
async def check_product(
    asin: str = Query(..., description="Amazon product ASIN"),
    currency: str = Query("USD", description="Currency code")
):
    """
    Main endpoint: Returns TCO data for a product
    
    Expected response format from functional spec:
    {
      "product_id": "B07VVK39F7",
      "status": "trap",  # or "fair" or "unknown"
      "category": "air_purifier",
      "math": {
        "sticker_price": 99.99,
        "consumable_name": "HEPA Filter Model-X",
        "consumable_price": 29.99,
        "consumable_lifespan_months": 4,
        "annual_maintenance": 89.97,
        "total_year_1": 189.96
      },
      "recommendation": {
        "asin": "B08PVDSW21",
        "name": "Winix 5500-2",
        "reason": "Filters last 12 months and cost 50% less."
      }
    }
    """
    
    # Currency validation
    if currency not in ["USD", "GBP", "CAD", "EUR", "INR"]:
        raise HTTPException(status_code=400, detail="Unsupported currency")
    
    # For now, only USD and INR are fully supported
    if currency not in ["USD", "INR"]:
        raise HTTPException(status_code=400, detail=f"Currency {currency} not yet implemented. Supported: USD, INR")
    
    conn = get_db_connection()
    
    try:
        # Skip static database - it may be outdated
        # Instead, check analyzed_products cache for recent AI analyses
        analyzed = conn.execute("""
            SELECT * FROM analyzed_products 
            WHERE asin = ? AND currency = ? AND expires_at > datetime('now')
        """, (asin, currency)).fetchone()
        
        if analyzed:
            # Return cached AI analysis (fresh within expiry date)
            return {
                "product_id": asin,
                "status": "low_risk" if analyzed["annual_maintenance"] < analyzed["base_price"] * 0.5 else "high_risk",
                "category": analyzed["category"],
                "math": {
                    "sticker_price": analyzed["base_price"],
                    "consumable_name": analyzed["consumable_name"],
                    "consumable_price": analyzed["consumable_price"],
                    "consumable_lifespan_months": analyzed["replacement_months"],
                    "annual_maintenance": analyzed["annual_maintenance"],
                    "total_year_1": analyzed["base_price"] + analyzed["annual_maintenance"]
                },
                "recommendation": {
                    "name": analyzed["bifl_name"],
                    "reason": analyzed["bifl_reasoning"]
                } if analyzed["bifl_name"] else None,
                "ai_powered": True,
                "confidence": analyzed["ai_confidence"],
                "data_source": "Cached AI Analysis",
                "cached_at": analyzed.get("created_at")
            }
        
        # Product not in cache - return unknown to trigger AI analysis
        return {
            "product_id": asin,
                "status": "unknown",
                "error": "Product not in database. Use /analyze-unknown-product endpoint."
            }
    
    finally:
        conn.close()


@app.post("/analyze-unknown-product")
async def analyze_unknown_product(
    asin: str = Query(..., description="Amazon product ASIN"),
    product_title: str = Query(..., description="Product title from Amazon page"),
    base_price: float = Query(..., description="Product price"),
    currency: str = Query("USD", description="Currency code")
):
    """
    Analyze unknown product using Groq AI (Llama 3.1 8B)
    
    This endpoint uses AI to:
    1. Classify product category
    2. Estimate consumable costs
    3. Suggest BIFL alternatives
    4. Cache results for future queries
    """
    
    # Import AI analyzer
    try:
        from ai_analyzer import analyze_product
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="AI analyzer not available. Install groq and set GROQ_API_KEY."
        )
    
    conn = get_db_connection()
    
    try:
        # Check cache first
        cached = conn.execute("""
            SELECT * FROM analyzed_products 
            WHERE asin = ? AND currency = ? AND expires_at > datetime('now')
        """, (asin, currency)).fetchone()
        
        if cached:
            return {
                "product_id": asin,
                "status": "cached",
                "category": cached["category"],
                "math": {
                    "sticker_price": cached["base_price"],
                    "consumable_name": cached["consumable_name"],
                    "consumable_price": cached["consumable_price"],
                    "annual_maintenance": cached["annual_maintenance"],
                    "total_year_1": cached["base_price"] + (cached["annual_maintenance"] or 0)
                },
                "recommendation": {
                    "name": cached["bifl_name"],
                    "price": cached["bifl_price"],
                    "reason": cached["bifl_reasoning"]
                } if cached["bifl_name"] else None,
                "ai_powered": True,
                "confidence": cached["ai_confidence"]
            }
        
        # Analyze with AI
        result = analyze_product(product_title, base_price, currency)
        
        # If low-risk, return early with enhanced data
        if result['status'] == 'low_risk':
            return {
                "product_id": asin,
                "status": "low_risk",
                "category": result.get('category', 'general'),
                "message": "This product likely has low recurring costs",
                "ai_powered": True,
                "confidence": result.get('confidence', 0.85),
                "reasoning": result.get('reasoning', 'Product classified as low-maintenance based on AI analysis'),
                "data_source": "Groq AI Analysis",
                "timestamp": datetime.now().isoformat()
            }
        
        # Cache the result
        math = result.get('math', {})
        recommendation = result.get('recommendation', {})
        
        conn.execute("""
            INSERT OR REPLACE INTO analyzed_products 
            (asin, product_name, category, base_price, currency, marketplace,
             consumable_name, consumable_price, replacement_months, annual_maintenance,
             bifl_name, bifl_price, bifl_reasoning, ai_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asin, product_title, result['category'], base_price, currency,
            'US' if currency == 'USD' else 'IN',
            math.get('consumable_name'), math.get('consumable_price'),
            math.get('consumable_lifespan_months'), math.get('annual_maintenance', 0),
            recommendation.get('name') if recommendation else None,
            recommendation.get('estimated_price') if recommendation else None,
            recommendation.get('reasoning') if recommendation else None,
            result.get('confidence', 0.5)
        ))
        conn.commit()
        
        return {
            "product_id": asin,
            "status": result['status'],
            "category": result['category'],
            "math": math,
            "recommendation": recommendation,
            "ai_powered": True,
            "confidence": result.get('confidence', 0.5)
        }
    
    finally:
        conn.close()




@app.get("/fetch-live-price")
async def fetch_live_price(asin: str = Query(..., description="Amazon product ASIN")):
    """
    Fetch live product data from Amazon via RapidAPI
    
    This endpoint uses RapidAPI to get real-time product information
    including current price, title, ratings, and availability.
    
    Returns:
        {
            "success": bool,
            "data": {
                "asin": str,
                "title": str,
                "price": float,
                "currency": str,
                "image_url": str,
                "rating": float,
                "reviews_count": int,
                "availability": str,
                "affiliate_link": str
            }
        }
    """
    try:
        from rapid_api_client import get_product_data, RapidAPIClient
        
        # Fetch product data from RapidAPI
        product = get_product_data(asin, country="IN")
        
        if not product:
            # Fallback: Try to get from database cache
            conn = get_db_connection()
            cached = conn.execute("""
                SELECT * FROM products WHERE parent_asin = ? LIMIT 1
            """, (asin,)).fetchone()
            conn.close()
            
            if cached:
                return {
                    "success": True,
                    "data": {
                        "asin": asin,
                        "title": cached["product_name"],
                        "price": cached["sticker_price"],
                        "currency": "INR",
                        "data_source": "Database Cache",
                        "affiliate_link": f"https://www.amazon.in/dp/{asin}?tag={os.getenv('AMAZON_TAG')}"
                    },
                    "warning": "Live data unavailable, showing cached data"
                }
            
            raise HTTPException(
                status_code=404,
                detail="Product not found or API error. Please try again later."
            )
        
        # Build affiliate link
        client = RapidAPIClient()
        affiliate_link = client.build_affiliate_link(asin, "IN")
        
        return {
            "success": True,
            "data": {
                **product,
                "affiliate_link": affiliate_link,
                "data_source": "RapidAPI",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except ValueError as e:
        # RapidAPI key not configured
        raise HTTPException(
            status_code=500,
            detail=f"RapidAPI configuration error: {str(e)}. Please configure API key."
        )
    except Exception as e:
        # Log error and return graceful message
        print(f"Error in fetch_live_price: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch product data. Service temporarily unavailable."
        )


@app.get("/scrape-price")
async def scrape_price(asin: str = Query(..., description="Amazon product ASIN")):
    """
    Scrapes current Amazon price for a product
    TODO: Implement with rotating proxy service
    """
    # Placeholder - will be implemented with BrightData/Scrape.do
    raise HTTPException(status_code=501, detail="Price scraping not yet implemented")


@app.get("/price-intelligence")
async def price_intelligence(
    asin: str = Query(..., description="Amazon product ASIN"),
    current_price: float = Query(..., description="Current product price"),
    currency: str = Query("INR", description="Currency code")
):
    """
    🎯 GhostPrice Intelligence: Price tracking, fake discount detection, and buy recommendations
    
    This is the KILLER FEATURE that sets GhostPrice apart from competitors.
    
    Features:
    - Tracks price history automatically
    - Detects fake discounts (inflated before 'sale')
    - Provides AI-powered buy/wait recommendations
    - Shows 30-day price statistics
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
            "message": "👻 GhostPrice is now tracking this product! Check back in a few days for price intelligence.",
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


@app.post("/analyze-ecosystem")
async def analyze_ecosystem(
    asin: str,
    product_title: str,
    product_price: float,
    user_intent: str,
    user_details: str = "",
    currency: str = "INR"
):
    """
    🛍️ Deep Ecosystem Analysis: Complete product ecosystem with required items,
    maintenance, hidden costs, and better alternatives
    
    This feature asks users WHY they need a product and provides comprehensive
    analysis including all necessary accessories, ongoing costs, and alternatives.
    
    Args:
        asin: Product ASIN
        product_title: Product name
        product_price: Product price
        user_intent: Why user wants this (personal, work, gift, upgrade)
        user_details: Specific requirements or use case
        currency: Currency code (default: INR)
    """
    from ecosystem_analyzer import EcosystemAnalyzer
    
    try:
        analyzer = EcosystemAnalyzer()
        
        # Get AI analysis
        analysis = analyzer.analyze_ecosystem(
            product_title=product_title,
            product_price=product_price,
            user_intent=user_intent,
            user_details=user_details,
            currency=currency
        )
        
        if analysis.get("status") == "error":
            return analysis
        
        # Enrich with real prices from RapidAPI
        enriched_analysis = analyzer.enrich_with_real_prices(analysis)
        
        return {
            **enriched_analysis,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Groq AI + RapidAPI"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": "Ecosystem analysis failed",
            "details": str(e)
        }


@app.get("/price-stats")
async def get_price_stats(
    asin: str = Query(..., description="Amazon product ASIN"),
    days: int = Query(30, description="Number of days for statistics"),
    country: str = Query("IN", description="Marketplace country (IN, US, etc.)")
):
    """
    Get price statistics and intelligence for a product
    
    Returns price intelligence including:
    - Current price vs 30-day low/high/average
    - Buy recommendation
    - Data source
    """
    try:
        from price_tracker import PriceTracker
        
        tracker = PriceTracker()
        # Pass country to tracker for proper routing (US -> Apify, IN -> Crowdsourcing)
        stats = tracker.get_price_stats(asin, days=days, country=country)
        
        if not stats:
            return {
                "success": False,
                "message": "No price data available",
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
            "source": stats.get("source", "Unknown"),
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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
