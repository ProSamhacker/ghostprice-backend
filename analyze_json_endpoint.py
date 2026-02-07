"""
New FastAPI JSON endpoint for React frontend
Add this endpoint to your main.py file after the /analyze endpoint
"""

@app.get("/analyze-json")
async def analyze_json(asin: str = Query(..., description="Amazon product ASIN")):
    """
    Returns full comparison data as JSON for React frontend
    Compatible with React app's ComparisonData interface
    """
    conn = get_db_connection()
    
    try:
        # Get trap product
        trap_product = conn.execute("""
            SELECT * FROM products WHERE parent_asin = ?
        """, (asin,)).fetchone()
        
        if not trap_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get consumable for trap product
        trap_consumable = conn.execute("""
            SELECT * FROM consumables WHERE parent_asin = ?
        """, (asin,)).fetchone()
        
        # Get BIFL alternative
        alternative_data = conn.execute("""
            SELECT * FROM bifl_alternatives WHERE trap_asin = ?
        """, (asin,)).fetchone()
        
        if not alternative_data:
            raise HTTPException(status_code=404, detail="No BIFL alternative found for this product")
        
        # Get BIFL product details
        bifl_product = conn.execute("""
            SELECT * FROM products WHERE parent_asin = ?
        """, (alternative_data["bifl_asin"],)).fetchone()
        
        bifl_consumable = conn.execute("""
            SELECT * FROM consumables WHERE parent_asin = ?
        """, (alternative_data["bifl_asin"],)).fetchone()
        
        # Calculate TCOs
        trap_tco = calculate_tco_for_product(trap_product, trap_consumable)
        bifl_tco = calculate_tco_for_product(bifl_product, bifl_consumable)
        
        # Calculate break-even months
        if bifl_tco["sticker_price"] > trap_tco["sticker_price"]:
            upfront_diff = bifl_tco["sticker_price"] - trap_tco["sticker_price"]
            monthly_savings = (trap_tco["annual_maintenance"] - bifl_tco["annual_maintenance"]) / 12
            
            if monthly_savings > 0:
                break_even_months = int(upfront_diff / monthly_savings)
            else:
                break_even_months = 999  # Never breaks even
        else:
            break_even_months = 0  # Already cheaper upfront
        
        # Calculate 5-year savings
        trap_five_year = trap_tco["sticker_price"] + (trap_tco["annual_maintenance"] * 5)
        bifl_five_year = bifl_tco["sticker_price"] + (bifl_tco["annual_maintenance"] * 5)
        five_year_savings = int(trap_five_year - bifl_five_year)
        
        # Return data matching React frontend's ComparisonData interface
        return {
            "trap": {
                "name": trap_product["product_name"],
                "price": float(trap_product["base_price"]),
                "consumableCost": float(trap_consumable["consumable_price"]) if trap_consumable else 0,
                "consumableFrequencyMonths": int(trap_consumable["replacement_frequency_months"]) if trap_consumable else 0,
            },
            "winner": {
                "name": bifl_product["product_name"],
                "price": float(bifl_product["base_price"]),
                "consumableCost": float(bifl_consumable["consumable_price"]) if bifl_consumable else 0,
                "consumableFrequencyMonths": int(bifl_consumable["replacement_frequency_months"]) if bifl_consumable else 0,
            },
            "breakEvenMonths": break_even_months,
            "fiveYearSavings": five_year_savings,
            "trap_asin": asin,
            "winner_asin": alternative_data["bifl_asin"],
        }
    
    finally:
        conn.close()
