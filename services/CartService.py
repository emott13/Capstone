# services/CartService.py
from repositories.CartRepository import CartRepository
from services.OrderPricingService import OrderPricingService

class CartService:

    @staticmethod
    def get_cart(customer_id, promo_code=None):
        """
        Returns the cart with full pricing info.
        """
        cart = CartRepository.get_cart(customer_id)
        if not cart:
            return None

        items = cart["items"]

        # Ensure Python list of dicts
        if isinstance(items, str):
            import json
            items = json.loads(items)
            cart["items"] = items

        pricing = OrderPricingService.calculate_cart(
            items=items,
            customer_id=customer_id,
            promo_code=promo_code
        )

        # Merge pricing info into cart dict
        cart.update(pricing)
        print('CartService.get_cart - Final cart data:', cart)  # Debug log
        return cart

    @staticmethod
    def add_item(customer_id, product_id, quantity):
        """
        Adds item to the customer's cart
        """
        cart_id = CartRepository.get_or_create_cart(customer_id)
        CartRepository.add_item(cart_id, product_id, quantity)