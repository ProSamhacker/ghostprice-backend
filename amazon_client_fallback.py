"""
Amazon Client with Database Fallback
Works even when API access is not yet approved
"""

import os
import sys
import sqlite3
from dotenv import load_dotenv

# Add SDK to path
sdk_path = os.path.join(os.path.dirname(__file__), 'creatorsapi-python-sdk')
sys.path.insert(0, sdk_path)

from creatorsapi_python_sdk.api_client import ApiClient
from creatorsapi_python_sdk.api.default_api import DefaultApi
from creatorsapi_python_sdk.models.get_items_request_content import GetItemsRequestContent
from creatorsapi_python_sdk.exceptions import ApiException

load_dotenv()

class AmazonClientWithFallback:
    def __init__(self, db_path='lifecycle.db'):
        """Initialize with database fallback"""
        self.db_path = db_path
        self.api_available = False
        
        # Try to initialize API client
        try:
            credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
            credential_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
            self.partner_tag = os.getenv("AMAZON_TAG")
            self.marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")
            
            self.api_client = ApiClient(
                credential_id=credential_id,
                credential_secret=credential_secret,
                version=os.getenv("AMAZON_API_VERSION", "2.2")
            )
            self.api = DefaultApi(self.api_client)
            
            # Test if API is accessible
            self._test_api_access()
            
        except Exception as e:
            print(f"[INFO] API not available, using database fallback: {e}")
            self.api_available = False
    
    def _test_api_access(self):
        """Test if API access is granted"""
        try:
            # Try a minimal request
            request = GetItemsRequestContent(
                partner_tag=self.partner_tag,
                item_ids=['B08CFYH6G2'],  # Test ASIN
                resources=['itemInfo.title']
            )
            self.api.get_items(
                x_marketplace=self.marketplace,
                get_items_request_content=request
            )
            self.api_available = True
            print("[OK] Amazon API access granted!")
        except ApiException as e:
            if 'eligibility' in str(e.body).lower():
                print("[INFO] API access pending approval, using database")
            else:
                print(f"[INFO] API error: {e.reason}")
            self.api_available = False
    
    def get_product_details(self, asins: list):
        """
        Get product details from API or database
        Automatically falls back to database if API not available
        """
        if self.api_available:
            try:
                return self._get_from_api(asins)
            except Exception as e:
                print(f"[WARN] API call failed, falling back to database: {e}")
                return self._get_from_database(asins)
        else:
            print(f"[INFO] Using database for {len(asins)} products")
            return self._get_from_database(asins)
    
    def _get_from_api(self, asins: list):
        """Fetch from Amazon API"""
        resources = [
            'images.primary.large',
            'itemInfo.title',
            'offersV2.listings.price',
            'offersV2.listings.availability'
        ]
        
        request = GetItemsRequestContent(
            partner_tag=self.partner_tag,
            item_ids=asins,
            resources=resources
        )
        
        response = self.api.get_items(
            x_marketplace=self.marketplace,
            get_items_request_content=request
        )
        
        return self._parse_api_response(response, asins)
    
    def _parse_api_response(self, response, requested_asins):
        """Parse API response"""
        results = {}
        
        if hasattr(response, 'to_dict'):
            response_dict = response.to_dict()
        else:
            response_dict = response
        
        items = response_dict.get('items_result', {}).get('items', [])
        
        for item in items:
            asin = item.get('asin')
            
            # Extract data
            title = item.get('item_info', {}).get('title', {}).get('display_value', 'Unknown Product')
            
            price = 0.0
            currency = "INR"
            offers = item.get('offers_v2', {}).get('listings', [])
            if offers:
                price_obj = offers[0].get('price', {})
                if price_obj:
                    price = float(price_obj.get('amount', 0))
                    currency = price_obj.get('currency', 'INR')
            
            link = item.get('detail_page_url', f"https://{self.marketplace}/dp/{asin}?tag={self.partner_tag}")
            
            image = item.get('images', {}).get('primary', {}).get('large', {}).get('url', '')
            
            results[asin] = {
                "title": title,
                "price": price,
                "currency": currency,
                "link": link,
                "image": image,
                "source": "api"
            }
        
        return results if results else None
    
    def _get_from_database(self, asins: list):
        """Fetch from local database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results = {}
            for asin in asins:
                # Query using actual column names from database schema
                cursor.execute("""
                    SELECT parent_asin, product_name, base_price
                    FROM products
                    WHERE parent_asin = ?
                """, (asin,))
                
                row = cursor.fetchone()
                if row:
                    asin_val, title, price = row
                    
                    # Construct affiliate link
                    link = f"https://www.amazon.in/dp/{asin}?tag={self.partner_tag}"
                    
                    results[asin] = {
                        "title": title if title else "Unknown Product",
                        "price": float(price) if price else 0.0,
                        "currency": "INR",
                        "link": link,
                        "image": "",  # Image not stored in products table
                        "source": "database"
                    }
            
            conn.close()
            return results if results else None
            
        except Exception as e:
            print(f"[ERROR] Database query failed: {e}")
            import traceback
            traceback.print_exc()
            return None

# Global instance
amazon_client = AmazonClientWithFallback()

# For backward compatibility
def get_product_details(asins):
    return amazon_client.get_product_details(asins)
