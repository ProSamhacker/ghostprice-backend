"""
Price Tracker Module
Handles price history tracking, statistics calculation, and buy recommendations.
"""

from datetime import datetime, timedelta
import os
from typing import Dict, Optional, List, Tuple
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class PriceTracker:
    def __init__(self):
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        self.conn_string = DATABASE_URL
        
    def _get_connection(self):
        """Get database connection"""
        return psycopg.connect(self.conn_string, row_factory=dict_row)

    def track_price(
        self, 
        asin: str, 
        current_price: float, 
        currency: str = "INR", 
        marketplace: str = "IN",
        source: str = "extension"
    ) -> bool:
        """
        Record a new price point for a product.
        Updates the price_history table and the last_updated_at in tracked_products.
        """
        try:
            with self._get_connection() as conn:
                # 1. Update/Insert into tracked_products
                conn.execute("""
                    INSERT INTO tracked_products (asin, last_updated_at, currency, marketplace)
                    VALUES (%s, CURRENT_TIMESTAMP, %s, %s)
                    ON CONFLICT(asin) DO UPDATE SET
                        last_updated_at = CURRENT_TIMESTAMP,
                        currency = excluded.currency
                """, (asin, currency, marketplace))
                
                # 2. Insert into price_history
                conn.execute("""
                    INSERT INTO price_history (asin, price, currency, marketplace, source, timestamp)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (asin, current_price, currency, marketplace, source))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error tracking price for {asin}: {e}")
            return False

    def get_price_stats(
        self, 
        asin: str, 
        days: int = 30,
        use_keepa: bool = False,
        country: str = "IN"
    ) -> Optional[Dict]:
        """
        Calculate price statistics for the given period.
        Returns min, max, avg, current price, and other metrics.
        """
        try:
            with self._get_connection() as conn:
                # Get stats from DB
                stats = conn.execute("""
                    SELECT 
                        MIN(price) as min_price,
                        MAX(price) as max_price,
                        AVG(price) as avg_price,
                        COUNT(*) as data_points,
                        MAX(timestamp) as last_seen
                    FROM price_history
                    WHERE asin = %s
                    AND timestamp > NOW() - INTERVAL '%s days'
                """, (asin, days)).fetchone()
                
                if not stats or stats['data_points'] == 0:
                    return None
                
                # Get current price separately (latest entry)
                latest = conn.execute("""
                    SELECT price, currency, source
                    FROM price_history
                    WHERE asin = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (asin,)).fetchone()
                
                if not latest:
                    return None
                
                current_price = latest['price']
                min_price = stats['min_price']
                max_price = stats['max_price']
                avg_price = stats['avg_price']
                
                # Determine if current price is lowest/highest
                is_lowest = current_price <= min_price
                is_highest = current_price >= max_price
                
                # Calculate volatility (standard deviation estimate or simpler range %)
                price_range = max_price - min_price
                volatility = (price_range / avg_price * 100) if avg_price > 0 else 0
                
                return {
                    "current": current_price,
                    "min_30d": min_price,
                    "max_30d": max_price,
                    "avg_30d": avg_price,
                    "is_lowest": is_lowest,
                    "is_highest": is_highest,
                    "price_range": price_range,
                    "volatility": round(volatility, 2),
                    "data_points": stats['data_points'],
                    "source": latest['source']
                }
        except Exception as e:
            print(f"Error getting stats for {asin}: {e}")
            return None

    def detect_fake_discount(self, asin: str, current_price: float) -> Dict:
        """
        Detect if the current 'discount' is likely fake based on history.
        e.g. if current price is higher than 30-day average despite being 'on sale'.
        """
        stats = self.get_price_stats(asin, days=30)
        if not stats:
            return {"is_fake": False, "confidence": 0, "reason": "Insufficient data"}
            
        avg_price = stats['avg_30d']
        
        # Simple logic: if current price is significantly above average (>10%),
        # but claimed to be a discount, it might be fake.
        # Since we don't have the "MRP" or "List Price" here easily without scraping,
        # we rely on price history.
        
        if current_price > avg_price * 1.10:
            return {
                "is_fake": True,
                "confidence": 0.8,
                "reason": f"Current price is 10% higher than 30-day average ({avg_price:.2f})"
            }
        
        return {"is_fake": False, "confidence": 0.5, "reason": "Price is consistent with history"}

    def get_buy_recommendation(self, asin: str, current_price: float) -> str:
        """
        Generate a buy recommendation: BUY_NOW, GOOD_DEAL, WAIT, FAIR_PRICE
        """
        stats = self.get_price_stats(asin, days=30)
        
        if not stats:
            return "UNKNOWN"
            
        min_price = stats['min_30d']
        avg_price = stats['avg_30d']
        max_price = stats['max_30d']
        
        if current_price <= min_price * 1.01: # Within 1% of lowest
            return "BUY_NOW"
        elif current_price < avg_price:
            return "GOOD_DEAL"
        elif current_price > avg_price * 1.1:
            return "WAIT"
        else:
            return "FAIR_PRICE"
