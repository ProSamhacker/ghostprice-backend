import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'creatorsapi-python-sdk'))

from dotenv import load_dotenv
from creatorsapi_python_sdk.api_client import ApiClient
from creatorsapi_python_sdk.api.default_api import DefaultApi
from creatorsapi_python_sdk.models.get_items_request_content import GetItemsRequestContent
from creatorsapi_python_sdk.exceptions import ApiException

load_dotenv()

print("=" * 60)
print("AMAZON CREATORS API TEST")
print("=" * 60)

# Setup
credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
credential_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
partner_tag = os.getenv("AMAZON_TAG")
marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")

print(f"\nCredentials: {credential_id[:10]}...****")
print(f"Partner Tag: {partner_tag}")
print(f"Marketplace: {marketplace}")

# Initialize
api_client = ApiClient(
    credential_id=credential_id,
    credential_secret=credential_secret,
    version="2.2"
)
api = DefaultApi(api_client)

print("\n[OK] API Client initialized")

# Test ASIN
test_asin = 'B0DLFMFBJW'  # From your sample data
print(f"\nTesting with ASIN: {test_asin}")
print("-" * 60)

# Create request
request = GetItemsRequestContent(
    partner_tag=partner_tag,
    item_ids=[test_asin],
    resources=['itemInfo.title', 'offersV2.listings.price', 'images.primary.large']
)

try:
    # Make API call
    print("\nCalling Amazon API...")
    response = api.get_items(
        x_marketplace=marketplace,
        get_items_request_content=request
    )
    
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    
    # Parse response
    if hasattr(response, 'to_dict'):
        data = response.to_dict()
        print("\nResponse Data:")
        print(json.dumps(data, indent=2, default=str))
        
        # Extract product info
        items_result = data.get('items_result', {})
        items = items_result.get('items', [])
        
        if items:
            item = items[0]
            print("\n" + "=" * 60)
            print("PRODUCT DETAILS:")
            print("=" * 60)
            
            # Title
            title = item.get('item_info', {}).get('title', {}).get('display_value', 'N/A')
            print(f"Title: {title}")
            
            # Price
            offers = item.get('offers_v2', {}).get('listings', [])
            if offers:
                price_obj = offers[0].get('price', {})
                amount = price_obj.get('amount', 'N/A')
                currency = price_obj.get('currency', 'INR')
                print(f"Price: {currency} {amount}")
            
            # Image
            images = item.get('images', {}).get('primary', {}).get('large', {})
            image_url = images.get('url', 'N/A')
            print(f"Image: {image_url}")
            
            # Link
            link = item.get('detail_page_url', 'N/A')
            print(f"Link: {link}")
    
except ApiException as e:
    print("\n" + "=" * 60)
    print("API ERROR")
    print("=" * 60)
    print(f"Status: {e.status}")
    print(f"Reason: {e.reason}")
    print(f"Body: {e.body}")
    
    if "ASSOCIATE_NOT_ELIGIBLE" in str(e.body):
        print("\n[WARNING] Your Amazon Associates account is not yet eligible for API access")
        print("Possible reasons:")
        print("  - Account is new (needs 3 sales within 180 days)")
        print("  - Still under review")
        print("  - API access not approved yet")
        print("\nSolution: Use cached/mock data until account is approved")

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
