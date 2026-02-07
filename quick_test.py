"""
Simple Amazon API test
"""
from amazon_client import amazon_client

print("\nTesting Amazon Creators API...")
print("-" * 50)

# Test with a sample ASIN
result = amazon_client.get_product_details(['B0DLFMFBJW'])

if result:
    print("\n[SUCCESS] API is working!")
    print(f"Results: {result}")
else:
    print("\n[FAILED] API returned no results")
    print("\nThis is likely due to ASSOCIATE_NOT_ELIGIBLE error.")
    print("\nYour Amazon Associates account needs:")
    print("  1. 3 qualifying sales within 180 days, OR")
    print("  2. Approved Amazon Influencer status")
    print("\nCheck your Associates dashboard for account status.")
