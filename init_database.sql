-- GhostPrice Database Schema
-- Clean, dynamic schema with NO hardcoded sample data

-- Table 1: AI-Analyzed Products Cache
-- Stores AI analysis results to avoid re-analyzing same products
CREATE TABLE IF NOT EXISTS analyzed_products (
    asin VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    base_price DECIMAL(8,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    marketplace VARCHAR(2) NOT NULL,
    
    -- Consumable data (from AI)
    consumable_name VARCHAR(255),
    consumable_price DECIMAL(8,2),
    replacement_months INTEGER,
    annual_maintenance DECIMAL(8,2),
    
    -- BIFL alternative (from AI)
    bifl_name VARCHAR(255),
    bifl_price DECIMAL(8,2),
    bifl_reasoning TEXT,
    
    -- Metadata
    ai_confidence FLOAT DEFAULT 0.5,
    analysis_method VARCHAR(20) DEFAULT 'groq_ai',
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (datetime('now', '+7 days'))
);

-- Table 2: Price History (Hybrid: Keepa import + user visits)
-- Stores historical prices for intelligence and fake discount detection
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asin TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT DEFAULT 'extension',  -- Values: 'extension', 'keepa_import', 'rapidapi'
    CONSTRAINT price_positive CHECK (price > 0)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_price_asin_time ON price_history(asin, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_price_currency ON price_history(asin, currency);
CREATE INDEX IF NOT EXISTS idx_price_source ON price_history(source);
CREATE INDEX IF NOT EXISTS idx_analyzed_expires ON analyzed_products(expires_at);
CREATE INDEX IF NOT EXISTS idx_analyzed_currency ON analyzed_products(currency);

-- No sample data is loaded!
-- All data comes from:
-- 1. Keepa API (imported into price_history)
-- 2. User visits (tracked in price_history)
-- 3. AI analysis (cached in analyzed_products)
