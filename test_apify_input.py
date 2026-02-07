"""
Test Apify actor with different input formats to find the correct one
"""

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("APIFY_API_TOKEN")
actor_id = "gvFpWjQm90ZfTDdEf"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test different input formats
test_inputs = [
    {
        "name": "URL only",
        "input": {
            "url": "https://www.amazon.in/dp/B0DSPYPKRG"
        }
    },
    {
        "name": "URLs array",
        "input": {
            "urls": ["https://www.amazon.in/dp/B0DSPYPKRG"]
        }
    },
    {
        "name": "ASIN only",
        "input": {
            "asin": "B0DSPYPKRG"
        }
    },
    {
        "name": "ASINs array",
        "input": {
            "asins": ["B0DSPYPKRG"]
        }
    },
    {
        "name": "amazonProductUrLsorASINs (current)",
        "input": {
            "amazonProductUrLsorASINs": ["https://www.amazon.in/dp/B0DSPYPKRG"],
            "amazonMarketplaceCountry": "IN"
        }
    }
]

print("🧪 Testing different input formats...\n")

for test in test_inputs:
    print(f"Testing: {test['name']}")
    print(f"Input: {json.dumps(test['input'], indent=2)}")
    
    response = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        json=test['input'],
        headers=headers,
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ SUCCESS! This format works!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        break
    else:
        print(f"❌ Failed")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Error: {response.text}")
    
    print("-" * 60)
    print()
