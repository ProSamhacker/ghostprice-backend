# Apify Setup Guide for GhostPrice

## What is Apify?

Apify is a web scraping and automation platform. We use their **Amazon Price History API** to get historical price data.

---

## Actor We're Using

**Amazon Price History API**
- **Creator:** radeance
- **Actor ID:** `radeance/amazon-price-history-api`
- **URL:** https://console.apify.com/actors/radeance~amazon-price-history-api

### What It Provides:
✅ Current price  
✅ Buy Box price history  
✅ Prime exclusive pricing  
✅ List price (MSRP)  
✅ Ratings & reviews  
✅ Seller information  
✅ Variant ASINs  
✅ Product images  

---

## Pricing Model

**Pay Per Event** (No monthly subscription!)

- Only pay when you use it
- Typical cost: **$0.01-0.05 per product**
- No monthly fees
- No request limits
- Scale as you need

### Example Costs:

```
10 products = ~$0.50
100 products = ~$5.00
1,000 products = ~$50.00
```

**Much cheaper than Keepa ($20/month) for low volume!**

---

## Setup Steps

### 1. Create Apify Account

1. Go to: https://console.apify.com/sign-up
2. Sign up (free account available)
3. No credit card needed initially

### 2. Get API Token

1. Log in to Apify Console
2. Go to: Settings → Integrations
3. Copy your **Personal API token**
4. It looks like: `apify_api_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789`

### 3. Add to GhostPrice `.env`

```bash
# In ext/backend/.env
APIFY_API_TOKEN=apify_api_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789
```

---

## How It Works

### Smart Fallback Chain:

```
1. Try Apify (pay-per-use)
   ↓ (if fails or no credit)
2. Try Free Scraper (bootstrap)
   ↓ (if succeeds)
3. Save to database → Crowdsourcing
```

### First Product Lookup:

```python
User visits Raspberry Pi 5
  ↓
Check local DB → EMPTY
  ↓
Call Apify API → $0.03
  ↓
Get full price history!
  ↓
Save to database
  ↓
User sees complete price intelligence
```

### Second User (Same Product):

```python
User visits same Raspberry Pi 5
  ↓
Check local DB → HAS DATA
  ↓
NO API call! → $0.00
  ↓
Use crowdsourced data
```

---

## Cost Comparison

### Scenario: 100 New Products/Month

**Option 1: Keepa**
- Cost: $20/month (fixed)
- Data quality: Excellent

**Option 2: Apify (Our Choice)**
- Cost: ~$5/month (variable)
- Data quality: Excellent
- **75% cheaper!**

**Option 3: Free Scraper Only**
- Cost: $0/month
- Data quality: Generated (30 days)

---

## Testing Apify

### Test the Integration:

```bash
cd ext/backend
python -c "from apify_client import get_apify_price_history; print(get_apify_price_history('B0CK2FCG1K', 'IN'))"
```

**Expected output:**
```json
{
  "asin": "B0CK2FCG1K",
  "title": "Raspberry Pi 5 8GB RAM",
  "current_price": 12249.0,
  "price_history": [...],
  "source": "Apify"
}
```

---

## When to Use Apify vs Free Scraper

### Use Apify When:
✅ Launching (first 100-1000 products)  
✅ Need accurate historical data  
✅ Low monthly volume (<500 products)  
✅ Have small budget (~$10-20/month)  

### Use Free Scraper When:
✅ No budget  
✅ High volume (>1000 products/month)  
✅ Don't mind generated initial data  
✅ Crowdsourcing will provide real data soon  

---

## Best Strategy

### Phase 1: Launch (Month 1-3)
Use Apify for popular products:
- Top 50 most-searched products → Apify
- Other products → Free scraper
- Cost: ~$2-5/month

### Phase 2: Growth (Month 4-6)
Crowdsourcing kicks in:
- Popular products → Local DB (crowdsourced)
- New products → Apify
- Cost: ~$1-3/month

### Phase 3: Mature (Month 7+)
Mostly crowdsourced:
- 90% local data
- 10% Apify (rare products)
- Cost: ~$0.50-1/month

---

## Summary

✅ **Apify is perfect for GhostPrice:**
- Pay-per-use (no monthly fee)
- Professional data quality
- Automatic fallback to free scraper
- Scales with your growth

✅ **Setup is simple:**
1. Create free Apify account
2. Add API token to `.env`
3. Done! System handles the rest

**Total setup time: 5 minutes** ⏱️
