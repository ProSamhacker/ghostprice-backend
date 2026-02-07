# Automated Product Discovery & Price Collection System

## 🤖 Complete Automation Setup

### What Gets Automated

**1. Product Discovery (discover_products.py)**
- Scrapes Amazon Best Seller lists
- Finds top 20 products in each electronics category
- Auto-detects Amazon's Choice badges
- Adds ~200 new products daily
- **Runtime: ~10-15 minutes**

**2. Price Collection (daily_price_scraper.py)**
- Scrapes prices for ALL tracked products
- Updates price_history automatically
- **Runtime: ~2-5 minutes per 100 products**

### Quick Start

**Run Once Manually:**
```bash
# Discover products from best seller lists
python discover_products.py

# Then scrape prices
python daily_price_scraper.py
```

### Schedule Daily (Recommended)

**Windows Task Scheduler:**

Create TWO tasks:

**Task 1: Product Discovery**
- Name: "GhostPrice Discovery"
- Trigger: Daily at 1:00 AM
- Action: `python discover_products.py`
- Working Directory: `C:\Users\SAMIR\Desktop\WEBSITE\GHOST PRICE\ext\backend`

**Task 2: Price Scraping**
- Name: "GhostPrice Scraper"  
- Trigger: Daily at 2:00 AM (after discovery completes)
- Action: `python daily_price_scraper.py`
- Working Directory: `C:\Users\SAMIR\Desktop\WEBSITE\GHOST PRICE\ext\backend`

**Linux/Mac (Crontab):**
```bash
# Product discovery at 1 AM
0 1 * * * cd /path/to/backend && python discover_products.py >> discovery.log 2>&1

# Price scraping at 2 AM  
0 2 * * * cd /path/to/backend && python daily_price_scraper.py >> scraper.log 2>&1
```

## 📊 Growth Timeline

### Day 1
- Discovery: 200 products found
- Price scraping: 200 prices recorded
- **Database: 200 products, 200 price points**

### Week 1 (Day 7)
- Discovery adds 50 new products (most already exist)
- Price scraping: 250 products × 7 days = 1,750 price points
- **Database: 250 products, 1,750 price points**

### Month 1 (Day 30)
- Discovery: 300-400 products total
- Price scraping: 400 products × 30 days = 12,000 price points
- **Full 30-day price histories** for all products!

## ⚙️ Rate Limiting Strategy

**To Avoid Amazon Bans:**

### Discovery Bot
- ✅ 3-5 second delay between products
- ✅ 10-15 second "cooling" every 10 products
- ✅ Random user agents
- ✅ Realistic browser headers
- ✅ Max 200 products per run (~15 minutes)

### Price Scraper
- ✅ 3 second delay between products
- ✅ Runs at low-traffic hours (2 AM)
- ✅ Can safely scrape 300-500 products/day

**Safe Daily Limits:**
- **Discovery**: 200 products = ~600 requests (~15 min)
- **Price scraping**: 500 products = ~500 requests (~25 min)
- **Total**: ~1,100 requests/day (well under Amazon's limits)

## 🎯 Tuning Parameters

### Increase Product Count

Edit `discover_products.py`, line 264:
```python
# Conservative (current)
discover_products(max_per_category=20, max_total=200)

# Aggressive (more products, slower)
discover_products(max_per_category=50, max_total=500)
```

**Warning**: More products = longer runtime & higher ban risk

### Add More Categories

Edit `BEST_SELLER_CATEGORIES` in `discover_products.py`:
```python
BEST_SELLER_CATEGORIES = {
    'keyboards': 'https://www.amazon.in/gp/bestsellers/computers/1375346031',
    'mice': 'https://www.amazon.in/gp/bestsellers/computers/1375347031',
    # Add more...
}
```

## 📈 Expected Results

**After 1 Month of Automation:**
- 300-500 products tracked
- 12,000-15,000 price data points
- Full 30-day price histories
- Recommendations for ALL electronics

**Your extension becomes as good as Keepa, but 100% free!** 🎉

## 🔍 Monitor Progress

```bash
# Daily check
python view_database.py stats

# See recent discoveries
python view_database.py products | tail -50

# Check price collection
python view_database.py prices | head -20
```

## ⚠️ Safety Tips

1. **Start conservative** (200 products/day)
2. **Monitor for blocks** (check logs)
3. **Increase gradually** if no issues
4. **Use VPN/proxy** if you get blocked
5. **Respect robots.txt** (current setup does)

## 🚀 One-Command Full Automation

Create `run_daily.py`:
```python
import subprocess
import time

print("Running product discovery...")
subprocess.run(["python", "discover_products.py"])

print("\nWaiting 5 minutes before scraping...")
time.sleep(300)

print("\nRunning price scraper...")
subprocess.run(["python", "daily_price_scraper.py"])

print("\nDone! Check database:")
subprocess.run(["python", "view_database.py", "stats"])
```

Then schedule just this one script!

Your GhostPrice is now **100% automated!** 🤖
