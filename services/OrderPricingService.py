# services/OrderPricingService.py
from services.PromotionService import PromotionService
from services.TaxService import TaxService

class OrderPricingService:

    @staticmethod
    def calculate_cart(items, customer_id, promo_code=None):
        """
        Compute subtotal, discounts, tax, and total for the cart.
        Expects items as a list of dicts (Python-native, not JSON string).
        """
        print("CART ITEMS:", items)
        if not items:
            return {
                "subtotal": 0,
                "discounts": 0,
                "tax": 0,
                "total": 0,
                "applied_promotions": []
            }

        # Ensure items are dicts
        if isinstance(items, str):
            import json
            items = json.loads(items)

        # ensures iterating through the list of items from the dict but not the dict itself
        if isinstance(items, dict) and "items" in items:
            items = items["items"]

        subtotal = 0
        print("ALL ITEMS", items)
        for item in items:
            print("ITEM ________", item) # Debug log
            # Defensive casting
            price = int(item.get("price", 0))
            quantity = int(item.get("quantity", 0))
            subtotal += price * quantity

        # Apply promotions 
        discount_total, applied_promotions = PromotionService.apply_promotions(
            items,
            subtotal,
            customer_id,
            promo_code
        )

        # Calculate tax on discounted subtotal
        try:
            taxable_amount = max(subtotal - discount_total, 0)
        except:
            taxable_amount = max(subtotal, 0)

        tax = TaxService.calculate_tax(
            items,
            "PA",  # Replace with customer address if available
            taxable_amount
        )

        total = taxable_amount + tax

        try:
            return {
                "subtotal": subtotal,
                "discounts": discount_total,
                "tax": tax,
                "total": total,
                "applied_promotions": applied_promotions
            }
        except:
            return {
                "subtotal": subtotal,
                "discounts": 0,
                "tax": tax,
                "total": total,
                "applied_promotions": []
            }