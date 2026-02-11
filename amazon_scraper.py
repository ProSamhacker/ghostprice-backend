"""
Free Amazon Price Scraper
100% free alternative to Keepa/PriceHistory.app

Uses a simple scraping approach with built-in safety:
- Respects rate limits
- Rotates user agents
- Handles errors gracefully
- No paid APIs required!
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Dict, Optional
from datetime import datetime, timedelta
import json

class AmazonScraperClient:
    """Free Amazon price scraper for bootstrapping price history"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate between different user agents to avoid blocks
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def get_current_price(self, asin: str, country: str = "IN") -> Optional[Dict]:
        """
        Scrape current price from Amazon product page
        
        Args:
            asin: Amazon product ASIN
            country: Country code (IN, US, etc.)
            
        Returns:
            Dictionary with current price data
        """
        try:
            # Build Amazon URL based on country
            country_domains = {
                "IN": "amazon.in",
                "US": "amazon.com",
                "UK": "amazon.co.uk",
                "DE": "amazon.de",
                "CA": "amazon.ca"
            }
            
            domain = country_domains.get(country, "amazon.in")
            url = f"https://www.{domain}/dp/{asin}"
            
            # Random user agent to avoid detection
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '115',
                'Connection': 'keep-alive',
            }
            
            # Add delay to be polite (1-3 seconds)
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract price (try multiple selectors)
            price = self._extract_price(soup)
            title = self._extract_title(soup)
            
            if not price:
                print(f"⚠️ Could not extract price for {asin}")
                return None
            
            return {
                "asin": asin,
                "title": title or "Unknown Product",
                "current_price": price,
                "currency": "INR" if country == "IN" else "USD",
                "timestamp": datetime.now().isoformat(),
                "source": "scraper"
            }
            
        except Exception as e:
            print(f"❌ Scraping error for {asin}: {e}")
            return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Amazon page using multiple selectors"""
        
        # Check for Captcha
        if "captcha" in soup.text.lower() or soup.find('form', action=lambda x: x and 'captcha' in x):
            print(f"⚠️  Amazon Captcha detected")
            return None

        # Try different price selectors (Amazon changes them frequently)
        price_selectors = [
            # Standard modern price (e.g. "₹1,299")
            {'name': 'span', 'attrs': {'class': 'a-price-whole'}},
            # Price inside the apex price box
            {'name': 'span', 'attrs': {'class': 'a-offscreen'}},
            # Deal block
            {'name': 'div', 'attrs': {'id': 'corePriceDisplay_desktop_feature_div'}},
            {'name': 'div', 'attrs': {'id': 'corePrice_feature_div'}},
            # Legacy selectors
            {'name': 'span', 'attrs': {'id': 'priceblock_ourprice'}},
            {'name': 'span', 'attrs': {'id': 'priceblock_dealprice'}},
            {'name': 'span', 'attrs': {'id': 'priceblock_saleprice'}},
        ]
        
        for selector in price_selectors:
            try:
                elements = soup.find_all(selector['name'], selector['attrs'])
                for element in elements:
                    if not element: continue
                    
                    # Get text
                    price_text = element.get_text().strip()
                    
                    # Cleanup: remove "₹", ",", "$", "MRP:", "Deal of the Day"
                    # We look for the first valid number
                    import re
                    match = re.search(r'[\d,]+(\.\d+)?', price_text)
                    
                    if match:
                        clean_price = match.group(0).replace(',', '')
                        price = float(clean_price)
                        
                        # Sanity check: Price shouldn't be tiny or massive (unless it's a book/ebook)
                        if 10 < price < 1000000:
                            return price
            except:
                continue
        
        return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from Amazon page"""
        try:
            title_element = soup.find('span', {'id': 'productTitle'})
            if title_element:
                return title_element.get_text().strip()
        except:
            pass
        return None
    
    def generate_fake_history(self, current_price: float, days: int = 30) -> list:
        """
        Generate realistic fake price history for bootstrapping
        
        Since we can't scrape historical data, we generate realistic
        price variations based on the current price.
        
        This is OPTIONAL - only use if you want to seed the database
        with realistic-looking data for demo purposes.
        """
        history = []
        
        for day in range(days, 0, -1):
            # Generate realistic price variation (-10% to +15%)
            variation = random.uniform(-0.10, 0.15)
            price = current_price * (1 + variation)
            price = round(price / 10) * 10  # Round to nearest 10
            
            timestamp = datetime.now() - timedelta(days=day)
            
            history.append({
                "price": price,
                "timestamp": timestamp.isoformat()
            })
        
        # Add current price at the end
        history.append({
            "price": current_price,
            "timestamp": datetime.now().isoformat()
        })
        
        return history


# Country codes
SCRAPER_COUNTRIES = {
    "US": "US",
    "UK": "UK",
    "DE": "DE",
    "FR": "FR",
    "JP": "JP",
    "CA": "CA",
    "IN": "IN",
    "ES": "ES",
}


def get_scraper_price(asin: str, country: str = "IN") -> Optional[Dict]:
    """
    Convenience function to scrape current Amazon price
    
    Args:
        asin: Amazon product ASIN
        country: Country code (IN, US, etc.)
        
    Returns:
        Current price data
    """
    try:
        client = AmazonScraperClient()
        return client.get_current_price(asin, country)
    except Exception as e:
        print(f"Scraper error: {e}")
        return None
