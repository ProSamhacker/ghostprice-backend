"""
Test the smart fallback chain for price history
"""

from price_tracker import PriceTracker

# Initialize tracker
tracker = PriceTracker()

# Test with Raspberry Pi 5 16GB
asin = "B0DSPYPKRG"

print(f"\n{'='*60}")
print(f"Testing Smart Fallback Chain for ASIN: {asin}")
print(f"{'='*60}\n")

# This should trigger:
# 1. Try Apify (if token exists)
# 2. Fall back to scraper (if Apify fails)
# 3. Save to database

stats = tracker.get_price_stats(asin)

if stats:
    print(f"\n{'='*60}")
    print("✅ SUCCESS! Price Intelligence Generated:")
    print(f"{'='*60}")
    print(f"Current Price: ₹{stats['current']:.2f}")
    print(f"30-day Low:    ₹{stats['min_30d']:.2f}")
    print(f"30-day High:   ₹{stats['max_30d']:.2f}")
    print(f"30-day Avg:    ₹{stats['avg_30d']:.2f}")
    print(f"Is Lowest:     {'✅ YES! Great deal!' if stats['is_lowest'] else '❌ Not the lowest'}")
    print(f"Data Points:   {stats['data_points']}")
    print(f"Volatility:    {stats['volatility']:.1f}%")
    print(f"Data Source:   {stats['source']}")
    print(f"{'='*60}\n")
else:
    print("\n❌ Failed to get price stats")
    print("This might be normal if:")
    print("  - No Apify token in .env")
    print("  - Scraper blocked by Amazon")
    print("  - Product page structure changed")
    print("\nTry visiting the product with the extension instead!")
