"""
Test script for RapidAPI Amazon Product Data Integration
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rapid_api_client import RapidAPIClient, get_product_data

load_dotenv()

print("=" * 70)
print("RAPIDAPI AMAZON PRODUCT DATA TEST")
print("=" * 70)

# Check API key
api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST", "real-time-amazon-data.p.rapidapi.com")

print(f"\n1. CONFIGURATION CHECK:")
if api_key and api_key != "YOUR_RAPIDAPI_KEY_HERE":
    print(f"   ✓ API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"   ✓ API Host: {api_host}")
else:
    print(f"   ✗ API Key not configured!")
    print(f"\n   Please update your .env file with your RapidAPI key:")
    print(f"   1. Go to https://rapidapi.com/hub")
    print(f"   2. Sign up or log in")
    print(f"   3. Subscribe to 'Real-Time Amazon Data' API (free tier)")
    print(f"   4. Copy your API key")
    print(f"   5. Update RAPIDAPI_KEY in .env file")
    print("\n" + "=" * 70)
    sys.exit(1)

print(f"\n2. TEST PRODUCT FETCH:")
test_asin = "B0DLFMFBJW"
print(f"   Testing with ASIN: {test_asin}")

try:
    client = RapidAPIClient()
    print("   ✓ RapidAPI client initialized")
    
    print(f"\n3. FETCHING PRODUCT DATA...")
    product = client.get_product_details(test_asin, country="IN")
    
    if product:
        print("\n" + "=" * 70)
        print("SUCCESS! Product Data Retrieved:")
        print("=" * 70)
        print(f"\nASIN: {product.get('asin')}")
        print(f"Title: {product.get('title')}")
        print(f"Price: {product.get('currency')} {product.get('price')}")
        print(f"Rating: {product.get('rating')} ({product.get('reviews_count')} reviews)")
        print(f"Availability: {product.get('availability')}")
        print(f"Image URL: {product.get('image_url')}")
        
        # Test affiliate link generation
        affiliate_link = client.build_affiliate_link(test_asin, "IN")
        print(f"\nAffiliate Link: {affiliate_link}")
        
        print("\n" + "=" * 70)
        print("✓ All tests passed!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("ERROR: No product data returned")
        print("=" * 70)
        print("\nPossible reasons:")
        print("1. Invalid ASIN")
        print("2. API rate limit exceeded")
        print("3. Product not available in selected marketplace")
        print("4. Network connectivity issues")
        
except Exception as e:
    print("\n" + "=" * 70)
    print("ERROR OCCURRED")
    print("=" * 70)
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Verify your RapidAPI key is correct")
    print("2. Check you're subscribed to the API")
    print("3. Ensure you haven't exceeded rate limits")
    print("4. Check your internet connection")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 70)
