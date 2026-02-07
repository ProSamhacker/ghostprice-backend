"""
Electronics Categories Module
Handles category detection and filtering for electronics products
"""

from typing import Optional, Dict, List

# Curated electronics categories with detection keywords
CATEGORIES = {
    "laptops": {
        "keywords": ["laptop", "notebook", "macbook", "chromebook", "ultrabook", "gaming laptop"],
        "description": "Laptops & Notebooks",
        "emoji": "💻"
    },
    "headphones": {
        "keywords": ["headphone", "earphone", "earbud", "airpods", "earbuds", "wireless earbuds", "headset"],
        "description": "Headphones & Audio",
        "emoji": "🎧"
    },
    "smartphones": {
        "keywords": ["phone", "smartphone", "iphone", "samsung galaxy", "oneplus", "pixel", "mobile phone"],
        "description": "Smartphones",
        "emoji": "📱"
    },
    "monitors": {
        "keywords": ["monitor", "display", "screen", "gaming monitor", "4k monitor", "ultrawide"],
        "description": "Monitors & Displays",
        "emoji": "🖥️"
    },
    "tablets": {
        "keywords": ["tablet", "ipad", "android tablet", "tab"],
        "description": "Tablets",
        "emoji": "📱"
    },
    "smartwatches": {
        "keywords": ["smartwatch", "smart watch", "apple watch", "fitbit", "fitness tracker", "band"],
        "description": "Smartwatches & Fitness",
        "emoji": "⌚"
    },
    "cameras": {
        "keywords": ["camera", "dslr", "mirrorless", "gopro", "action camera", "digital camera"],
        "description": "Cameras & Photography",
        "emoji": "📷"
    },
    "gaming": {
        "keywords": ["playstation", "xbox", "nintendo", "console", "ps5", "ps4", "switch", "gaming console"],
        "description": "Gaming Consoles",
        "emoji": "🎮"
    },
    "pc_components": {
        "keywords": [
            "graphics card", "gpu", "nvidia", "amd", "rtx",
            "processor", "cpu", "intel", "ryzen",
            "motherboard", "ram", "memory",
            "ssd", "hard drive", "storage",
            "power supply", "psu", "cooling fan",
            "raspberry pi", "arduino", "single board computer"
        ],
        "description": "PC Components",
        "emoji": "🔧"
    },
    "keyboards_mice": {
        "keywords": ["keyboard", "mechanical keyboard", "gaming keyboard", "mouse", "gaming mouse", "trackpad"],
        "description": "Keyboards & Mice",
        "emoji": "⌨️"
    },
    "speakers": {
        "keywords": ["speaker", "bluetooth speaker", "soundbar", "home theater", "subwoofer"],
        "description": "Speakers & Audio",
        "emoji": "🔊"
    },
    "routers": {
        "keywords": ["router", "wifi router", "mesh wifi", "modem", "networking"],
        "description": "Routers & Networking",
        "emoji": "📡"
    },
    "storage": {
        "keywords": ["external hard drive", "external ssd", "usb drive", "pen drive", "flash drive", "memory card"],
        "description": "External Storage",
        "emoji": "💾"
    },
    "electronics_accessories": {
        "keywords": [
            # Power & Voltage
            "dc converter", "dc-dc converter", "buck converter", "boost converter", "step down", "step up",
            "smps", "power adapter", "power supply module", "voltage regulator", "dc power",
            "ac adapter", "ac-dc", "switching power",
            
            # DIY & Maker
            "soldering", "solder", "soldering iron", "soldering kit", "heat gun",
            "breadboard", "jumper wire", "jumper cable", "dupont wire",
            "multimeter", "oscilloscope", "logic analyzer",
            
            # Development Boards & Accessories
            "arduino", "raspberry pi", "esp32", "esp8266", "nodemcu", "stm32",
            "development board", "microcontroller", "sensor module",
            "gpio", "breakout board", "shield", "expansion board",
            
            # Electronic Components
            "led driver", "relay module", "transistor", "resistor pack", "capacitor kit",
            "electronic components", "ic chip", "diode", "mosfet",
            "prototype board", "pcb", "circuit board",
            
            # Cables & Connectors
            "usb cable", "hdmi cable", "aux cable", "audio cable", "connector",
            "adapter cable", "extension cable", "splitter", "hub",
            
            # Lighting & LED
            "led strip", "led light", "ws2812", "addressable led",
            "ring light", "studio light", "desk lamp",
            
            # Tools
            "wire stripper", "crimping tool", "pliers", "screwdriver set",
            "helping hands", "magnifying glass", "heat shrink"
        ],
        "description": "Electronics Accessories & Components",
        "emoji": "🔌"
    },
    "chargers": {
        "keywords": ["charger", "power bank", "charging cable", "adapter", "wireless charger"],
        "description": "Chargers & Power Banks",
        "emoji": "🔋"
    }
}


def detect_category(product_title: str) -> Optional[str]:
    """
    Detect electronics category from product title
    
    Args:
        product_title: Product title/name from Amazon
        
    Returns:
        Category key (e.g., 'laptops') or None if not electronics
    """
    if not product_title:
        return None
    
    title_lower = product_title.lower()
    
    # Check each category's keywords
    for category_key, category_data in CATEGORIES.items():
        for keyword in category_data["keywords"]:
            if keyword.lower() in title_lower:
                return category_key
    
    return None


def is_electronics(product_title: str) -> bool:
    """
    Check if a product is in any electronics category
    
    Args:
        product_title: Product title/name from Amazon
        
    Returns:
        True if product is electronics, False otherwise
    """
    return detect_category(product_title) is not None


def get_category_info(category_key: str) -> Optional[Dict]:
    """
    Get metadata for a category
    
    Args:
        category_key: Category key (e.g., 'laptops')
        
    Returns:
        Dictionary with category metadata or None
    """
    return CATEGORIES.get(category_key)


def get_all_categories() -> List[str]:
    """
    Get list of all supported category keys
    
    Returns:
        List of category keys
    """
    return list(CATEGORIES.keys())


def get_category_display_name(category_key: str) -> str:
    """
    Get human-readable display name for category
    
    Args:
        category_key: Category key (e.g., 'laptops')
        
    Returns:
        Display name with emoji (e.g., '💻 Laptops & Notebooks')
    """
    category = CATEGORIES.get(category_key)
    if category:
        return f"{category['emoji']} {category['description']}"
    return "📦 Electronics"


# Example usage
if __name__ == "__main__":
    # Test category detection
    test_products = [
        "Dell XPS 13 Laptop",
        "iPhone 15 Pro Max",
        "LG 27 inch 4K Monitor",
        "Sony WH-1000XM5 Headphones",
        "Air Purifier for Home",
        "NVIDIA RTX 4090 Graphics Card",
        "Logitech MX Master 3S Mouse"
    ]
    
    print("🧪 Testing Electronics Category Detection\n")
    for product in test_products:
        category = detect_category(product)
        is_elec = is_electronics(product)
        
        if category:
            display = get_category_display_name(category)
            print(f"✅ '{product}'")
            print(f"   Category: {display}")
        else:
            print(f"❌ '{product}'")
            print(f"   Not tracked (non-electronics)")
        print()
