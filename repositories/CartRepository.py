# services/CartRepository.py
from sqlalchemy import text
from extensions import db
import json

class CartRepository:

    @staticmethod
    def get_cart_items(cart_id):

        sql = """
        SELECT
            ci.product_id,
            ci.quantity,
            p.price,
            p.vendor_id
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.product_id
        WHERE ci.cart_id = :cart_id
        """

        result = db.session.execute(
            text(sql),
            {"cart_id": cart_id}
        ).mappings().all()

        return result


    @staticmethod
    def get_cart_id(customer_id):

        sql = """
        SELECT cart_id
        FROM carts
        WHERE customer_id = :customer_id
        """

        result = db.session.execute(
            text(sql),
            {"customer_id": customer_id}
        ).scalar()

        return result


    @staticmethod
    def get_cart(customer_id):
        """
        Fetch the customer's cart and all items as Python-native list of dicts.
        """
        sql = """
        SELECT
            c.cart_id,
            c.customer_id,

            COALESCE(
                json_agg(
                    json_build_object(
                        'product_id', p.product_id,
                        'product_name', p.product_name,
                        'vendor_id', p.vendor_id,
                        'price', p.price,
                        'quantity', ci.quantity,
                        'line_total', ci.quantity * p.price
                    )
                ) FILTER (WHERE ci.product_id IS NOT NULL),
                '[]'
            ) AS items

        FROM carts c
        LEFT JOIN cart_items ci ON c.cart_id = ci.cart_id
        LEFT JOIN products p ON ci.product_id = p.product_id
        WHERE c.customer_id = :customer_id
        GROUP BY c.cart_id
        """

        result = db.session.execute(text(sql), {"customer_id": customer_id}).mappings().fetchone()

        if not result:
            return None

        items = result["items"]

        # Ensure we have Python objects
        if isinstance(items, str):
            items = json.loads(items)

        return {
            "cart_id": result["cart_id"],
            "customer_id": result["customer_id"],
            "items": items
        }
    

    @staticmethod
    def update_quantity(cart_item_id, quantity):

        sql = """
        UPDATE cart_items
        SET quantity = :quantity
        WHERE cart_item_id = :cart_item_id
        """

        db.session.execute(
            text(sql),
            {
                "quantity": quantity,
                "cart_item_id": cart_item_id
            }
        )


    @staticmethod
    def clear_cart(cart_id):

        sql = """
        DELETE FROM cart_items
        WHERE cart_id = :cart_id
        """

        db.session.execute(text(sql), {"cart_id": cart_id})