# RapidAPI Setup Guide for LifeCycle Backend

## Quick Setup Steps

### 1. Get Your RapidAPI Key

1. **Sign up for RapidAPI**
   - Go to https://rapidapi.com/hub
   - Click "Sign Up" (or log in if you already have an account)
   - You can sign up with Google, GitHub, or email

2. **Subscribe to Real-Time Amazon Data API**
   - Visit: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data
   - Click "Subscribe to Test" button
   - Select the **"Basic" plan (FREE)**
     - 500 requests/month
     - No credit card required
   - Click "Subscribe"

3. **Get Your API Key**
   - After subscribing, you'll see the API key on the API page
   - Look for `X-RapidAPI-Key` in the code snippets section
   - Copy this key

### 2. Configure Your Backend

1. **Update `.env` file**
   ```bash
   cd "c:\Users\SAMIR\Desktop\WEBSITE\GHOST PRICE\ext\backend"
   ```

2. **Edit `.env` and replace the placeholder:**
   ```env
   RAPIDAPI_KEY=YOUR_ACTUAL_API_KEY_HERE
   ```

### 3. Install Dependencies

The only new dependency is `requests` which is likely already installed:

```bash
pip install requests python-dotenv
```

### 4. Test the Integration

Run the test script:

```bash
python test_api_detailed.py
```

Expected output:
```
======================================================================
RAPIDAPI AMAZON PRODUCT DATA TEST
======================================================================

1. CONFIGURATION CHECK:
   ✓ API Key: abcd1234...xyz89
   ✓ API Host: real-time-amazon-data.p.rapidapi.com

2. TEST PRODUCT FETCH:
   Testing with ASIN: B0DLFMFBJW
   ✓ RapidAPI client initialized

3. FETCHING PRODUCT DATA...

======================================================================
SUCCESS! Product Data Retrieved:
======================================================================

ASIN: B0DLFMFBJW
Title: [Product Name]
Price: INR 999.0
Rating: 4.5 (1234 reviews)
Affiliate Link: https://www.amazon.in/dp/B0DLFMFBJW?tag=nocreditai-21

======================================================================
✓ All tests passed!
======================================================================
```

### 5. Test the API Endpoint

Start the server:

```bash
python -m uvicorn main:app --reload --port 8000
```

Test with curl or browser:

```bash
# Using curl
curl "http://localhost:8000/fetch-live-price?asin=B0DLFMFBJW"

# Or open in browser:
http://localhost:8000/fetch-live-price?asin=B0DLFMFBJW
```

## API Endpoints

### New Endpoint: `/fetch-live-price`

Fetches real-time product data from Amazon via RapidAPI.

**Request:**
```
GET /fetch-live-price?asin=B0DLFMFBJW
```

**Response:**
```json
{
  "success": true,
  "data": {
    "asin": "B0DLFMFBJW",
    "title": "Product Name",
    "price": 999.0,
    "currency": "INR",
    "image_url": "https://...",
    "rating": 4.5,
    "reviews_count": 1234,
    "availability": "In Stock",
    "affiliate_link": "https://www.amazon.in/dp/B0DLFMFBJW?tag=nocreditai-21"
  }
}
```

### Existing Endpoint: `/check-product`

Still works with database fallback - uses cached/pre-analyzed product data.

## Rate Limits

**Free Tier:**
- 500 requests per month
- ~16 requests per day
- Perfect for development and testing

**Upgrade Options:**
- Basic: 10,000 requests/month ($9.99)
- Pro: 50,000 requests/month ($49.99)
- Ultra: 250,000 requests/month ($199.99)

## Troubleshooting

### "RAPIDAPI_KEY environment variable is required"
- Make sure you updated the `.env` file
- Restart your terminal/IDE after changing `.env`
- Check that the key doesn't have quotes around it

### "403 Forbidden" or Authentication Error
- Verify you're subscribed to the API
- Check your API key is correct
- Ensure you haven't exceeded rate limits

### "Product not found"
- Try a different ASIN
- Make sure the product exists on Amazon India
- Check the marketplace setting (IN vs US)

### Rate Limit Exceeded
- Check your usage at: https://rapidapi.com/developer/dashboard
- Wait for the monthly reset
- Upgrade to a paid plan

## Next Steps

1. ✅ Get RapidAPI key
2. ✅ Update `.env` file
3. ✅ Test with `python test_api_detailed.py`
4. ✅ Start server and test endpoint
5. 🔄 Integrate with your Chrome extension

## Support

- RapidAPI Docs: https://docs.rapidapi.com/
- API Documentation: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data
- RapidAPI Support: https://support.rapidapi.com/
