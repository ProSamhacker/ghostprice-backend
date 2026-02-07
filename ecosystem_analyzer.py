"""
Ecosystem Analyzer for GhostPrice
Analyzes complete product ecosystem including accessories, maintenance, and alternatives
"""

import os
import json
from groq import Groq
from typing import Dict, List, Optional


class EcosystemAnalyzer:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "mixtral-8x7b-32768"
    
    def analyze_ecosystem(
        self,
        product_title: str,
        product_price: float,
        user_intent: str,
        user_details: str = "",
        currency: str = "INR"
    ) -> Dict:
        """
        Deep ecosystem analysis based on user intent
        
        Args:
            product_title: Name of the product
            product_price: Base price of the product
            user_intent: Why user wants this (personal, work, gift, upgrade)
            user_details: Specific requirements or use case
            currency: Currency code
            
        Returns:
            Complete ecosystem analysis with required items, costs, and alternatives
        """
        
        # Construct AI prompt
        prompt = f"""
You are a smart shopping assistant analyzing a product purchase decision.

PRODUCT: {product_title}
PRICE: {currency} {product_price}
USER INTENT: {user_intent}
SPECIFIC NEEDS: {user_details}

Analyze this purchase comprehensively and return ONLY valid JSON (no markdown, no code blocks):

{{
    "summary": "Brief analysis of whether this is a good purchase",
    
    "required_items": [
        {{
            "name": "exact product name to search on Amazon",
            "reason": "why it's required",
            "estimated_price": 500,
            "priority": "high"
        }}
    ],
    
    "optional_items": [
        {{
            "name": "exact product name",
            "benefit": "what it adds",
            "estimated_price": 300,
            "priority": "medium"
        }}
    ],
    
    "maintenance_items": [
        {{
            "name": "consumable or maintenance product",
            "frequency": "monthly/yearly",
            "estimated_annual_cost": 1200,
            "why_needed": "explanation"
        }}
    ],
    
    "hidden_costs": [
        {{
            "type": "subscription/electricity/storage/etc",
            "estimated_cost": 500,
            "frequency": "monthly/yearly",
            "description": "what this cost is"
        }}
    ],
    
    "total_ecosystem_cost": {{
        "first_year": 15000,
        "annual_ongoing": 3000
    }},
    
    "better_alternatives": [
        {{
            "product_name": "alternative product to search",
            "why_better": "reason it's better for user intent",
            "estimated_price": 10000,
            "includes_items": ["what comes with it"],
            "total_ecosystem_cost": 12000
        }}
    ],
    
    "recommendation": {{
        "action": "buy | wait | consider_alternative",
        "reason": "detailed explanation",
        "confidence": 0.85
    }}
}}

IMPORTANT RULES:
1. For required_items, optional_items, and better_alternatives: use EXACT product names that can be searched on Amazon
2. Be realistic with price estimates for India market (INR)
3. Consider the user's specific intent: {user_intent}
4. Focus on {user_details} if provided
5. Return ONLY the JSON object, no other text
"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if ai_response.startswith("```"):
                ai_response = ai_response.split("```")[1]
                if ai_response.startswith("json"):
                    ai_response = ai_response[4:]
                ai_response = ai_response.strip()
            
            ecosystem_analysis = json.loads(ai_response)
            
            return {
                "status": "success",
                "product_title": product_title,
                "product_price": product_price,
                "currency": currency,
                "user_intent": user_intent,
                "analysis": ecosystem_analysis
            }
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                "status": "error",
                "error": "Failed to parse AI response",
                "details": str(e)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": "AI analysis failed",
                "details": str(e)
            }
    
    def enrich_with_real_prices(self, analysis: Dict) -> Dict:
        """
        Fetch real prices from RapidAPI for recommended items
        
        Args:
            analysis: Ecosystem analysis from analyze_ecosystem
            
        Returns:
            Analysis enriched with real Amazon prices
        """
        from rapid_api_client import RapidAPIClient
        
        try:
            client = RapidAPIClient()
            enriched_analysis = analysis.copy()
            
            # Enrich required items
            if "required_items" in enriched_analysis.get("analysis", {}):
                for item in enriched_analysis["analysis"]["required_items"]:
                    try:
                        # Search for product
                        search_result = client.search_product(item["name"], country="IN")
                        if search_result:
                            item["actual_price"] = search_result.get("price")
                            item["asin"] = search_result.get("asin")
                            item["affiliate_link"] = client.build_affiliate_link(
                                search_result.get("asin"), "IN"
                            )
                    except:
                        # Keep estimated price if search fails
                        pass
            
            # Enrich alternatives
            if "better_alternatives" in enriched_analysis.get("analysis", {}):
                for alt in enriched_analysis["analysis"]["better_alternatives"]:
                    try:
                        search_result = client.search_product(alt["product_name"], country="IN")
                        if search_result:
                            alt["actual_price"] = search_result.get("price")
                            alt["asin"] = search_result.get("asin")
                            alt["affiliate_link"] = client.build_affiliate_link(
                                search_result.get("asin"), "IN"
                            )
                    except:
                        pass
            
            return enriched_analysis
            
        except Exception as e:
            # Return original analysis if enrichment fails
            return analysis
    
    def compare_total_costs(
        self,
        original_analysis: Dict,
        alternatives: List[Dict]
    ) -> Dict:
        """
        Compare total costs including all ecosystem items
        
        Args:
            original_analysis: Analysis of original product
            alternatives: List of alternative products with their ecosystems
            
        Returns:
            Cost comparison with recommendation
        """
        original_total = original_analysis.get("analysis", {}).get(
            "total_ecosystem_cost", {}
        ).get("first_year", 0)
        
        comparisons = []
        for alt in alternatives:
            alt_total = alt.get("total_ecosystem_cost", 0)
            savings = original_total - alt_total
            
            comparisons.append({
                "alternative": alt.get("product_name"),
                "total_cost": alt_total,
                "savings": savings,
                "is_better": savings > 0
            })
        
        best_alternative = max(comparisons, key=lambda x: x["savings"]) if comparisons else None
        
        return {
            "original_total": original_total,
            "comparisons": comparisons,
            "best_alternative": best_alternative,
            "recommendation": (
                f"Save ₹{best_alternative['savings']:,.0f} with {best_alternative['alternative']}"
                if best_alternative and best_alternative["is_better"]
                else "Original choice is the most economical"
            )
        }
