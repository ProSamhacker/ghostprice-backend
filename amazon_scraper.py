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
        
        # Try different price selectors (Amazon changes them frequently)
        price_selectors = [
            # Deal price
            {'name': 'span', 'attrs': {'class': 'a-price-whole'}},
            # Regular price
            {'name': 'span', 'attrs': {'id': 'priceblock_ourprice'}},
            {'name': 'span', 'attrs': {'id': 'priceblock_dealprice'}},
            # Sale price
            {'name': 'span', 'attrs': {'id': 'priceblock_saleprice'}},
            # New style
            {'name': 'span', 'attrs': {'class': 'a-offscreen'}},
        ]
        
        for selector in price_selectors:
            try:
                element = soup.find(selector['name'], selector['attrs'])
                if element:
                    # Clean price text
                    price_text = element.get_text().strip()
                    # Remove currency symbols and commas
                    price_text = price_text.replace('₹', '').replace(',', '').replace('$', '')
                    
                    # Convert to float
                    price = float(price_text.split()[0])  # Get first number
                    
                    if price > 0:
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
