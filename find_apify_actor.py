"""
Quick test to find the correct Apify actor ID
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("APIFY_API_TOKEN")

if not token:
    print("❌ No APIFY_API_TOKEN found in .env")
    exit(1)

print(f"✅ Token found: {token[:20]}...")

# List all available actors to find the right one
headers = {
    "Authorization": f"Bearer {token}"
}

# Try to list your actors
print("\n🔍 Fetching your Apify actors...")
response = requests.get(
    "https://api.apify.com/v2/acts",
    headers=headers,
    params={"my": True}
)

if response.status_code == 200:
    actors = response.json()
    print(f"\n✅ Found {len(actors.get('data', {}).get('items', []))} actors")
    for actor in actors.get('data', {}).get('items', []):
        print(f"  - {actor.get('name')} (ID: {actor.get('id')})")
else:
    print(f"❌ Failed to fetch actors: {response.status_code}")
    print(f"Response: {response.text}")

# Also try the public store
print("\n🔍 Searching for Amazon price history actors in store...")
search_response = requests.get(
    "https://api.apify.com/v2/store",
    params={"search": "amazon price history"}
)

if search_response.status_code == 200:
    results = search_response.json()
    print(f"\n✅ Found {len(results.get('data', {}).get('items', []))} matching actors")
    for actor in results.get('data', {}).get('items', [])[:5]:
        print(f"  - {actor.get('title')} by {actor.get('username')}")
        print(f"    ID: {actor.get('id')}")
        print(f"    Name: {actor.get('name')}")
        print()
