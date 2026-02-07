"""
ALL-IN-ONE: Product Discovery + Price Scraping
Discovers new products AND scrapes prices in one go

Use this if you prefer simplicity over modularity
Warning: Takes longer (~45-60 min for 500 products)
"""

import subprocess
import sys
from datetime import datetime

def run_script(script_name):
    """Run a Python script and show output"""
    print(f"\n{'='*70}")
    print(f"🚀 Running: {script_name}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully\n")
            return True
        else:
            print(f"\n❌ {script_name} failed with code {result.returncode}\n")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}\n")
        return False

def main():
    print("🤖 GHOSTPRICE ALL-IN-ONE AUTOMATION")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Step 1: Discover new products
    print("\n📂 STEP 1: Product Discovery")
    print("Finding best sellers from Amazon...")
    discovery_success = run_script("discover_products.py")
    
    if not discovery_success:
        print("⚠️  Discovery failed, but continuing with price scraping...")
    
    # Small delay between steps
    print("\n⏳ Waiting 30 seconds before price scraping...")
    import time
    time.sleep(30)
    
    # Step 2: Scrape prices
    print("\n💰 STEP 2: Price Scraping")
    print("Updating prices for all tracked products...")
    scraper_success = run_script("daily_price_scraper.py")
    
    # Step 3: Show results
    print("\n📊 STEP 3: Database Statistics")
    run_script("view_database.py")
    
    # Summary
    print("\n" + "="*70)
    print("🎉 ALL-IN-ONE AUTOMATION COMPLETE!")
    print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if discovery_success and scraper_success:
        print("✅ All tasks completed successfully!")
    else:
        print("⚠️  Some tasks had issues, check logs above")
    
    print("="*70)

if __name__ == "__main__":
    main()
