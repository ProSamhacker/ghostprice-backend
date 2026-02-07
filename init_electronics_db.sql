-- Simplified Database Schema for Electronics Price Tracking
-- Focused on price tracking only, removed TCO/ecosystem analysis tables

-- Electronics products being tracked
CREATE TABLE IF NOT EXISTS tracked_products (
    asin TEXT PRIMARY KEY,
    product_title TEXT NOT NULL,
    category TEXT,  -- laptops, smartphones, monitors, etc.
    marketplace TEXT DEFAULT 'IN',  -- IN or US
    currency TEXT DEFAULT 'INR',
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price history (crowdsourced + scraped data)
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT DEFAULT 'INR',
    marketplace TEXT DEFAULT 'IN',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT DEFAULT 'extension',  -- extension, scraper, rapidapi
    FOREIGN KEY (asin) REFERENCES tracked_products(asin)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_price_asin ON price_history(asin);
CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_tracked_category ON tracked_products(category);
CREATE INDEX IF NOT EXISTS idx_tracked_marketplace ON tracked_products(marketplace);
