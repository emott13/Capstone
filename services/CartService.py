# services/CartService.py
from flask import request, session
from flask_login import current_user

from repositories.CartRepository import CartRepository
from services.OrderPricingService import OrderPricingService
from extensions import db
from datetime import datetime, timezone
from models import (
    Carts,
    Promotion,
    PromotionTarget,
    PromotionRedemption,
    ProductCategories,
    product_category_map
)

class CartService:

    @staticmethod
    def get_cart(customer_id, promo_code=None):
        """
        Returns the cart with full pricing info.
        """
        cart = CartRepository.get_cart(customer_id)
        if not cart:
            return None

        promo_code = session.get("manual_promo_code")

        pricing = OrderPricingService.calculate_cart(
            items=cart["items"],
            customer_id=customer_id,
            promo_code=promo_code
        )

        # Merge pricing info into cart dict
        # cart.update(pricing)

        print("Pricing Information: ", pricing)
        print('CartService.get_cart - Final cart data:', cart)  # Debug log
        return cart, pricing
    
    @staticmethod
    def get_cart_by_user_id(user_id):
        cart = CartRepository.get_cart_by_user_id(user_id=user_id)
        return cart

    @staticmethod
    def add_item(customer_id, product_id, quantity):
        cart_id = CartRepository.get_or_create_cart(customer_id)
        CartRepository.add_item(cart_id, product_id, quantity)

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

    @staticmethod
    def set_cart_address(user_id, address_id=None, address_data=None):
        """
        Unified method:
        - If address_id is provided -> use existing address
        - If address_data is provided -> create new address
        """

        if address_id:
            address = CartRepository.get_existing_address(address_id, user_id)
        elif address_data:
            address = CartRepository.create_address(user_id, address_data)
        else:
            raise ValueError("Must provide address_id or address_data")

        CartRepository.assign_address_to_cart(user_id, address)

    @staticmethod
    def get_user_addresses(user_id):
        return CartRepository.get_user_addresses(user_id)
    

    