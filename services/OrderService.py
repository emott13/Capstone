from extensions import db

from repositories.CartRepository import CartRepository
from repositories.OrderRepository import OrderRepository
from services.OrderPricingService import OrderPricingService


class OrderService:

    @staticmethod
    def checkout_cart(customer_id, promo_code=None):

        cart_id = CartRepository.get_cart_id(customer_id)

        if not cart_id:
            return None

        items = CartRepository.get_cart_items(cart_id)

        if not items:
            return None

        pricing = OrderPricingService.calculate_cart(
            items,
            customer_id,
            promo_code
        )

        order_id = OrderRepository.create_order(
            customer_id,
            pricing["subtotal"],
            pricing["tax"],
            pricing["total"]
        )
        print("Applied Promotions:", pricing["applied_promotions"])
        for promo in pricing["applied_promotions"]:


            OrderRepository.insert_discount(
                order_id,
                promo["promotion_id"],
                promo["code"],
                promo["discount_amount"]
            )

            OrderRepository.record_redemption(
                promo["promotion_id"],
                customer_id,
                order_id
            )
        
        for item in items:
            OrderRepository.add_order_item(
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            )

        CartRepository.clear_cart(cart_id)

        db.session.commit()

        return order_id