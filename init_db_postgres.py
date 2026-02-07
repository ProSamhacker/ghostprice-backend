"""
PostgreSQL Database Initialization Script
Loads CSV data into PostgreSQL database (for production)
"""

import psycopg2
from psycopg2.extras import execute_values
import csv
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set in environment!")
    print("Please set DATABASE_URL in your .env file or environment variables")
    exit(1)

# Paths
SCRIPT_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(SCRIPT_DIR, "..", "data", "sample_products.csv")


def init_database():
    """Initialize PostgreSQL database with schema and sample data"""
    
    print("📊 Initializing PostgreSQL database...")
    
    # Create database connection
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Connected to PostgreSQL")
    
    # Create schema
    create_schema(cursor)
    
    # Load CSV data
    if os.path.exists(CSV_PATH):
        load_csv_data(conn, cursor)
    else:
        print("⚠️  CSV file not found")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ PostgreSQL database initialized successfully!")


def create_schema(cursor):
    """Create database tables"""
    
    print("📋 Creating tables...")
    
    # Drop existing tables (for clean install)
    cursor.execute("DROP TABLE IF EXISTS subscription_flags CASCADE")
    cursor.execute("DROP TABLE IF EXISTS bifl_alternatives CASCADE")
    cursor.execute("DROP TABLE IF EXISTS consumables CASCADE")
    cursor.execute("DROP TABLE IF EXISTS products CASCADE")
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            parent_asin VARCHAR(10) PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            base_price DECIMAL(8,2) NOT NULL,
            has_consumable BOOLEAN DEFAULT FALSE,
            has_subscription BOOLEAN DEFAULT FALSE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create consumables table
    cursor.execute("""
        CREATE TABLE consumables (
            consumable_id SERIAL PRIMARY KEY,
            parent_asin VARCHAR(10) NOT NULL,
            consumable_asin VARCHAR(10),
            consumable_name VARCHAR(255) NOT NULL,
            consumable_price DECIMAL(8,2) NOT NULL,
            replacement_frequency_months INTEGER NOT NULL,
            yield_quantity INTEGER,
            yield_unit VARCHAR(20),
            FOREIGN KEY (parent_asin) REFERENCES products(parent_asin)
        )
    """)
    
    # Create bifl_alternatives table
    cursor.execute("""
        CREATE TABLE bifl_alternatives (
            alternative_id SERIAL PRIMARY KEY,
            trap_asin VARCHAR(10) NOT NULL,
            bifl_asin VARCHAR(10) NOT NULL,
            bifl_name VARCHAR(255) NOT NULL,
            bifl_price DECIMAL(8,2) NOT NULL,
            annual_savings DECIMAL(8,2) NOT NULL,
            reasoning TEXT,
            FOREIGN KEY (trap_asin) REFERENCES products(parent_asin)
        )
    """)
    
    # Create subscription_flags table
    cursor.execute("""
        CREATE TABLE subscription_flags (
            parent_asin VARCHAR(10) PRIMARY KEY,
            subscription_type VARCHAR(50) NOT NULL,
            monthly_cost DECIMAL(6,2) NOT NULL,
            is_optional BOOLEAN DEFAULT TRUE,
            highlight_text VARCHAR(255),
            FOREIGN KEY (parent_asin) REFERENCES products(parent_asin)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_category ON products(category)")
    cursor.execute("CREATE INDEX idx_consumable_parent ON consumables(parent_asin)")
    cursor.execute("CREATE INDEX idx_bifl_trap ON bifl_alternatives(trap_asin)")
    
    print("✅ Tables created")


def load_csv_data(conn, cursor):
    """Load product data from CSV"""
    
    print("📄 Loading CSV data...")
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        products_count = 0
        consumables_count = 0
        bifl_count = 0
        
        for row in reader:
            # Insert product
            cursor.execute("""
                INSERT INTO products 
                (parent_asin, product_name, category, base_price, has_consumable, has_subscription)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (parent_asin) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    base_price = EXCLUDED.base_price
            """, (
                row['parent_asin'],
                row['product_name'],
                row['category'],
                float(row['base_price']),
                True if row['consumable_asin'] else False,
                True if row['consumable_asin'] == 'SUBSCRIPTION' else False
            ))
            products_count += 1
            
            # Insert consumable (if exists)
            if row['consumable_asin'] and row['consumable_asin'] != 'SUBSCRIPTION':
                cursor.execute("""
                    INSERT INTO consumables
                    (parent_asin, consumable_asin, consumable_name, consumable_price, 
                     replacement_frequency_months, yield_quantity, yield_unit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['parent_asin'],
                    row['consumable_asin'],
                    row['consumable_name'],
                    float(row['consumable_price']),
                    float(row['replacement_months']),
                    int(row['yield_qty']) if row['yield_qty'] else None,
                    row['yield_unit']
                ))
                consumables_count += 1
            
            # Handle subscription
            elif row['consumable_asin'] == 'SUBSCRIPTION':
                cursor.execute("""
                    INSERT INTO subscription_flags
                    (parent_asin, subscription_type, monthly_cost, is_optional, highlight_text)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (parent_asin) DO NOTHING
                """, (
                    row['parent_asin'],
                    row['consumable_name'],
                    float(row['consumable_price']),
                    False,
                    f"Requires {row['consumable_name']}"
                ))
            
            # Insert BIFL alternative
            if row['bifl_asin']:
                cursor.execute("""
                    INSERT INTO bifl_alternatives
                    (trap_asin, bifl_asin, bifl_name, bifl_price, annual_savings, reasoning)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    row['parent_asin'],
                    row['bifl_asin'],
                    row['bifl_name'],
                    float(row['bifl_price']),
                    float(row['annual_savings']),
                    f"Saves ${row['annual_savings']} per year on consumables"
                ))
                bifl_count += 1
    
    print(f"✅ Loaded {products_count} products")
    print(f"✅ Loaded {consumables_count} consumables")
    print(f"✅ Loaded {bifl_count} BIFL alternatives")


if __name__ == "__main__":
    init_database()
