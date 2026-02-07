# Keepa API Integration Guide

## What is Keepa?

Keepa is a professional Amazon price tracking service that has been collecting price data since 2011. It provides:
- **Historical price data** for millions of Amazon products
- **90+ days of price history** (or more with premium plans)
- **Multiple Amazon marketplaces** (US, UK, Germany, France, India, etc.)
- **Sales rank tracking**
- **Price drop alerts**

## Why Use Keepa for GhostPrice?

### Problem with Crowdsourced Data
As a new extension with no users, building price history from scratch would take weeks:
```
Day 1:  1 user visit → 1 data point
Day 7:  5 user visits → 5 data points (not enough!)
Day 30: 20 user visits → 20 data points (barely useful)
```

### Solution: Keepa API
With Keepa, you get **instant access** to years of historical data:
```
API call → Returns 90 days of price history instantly!
          → Thousands of data points
          → Professional-grade accuracy
```

---

## Getting Started with Keepa

### Step 1: Create Keepa Account

1. Go to: https://keepa.com
2. Create a free account
3. Navigate to: https://keepa.com/#!api

### Step 2: Subscribe to API Access

Keepa API requires a paid subscription:

| Plan | Requests/Month | Price | Best For |
|------|---------------|-------|----------|
| Basic | 100,000 | ~$20/month | Small extensions |
| Pro | 500,000 | ~$80/month | Growing apps |
| Enterprise | Unlimited | Custom | Large scale |

**For testing:** Start with the Basic plan (100k requests = ~3,300 requests/day)

### Step 3: Get Your API Key

1. After subscribing, go to: https://keepa.com/#!api
2. Your API key will be displayed (64 characters long)
3. Copy the key

### Step 4: Add to GhostPrice

1. Open `ext/backend/.env` file
2. Add your Keepa API key:
```bash
KEEPA_API_KEY=your_64_character_api_key_here
```

---

## How GhostPrice Uses Keepa

### Hybrid Approach: Keepa + Local DB

```python
def get_price_stats(asin):
    # 1. Try Keepa first (instant historical data)
    try:
        keepa_stats = keepa_api.get_30day_stats(asin)
        if keepa_stats:
            return keepa_stats  # ✅ Years of data instantly!
    except:
        pass
    
    # 2. Fallback to local database (crowdsourced data)
    local_stats = query_local_db(asin)
    return local_stats  # Only if Keepa fails
```

### Benefits of This Approach

1. **Instant Intelligence** - Even for products no one has visited yet
2. **Cost-Effective** - Only call Keepa when needed
3. **Resilient** - Falls back to local data if Keepa is unavailable
4. **Future-Proof** - As you gain users, rely less on Keepa

---

## Keepa API Response Format

### Example Request
```python
from keepa_client import KeepaClient

client = KeepaClient()
history = client.get_price_history(
    asin="B0CK2FCG1K",  # Raspberry Pi 5
    domain=8,           # 8 = Amazon.in
    days=30             # Last 30 days
)
```

### Example Response
```python
{
    "asin": "B0CK2FCG1K",
    "title": "Raspberry Pi 5 8GB RAM",
    "current_price": 12249.0,
    "price_history": [
        {"timestamp": "2026-01-08T10:00:00", "price": 12450.0},
        {"timestamp": "2026-01-10T14:30:00", "price": 12399.0},
        {"timestamp": "2026-02-01T09:00:00", "price": 13499.0},  # Price spike!
        {"timestamp": "2026-02-06T20:00:00", "price": 12249.0}
    ],
    "stats": {
        "min_price": 12249.0,
        "max_price": 13499.0,
        "avg_price": 12649.25,
        "data_points": 4561  # Thousands of data points!
    },
    "source": "Keepa API"
}
```

---

## API Usage & Costs

### Token Consumption

Each API call to Keepa uses **1 token** per product.

Example usage for GhostPrice:
```
100 users/day × 5 products each = 500 requests/day
500 requests/day × 30 days = 15,000 requests/month

Cost: Basic plan ($20/month) ✅ Plenty of headroom!
```

### Optimization Strategies

1. **Cache Keepa Data**
   ```python
   # Cache stats for 24 hours
   if cached_data and age < 24_hours:
       return cached_data
   else:
       fresh_data = keepa_api.get_stats(asin)
       cache(fresh_data, ttl=24_hours)
   ```

