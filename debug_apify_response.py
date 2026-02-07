"""
Test Apify actor and inspect the actual response format
"""

import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("APIFY_API_TOKEN")
actor_id = "gvFpWjQm90ZfTDdEf"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Correct input format
actor_input = {
    "identifiers": ["B0DSPYPKRG"],
    "country": "in"
}

print("🚀 Starting Apify actor...")
response = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/runs",
    json=actor_input,
    headers=headers,
    timeout=30
)

print(f"Status: {response.status_code}")
run_data = response.json()
print(json.dumps(run_data, indent=2))

run_id = run_data.get("data", {}).get("id")
print(f"\n✅ Run ID: {run_id}")
print("\n⏳ Waiting for completion...")

# Wait for completion
time.sleep(10)

status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
status_response = requests.get(status_url, headers=headers)
status_data = status_response.json()

print(f"\nStatus: {status_data.get('data', {}).get('status')}")
dataset_id = status_data.get("data", {}).get("defaultDatasetId")
print(f"Dataset ID: {dataset_id}")

if dataset_id:
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    print(f"\n📊 Fetching from: {dataset_url}")
    
    dataset_response = requests.get(dataset_url, headers=headers)
    print(f"Dataset status: {dataset_response.status_code}")
    
    results = dataset_response.json()
    print(f"\nDataset response type: {type(results)}")
    print(f"Dataset length: {len(results) if isinstance(results, list) else 'not a list'}")
    print(f"\nFull dataset response:")
    print(json.dumps(results, indent=2)[:2000])  # First 2000 chars
