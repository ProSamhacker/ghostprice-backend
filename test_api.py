from amazon_client import amazon_client

# Test with a common Indian product ASIN (e.g., a Printer or Mouse)
# Example: HP Deskjet 2331 (ASIN: B08D9N7Q79)
test_asins = ["B08D9N7Q79"] 

print("🚀 Testing Amazon API Connection...")
data = amazon_client.get_product_details(test_asins)

if data:
    print("\n✅ Success! Received Data:")
    for asin, info in data.items():
        print(f"Product: {info['title']}")
        print(f"Price: {info['currency']} {info['price']}")
        print(f"Affiliate Link: {info['link']}")
else:
    print("\n❌ Failed to fetch data. Check your .env credentials.")
