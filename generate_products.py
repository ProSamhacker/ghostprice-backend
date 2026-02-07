"""
Product Database Generator
Generates 1052 realistic products for both US and Indian markets
"""

import csv
import random
import string

# ASIN generator
def generate_asin(prefix="B0"):
    """Generate realistic Amazon ASIN"""
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(random.choices(chars, k=8))

# Product name generators
BRAND_NAMES = {
    'inkjet_printer': {
        'US': ['HP', 'Canon', 'Epson', 'Brother', 'Lexmark'],
        'IN': ['HP', 'Canon', 'Epson', 'Brother', 'Pantum']
    },
    'pod_coffee': {
        'US': ['Keurig', 'Nespresso', 'Hamilton Beach', 'Cuisinart', 'Mr. Coffee'],
        'IN': ['Nespresso', 'Philips', 'Morphy Richards', 'Prestige', 'Bosch']
    },
    'air_purifier': {
        'US': ['LEVOIT', 'Honeywell', 'Coway', 'Dyson', 'Blueair', 'Winix'],
        'IN': ['Mi', 'Philips', 'Honeywell', 'Atlanta Healthcare', 'Coway', 'Sharp']
    },
    'electric_toothbrush': {
        'US': ['Oral-B', 'Philips Sonicare', 'Colgate', 'Fairywill', 'Waterpik'],
        'IN': ['Oral-B', 'Philips', 'Colgate', 'Mi', 'Agaro']
    },
    'water_filter': {
        'US': ['Brita', 'PUR', 'ZeroWater', 'Waterdrop', 'LARQ'],
        'IN': ['Kent', 'Aquaguard', 'Pureit', 'Livpure', 'Blue Star', 'Havells']
    },
    'robot_vacuum': {
        'US': ['iRobot Roomba', 'Shark', 'Eufy', 'Roborock', 'ECOVACS'],
        'IN': ['Mi Robot', 'iRobot', 'ECOVACS', 'iLife', 'Eufy']
    },
    'cartridge_razor': {
        'US': ['Gillette', 'Schick', 'Harry\'s', 'Bic', 'Dorco'],
        'IN': ['Gillette', 'Vi-John', 'Bombay Shaving Company', 'LetsShave', 'Wilkinson']
    },
    'instant_camera': {
        'US': ['Fujifilm Instax', 'Polaroid', 'Kodak', 'Canon Ivy'],
        'IN': ['Fujifilm Instax', 'Polaroid', 'Kodak', 'Canon']
    },
    'security_camera': {
        'US': ['Ring', 'Blink', 'Arlo', 'Wyze', 'Google Nest', 'Eufy'],
        'IN': ['Mi Security', 'TP-Link', 'Imou', 'Qubo', 'CP Plus', 'Hikvision']
    },
    'contact_lens_solution': {
        'US': ['Bausch + Lomb', 'Alcon', 'Opti-Free', 'Clear Care', 'Boston'],
        'IN': ['Bausch + Lomb', 'Alcon', 'Aqualens', 'iConnect', 'Johnson & Johnson']
    }
}

# Model suffixes
MODEL_SUFFIXES = ['', ' Pro', ' Plus', ' Max', ' Ultra', ' Lite', ' Mini', ' Elite', ' Advanced', ' Premium']

# Price ranges (base_price) - US market in USD
PRICE_RANGES_USD = {
    'inkjet_printer': (39, 299),
    'pod_coffee': (49, 249),
    'air_purifier': (29, 299),
    'electric_toothbrush': (19, 229),
    'water_filter': (19, 89),
    'robot_vacuum': (149, 599),
    'cartridge_razor': (9, 39),
    'instant_camera': (49, 129),
    'security_camera': (29, 149),
    'contact_lens_solution': (9, 29)
}

# Price ranges - Indian market in INR
PRICE_RANGES_INR = {
    'inkjet_printer': (3299, 24999),
    'pod_coffee': (4099, 20999),
    'air_purifier': (2499, 24999),
    'electric_toothbrush': (1599, 18999),
    'water_filter': (1599, 7499),
    'robot_vacuum': (12499, 49999),
    'cartridge_razor': (799, 3299),
    'instant_camera': (4099, 10699),
    'security_camera': (2499, 12499),
    'contact_lens_solution': (799, 2499)
}

