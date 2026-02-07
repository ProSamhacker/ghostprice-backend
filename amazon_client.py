"""
Amazon Creators API Client using Official SDK
Handles authentication and product data retrieval
"""

import os
import sys
from dotenv import load_dotenv

# Add SDK to path
sdk_path = os.path.join(os.path.dirname(__file__), 'creatorsapi-python-sdk')
sys.path.insert(0, sdk_path)

from creatorsapi_python_sdk.api_client import ApiClient
from creatorsapi_python_sdk.api.default_api import DefaultApi
from creatorsapi_python_sdk.models.get_items_request_content import GetItemsRequestContent
from creatorsapi_python_sdk.exceptions import ApiException

load_dotenv()

class AmazonCreatorsAPIClient:
    def __init__(self):
        # Load credentials from environment
        self.credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
        self.credential_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
        self.version = os.getenv("AMAZON_API_VERSION", "2.2")
        self.partner_tag = os.getenv("AMAZON_TAG")
        self.marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")
        
        # Initialize API client (handles OAuth automatically)
        self.api_client = ApiClient(
            credential_id=self.credential_id,
            credential_secret=self.credential_secret,
            version=self.version
        )
        
        # Initialize API
        self.api = DefaultApi(self.api_client)
        
        print(f"[OK] Amazon Creators API Client initialized")
        print(f"   Marketplace: {self.marketplace}")
        print(f"   Version: {self.version}")
        print(f"   Partner Tag: {self.partner_tag}")

    def get_product_details(self, asins: list):
        """
        Fetch product details for given ASINs
        
        Args:
            asins: List of Amazon product ASINs
            
        Returns:
            Dict mapping ASIN to product data (title, price, link, image)
        """
        print(f"\n[INFO] Fetching details for ASINs: {asins}")
        
        # Define resources to fetch
        resources = [
            'images.primary.large',
            'itemInfo.title',
            'offersV2.listings.price',
            'offersV2.listings.availability'
        ]
        
        # Create request
        request = GetItemsRequestContent(
            partner_tag=self.partner_tag,
            item_ids=asins,
            resources=resources
        )
        
        try:
            # Call API
            response = self.api.get_items(
                x_marketplace=self.marketplace,
                get_items_request_content=request
            )
            
            print("[OK] API call successful!")
            
            # Parse response
            return self._parse_response(response, asins)
            
        except ApiException as e:
            print(f"[ERROR] API Exception: {e}")
            return None
            
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return None
    
    def _parse_response(self, response, requested_asins):
        """
        Parse API response into simplified format
        """
        results = {}
        
        # Convert response to dict if it's an object
        if hasattr(response, 'to_dict'):
            response_dict = response.to_dict()
        else:
            response_dict = response
        
        # Navigate to items
        items_result = response_dict.get('items_result', {})
        items = items_result.get('items', [])
        
        if not items:
            print(f"[WARN] No items found in response")
            return None
        
        print(f"[OK] Found {len(items)} items")
        
        for item in items:
            asin = item.get('asin')
            
            # Extract title
            title = "Unknown Product"
            item_info = item.get('item_info', {})
            title_obj = item_info.get('title', {})
            if title_obj and 'display_value' in title_obj:
                title = title_obj['display_value']
            
            # Extract price
            price = 0.0
            currency = "INR" if "amazon.in" in self.marketplace else "USD"
            currency_symbol = "Rs." if currency == "INR" else "$"
            
            offers_v2 = item.get('offers_v2', {})
            listings = offers_v2.get('listings', [])
            if listings and len(listings) > 0:
                price_obj = listings[0].get('price')
                if price_obj:
                    amount_obj = price_obj.get('amount')
                    if amount_obj:
                        price = float(amount_obj)
                    currency_obj = price_obj.get('currency')
                    if currency_obj:
                        currency = currency_obj
            
            # Get affiliate link
            detail_url = item.get('detail_page_url')
            if not detail_url:
                detail_url = f"https://{self.marketplace}/dp/{asin}?tag={self.partner_tag}"
            
            # Get image
            image_url = ""
            images = item.get('images', {})
            if images:
                primary = images.get('primary', {})
                if primary:
                    large = primary.get('large', {})
                    if large:
                        image_url = large.get('url', '')
            
            results[asin] = {
                "title": title,
                "price": price,
                "currency": currency,
                "link": detail_url,
                "image": image_url
            }
            
            print(f"   [+] {asin}: {title} - {currency_symbol}{price}")
        
        # Check for errors
        errors = response_dict.get('errors', [])
        if errors:
            print(f"\n[WARN] API returned {len(errors)} error(s):")
            for error in errors:
                print(f"   * {error.get('code', 'Unknown')}: {error.get('message', 'No message')}")
        
        return results if results else None

# Initialize global client
amazon_client = AmazonCreatorsAPIClient()
