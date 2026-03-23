# services/CartService.py
from flask import request
from flask_login import current_user

from repositories.CartRepository import CartRepository
from services.OrderPricingService import OrderPricingService
from extensions import db

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
    def update_quantities(customer_id, form_data):

        cart_id = CartRepository.get_cart_id(customer_id)

        for field, value in form_data.items():

            if field.startswith("quantity_"):

                cart_item_id = field.replace("quantity_", "")
                quantity = int(value)

                if quantity <= 0:
                    CartRepository.remove_item(cart_item_id)
                else:
                    CartRepository.update_quantity(
                        cart_item_id,
                        quantity
                    )

        db.session.commit()

    def set_cart_address(user_id, add1, add2, city, state, zip_code, country):

        # create cart address
        CartRepository.create_cart_address(
            user_id,
            add1,
            add2,
            city,
            state,
            zip_code,
            country
        )

        db.session.commit()

       