# Consumable data
CONSUMABLES = {
    'inkjet_printer': {
        'name_templates': ['{brand} Ink Cartridge', '{brand} Black Ink', '{brand} Color Ink Pack', '{brand} XL Ink'],
        'price_range_usd': (15, 49),
        'price_range_inr': (899, 3999),
        'lifespan_months': [1, 2, 3],
        'yield': (200, 800),
        'unit': 'pages'
    },
    'pod_coffee': {
        'name_templates': ['{brand} Coffee Pods 24ct', '{brand} K-Cup Pack', '{brand} Espresso Capsules', '{brand} Coffee Pods 50ct'],
        'price_range_usd': (15, 35),
        'price_range_inr': (999, 2499),
        'lifespan_months': [0.5, 1],
        'yield': (24, 100),
        'unit': 'cups'
    },
    'air_purifier': {
        'name_templates': ['{brand} HEPA Filter', '{brand} Replacement Filter Set', '{brand} True HEPA Filter', '{brand} Carbon Filter'],
        'price_range_usd': (19, 79),
        'price_range_inr': (1299, 5999),
        'lifespan_months': [3, 6, 9, 12],
        'yield': (3, 12),
        'unit': 'months'
    },
    'electric_toothbrush': {
        'name_templates': ['{brand} Brush Heads 3-Pack', '{brand} Replacement Heads', '{brand} Brush Heads 6-Pack', '{brand} Refills'],
        'price_range_usd': (12, 45),
        'price_range_inr': (799, 2999),
        'lifespan_months': [3],
        'yield': (3, 6),
        'unit': 'heads'
    },
    'water_filter': {
        'name_templates': ['{brand} Replacement Filter', '{brand} Filter Cartridge 3-Pack', '{brand} Water Filter', '{brand} Pitcher Filters'],
        'price_range_usd': (8, 35),
        'price_range_inr': (599, 2499),
        'lifespan_months': [1, 2, 3],
        'yield': (1, 6),
        'unit': 'filters'
    },
    'robot_vacuum': {
        'name_templates': ['{brand} Replacement Kit', '{brand} Filter Set', '{brand} Brush & Filter Kit', '{brand} Maintenance Kit'],
        'price_range_usd': (15, 49),
        'price_range_inr': (999, 3999),
        'lifespan_months': [2, 3, 4, 6],
        'yield': (1, 2),
        'unit': 'kit'
    },
    'cartridge_razor': {
        'name_templates': ['{brand} Cartridges 8-Pack', '{brand} Razor Blades', '{brand} Replacement Cartridges', '{brand} Blade Refills'],
        'price_range_usd': (18, 45),
        'price_range_inr': (899, 3499),
        'lifespan_months': [1, 2],
        'yield': (4, 12),
        'unit': 'cartridges'
    },
    'instant_camera': {
        'name_templates': ['{brand} Film Pack 40ct', '{brand} Instant Film', '{brand} Photo Paper', '{brand} Film Twin Pack'],
        'price_range_usd': (15, 30),
        'price_range_inr': (999, 2199),
        'lifespan_months': [1, 2],
        'yield': (20, 60),
        'unit': 'photos'
    },
    'security_camera': {
        'name_templates': ['{brand} Cloud Plan', '{brand} Subscription', '{brand} Storage Plan', '{brand} Premium Service'],
        'price_range_usd': (3, 10),
        'price_range_inr': (199, 799),
        'lifespan_months': [1],
        'yield': (1, 1),
        'unit': 'month',
        'is_subscription': True
    },
    'contact_lens_solution': {
        'name_templates': ['{brand} Solution 12oz', '{brand} Multipurpose Solution', '{brand} Contact Solution', '{brand} Lens Care Solution'],
        'price_range_usd': (5, 18),
        'price_range_inr': (399, 1299),
        'lifespan_months': [1, 2],
        'yield': (1, 2),
        'unit': 'bottles'
    }
}

