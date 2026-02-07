"""
Keepa API Client for Price History Data
Provides instant access to historical Amazon pricing data
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

KEEPA_API_KEY = os.getenv("KEEPA_API_KEY")


class KeepaClient:
    """Client for fetching historical price data from Keepa"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or KEEPA_API_KEY
        self.base_url = "https://api.keepa.com"
        
        if not self.api_key:
            raise ValueError("KEEPA_API_KEY environment variable is required")
    
    def get_price_history(
        self,
        asin: str,
        domain: int = 8,  # 8 = Amazon.in (India), 1 = Amazon.com (US)
        days: int = 90
    ) -> Optional[Dict]:
        """
        Fetch price history from Keepa
        
        Args:
            asin: Amazon product ASIN
            domain: Amazon domain (8=India, 1=US, 3=Germany, 4=France, etc.)
            days: Number of days of history to fetch
            
        Returns:
            Dictionary with price history data or None
        """
        try:
            # Keepa API endpoint
            url = f"{self.base_url}/product"
            
            params = {
                "key": self.api_key,
                "domain": domain,
                "asin": asin,
                "stats": days,  # Get statistics for last N days
                "history": 1    # Include price history
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or "products" not in data or len(data["products"]) == 0:
                return None
            
            product = data["products"][0]
            
            # Parse Keepa data
            return self._parse_keepa_response(product)
            
        except Exception as e:
            print(f"Keepa API error for {asin}: {e}")
            return None
    
    def _parse_keepa_response(self, product: Dict) -> Dict:
        """
        Parse Keepa API response into our format
        
        Keepa stores prices in a compressed format:
        - Prices are in "Keepa Time" (minutes since Keepa epoch: 2011-01-01)
        - Prices are stored as integers (actual_price * 100)
        """
        
        # Keepa epoch: January 1, 2011, 00:00:00 UTC
        keepa_epoch = datetime(2011, 1, 1)
        
        # Get Amazon price history (csv[0] contains [time, price, time, price, ...])
        amazon_prices = product.get("csv", [[]])[0]  # Amazon price
        
        if not amazon_prices or len(amazon_prices) < 2:
            # Try other price types
            amazon_prices = product.get("csv", [[], []])[1]  # New price
        
        if not amazon_prices or len(amazon_prices) < 2:
            return None
        
        # Parse price history
        price_history = []
        for i in range(0, len(amazon_prices), 2):
            if i + 1 >= len(amazon_prices):
                break
            
            keepa_time = amazon_prices[i]
            keepa_price = amazon_prices[i + 1]
            
            # Skip if price is -1 (out of stock)
            if keepa_price == -1:
                continue
            
            # Convert Keepa time to datetime
            timestamp = keepa_epoch + timedelta(minutes=keepa_time)
            
            # Convert Keepa price to actual price (divide by 100)
            actual_price = keepa_price / 100.0
            
            price_history.append({
                "timestamp": timestamp.isoformat(),
                "price": actual_price
            })
        
        if not price_history:
            return None
        
        # Calculate statistics
        prices = [p["price"] for p in price_history]
        current_price = prices[-1]  # Most recent
        
        # Get stats from Keepa's stats object if available
        stats = product.get("stats", {})
        
        return {
            "asin": product.get("asin"),
            "title": product.get("title"),
            "current_price": current_price,
            "price_history": price_history,
            "stats": {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "current_rank": product.get("salesRanks", {}).get("current", [None])[0],
                "data_points": len(price_history)
            },
            "source": "Keepa API"
        }
    
    def get_30day_stats(self, asin: str, domain: int = 8) -> Optional[Dict]:
        """
        Get 30-day price statistics
        
        Args:
            asin: Amazon product ASIN
            domain: Amazon domain
            
        Returns:
            30-day price statistics
        """
        data = self.get_price_history(asin, domain, days=30)
        
        if not data:
            return None
        
        # Filter to last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_prices = [
            p for p in data["price_history"]
            if datetime.fromisoformat(p["timestamp"]) >= thirty_days_ago
        ]
        
        if not recent_prices:
            recent_prices = data["price_history"]
        
        prices = [p["price"] for p in recent_prices]
        
        return {
            "current": prices[-1],
            "min_30d": min(prices),
            "max_30d": max(prices),
            "avg_30d": sum(prices) / len(prices),
            "is_lowest": prices[-1] == min(prices),
            "is_highest": prices[-1] == max(prices),
            "data_points": len(prices),
            "price_range": max(prices) - min(prices),
            "volatility": ((max(prices) - min(prices)) / (sum(prices) / len(prices))) * 100 if prices else 0,
            "source": "Keepa API"
        }


# Domain codes for reference
KEEPA_DOMAINS = {
    "US": 1,   # Amazon.com
    "GB": 2,   # Amazon.co.uk
    "DE": 3,   # Amazon.de
    "FR": 4,   # Amazon.fr
    "JP": 5,   # Amazon.co.jp
    "CA": 6,   # Amazon.ca
    "IT": 7,   # Amazon.it
    "IN": 8,   # Amazon.in
    "ES": 9,   # Amazon.es
}


def get_keepa_stats(asin: str, country: str = "IN") -> Optional[Dict]:
    """
    Convenience function to get Keepa stats
    
    Args:
        asin: Amazon product ASIN
        country: Country code (IN, US, etc.)
        
    Returns:
        30-day price statistics from Keepa
    """
    try:
        client = KeepaClient()
        domain = KEEPA_DOMAINS.get(country, 8)
        return client.get_30day_stats(asin, domain)
    except Exception as e:
        print(f"Keepa stats error: {e}")
        return None
