"""
AI Product Analyzer using Groq API with Llama 3.1 8B
Provides free, fast AI analysis for unknown products
"""

import os
from dotenv import load_dotenv
from groq import Groq
import json
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# High-risk categories that require consumables
HIGH_RISK_CATEGORIES = [
    'inkjet_printer',
    'pod_coffee',
    'air_purifier',
    'electric_toothbrush',
    'water_filter',
    'robot_vacuum',
    'cartridge_razor',
    'instant_camera',
    'security_camera',
    'contact_lens_solution'
]

# Model to use
MODEL = "llama-3.1-8b-instant"


def classify_product_category(product_title: str, price: float = None) -> dict:
    """
    Classify product into a category using Groq AI
    
    Args:
        product_title: Product name/title from Amazon
        price: Product price (optional, helps with classification)
    
    Returns:
        {
            "category": "inkjet_printer" or "low_risk_other",
            "confidence": 0.95,
            "reasoning": "This is an inkjet printer based on..."
        }
    """
    
    prompt = f"""You are a product classifier. Classify this Amazon product into ONE of these categories:

HIGH-RISK CATEGORIES (require consumables/subscriptions):
- inkjet_printer: Printers that use ink cartridges
- pod_coffee: Coffee makers using pods/capsules (K-cups, Nespresso, etc.)
- air_purifier: Air purifiers requiring filter replacements
- electric_toothbrush: Electric toothbrushes needing brush head replacements
- water_filter: Water filter pitchers/systems needing filter replacements
- robot_vacuum: Robot vacuums needing filter/brush replacements
- cartridge_razor: Razors using disposable cartridge blades
- instant_camera: Instant cameras requiring film
- security_camera: Security cameras requiring cloud subscriptions
- contact_lens_solution: Contact lens solution bottles

OR:
- low_risk_other: Any product that doesn't fit above categories or has low recurring costs

Product: {product_title}
{"Price: $" + str(price) if price else ""}

Respond ONLY with a valid JSON object in this exact format:
{{
  "category": "category_name",
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}

Do not include any text before or after the JSON."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a product classification expert. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL,
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=200
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Extract JSON from response (sometimes AI adds extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()
        
        result = json.loads(response_text)
        
        # Validate category
        valid_categories = HIGH_RISK_CATEGORIES + ['low_risk_other']
        if result.get('category') not in valid_categories:
            result['category'] = 'low_risk_other'
            result['confidence'] = 0.5
        
        return result
        
    except Exception as e:
        print(f"AI classification error: {str(e)}")
        return {
            "category": "low_risk_other",
            "confidence": 0.0,
            "reasoning": f"Error during classification: {str(e)}"
        }


def estimate_consumable_costs(product_title: str, category: str, base_price: float) -> dict:
    """
    Estimate consumable costs for a product using AI
    
    Args:
        product_title: Product name
        category: Classified category
        base_price: Product base price
    
    Returns:
        {
            "consumable_name": "Ink Cartridge",
            "consumable_price": 29.99,
            "replacement_months": 2,
            "confidence": 0.8
        }
    """
    
    if category == 'low_risk_other':
        return None
    
    prompt = f"""You are a product cost analyst. Estimate the consumable/recurring costs for this product.

Product: {product_title}
Category: {category}
Base Price: ${base_price}

For this product type, estimate:
1. What consumable/replacement item is needed? (e.g., "Ink Cartridge", "HEPA Filter", "K-Cup Pods")
2. Typical price of the consumable? (realistic market price in USD)
3. How often does it need replacement? (in months)

Respond ONLY with valid JSON:
{{
  "consumable_name": "name of consumable",
  "consumable_price": 29.99,
  "replacement_months": 2,
  "annual_cost": 179.94,
  "confidence": 0.85
}}

Do not include any text before or after the JSON."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a cost estimation expert. Always respond with valid JSON only. Be conservative with estimates."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL,
            temperature=0.3,
            max_tokens=250
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()
        
        result = json.loads(response_text)
        
        # Calculate annual cost if not provided
        if 'annual_cost' not in result:
            result['annual_cost'] = round(
                result['consumable_price'] * (12 / result['replacement_months']), 2
            )
        
        return result
        
    except Exception as e:
        print(f"Cost estimation error: {str(e)}")
        return None


