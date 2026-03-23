from datetime import datetime
from sqlalchemy import func
from extensions import db
from models import Promotion, PromotionTarget, PromotionCondition, PromotionRedemption, Users, Orders

class PromotionService:

    @staticmethod
    def apply_promotions(items, subtotal, customer_id, promo_code=None):
        """
        Apply all eligible promotions to the cart.
        Returns: (total_discount, list_of_applied_promotions)
        """
        customer = Users.query.get(customer_id)
        applied_promotions = []
        total_discount = 0
        applied_non_stackable = False

        # Fetch active promotions
        promos = Promotion.query.filter(Promotion.is_active == True).all()

        # Optionally filter by promo code if provided
        if promo_code:
            promos = [p for p in promos if p.code and p.code.upper() == promo_code.upper()]

        # Shuffle or sort by discount value (optional)
        promos.sort(key=lambda p: p.discount_value, reverse=True)

        for promo in promos:
            # Check usage limits
            if not PromotionService.check_usage_limits(promo, customer_id):
                continue

            # Check conditions
            if not PromotionService.check_conditions(promo, customer, subtotal):
                continue

            # Check if scope matches cart items
            if not PromotionService.scope_matches(promo, items):
                continue

            # Non-stackable promotion conflict
            if applied_non_stackable and not promo.stackable:
                continue

            # Calculate discount
            discount_amount = PromotionService.calculate_discount(promo, items, subtotal)
            if discount_amount <= 0:
                continue

            total_discount += discount_amount
            applied_promotions.append({
                "promotion_id": promo.promotion_id,
                "code": promo.code,
                "name": promo.name,
                "discount_amount": discount_amount
            })

            if not promo.stackable:
                applied_non_stackable = True

        return total_discount, applied_promotions

    @staticmethod
    def check_usage_limits(promo, customer_id):
        """
        Returns True if promotion usage is under limits.
        """
        total_usage = db.session.query(func.count(PromotionRedemption.promotion_redemption_id))\
            .filter_by(promotion_id=promo.promotion_id).scalar()

        if promo.usage_limit and total_usage >= promo.usage_limit:
            return False

        customer_usage = db.session.query(func.count(PromotionRedemption.promotion_redemption_id))\
            .filter_by(promotion_id=promo.promotion_id, customer_id=customer_id).scalar()

        if promo.per_customer_limit and customer_usage >= promo.per_customer_limit:
            return False

        return True

    @staticmethod
    def check_conditions(promo, customer, cart_subtotal):
        """
        Returns True if promotion meets all conditions.
        """
        conditions = PromotionCondition.query.filter_by(promotion_id=promo.promotion_id).all()
        for condition in conditions:
            if condition.condition_type == "min_cart_total":
                if cart_subtotal < int(condition.condition_value):
                    return False
            elif condition.condition_type == "first_order_only":
                previous_orders = Orders.query.filter(
                    Orders.customer_id == customer.user_id
                ).count()
                if previous_orders > 0:
                    return False
            elif condition.condition_type == "customer_role":
                if not customer.has_role(condition.condition_value):
                    return False
        return True

    @staticmethod
    def scope_matches(promo, items):
        """
        Returns True if promo scope applies to cart items.
        `items` should be a list of dicts:
        [{'product_id': ..., 'vendor_id': ..., 'category_id': ...}]
        """
        if promo.scope_type == "cart":
            return True

        targets = PromotionTarget.query.filter_by(promotion_id=promo.promotion_id).all()
        for item in items:
            for target in targets:
                if promo.scope_type == "product" and target.product_id == item["product_id"]:
                    return True
                if promo.scope_type == "vendor" and target.vendor_id == item["vendor_id"]:
                    return True
                if promo.scope_type == "category" and hasattr(item, "category_id") and target.category_id == item.get("category_id"):
                    return True
        return False

    @staticmethod
    def calculate_discount(promo, items, subtotal):
        """
        Compute discount amount based on type.
        """
        if promo.discount_type == "percentage":
            return int(subtotal * (promo.discount_value / 100))
        elif promo.discount_type == "fixed_amount":
            return min(promo.discount_value, subtotal)
        elif promo.discount_type == "bogo":
            # Simplified: 50% off cheapest item if eligible
            if not items:
                return 0
            cheapest_item = min(items, key=lambda x: x["price"])
            return int(cheapest_item["price"] * 0.5)
        elif promo.discount_type == "free_shipping":
            # Handle shipping discount elsewhere if needed
            return 0
        return 0