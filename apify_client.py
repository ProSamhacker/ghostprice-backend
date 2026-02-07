"""
Apify Amazon Price History Client
Primary source with automatic fallback to free scraper
"""

import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")


class ApifyClient:
    """Client for Apify Amazon Price History with free scraper fallback"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or APIFY_API_TOKEN
        self.base_url = "https://api.apify.com/v2"
        
        # Apify actor for Amazon price history (from your account)
        # This is YOUR actor ID - found via API
        self.actor_id = "gvFpWjQm90ZfTDdEf"  # amazon-price-history-api
    
    def get_price_history(
        self,
        asin: str,
        country: str = "IN",
        days: int = 90
    ) -> Optional[Dict]:
        """
        Fetch price history from Apify
        
        Args:
            asin: Amazon product ASIN
            country: Country code (IN=India, US=USA, etc.)
            days: Number of days of history
            
        Returns:
            Dictionary with price history or None
        """
        
        if not self.api_token:
            print("⚠️ No Apify API token, skipping Apify...")
            return None
        
        try:
            # Apify actor input for radeance/amazon-price-history-api
            # Build Amazon URL from ASIN
            country_domains = {
                "IN": "amazon.in",
                "US": "amazon.com",
                "UK": "amazon.co.uk",
                "DE": "amazon.de",
                "CA": "amazon.ca"
            }
            
            domain = country_domains.get(country.upper(), "amazon.in")
            amazon_url = f"https://www.{domain}/dp/{asin}"
            
            # CRITICAL: Must send full URL, not just ASIN!
            # Successful runs use full URLs like the console example
            actor_input = {
                "identifiers": [amazon_url],  # Full URL required!
                "country": country.lower()  # Must be lowercase: "in", "us", etc.
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            # Run the actor
            run_url = f"{self.base_url}/acts/{self.actor_id}/runs"
            
            print(f"🚀 Running Apify actor for {asin}...")
            
            response = requests.post(
                run_url,
                json=actor_input,
                headers=headers,
                timeout=30
            )
            
            # Check for quota/credit errors
            if response.status_code == 402:
                print("💳 Apify credits exhausted!")
                return None
            
            if response.status_code == 429:
                print("⏰ Apify rate limit reached!")
                return None
            
            response.raise_for_status()
            
            run_data = response.json()
            run_id = run_data.get("data", {}).get("id")
            
            if not run_id:
                print("❌ Failed to start Apify actor")
                print(f"Response: {run_data}")
                return None
            
            print(f"✅ Actor started, run ID: {run_id}")
            print(f"⏳ Waiting for actor to complete...")
            
            # Wait for actor to finish (poll status)
            import time
            max_wait = 60  # 60 seconds max
            wait_interval = 3  # Check every 3 seconds
            elapsed = 0
            
            while elapsed < max_wait:
                status_url = f"{self.base_url}/actor-runs/{run_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data.get("data", {}).get("status")
                
                if status == "SUCCEEDED":
                    print(f"✅ Actor completed successfully!")
                    break
                elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                    print(f"❌ Actor failed with status: {status}")
                    return None
                
                time.sleep(wait_interval)
                elapsed += wait_interval
            
            if elapsed >= max_wait:
                print(f"⏰ Actor timed out after {max_wait}s")
                return None
            
            # Get dataset ID
            dataset_id = status_data.get("data", {}).get("defaultDatasetId")
            
            if not dataset_id:
                print("❌ No dataset returned from Apify")
                return None
            
            # Fetch results from dataset
            dataset_url = f"{self.base_url}/datasets/{dataset_id}/items"
            
            print(f"📊 Fetching results from dataset...")
            dataset_response = requests.get(dataset_url, headers=headers, timeout=15)
            dataset_response.raise_for_status()
            
            results = dataset_response.json()
            
            if not results:
                print(f"⚠️ No data returned from Apify for {asin}")
                return None
            
            print(f"✅ Got {len(results)} results from Apify")
            
            # DEBUG: Write full response to file
            if results:
                try:
                    with open("apify_debug.txt", "w", encoding="utf-8") as f:
                        import json
                        f.write(json.dumps(results[0], indent=2))
                    print(f"📝 Debug info written to apify_debug.txt")
                except Exception as e:
                    print(f"❌ Failed to write debug info: {e}")
                
            return self._parse_apify_response(results[0], asin)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 402:
                print("💳 Apify credits exhausted!")
            elif e.response.status_code == 429:
                print("⏰ Apify rate limit reached!")
            else:
                print(f"❌ Apify API error: {e}")
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Apify error for {asin}: {e}")
            return None
    
    def _parse_apify_response(self, data: Dict, asin: str) -> Dict:
        """Parse Apify response into our format"""
        # Note: We don't filter by days here because we want to store all available history
        # The database query later will filter for specific time ranges (e.g. 30 days)
        
        # Apify returns price history in various formats
        # Check all possible keys in order of preference
        price_history = (
            data.get("price_new_history") or 
            data.get("priceHistory") or 
            data.get("price_history") or 
            []
        )
        
        if not price_history:
            print(f"⚠️ No price history found in keys: {list(data.keys())}")
            return None
        
        parsed_history = []
        for entry in price_history:
            # Handle null prices safely
            raw_price = entry.get("price")
            if raw_price is None:
                continue
                
            # Entry format: {"date": "2024-01-01", "price": 12.99}
            parsed_history.append({
                "timestamp": entry.get("date", "").split("T")[0] + "T00:00:00",
                "price": float(raw_price)
            })
        
        prices = [p["price"] for p in parsed_history if p["price"] > 0]
        
        if not prices:
            return None
        
        return {
            "asin": asin,
            "title": data.get("title", ""),
            "current_price": prices[-1],
            "price_history": parsed_history,
            "stats": {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "data_points": len(price_history)
            },
            "source": "Apify"
        }


def get_apify_price_history(asin: str, country: str = "IN", days: int = 90) -> Optional[Dict]:
    """
    Convenience function to get Apify price history with fallback
    
    Args:
        asin: Amazon product ASIN
        country: Country code
        days: Days of history
        
    Returns:
        Price history from Apify or None if failed
    """
    try:
        client = ApifyClient()
        return client.get_price_history(asin, country, days)
    except Exception as e:
        print(f"Apify error: {e}")
        return None
