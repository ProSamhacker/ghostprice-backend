# Multi-Market Support Strategy

GhostPrice now supports **both US and India marketplaces** with intelligent routing:

## 🌎 How It Works

### US Products (amazon.com)
```
User visits amazon.com product
    ↓
✅ Try Apify API (proven working!)
    ↓
Get REAL 90-day price history ($0.03/product)
    ↓
Save to database
    ↓
Show user accurate price intelligence
```

### India Products (amazon.in)
```
User visits amazon.in product
    ↓
⚠️ Skip Apify (India not supported well)
    ↓
Use crowdsourcing only
    ↓
Build REAL price history over time (FREE!)
```

## 💰 Cost Breakdown

| Market | Data Source | Cost | Quality |
|--------|-------------|------|---------|
| **US** | Apify API | ~$0.03/product | ⭐⭐⭐⭐⭐ Real 90-day history |
| **India** | Crowdsourcing | $0 | ⭐⭐⭐⭐ Builds over time |

## 🎯 Benefits

**For US users:**
- Instant price intelligence
- 90 days of historical data
- Professional quality data
- Worth the small cost (~$3 for 100 products)

**For India users:**
- 100% free forever
- Builds authentic community data
- No fake generated data
- Honest with users about data availability

## 📊 Expected Experience

### Day 1 (Launch)
- **US:** Full price stats immediately
- **India:** "Building price history, check back soon"

### Week 1
- **US:** Thousands of products with full data
- **India:** Starting to build crowdsourced history

### Month 1
- **US:** Comprehensive coverage
- **India:** Real 30-day price trends appearing

## 🔧 Technical Implementation

The backend automatically detects marketplace from:
1. Product URL domain (.com vs .in)
2. Currency (USD vs INR)
3. ASIN region

Then routes to appropriate data source without any manual configuration.

## 🚀 Future Expansion

Easy to add more markets:
- **UK (.co.uk)** → Try Apify (likely works)
- **Germany (.de)** → Try Apify (likely works)
- **Japan (.jp)** → Crowdsourcing (might not work)

The system gracefully falls back to crowdsourcing for any market where Apify fails.
