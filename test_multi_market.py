"""
Test Multi-Market Support Strategy
Verifies that:
1. US products -> Use Apify
2. IN products -> Skip Apify (Crowdsourcing)
"""

import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from price_tracker import PriceTracker

tracker = PriceTracker()

print("\n" + "="*60)
print("🧪 TESTING US MARKETPLACE (Should use Apify)")
print("="*60)
us_asin = "B0BN72FYFG" # iPhone 14 (US)
print(f"Checking {us_asin} with country='US'...")
tracker.import_price_history_to_db(us_asin, country="US")

print("\n" + "="*60)
print("🧪 TESTING INDIA MARKETPLACE (Should SKIP Apify)")
print("="*60)
in_asin = "B0DSPYPKRG" # Raspberry Pi 5 (IN)
print(f"Checking {in_asin} with country='IN'...")
tracker.import_price_history_to_db(in_asin, country="IN")

print("\n" + "="*60)
print("✅ Test Complete")
print("="*60)
