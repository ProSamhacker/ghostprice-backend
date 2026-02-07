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

print("=" * 70)
print("DETAILED AMAZON API DEBUGGING")
print("=" * 70)

# Load credentials
credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
credential_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
partner_tag = os.getenv("AMAZON_TAG")
marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")

print(f"\n1. CHECKING CREDENTIALS:")
print(f"   Credential ID: {credential_id}")
print(f"   Secret Length: {len(credential_secret)} chars")
print(f"   Partner Tag: {partner_tag}")
print(f"   Marketplace: {marketplace}")

# Verify credentials match screenshot
print(f"\n2. VERIFICATION:")
if credential_id == "vdp2k685pg16tpscgedh44dp1":
    print("   [OK] Credential ID matches dashboard!")
else:
    print("   [ERROR] Credential ID does NOT match!")

if partner_tag == "nocreditai-21":
    print("   [OK] Partner tag matches dashboard!")
else:
    print("   [ERROR] Partner tag does NOT match!")

print(f"\n3. INITIALIZING API CLIENT...")
try:
    api_client = ApiClient(
        credential_id=credential_id,
        credential_secret=credential_secret,
        version="2.2"
    )
    api = DefaultApi(api_client)
    print("   [OK] API Client initialized")
except Exception as e:
    print(f"   [ERROR] Failed: {e}")
    sys.exit(1)

# Try a minimal request first
print(f"\n4. TESTING WITH MINIMAL RESOURCES...")
test_asin = 'B0DLFMFBJW'

# Test 1: Minimal request
print(f"\n   Test 1: Title only")
request1 = GetItemsRequestContent(
    partner_tag=partner_tag,
    item_ids=[test_asin],
    resources=['itemInfo.title']
)

try:
    response = api.get_items(
        x_marketplace=marketplace,
        get_items_request_content=request1
    )
    print("   [SUCCESS] Minimal request worked!")
    if hasattr(response, 'to_dict'):
        data = response.to_dict()
        print(f"   Response: {json.dumps(data, indent=4, default=str)}")
except ApiException as e:
    print(f"   [FAILED] Status: {e.status}")
    print(f"   Reason: {e.reason}")
    print(f"   Body: {e.body}")
    
    # Parse error details
    try:
        error_data = json.loads(e.body)
        print(f"\n   ERROR DETAILS:")
        print(f"   - Type: {error_data.get('__type', 'Unknown')}")
        print(f"   - Message: {error_data.get('message', 'No message')}")
        
        # Check specific error types
        error_type = error_data.get('__type', '')
        if 'AccessDenied' in error_type:
            print(f"\n   DIAGNOSIS: Access Denied")
            print(f"   This could mean:")
            print(f"   1. Account still under review (even if marked ACTIVE)")
            print(f"   2. API quota not enabled yet")
            print(f"   3. Need to wait 24-48 hours after credential creation")
            print(f"   4. Marketplace mismatch (trying .in but approved for .com?)")
            
        if 'ASSOCIATE_NOT_ELIGIBLE' in str(error_data):
            print(f"\n   DIAGNOSIS: Associate Not Eligible")
            print(f"   Need 3 qualifying sales within 180 days")
            
    except:
        print(f"   Could not parse error body")

except Exception as e:
    print(f"   [ERROR] Unexpected: {e}")

# Try different marketplace
print(f"\n5. TRYING DIFFERENT MARKETPLACES...")
marketplaces = [
    "www.amazon.in",
    "www.amazon.com",
    "amazon.in",
    "amazon.com"
]

for mp in marketplaces:
    print(f"\n   Testing marketplace: {mp}")
    request = GetItemsRequestContent(
        partner_tag=partner_tag,
        item_ids=[test_asin],
        resources=['itemInfo.title']
    )
    try:
        response = api.get_items(
            x_marketplace=mp,
            get_items_request_content=request
        )
        print(f"   [SUCCESS] This marketplace works: {mp}")
        break
    except ApiException as e:
        print(f"   [FAILED] {e.status}: {e.reason}")
    except Exception as e:
        print(f"   [ERROR] {e}")

print("\n" + "=" * 70)
print("DEBUGGING COMPLETE")
print("=" * 70)

# Recommendations
print("\nRECOMMENDATIONS:")
print("1. Check your Amazon Associates dashboard for any pending actions")
print("2. Verify your account has completed the 3 sales requirement")
print("3. Wait 24-48 hours after credential creation")
print("4. Try regenerating your credentials (Add new credential button)")
print("5. Contact Amazon Associates support if issue persists")