# BIFL alternatives
BIFL_ALTERNATIVES = {
    'US': {
        'inkjet_printer': [
            ('Brother MFC-L2710DW Laser Printer', 199.99),
            ('HP LaserJet Pro M404n', 249.99),
            ('Canon ImageClass MF445dw', 299.99),
            ('Brother HL-L2350DW', 149.99),
            ('Xerox B230 Laser Printer', 179.99)
        ],
        'pod_coffee': [
            ('Ninja CFP301 DualBrewPro', 99.99),
            ('Cuisinart DCC-3200 Drip Coffee Maker', 79.99),
            ('Braun BrewSense KF7150', 89.99),
            ('OXO Brew 9-Cup Coffee Maker', 149.99),
            ('Technivorm Moccamaster', 329.99)
        ],
        'air_purifier': [
            ('Honeywell HPA300 HEPA', 249.99),
            ('Coway Airmega 400', 329.99),
            ('Blueair Blue Pure 211+', 299.99),
            ('Levoit Core 600S', 349.99),
            ('Winix 5500-2', 179.99)
        ],
        'electric_toothbrush': [
            ('Philips Sonicare 4100', 79.99),
            ('Oral-B Pro 1000', 49.99),
            ('Philips Sonicare ProtectiveClean', 89.99),
            ('Oral-B iO Series 5', 129.99),
            ('Fairywill Sonic Toothbrush', 39.99)
        ],
        'water_filter': [
            ('ZeroWater 10-Cup Pitcher', 39.99),
            ('Brita Ultramax Dispenser', 49.99),
            ('APEC ROES-50 RO System', 199.99),
            ('Waterdrop G3 RO System', 449.99),
            ('Big Berkey Water Filter', 299.99)
        ],
        'robot_vacuum': [
            ('Roborock Q5', 429.99),
            ('ECOVACS Deebot N8', 299.99),
            ('Eufy RoboVac 11S MAX', 249.99),
            ('Shark AI Robot', 399.99),
            ('iRobot Roomba j7+', 699.99)
        ],
        'cartridge_razor': [
            ('Edwin Jagger Safety Razor', 35.99),
            ('Merkur 34C Safety Razor', 44.99),
            ('Braun Series 7 Electric Shaver', 199.99),
            ('Philips Norelco OneBlade', 39.99),
            ('Feather AS-D2 Safety Razor', 179.99)
        ],
        'instant_camera': [
            ('Canon Selphy CP1500', 129.99),
            ('HP Sprocket Photo Printer', 99.99),
            ('Kodak Mini 3 Printer', 79.99),
            ('Polaroid Hi-Print', 149.99),
            ('Canon IVY Mobile Printer', 89.99)
        ],
        'security_camera': [
            ('Wyze Cam v3', 35.99),
            ('TP-Link Kasa Spot', 39.99),
            ('Reolink RLC-410', 49.99),
            ('Amcrest 4MP Camera', 59.99),
            ('Eufy Indoor Cam 2K', 44.99)
        ],
        'contact_lens_solution': [
            ('Refresh Tears Preservative-Free', 14.99),
            ('Systane Complete', 12.99),
            ('Blink Tears Lubricant', 9.99),
            ('TheraTears Dry Eye Therapy', 11.99),
            ('Clear Eyes Pure Relief', 8.99)
        ]
    },
    'IN': {
        'inkjet_printer': [
            ('Brother HL-L2321D Laser', 14999),
            ('HP LaserJet M126nw', 17999),
            ('Canon LBP 2900B Laser', 8499),
            ('Pantum P2500W Laser', 9999),
            ('HP LaserJet Pro M1136', 12999)
        ],
        'pod_coffee': [
            ('French Press Coffee Maker', 1999),
            ('South Indian Filter Coffee Set', 599),
            ('Philips Drip Coffee Maker', 3499),
            ('Prestige PCMD 3.0 Coffee Maker', 2999),
            ('Morphy Richards Cafe 10 Cups', 4999)
        ],
        'air_purifier': [
            ('Mi Air Purifier 3', 12999),
            ('Philips AC1215/20', 14999),
            ('Atlanta Healthcare Aura', 8999),
            ('Sharp FP-F40E-W', 16999),
            ('Coway Airmega Storm', 24999)
        ],
        'electric_toothbrush': [
            ('Oral-B Pro 500', 4999),
            ('Philips Sonicare HX3213', 3999),
            ('Colgate 360 Battery Powered', 1499),
            ('Mi Electric Toothbrush T300', 1999),
            ('Agaro Cosmic Sonic Brush', 2499)
        ],
        'water_filter': [
            ('Kent Grand Plus RO', 8299),
            ('Aquaguard Delight NXT', 7499),
            ('Pureit Copper+ Eco Mineral', 6999),
            ('Livpure Glo Pro++ RO', 9499),
            ('Blue Star Majesto MA3BSAM01', 8999)
        ],
        'robot_vacuum': [
            ('Mi Robot Vacuum-Mop 2 Pro', 24999),
            ('ECOVACS Deebot N8+', 29999),
            ('iLife V5s Pro', 14999),
            ('Eufy RoboVac G30', 27999),
            ('iRobot Roomba 694', 32999)
        ],
        'cartridge_razor': [
            ('Bombay Shaving Safety Razor', 2999),
            ('LetsShave Pro 6 Safety Razor', 2499),
            ('Philips AquaTouch S1121', 3999),
            ('Havells BT6151C Trimmer', 4999),
            ('Gillette Guard Safety Razor', 999)
        ],
        'instant_camera': [
            ('Canon Selphy CP1300', 10699),
            ('HP Sprocket Plus', 8499),
            ('Kodak Mini 2 Printer', 6999),
            ('Canon Ivy Mini Printer', 7499),
            ('Polaroid Mint Printer', 5999)
        ],
        'security_camera': [
            ('Mi 360° Security Camera', 2499),
            ('TP-Link Tapo C200', 2999),
            ('Imou 1080p Camera', 3499),
            ('Qubo Smart Cam 360', 2799),
            ('CP Plus 2.4MP Dome', 3999)
        ],
        'contact_lens_solution': [
            ('Refresh Tears Eye Drops', 499),
            ('Systane Ultra Lubricant', 799),
            ('Aqualens Multipurpose Solution', 399),
            ('iConnect Lens Solution', 599),
            ('Bausch + Lomb Sensitive Eyes', 699)
        ]
    }
}

