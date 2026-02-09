"""
Price Tracker Module for GhostPrice
Tracks price history and detects fake discounts
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class PriceTracker:
    def __init__(self, db_path="lifecycle.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def track_price(self, asin: str, price: float, currency: str = "INR", source: str = "extension"):
        """
        Record a price snapshot
        
        Args:
            asin: Amazon product ASIN
            price: Current price
            currency: Currency code (default: INR)
            source: Data source (extension, rapidapi, etc.)
        """
        conn = self.get_connection()
        try:
            conn.execute("""
                INSERT INTO price_history (asin, price, currency, timestamp, source)
                VALUES (?, ?, ?, datetime('now'), ?)
            """, (asin, price, currency, source))
            conn.commit()
        finally:
            conn.close()
    
    def import_price_history_to_db(self, asin: str, country: str = "IN"):
        """
        Smart fallback chain for bootstrapping price history
        
        Priority:
        1. Try Apify (10 free runs/month, best data)
        2. If Apify fails → Try free scraper
        3. Save to database for crowdsourcing
        
        Args:
            asin: Amazon product ASIN
            country: Country code for marketplace
        """
        
        # Step 1: Try Apify first (best quality data)
        print(f"📊 Attempting to fetch price history for {asin}...")
        print("🥇 Priority 1: Trying Apify...")
        
        history_data = None
        source = None
        
        try:
            from apify_client import get_apify_price_history
            
            # Apify works reliably for US, but not for India
            if country.upper() == "US":
                history_data = get_apify_price_history(asin, country, days=30)
                
                if history_data and history_data.get("price_history"):
                    print(f"✅ Apify success! Got {len(history_data['price_history'])} data points")
                    source = "apify_import"
                else:
                    print("⚠️ Apify failed or returned no data")
            else:
                print(f"⚠️ Skipping Apify for {country.upper()} marketplace (India not well supported)")
                print("💡 Using crowdsourcing strategy for India products")
        except Exception as e:
            print(f"⚠️ Apify error: {e}")
        
        # Step 2: Fallback to crowdsourcing only if Apify failed
        if not history_data:
            print("⚠️ No Apify data available")
            print("💡 Will rely on crowdsourcing only (no fake data)")
            return False
        
        conn = self.get_connection()
        try:
            imported_count = 0
            for price_point in history_data["price_history"]:
                # Check if timestamp already exists
                existing = conn.execute("""
                    SELECT id FROM price_history
                    WHERE asin = ? AND timestamp = ?
                """, (asin, price_point["timestamp"])).fetchone()
                
                if not existing and price_point.get("price", 0) > 0:
                    conn.execute("""
                        INSERT INTO price_history (asin, price, currency, timestamp, source)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        asin,
                        price_point["price"],
                        "INR" if country == "IN" else "USD",
                        price_point["timestamp"],
                        source
                    ))
                    imported_count += 1
            
            conn.commit()
            
            data_source = "Apify" if source == "apify_import" else "Free Scraper"
            print(f"✅ Imported {imported_count} price points from {data_source}")
            return True
            
        finally:
            conn.close()
    
    def get_price_stats(self, asin: str, days: int = 30, use_keepa: bool = True, country: str = "IN") -> Optional[Dict]:
        """
        Get price statistics for the last N days
        
        Strategy:
        1. Check local database first
        2. If no data, import from Apify/Scraper (one-time)
        3. Future requests use local data only
        
        Args:
            asin: Amazon product ASIN
            days: Number of days to look back (default: 30)
            use_keepa: Whether to import external data if no local data (default: True)
            country: Marketplace country code (default: IN)
            
        Returns:
            Dictionary with price stats or None if insufficient data
        """
        
        # ALWAYS check local database first
        conn = self.get_connection()
        try:
            history = conn.execute("""
                SELECT price, timestamp FROM price_history
                WHERE asin = ? AND timestamp > datetime('now', '-{} days')
                ORDER BY timestamp DESC
            """.format(days), (asin,)).fetchall()
            
            # If we have enough local data, use it!
            if history and len(history) >= 5:
                # ... (rest of local data logic)
                prices = [row['price'] for row in history]
                # ...
                return {
                    # ... (return stats)
                    "current": prices[0],
                    "min_30d": min(prices),
                    "max_30d": max(prices),
                    "avg_30d": sum(prices) / len(prices),
                    "is_lowest": prices[0] == min(prices),
                    "is_highest": prices[0] == max(prices),
                    "data_points": len(prices),
                    "price_range": max(prices) - min(prices),
                    "volatility": ((max(prices) - min(prices)) / (sum(prices) / len(prices))) * 100 if sum(prices) > 0 else 0,
                    "source": "Local Database"
                }
        finally:
            conn.close()
        
        # Not enough local data - bootstrap using smart fallback chain
        if use_keepa:
            print(f"⚠️ No local data for {asin}, initiating smart fallback chain...")
            
            # Try Apify → Crowdsourcing fallback chain
            # Pass the country so we can decide whether to use Apify (US) or not (IN)
            success = self.import_price_history_to_db(asin, country=country)
            
            if success:
                # Now query our database again (which has imported data)
                conn = self.get_connection()
                try:
                    history = conn.execute("""
                        SELECT price, timestamp FROM price_history
                        WHERE asin = ? AND timestamp > datetime('now', '-{} days')
                        ORDER BY timestamp DESC
                    """.format(days), (asin,)).fetchall()
                    
                    if history and len(history) >= 2:
                        prices = [row['price'] for row in history]
                        current_price = prices[0]
                        min_price = min(prices)
                        max_price = max(prices)
                        avg_price = sum(prices) / len(prices)
                        
                        # Determine source from database
                        source_row = conn.execute("""
                            SELECT source FROM price_history
                            WHERE asin = ? LIMIT 1
                        """, (asin,)).fetchone()
                        
                        data_source = "Crowdsourced"
                        if source_row:
                            if "apify" in source_row[0]:
                                data_source = "Apify (Historical)"
                            elif "scraper" in source_row[0]:
                                data_source = "Bootstrapped (Scraper)"
                        
                        print(f"✅ Using {data_source.lower()} data for {asin} ({len(prices)} points)")
                        
                        return {
                            "current": current_price,
                            "min_30d": min_price,
                            "max_30d": max_price,
                            "avg_30d": avg_price,
                            "is_lowest": current_price == min_price,
                            "is_highest": current_price == max_price,
                            "data_points": len(prices),
                            "price_range": max_price - min_price,
                            "volatility": ((max_price - min_price) / avg_price) * 100 if avg_price > 0 else 0,
                            "source": data_source
                        }
                finally:
                    conn.close()
        
        # No data available anywhere
        return None
    
    def detect_fake_discount(self, asin: str, current_price: float, claimed_discount_pct: float = 0) -> Dict:
        """
        Detect if a discount is fake (price was inflated before sale)
        
        Args:
            asin: Amazon product ASIN
            current_price: Current selling price
            claimed_discount_pct: Claimed discount percentage (if available)
            
        Returns:
            Dictionary with fake discount analysis
        """
        stats = self.get_price_stats(asin)
        
        if not stats:
            return {
                "verified": False,
                "reason": "Insufficient price history data",
                "is_fake": False
            }
        
        # Check if price was artificially raised before sale
        # If max price in 30 days is >15% higher than average, it's suspicious
        if stats["max_30d"] > stats["avg_30d"] * 1.15:
            # Price spiked recently - likely inflated before discount
            real_discount = ((stats["max_30d"] - current_price) / stats["max_30d"]) * 100
            
            return {
                "is_fake": True,
                "verified": True,
                "real_avg_price": round(stats["avg_30d"], 2),
                "inflated_price": round(stats["max_30d"], 2),
                "current_price": current_price,
                "claimed_discount_pct": claimed_discount_pct,
                "real_discount_pct": round(real_discount, 1),
                "savings_vs_avg": round(stats["avg_30d"] - current_price, 2),
                "message": f"⚠️ Price was inflated to ₹{stats['max_30d']:.0f} before this 'sale'. Real average: ₹{stats['avg_30d']:.0f}"
            }
        
        # Check if current price is actually good
        if current_price <= stats["min_30d"]:
            return {
                "is_fake": False,
                "verified": True,
                "is_best_price": True,
                "message": "✅ Lowest price in 30 days - Genuine deal!"
            }
        elif current_price <= stats["avg_30d"] * 0.95:
            return {
                "is_fake": False,
                "verified": True,
                "is_good_deal": True,
                "message": f"✅ Good deal - Below 30-day average (₹{stats['avg_30d']:.0f})"
            }
        else:
            return {
                "is_fake": False,
                "verified": True,
                "is_average": True,
                "message": f"Fair price - Close to 30-day average (₹{stats['avg_30d']:.0f})"
            }
    
    def get_buy_recommendation(self, asin: str, current_price: float) -> Dict:
        """
        Get AI-powered buy recommendation based on price history
        
        Args:
            asin: Amazon product ASIN
            current_price: Current price
            
        Returns:
            Dictionary with buy recommendation
        """
        stats = self.get_price_stats(asin)
        
        if not stats:
            return {
                "action": "track",
                "confidence": 50,
                "reason": "Not enough data yet. We'll track prices for you!",
                "color": "gray"
            }
        
        # Best price - BUY NOW
        if current_price <= stats["min_30d"]:
            return {
                "action": "buy_now",
                "confidence": 95,
                "reason": f"🔥 Lowest price in 30 days! (₹{stats['min_30d']:.0f})",
                "color": "green",
                "urgency": "high"
            }
        
        # Below average - GOOD DEAL
        elif current_price <= stats["avg_30d"] * 0.95:
            return {
                "action": "good_deal",
                "confidence": 80,
                "reason": f"✓ Good price - 5% below average (avg: ₹{stats['avg_30d']:.0f})",
                "color": "green",
                "urgency": "medium"
            }
        
        # Above average - WAIT
        elif current_price >= stats["avg_30d"] * 1.15:
            expected_drop = current_price - stats["avg_30d"]
            return {
                "action": "wait",
                "confidence": 85,
                "reason": f"⏳ Wait for better price. Currently ₹{expected_drop:.0f} above average",
                "color": "orange",
                "urgency": "low",
                "expected_price": round(stats["avg_30d"], 2)
            }
        
        # Near maximum - DEFINITELY WAIT
        elif current_price >= stats["max_30d"] * 0.95:
            return {
                "action": "wait",
                "confidence": 90,
                "reason": f"❌ Near highest price (₹{stats['max_30d']:.0f}). Expect a drop soon!",
                "color": "red",
                "urgency": "very_low",
                "expected_price": round(stats["avg_30d"], 2)
            }
        
        # Average price - NEUTRAL
        else:
            return {
                "action": "neutral",
                "confidence": 65,
                "reason": f"Fair price - Near 30-day average (₹{stats['avg_30d']:.0f})",
                "color": "yellow",
                "urgency": "medium"
            }
    
    def get_price_history(self, asin: str, days: int = 30) -> List[Dict]:
        """
        Get full price history for charting
        
        Args:
            asin: Amazon product ASIN
            days: Number of days to look back
            
        Returns:
            List of price points with timestamps
        """
        conn = self.get_connection()
        try:
            history = conn.execute("""
                SELECT price, timestamp, source
                FROM price_history
                WHERE asin = ? AND timestamp > datetime('now', '-{} days')
                ORDER BY timestamp ASC
            """.format(days), (asin,)).fetchall()
            
            return [
                {
                    "price": row['price'],
                    "timestamp": row['timestamp'],
                    "source": row['source']
                }
                for row in history
            ]
        finally:
            conn.close()
