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

results = {
    "credentials_match": False,
    "api_client_init": False,
    "test_results": [],
    "error_details": None,
    "recommendations": []
}

# Check credentials
credential_id = os.getenv("AMAZON_CREDENTIAL_ID")
partner_tag = os.getenv("AMAZON_TAG")
marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.in")

results["credentials_match"] = (
    credential_id == "vdp2k685pg16tpscgedh44dp1" and 
    partner_tag == "nocreditai-21"
)

# Initialize API
try:
    api_client = ApiClient(
        credential_id=credential_id,
        credential_secret=os.getenv("AMAZON_CREDENTIAL_SECRET"),
        version="2.2"
    )
    api = DefaultApi(api_client)
    results["api_client_init"] = True
except Exception as e:
    results["api_client_init"] = False
    results["error_details"] = str(e)

# Test API call
if results["api_client_init"]:
    test_asin = 'B0DLFMFBJW'
    request = GetItemsRequestContent(
        partner_tag=partner_tag,
        item_ids=[test_asin],
        resources=['itemInfo.title']
    )
    
    try:
        response = api.get_items(
            x_marketplace=marketplace,
            get_items_request_content=request
        )
        results["test_results"].append({
            "marketplace": marketplace,
            "status": "SUCCESS",
            "message": "API call successful!"
        })
        
    except ApiException as e:
        error_body = None
        try:
            error_body = json.loads(e.body)
        except:
            error_body = str(e.body)
            
        results["test_results"].append({
            "marketplace": marketplace,
            "status": "FAILED",
            "http_status": e.status,
            "reason": e.reason,
            "error_body": error_body
        })
        
        results["error_details"] = error_body
        
        # Diagnose
        if isinstance(error_body, dict):
            error_type = error_body.get('__type', '')
            error_msg = error_body.get('message', '')
            
            if 'AccessDenied' in error_type:
                results["recommendations"].append("Account may still be under review")
                results["recommendations"].append("Wait 24-48 hours after credential creation")
                results["recommendations"].append("Check for pending actions in dashboard")
                
            if 'ASSOCIATE_NOT_ELIGIBLE' in error_msg:
                results["recommendations"].append("Account needs 3 qualifying sales")
                results["recommendations"].append("Verify sales in Associates dashboard")

# Save results
with open('api_debug_result.json', 'w') as f:
    json.dump(results, f, indent=2)

# Print summary
print("\nSUMMARY:")
print(f"Credentials Match: {results['credentials_match']}")
print(f"API Client Init: {results['api_client_init']}")
if results['test_results']:
    print(f"API Call Status: {results['test_results'][0]['status']}")
    if results['test_results'][0]['status'] == 'FAILED':
        print(f"Error: {results['test_results'][0]['reason']}")

print("\nCheck api_debug_result.json for full details")