2. **Smart Fallback**
   ```python
   # Only call Keepa if local DB has no data
   if local_db_has_data(asin):
       return local_stats
   else:
       return keepa_stats
   ```

3. **Batch Requests**
   Keepa supports fetching multiple products in one request

---

## Domain Codes

Keepa supports multiple Amazon marketplaces:

```python
KEEPA_DOMAINS = {
    "US": 1,   # Amazon.com
    "GB": 2,   # Amazon.co.uk
    "DE": 3,   # Amazon.de
    "FR": 4,   # Amazon.fr
    "JP": 5,   # Amazon.co.jp
    "CA": 6,   # Amazon.ca
    "IT": 7,   # Amazon.it
    "IN": 8,   # Amazon.in (India)
    "ES": 9,   # Amazon.es
}
```

For GhostPrice focused on India:
```python
keepa.get_price_history(asin, domain=8)  # Always use domain=8
```

---

## Testing Keepa Integration

### 1. Test API Connection
```bash
cd ext/backend
python -c "from keepa_client import KeepaClient; client = KeepaClient(); print('✅ Keepa connected!')"
```

### 2. Test Price History Fetch
```bash
python -c "from keepa_client import get_keepa_stats; stats = get_keepa_stats('B0CK2FCG1K', 'IN'); print(stats)"
```

### 3. Test Keepa + Local DB Integration
```bash
curl "http://localhost:8000/price-intelligence?asin=B0CK2FCG1K&current_price=12249"
```

Expected response:
```json
{
    "status": "success",
    "price_stats": {
        "source": "Keepa API",  // ← Using Keepa!
        "data_points": 4561,    // ← Thousands of points
        "lowest_30d": 12249,
        "highest_30d": 13499,
        "average_30d": 12649.25
    },
    "fake_discount": {
        "is_fake": true,
        "message": "⚠️ Price was inflated..."
    }
}
```

---

## Fallback Strategy

```
┌─────────────────┐
│ User visits     │
│ product page    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Try Keepa API   │
└────┬───────┬────┘
     │       │
     │       └──(fails)──┐
     │                   │
  (success)              ▼
     │          ┌─────────────────┐
     │          │ Try Local DB    │
     │          └────┬───────┬────┘
     │               │       │
     │            (has      (no
     │             data)     data)
     │               │       │
     ▼               ▼       ▼
┌─────────┐   ┌──────────┐ ┌──────────────┐
│ Show    │   │ Show     │ │ "Tracking   │
│ Keepa   │   │ Local    │ │  started"   │
│ stats   │   │ stats    │ │  message    │
└─────────┘   └──────────┘ └──────────────┘
```

---

## Cost-Benefit Analysis

### Without Keepa (Pure Crowdsourcing)
- ❌ No data for first 2-4 weeks
- ❌ Users see "tracking started" message (poor UX)
- ❌ Can't detect fake discounts without history
- ✅ Free

### With Keepa
- ✅ Instant price intelligence (day 1!)
- ✅ Professional-grade accuracy
- ✅ Works even for rarely-visited products
- ✅ Can detect fake discounts immediately
- ⚠️ $20/month cost

**Recommendation:** Start with Keepa, transition to hybrid as user base grows.

---

## Future Optimization

As GhostPrice gains users, you can reduce reliance on Keepa:

### Phase 1: Pure Keepa (Months 1-3)
```python
# Always use Keepa
stats = keepa_api.get_stats(asin)
```

### Phase 2: Hybrid (Months 4-6)
```python
# Use local data if available, Keepa as backup
if local_db.has_recent_data(asin):
    stats = local_db.get_stats(asin)
else:
    stats = keepa_api.get_stats(asin)
```

### Phase 3: Keepa for New Products Only (Months 7+)
```python
# Only use Keepa for products without local history
if local_db.visits(asin) > 10:
    stats = local_db.get_stats(asin)  # Crowdsourced wins!
else:
    stats = keepa_api.get_stats(asin)  # Bootstrap with Keepa
```

---

## Summary

✅ **Keepa API** provides instant historical price data  
✅ **$20/month** for 100k requests (affordable for startups)  
✅ **Hybrid approach** uses Keepa + local DB for best results  
✅ **Future-proof** - rely less on Keepa as user base grows  

**Setup time:** 5 minutes  
**Value:** Instant price intelligence from day 1! 🚀
