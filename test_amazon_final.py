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

result = {
    "status": "UNKNOWN",
    "message": "",
    "data": None,
    "error": None
}

try:
    # Setup
    credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
    credential_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
    partner_tag = os.getenv("AMAZON_TAG")
    marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")
    
    result["config"] = {
        "credential_id": f"{credential_id[:10]}...****",
        "partner_tag": partner_tag,
        "marketplace": marketplace
    }
    
    # Initialize
    api_client = ApiClient(
        credential_id=credential_id,
        credential_secret=credential_secret,
        version="2.2"
    )
    api = DefaultApi(api_client)
    
    # Test ASIN
    test_asin = 'B0DLFMFBJW'
    
    # Create request
    request = GetItemsRequestContent(
        partner_tag=partner_tag,
        item_ids=[test_asin],
        resources=['itemInfo.title', 'offersV2.listings.price', 'images.primary.large']
    )
    
    # Make API call
    response = api.get_items(
        x_marketplace=marketplace,
        get_items_request_content=request
    )
    
    # Success!
    result["status"] = "SUCCESS"
    result["message"] = "Amazon API call successful"
    
    # Parse response
    if hasattr(response, 'to_dict'):
        data = response.to_dict()
        result["data"] = data
        
        # Extract product info
        items_result = data.get('items_result', {})
        items = items_result.get('items', [])
        
        if items:
            item = items[0]
            result["product"] = {
                "asin": item.get('asin'),
                "title": item.get('item_info', {}).get('title', {}).get('display_value', 'N/A'),
                "price": None,
                "image": item.get('images', {}).get('primary', {}).get('large', {}).get('url', 'N/A'),
                "link": item.get('detail_page_url', 'N/A')
            }
            
            # Price
            offers = item.get('offers_v2', {}).get('listings', [])
            if offers:
                price_obj = offers[0].get('price', {})
                amount = price_obj.get('amount', 'N/A')
                currency = price_obj.get('currency', 'INR')
                result["product"]["price"] = f"{currency} {amount}"

except ApiException as e:
    result["status"] = "API_ERROR"
    result["message"] = f"Amazon API returned error: {e.reason}"
    result["error"] = {
        "status_code": e.status,
        "reason": e.reason,
        "body": str(e.body)
    }
    
    if "ASSOCIATE_NOT_ELIGIBLE" in str(e.body):
        result["message"] = "Amazon Associates account not eligible for API access yet"
        result["solution"] = "Account needs 3 qualifying sales within 180 days or API approval"

except Exception as e:
    result["status"] = "ERROR"
    result["message"] = str(e)
    result["error"] = str(e)

# Write to JSON file
with open('amazon_test_result.json', 'w') as f:
    json.dump(result, indent=2, fp=f)

# Also print summary
print(json.dumps(result, indent=2))