def generate_product_name(category, brand, marketplace='US'):
    """Generate realistic product name"""
    model_num = random.randint(100, 999)
    suffix = random.choice(MODEL_SUFFIXES)
    
    if category == 'inkjet_printer':
        return f"{brand} {model_num}{suffix} Wireless Inkjet Printer"
    elif category == 'pod_coffee':
        return f"{brand} K-Series {model_num}{suffix} Pod Coffee Maker"
    elif category == 'air_purifier':
        return f"{brand} Air Purifier {model_num}{suffix}"
    elif category == 'electric_toothbrush':
        return f"{brand} Electric Toothbrush {model_num}{suffix}"
    elif category == 'water_filter':
        if marketplace == 'IN':
            return f"{brand} RO+UV Water Purifier {model_num}{suffix}"
        return f"{brand} Water Filter Pitcher {model_num}{suffix}"
    elif category == 'robot_vacuum':
        return f"{brand} Robot Vacuum {model_num}{suffix}"
    elif category == 'cartridge_razor':
        return f"{brand} {model_num}{suffix} Razor Handle + Cartridges"
    elif category == 'instant_camera':
        return f"{brand} Mini {model_num}{suffix}"
    elif category == 'security_camera':
        return f"{brand} Indoor Security Camera {model_num}{suffix}"
    elif category == 'contact_lens_solution':
        return f"{brand} Contact Lens Solution {model_num}ml"
    
    return f"{brand} {category.replace('_', ' ').title()} {model_num}"

