"""
PriceHistory.app API Client for Price History Data
More affordable alternative to Keepa with Amazon price tracking
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

PRICEHISTORY_API_KEY = os.getenv("PRICEHISTORY_API_KEY")


class PriceHistoryClient:
    """Client for fetching historical price data from PriceHistory.app"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or PRICEHISTORY_API_KEY
        self.base_url = "https://api.pricehistory.app/v1"
        
        if not self.api_key:
            raise ValueError("PRICEHISTORY_API_KEY environment variable is required")
    
    def get_price_history(
        self,
        asin: str,
        country: str = "IN",
        days: int = 90
    ) -> Optional[Dict]:
        """
        Fetch price history from PriceHistory.app
        
        Args:
            asin: Amazon product ASIN
            country: Country code (IN=India, US=USA, etc.)
            days: Number of days of history to fetch
            
        Returns:
            Dictionary with price history data or None
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "asin": asin,
                "country": country.upper(),
                "days": days
            }
            
            response = requests.get(
                f"{self.base_url}/product/history",
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data or "history" not in data:
                return None
            
            return self._parse_response(data, asin)
            
        except Exception as e:
            print(f"PriceHistory.app API error for {asin}: {e}")
            return None
    
    def _parse_response(self, data: Dict, asin: str) -> Dict:
        """Parse PriceHistory.app API response into our format"""
        
        history = data.get("history", [])
        
        if not history:
            return None
        
        # Parse price history
        price_history = []
        for entry in history:
            # PriceHistory.app format: {"date": "2024-01-01", "price": 12.99}
            price_history.append({
                "timestamp": entry.get("date") + "T00:00:00",
                "price": float(entry.get("price", 0))
            })
        
        # Calculate statistics
        prices = [p["price"] for p in price_history if p["price"] > 0]
        
        if not prices:
            return None
        
        return {
            "asin": asin,
            "title": data.get("product_name", ""),
            "current_price": prices[-1],  # Most recent
            "price_history": price_history,
            "stats": {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "data_points": len(price_history)
            },
            "source": "PriceHistory.app"
        }
    
    def get_30day_stats(self, asin: str, country: str = "IN") -> Optional[Dict]:
        """
        Get 30-day price statistics
        
        Args:
            asin: Amazon product ASIN
            country: Country code
            
        Returns:
            30-day price statistics
        """
        data = self.get_price_history(asin, country, days=30)
        
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
        
        prices = [p["price"] for p in recent_prices if p["price"] > 0]
        
        if not prices:
            return None
        
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
            "source": "PriceHistory.app"
        }


# Country codes supported by PriceHistory.app
PRICEHISTORY_COUNTRIES = {
    "US": "US",   # United States
    "UK": "GB",   # United Kingdom
    "DE": "DE",   # Germany
    "FR": "FR",   # France
    "JP": "JP",   # Japan
    "CA": "CA",   # Canada
    "IT": "IT",   # Italy
    "IN": "IN",   # India
    "ES": "ES",   # Spain
}


def get_pricehistory_stats(asin: str, country: str = "IN") -> Optional[Dict]:
    """
    Convenience function to get PriceHistory.app stats
    
    Args:
        asin: Amazon product ASIN
        country: Country code (IN, US, etc.)
        
    Returns:
        30-day price statistics from PriceHistory.app
    """
    try:
        client = PriceHistoryClient()
        return client.get_30day_stats(asin, country)
    except Exception as e:
        print(f"PriceHistory.app stats error: {e}")
        return None
