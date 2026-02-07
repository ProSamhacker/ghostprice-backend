"""
Simple Amazon API Test
"""

import sys
import os

# Ensure we're using the local environment
sys.path.insert(0, os.path.dirname(__file__))

# Import the amazon client
from amazon_client import amazon_client

print("=" * 70)
print("TESTING AMAZON CREATORS API")
print("=" * 70)

# Test with a sample ASIN
test_asins = ['B0DLFMFBJW']  # Sample ASIN from your data

print(f"\nTesting with ASIN(s): {test_asins}")
print("-" * 70)

try:
    result = amazon_client.get_product_details(test_asins)
    
    if result:
        print("\n" + "=" * 70)
        print("✅ SUCCESS - API CALL WORKED!")
        print("=" * 70)
        print(f"\nProduct Details Retrieved:")
        for asin, details in result.items():
            print(f"\nASIN: {asin}")
            print(f"  Title: {details['title']}")
            print(f"  Price: {details['currency']} {details['price']}")
            print(f"  Link: {details['link']}")
            print(f"  Image: {details['image'][:50]}..." if details['image'] else "  Image: Not available")
    else:
        print("\n" + "=" * 70)
        print("❌ FAILED - No results returned")
        print("=" * 70)
        print("\nThis could mean:")
        print("1. ASSOCIATE_NOT_ELIGIBLE error (account needs approval)")
        print("2. Invalid ASIN")
        print("3. Network/connectivity issue")
        
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR")
    print("=" * 70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
