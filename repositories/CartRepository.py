# services/CartRepository.py
from sqlalchemy import text
from extensions import db
from models import Addresses, Carts
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
                        'cart_item_id', ci.cart_item_id,
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
            "items": items,
        }
    
    @staticmethod
    def get_cart_by_user_id(user_id):
        cart = Carts.query.filter_by(customer_id=user_id).first()
        return cart

    @staticmethod
    def get_or_create_cart(customer_id):
        """
        Get the cart for the customer / create one if not avalible
        """
        result = db.session.execute(text("""
            SELECT cart_id FROM carts
            WHERE customer_id = :customer_id
        """), {"customer_id": customer_id}).fetchone()
        if result:
            return result[0]
        else:
            new_cart = db.session.execute(text("""
                INSERT INTO carts (customer_id) VALUES
                (:customer_id) RETURNING cart_id
            """), {"customer_id": customer_id}).fetchone()
            db.session.commit()
            return new_cart[0]

    @staticmethod
    def add_item(cart_id, product_id, quantity):
        """
        Add or update an item in the cart
        """
        existing = db.session.execute(text("""
            SELECT cart_item_id, quantity FROM cart_items
            WHERE cart_id = :cart_id AND product_id = :product_id
        """), {"cart_id": cart_id, "product_id": product_id}).fetchone()
        if existing:
            # Update the quantity
            new_quantity = existing[1] + quantity
            db.session.execute(text("""
                UPDATE cart_items SET quantity = :quantity, updated_at = CURRENT_TIMESTAMP
                WHERE cart_item_id = :cart_item_id
            """), {"quantity": new_quantity, "cart_item_id": existing[0]})
        else:
            # Insert the new item
            db.session.execute(text("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (:cart_id, :product_id, :quantity)
            """), {"cart_id": cart_id, "product_id": product_id, "quantity": quantity})
        db.session.commit()

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
        db.session.commit()

    @staticmethod
    def remove_item(cart_item_id):
        sql = """
        DELETE FROM cart_items
        WHERE cart_item_id = :cart_item_id
        """

        db.session.execute(text(sql), {"cart_item_id": cart_item_id})

    @staticmethod
    def clear_cart(cart_id):
        sql = """
            DELETE FROM cart_items
            WHERE cart_id = :cart_id
            """
        
        db.session.execute(text(sql), {"cart_id": cart_id})

    @staticmethod
    def get_existing_address(address_id, user_id):
        address = Addresses.query.filter_by(
            address_id=address_id,
            user_id=user_id
        ).first()

        if not address:
            raise ValueError("Address not found or unauthorized")
        
        return address
    
    @staticmethod
    def create_address(user_id, data):
        address = Addresses(
            user_id=user_id,
            address1=data.get("add1"),
            address2=data.get("add2"),
            city=data.get("city"),
            state=data.get("state"),
            zip=data.get("zip"),
            country=data.get("country"),
        )

        db.session.add(address)
        db.session.commit()

        return address
    
    @staticmethod
    def assign_address_to_cart(user_id, address):
        cart = Carts.query.filter_by(customer_id=user_id).first()

        if not cart:
            raise ValueError("Cart not found")
        
        cart.address_id = address.address_id
        db.session.commit()

    @staticmethod
    def get_user_addresses(user_id):
        addresses = Addresses.query.filter_by(user_id=user_id).all()

        if not addresses:
            raise ValueError("Addresses not found")
        
        return addresses