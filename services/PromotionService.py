from datetime import datetime
from models import (
    Promotion,
    PromotionTarget,
    PromotionCondition,
    PromotionRedemption
)
from sqlalchemy import func
from extensions import db


class PromotionService:

    @staticmethod
    def apply_promotions(order, order_items, subtotal, promo_code=None):

        promotions = PromotionService.get_valid_promotions(promo_code)

        discount_total = 0
        applied_promotions = []

        for promo in promotions:

            if not PromotionService.check_conditions(promo, order, subtotal):
                continue

            discount = PromotionService.calculate_discount(
                promo,
                order_items,
                subtotal
            )

            if discount > 0:
                discount_total += discount
                applied_promotions.append(promo)

        return discount_total, applied_promotions


    @staticmethod
    def get_valid_promotions(promo_code=None):

        now = datetime.utcnow()

        query = Promotion.query.filter(
            Promotion.is_active == True,
            Promotion.starts_at <= now,
            Promotion.ends_at >= now
        )

        if promo_code:
            query = query.filter(Promotion.code == promo_code)

        return query.all()


    @staticmethod
    def calculate_discount(promo, order_items, subtotal):

        if promo.discount_type == "percentage":
            return int(subtotal * (promo.discount_value / 100))

        if promo.discount_type == "fixed_amount":
            return promo.discount_value

        return 0


    @staticmethod
    def check_conditions(promo, order, subtotal):

        for condition in promo.conditions:

            if condition.condition_type == "min_cart_total":
                if subtotal < int(condition.condition_value):
                    return False

            if condition.condition_type == "first_order_only":
                if order.customer.orders.count() > 1:
                    return False

        return True

    # @staticmethod
    # def evaluate_cart(cart, customer):
    #     """
    #     Returns:
    #     {
    #         "discounts": [],
    #         "total_discount": int,
    #         "final_total": int
    #     }
    #     """

    #     now = datetime.utcnow()

    #     promotions = Promotion.query.filter(
    #         Promotion.is_active == True,
    #         Promotion.starts_at <= now,
    #         Promotion.ends_at >= now
    #     ).all()

    #     subtotal = cart["subtotal"]
    #     total_discount = 0
    #     applied_promos = []
    #     non_stackable_applied = False

    #     for promo in promotions:

    #         if not PromotionService._check_usage_limits(promo, customer.user_id):
    #             continue

    #         if not PromotionService._check_conditions(promo, cart, customer):
    #             continue

    #         if not PromotionService._check_scope(promo, cart):
    #             continue

    #         if non_stackable_applied and not promo.stackable:
    #             continue

    #         discount = PromotionService._calculate_discount(promo, cart)

    #         if discount <= 0:
    #             continue

    #         total_discount += discount

    #         applied_promos.append({
    #             "promotion_id": promo.promotion_id,
    #             "code": promo.code,
    #             "discount": discount
    #         })

    #         if not promo.stackable:
    #             non_stackable_applied = True

    #     final_total = max(subtotal - total_discount, 0)

    #     return {
    #         "discounts": applied_promos,
    #         "total_discount": total_discount,
    #         "final_total": final_total
    #     }

    # # ----------------------------
    # # Helper Methods
    # # ----------------------------

    # @staticmethod
    # def _check_usage_limits(promo, customer_id):
    #     total_usage = db.session.query(
    #         func.count(PromotionRedemption.promotion_id)
    #     ).filter_by(
    #         promotion_id=promo.promotion_id
    #     ).scalar()

    #     if promo.usage_limit and total_usage >= promo.usage_limit:
    #         return False

    #     customer_usage = db.session.query(
    #         func.count(PromotionRedemption.promotion_id)
    #     ).filter_by(
    #         promotion_id=promo.promotion_id,
    #         customer_id=customer_id
    #     ).scalar()

    #     if promo.per_customer_limit and customer_usage >= promo.per_customer_limit:
    #         return False

    #     return True

    # @staticmethod
    # def _check_conditions(promo, cart, customer):
    #     for condition in promo.conditions:

    #         if condition.condition_type == "min_cart_total":
    #             if cart["subtotal"] < int(condition.condition_value):
    #                 return False

    #     return True

    # @staticmethod
    # def _check_scope(promo, cart):

    #     if promo.scope_type == "cart":
    #         return True

    #     for item in cart["items"]:

    #         if promo.scope_type == "product":
    #             if item["product_id"] in [t.product_id for t in promo.targets]:
    #                 return True

    #         if promo.scope_type == "vendor":
    #             if item["vendor_id"] in [t.vendor_id for t in promo.targets]:
    #                 return True

    #     return False

    # @staticmethod
    # def _calculate_discount(promo, cart):

    #     subtotal = cart["subtotal"]

    #     if promo.discount_type == "percentage":
    #         return int(subtotal * (promo.discount_value / 100))

    #     if promo.discount_type == "fixed_amount":
    #         return min(promo.discount_value, subtotal)

    #     return 0