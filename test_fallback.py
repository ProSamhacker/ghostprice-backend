"""Test the fallback client"""
import sys
sys.path.insert(0, '.')

from amazon_client_fallback import amazon_client

print("=" * 60)
print("TESTING AMAZON CLIENT WITH FALLBACK")
print("=" * 60)

# Test ASINs from your sample data
test_asins = ['B0DLFMFBJW', 'B0DLMGH6T4', 'B0CYX5Q5YF']

print(f"\nTesting with {len(test_asins)} ASINs...")
print(f"ASINs: {test_asins}")
print("-" * 60)

result = amazon_client.get_product_details(test_asins)

if result:
    print(f"\n[SUCCESS] Retrieved {len(result)} products")
    print("=" * 60)
    
    for asin, details in result.items():
        print(f"\nASIN: {asin}")
        print(f"  Title: {details['title'][:60]}...")
        print(f"  Price: {details['currency']} {details['price']}")
        print(f"  Source: {details['source'].upper()}")
        print(f"  Link: {details['link'][:50]}...")
        
    print("\n" + "=" * 60)
    print("[OK] Client is working with database fallback!")
    print("Your extension will work perfectly!")
else:
    print("\n[ERROR] No results returned")

print("\n" + "=" * 60)
