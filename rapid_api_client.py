"""
RapidAPI Client for Amazon Product Data
Uses the Real-Time Amazon Data API
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# RapidAPI Configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "real-time-amazon-data.p.rapidapi.com")
AMAZON_TAG = os.getenv("AMAZON_TAG", "lifecycle-20")


class RapidAPIClient:
    """Client for fetching Amazon product data via RapidAPI"""
    
    def __init__(self, api_key: str = None, host: str = None):
        self.api_key = api_key or RAPIDAPI_KEY
        self.host = host or RAPIDAPI_HOST
        self.base_url = f"https://{self.host}"
        
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY environment variable is required")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to RapidAPI"""
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"RapidAPI request failed: {e}")
            raise
    
    def get_product_details(self, asin: str, country: str = "IN") -> Optional[Dict]:
        """
        Fetch product details for a given ASIN
        
        Args:
            asin: Amazon Standard Identification Number
            country: Country code (IN for India, US for USA)
        
        Returns:
            Dict with product information or None if not found
        """
        try:
            # Real-Time Amazon Data API endpoint
            params = {
                "asin": asin,
                "country": country
            }
            
            data = self._make_request("product-details", params)
            
            if not data or 'data' not in data:
                return None
            
            product = data['data']
            
            # Extract relevant fields
            return {
                "asin": asin,
                "title": product.get("product_title", ""),
                "price": self._extract_price(product),
                "currency": product.get("product_price_currency", "INR"),
                "image_url": product.get("product_photo", ""),
                "rating": product.get("product_star_rating", 0),
                "reviews_count": product.get("product_num_ratings", 0),
                "availability": product.get("product_availability", ""),
                "url": product.get("product_url", f"https://www.amazon.in/dp/{asin}"),
            }
            
        except Exception as e:
            print(f"Error fetching product details for {asin}: {e}")
            return None
    
    def _extract_price(self, product: Dict) -> float:
        """Extract price from product data"""
        # Try different price fields
        price_str = product.get("product_price", "0")
        
        # Remove currency symbols and convert to float
        if isinstance(price_str, str):
            # Remove common currency symbols and commas
            price_str = price_str.replace("₹", "").replace("$", "").replace(",", "").strip()
            try:
                return float(price_str)
            except ValueError:
                return 0.0
        
        return float(price_str) if price_str else 0.0
    
    def build_affiliate_link(self, asin: str, country: str = "IN") -> str:
        """
        Build Amazon affiliate link for a product
        
        Args:
            asin: Amazon Standard Identification Number
            country: Country code for marketplace
        
        Returns:
            Affiliate link URL
        """
        if country == "IN":
            base_url = "https://www.amazon.in"
        else:
            base_url = "https://www.amazon.com"
        
        return f"{base_url}/dp/{asin}?tag={AMAZON_TAG}"
    
    def search_product(self, query: str, country: str = "IN") -> Optional[Dict]:
        """
        Search for a product on Amazon by name
        
        Args:
            query: Product search query
            country: Country code (IN or US)
            
        Returns:
            First search result with product data or None
        """
        try:
            params = {
                "query": query,
                "country": country,
                "page": "1"
            }
            
            data = self._make_request("search", params)
            
            if not data or 'data' not in data or 'products' not in data['data']:
                return None
            
            products = data['data']['products']
            if not products or len(products) == 0:
                return None
            
            # Return first result
            first_product = products[0]
            
            return {
                "asin": first_product.get("asin", ""),
                "title": first_product.get("product_title", ""),
                "price": self._extract_price(first_product),
                "currency": first_product.get("product_price_currency", "INR"),
                "image_url": first_product.get("product_photo", ""),
                "rating": first_product.get("product_star_rating", 0),
                "url": first_product.get("product_url", "")
            }
            
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            return None


def get_product_data(asin: str, country: str = "IN") -> Optional[Dict]:
    """
    Convenience function to get product data
    
    Args:
        asin: Amazon product ASIN
        country: Country code (IN or US)
    
    Returns:
        Product data dictionary or None
    """
    try:
        client = RapidAPIClient()
        return client.get_product_details(asin, country)
    except ValueError as e:
        print(f"RapidAPI client error: {e}")
        return None
