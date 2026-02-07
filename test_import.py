import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'creatorsapi-python-sdk'))

print("Testing imports...")

try:
    from dotenv import load_dotenv
    print("✓ dotenv imported")
except Exception as e:
    print(f"✗ dotenv failed: {e}")

try:
    from creatorsapi_python_sdk.api_client import ApiClient
    print("✓ ApiClient imported")
except Exception as e:
    print(f"✗ ApiClient failed: {e}")

try:
    from creatorsapi_python_sdk.api.default_api import DefaultApi
    print("✓ DefaultApi imported")
except Exception as e:
    print(f"✗ DefaultApi failed: {e}")

try:
    from creatorsapi_python_sdk.models.get_items_request_content import GetItemsRequestContent
    print("✓ GetItemsRequestContent imported")
except Exception as e:
    print(f"✗ GetItemsRequestContent failed: {e}")

print("\nAll imports successful!")
print("\nNow testing API initialization...")

try:
    load_dotenv()
    credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
    credential_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
    
    print(f"Credential ID: {credential_id[:10]}..." if credential_id else "Missing!")
    print(f"Secret length: {len(credential_secret)} chars" if credential_secret else "Missing!")
    
    api_client = ApiClient(
        credential_id=credential_id,
        credential_secret=credential_secret,
        version="2.2"
    )
    print("✓ API Client created successfully")
    
    api = DefaultApi(api_client)
    print("✓ API initialized successfully")
    
    print("\n=== READY TO TEST API CALLS ===")
    
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
