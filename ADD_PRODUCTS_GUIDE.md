# How to Add More Products

## 🎯 Three Easy Ways

### 1. **Add Single Product (Quick)**

```bash
# Auto-fetch title from Amazon
python add_product.py B0D1XD1ZV3

# Or provide title manually
python add_product.py B0D1XD1ZV3 "Dell Inspiron 15 Laptop"
```

### 2. **Add Multiple Products from File (Best for Bulk)**

Edit `my_products.txt` and add ASINs:
```
B0XXXXXX | Your Product Title
B0YYYYYY | Another Product
```

Then run:
```bash
python add_product.py --file my_products.txt
```

### 3. **Re-run Seed Script (Fresh Start)**

Edit `seed_electronics.py`, add to `POPULAR_ELECTRONICS` list:
```python
POPULAR_ELECTRONICS = [
    ("B0XXXXXX", "Your Product Title"),
    ...
]
```

Then run:
```bash
python seed_electronics.py
```

## 🔍 Finding Top Products

### Get ASINs from Amazon

**Manually:**
1. Visit Amazon India: https://www.amazon.in/
2. Search for category (e.g., "laptop")
3. Look for "Amazon's Choice" or "Best Seller" badges
4. Open product page
5. ASIN is in the URL: `/dp/B0XXXXXX/`

**Example URLs:**
- Laptops: https://www.amazon.in/gp/bestsellers/computers/1375424031
- Smartphones: https://www.amazon.in/gp/bestsellers/electronics/1389401031
- Headphones: https://www.amazon.in/gp/bestsellers/electronics/1388921031

### Quick Copy-Paste List (Top Sellers Feb 2026)

Add these to `my_products.txt`:

```
# LAPTOPS - Best Sellers
B0D6ZQVYXY | HP 15s 12th Gen Intel Core i5 Laptop
B0CSYVFJMR | Lenovo IdeaPad Slim 5 Intel Core i5
B0CX4RGW8T | ASUS Vivobook 16X Creator Laptop

# SMARTPHONES - Amazon's Choice  
B0CWNQRGKN | Samsung Galaxy M35 5G
B0D1YT5RSN | Redmi Note 13 Pro
B0D4DJ4KZN | Realme Narzo 70 Pro 5G

# HEADPHONES - Top Rated
B0D3JQMX2P | Sony WH-CH720N Wireless
B0CKFZQ2T6 | JBL Tune 760NC Wireless
B0CLHB4Q8P | Boat Airdopes 141 TWS

# GAMING - Popular
B0CS3K6YDW | Logitech G502 HERO Gaming Mouse
B0BW5QZCJX | Ant Esports MK3400 Pro Gaming Keyboard
B0CRKQHCFX | Zebronics Zeb-Nitro Gaming Headphone
```

## 📊 Strategy for Maximum Coverage

### Start with Top 100 Products

**Recommended Distribution:**
- 30 Laptops (most searched)
- 25 Smartphones (high volume)
- 15 Headphones/Audio
- 10 Monitors
- 10 Gaming accessories
- 10 Other (tablets, smartwatches, etc.)

### Why Focus on Top Sellers?

✅ **Higher traffic** → More extension users will see them  
✅ **Better data** → Daily scraper builds history faster  
✅ **More relevant** → Users searching for these products  
✅ **Price volatility** → Top sellers have frequent sales  

## 🚀 Recommended Workflow

```bash
# 1. Add your products to my_products.txt (edit file)

# 2. Import them
python add_product.py --file my_products.txt

# 3. Verify
python view_database.py stats

# 4. Run scraper to collect first prices
python daily_price_scraper.py

# 5. Check results
python view_database.py prices
```

## ⚡ Quick Test

Try adding one product right now:

```bash
# Amazon's Choice laptop (real ASIN from Feb 2026)
python add_product.py B0D6ZQVYXY
```

Then check:
```bash
python view_database.py products | tail -20
```

Done! Your database now has one more product to track! 🎉
