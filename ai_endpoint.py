
@app.post("/analyze-unknown-product")
async def analyze_unknown_product(
    asin: str = Query(..., description="Amazon product ASIN"),
    product_title: str = Query(..., description="Product title from Amazon page"),
    base_price: float = Query(..., description="Product price"),
    currency: str = Query("USD", description="Currency code")
):
    """
   Analyze unknown product using Groq AI (Llama 3.1 8B)
    
    This endpoint uses AI to:
    1. Classify product category
    2. Estimate consumable costs
    3. Suggest BIFL alternatives
    4. Cache results for future queries
    """
    
    # Import AI analyzer
    try:
        from ai_analyzer import analyze_product
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="AI analyzer not available. Please install groq package and set GROQ_API_KEY."
        )
    
    # Check if already analyzed and cached
    conn = get_db_connection()
    
    try:
        cached = conn.execute("""
            SELECT * FROM analyzed_products 
            WHERE asin = ? AND currency = ? AND expires_at > datetime('now')
        """, (asin, currency)).fetchone()
        
        if cached:
            return {
                "product_id": asin,
                "status": "cached",
                "message": "Using cached AI analysis",
                "data": {
                    "category": cached["category"],
                    "math": {
                        "sticker_price": cached["base_price"],
                        "consumable_name": cached["consumable_name"],
                        "consumable_price": cached["consumable_price"],
                        "annual_maintenance": cached["annual_maintenance"],
                        "total_year_1": cached["base_price"] + cached["annual_maintenance"]
                    },
                    "recommendation": {
                        "name": cached["bifl_name"],
                        "price": cached["bifl_price"],
                        "reason": cached["bifl_reasoning"]
                    } if cached["bifl_name"] else None,
                    "ai_powered": True,
                    "confidence": cached["ai_confidence"]
                }
            }
        
        # Analyze with AI
        result = analyze_product(product_title, base_price, currency)
        
        # If low-risk, return early without caching
        if result['status'] == 'low_risk':
            return {
                "product_id": asin,
                "status": "low_risk",
                "category": result['category'],
                "message": "This product likely has low recurring costs",
                "ai_powered": True
            }
        
        # Cache the result
        math = result.get('math', {})
        recommendation = result.get('recommendation', {})
        
        conn.execute("""
            INSERT OR REPLACE INTO analyzed_products 
            (asin, product_name, category, base_price, currency, marketplace,
             consumable_name, consumable_price, replacement_months, annual_maintenance,
             bifl_name, bifl_price, bifl_reasoning, ai_confidence, analysis_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asin,
            product_title,
            result['category'],
            base_price,
            currency,
            'US' if currency == 'USD' else 'IN',
            math.get('consumable_name'),
            math.get('consumable_price'),
            math.get('consumable_lifespan_months'),
            math.get('annual_maintenance', 0),
            recommendation.get('name') if recommendation else None,
            recommendation.get('estimated_price') if recommendation else None,
            recommendation.get('reasoning') if recommendation else None,
            result.get('confidence', 0.5),
            'groq_ai'
        ))
        conn.commit()
        
        return {
            "product_id": asin,
            "status": result['status'],
            "category": result['category'],
            "math": math,
            "recommendation": recommendation,
            "ai_powered": True,
            "confidence": result.get('confidence', 0.5),
            "cached": False
        }
    
    finally:
        conn.close()