def suggest_bifl_alternative(product_title: str, category: str, base_price: float, currency: str = "USD") -> dict:
    """
    Suggest a BIFL (Buy It For Life) alternative using AI
    
    Args:
        product_title: Product name
        category: Classified category
        base_price: Product base price
        currency: Currency code
    
    Returns:
        {
            "name": "Brother MFC-L2710DW Laser Printer",
            "estimated_price": 199.99,
            "reasoning": "Laser printers have...",
            "confidence": 0.9
        }
    """
    
    if category == 'low_risk_other':
        return None
    
    currency_symbol = '$' if currency == 'USD' else '₹'
    
    prompt = f"""You are a product recommendation expert. Suggest a better long-term alternative.

Current Product: {product_title}
Category: {category}
Price: {currency_symbol}{base_price}

Suggest a "Buy It For Life" (BIFL) alternative that:
1. Has LOWER long-term maintenance costs
2. Is more durable and reliable
3. Costs between {currency_symbol}{base_price * 0.8} and {currency_symbol}{base_price * 2.5}
4. Is actually available on Amazon

Examples by category:
- inkjet_printer → Brother/HP Laser Printer
- pod_coffee → Drip coffee maker or French press
- air_purifier → Models with cheaper/longer-lasting filters
- cartridge_razor → Safety razor or electric shaver

Respond ONLY with valid JSON:
{{
  "name": "Specific product name",
  "estimated_price": 199.99,
  "reasoning": "Why this is better long-term (mention lower consumable costs)",
  "confidence": 0.85
}}

Do not include any text before or after the JSON."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a BIFL expert. Always respond with valid JSON only. Focus on long-term cost savings."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODEL,
            temperature=0.5,
            max_tokens=300
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()
        
        result = json.loads(response_text)
        return result
        
    except Exception as e:
        print(f"BIFL suggestion error: {str(e)}")
        return None


def analyze_product(product_title: str, base_price: float, currency: str = "USD") -> dict:
    """
    Complete AI analysis of an unknown product
    
    Args:
        product_title: Product name from Amazon
        base_price: Product price
        currency: Currency code
    
    Returns:
        Complete analysis with category, costs, and recommendation
    """
    
    print(f"🤖 Analyzing with Groq AI: {product_title}")
    
    # Step 1: Classify category
    classification = classify_product_category(product_title, base_price)
    category = classification['category']
    
    print(f"   Category: {category} (confidence: {classification['confidence']})")
    
    # Step 2: If low-risk, return early
    if category == 'low_risk_other':
        return {
            'status': 'low_risk',
            'category': category,
            'classification': classification,
            'message': 'This product likely has low recurring costs'
        }
    
    # Step 3: Estimate consumable costs
    consumable_data = estimate_consumable_costs(product_title, category, base_price)
    
    # Step 4: Suggest BIFL alternative
    bifl_alternative = suggest_bifl_alternative(product_title, category, base_price, currency)
    
    # Step 5: Calculate TCO
    if consumable_data:
        annual_maintenance = consumable_data['annual_cost']
        total_year_1 = base_price + annual_maintenance
        
        # Determine status
        if total_year_1 > base_price * 1.5:
            status = 'trap'
        elif total_year_1 > base_price * 1.2:
            status = 'warning'
        else:
            status = 'fair'
    else:
        annual_maintenance = 0
        total_year_1 = base_price
        status = 'unknown'
    
    print(f"   Status: {status}, Year-1 Cost: {currency}{total_year_1}")
    
    return {
        'status': status,
        'category': category,
        'classification': classification,
        'math': {
            'sticker_price': base_price,
            'consumable_name': consumable_data['consumable_name'] if consumable_data else None,
            'consumable_price': consumable_data['consumable_price'] if consumable_data else None,
            'consumable_lifespan_months': consumable_data['replacement_months'] if consumable_data else None,
            'annual_maintenance': round(annual_maintenance, 2),
            'total_year_1': round(total_year_1, 2)
        },
        'recommendation': bifl_alternative,
        'ai_powered': True,
        'confidence': min(
            classification.get('confidence', 0.5),
            consumable_data.get('confidence', 0.5) if consumable_data else 0.5
        )
    }


if __name__ == "__main__":
    # Test the AI analyzer
    test_products = [
        ("HP DeskJet 2755e Wireless Color Inkjet Printer", 59.99, "USD"),
        ("Keurig K-Mini Single Serve K-Cup Pod Coffee Maker", 79.99, "USD"),
        ("Samsung Galaxy S24 Ultra Smartphone", 1199.99, "USD"),  # Low risk
    ]
    
    for title, price, currency in test_products:
        print(f"\n{'='*60}")
        result = analyze_product(title, price, currency)
        print(f"\nResult: {json.dumps(result, indent=2)}")