def generate_products():
    """Generate all products for both markets"""
    products = []
    used_asins = set()
    
    # Distribution per market
    distribution = {
        'inkjet_printer': 50,
        'pod_coffee': 50,
        'air_purifier': 60,
        'electric_toothbrush': 50,
        'water_filter': 50,
        'robot_vacuum': 50,
        'cartridge_razor': 40,
        'instant_camera': 30,
        'security_camera': 60,
        'contact_lens_solution': 40
    }
    
    # Generate for both markets
    for marketplace, currency in [('US', 'USD'), ('IN', 'INR')]:
        price_ranges = PRICE_RANGES_USD if currency == 'USD' else PRICE_RANGES_INR
        bifl_list = BIFL_ALTERNATIVES[marketplace]
        
        for category, count in distribution.items():
            brands = BRAND_NAMES[category][marketplace]
            consumable_data = CONSUMABLES[category]
            
            # Get BIFL alternatives for this category
            bifl_products = bifl_list[category]
            
            for i in range(count):
                # Generate unique ASIN
                while True:
                    asin = generate_asin()
                    if asin not in used_asins:
                        used_asins.add(asin)
                        break
                
                # Select brand
                brand = random.choice(brands)
                
                # Generate product name
                product_name = generate_product_name(category, brand, marketplace)
                
                # Generate base price
                price_min, price_max = price_ranges[category]
                base_price = round(random.uniform(price_min, price_max), 2)
                
                # Generate consumable ASIN
                while True:
                    consumable_asin = generate_asin()
                    if consumable_asin not in used_asins:
                        used_asins.add(consumable_asin)
                        break
                
                # Generate consumable details
                consumable_name = random.choice(consumable_data['name_templates']).format(brand=brand)
                cons_price_min, cons_price_max = consumable_data['price_range_usd' if currency == 'USD' else 'price_range_inr']
                consumable_price = round(random.uniform(cons_price_min, cons_price_max), 2)
                replacement_months = random.choice(consumable_data['lifespan_months'])
                yield_qty = random.randint(*consumable_data['yield'])
                yield_unit = consumable_data['unit']
                
                # Select BIFL alternative (cycle through them)
                bifl_name, bifl_price = bifl_products[i % len(bifl_products)]
                
                # Generate BIFL ASIN
                while True:
                    bifl_asin = generate_asin()
                    if bifl_asin not in used_asins:
                        used_asins.add(bifl_asin)
                        break
                
                # Calculate annual savings (consumable cost per year)
                annual_consumable_cost = consumable_price * (12 / replacement_months)
                annual_savings = round(annual_consumable_cost * 0.7, 2)  # Assume 70% reduction
                
                products.append({
                    'parent_asin': asin,
                    'product_name': product_name,
                    'category': category,
                    'base_price': base_price,
                    'consumable_asin': consumable_asin if not consumable_data.get('is_subscription') else 'SUBSCRIPTION',
                    'consumable_name': consumable_name,
                    'consumable_price': consumable_price,
                    'replacement_months': replacement_months,
                    'yield_qty': yield_qty,
                    'yield_unit': yield_unit,
                    'bifl_asin': bifl_asin,
                    'bifl_name': bifl_name,
                    'bifl_price': bifl_price,
                    'annual_savings': annual_savings,
                    'currency': currency,
                    'marketplace': marketplace
                })
    
    return products

def write_csv(products, filename):
    """Write products to CSV file"""
    fieldnames = [
        'parent_asin', 'product_name', 'category', 'base_price',
        'consumable_asin', 'consumable_name', 'consumable_price',
        'replacement_months', 'yield_qty', 'yield_unit',
        'bifl_asin', 'bifl_name', 'bifl_price', 'annual_savings',
        'currency', 'marketplace'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    
    print(f"✅ Generated {len(products)} products")
    print(f"📁 Saved to: {filename}")

if __name__ == "__main__":
    print("🚀 Generating multi-currency product database...")
    products = generate_products()
    
    # Count by marketplace
    us_count = sum(1 for p in products if p['marketplace'] == 'US')
    in_count = sum(1 for p in products if p['marketplace'] == 'IN')
    
    print(f"📊 US Market (USD): {us_count} products")
    print(f"📊 Indian Market (INR): {in_count} products")
    print(f"📊 Total: {len(products)} products")
    
    # Write to CSV
    csv_path = '../data/sample_products.csv'
    write_csv(products, csv_path)
    print("\n✅ Database generation complete!")
