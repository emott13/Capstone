from sqlalchemy import text
from extensions import db


class OrderRepository:

    @staticmethod
    def create_order(customer_id, subtotal, tax, total):

        sql = """
        INSERT INTO orders (
            customer_id,
            order_date,
            order_subtotal,
            order_tax,
            order_total,
            order_status
        )
        VALUES (:customer_id, NOW(), :subtotal, :tax, :total, 'pending')
        RETURNING order_id
        """

        result = db.session.execute(
            text(sql),
            {
                "customer_id": customer_id,
                "subtotal": subtotal,
                "tax": tax,
                "total": total
            }
        )


        return result.scalar()
    
    @staticmethod
    def add_order_item(order_id, product_id, quantity, price_at_purchase):

        sql = """
        INSERT INTO order_items (
            order_id,
            product_id,
            quantity,
            price_at_purchase
        )
        VALUES (:order_id, :product_id, :quantity, :price_at_purchase)
        """

        db.session.execute(text(sql), {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "price_at_purchase": price_at_purchase
        })


    @staticmethod
    def insert_discount(order_id, promotion_id, code, amount):

        sql = """
        INSERT INTO order_discounts (
            order_id,
            promotion_id,
            code_used,
            discount_amount_applied
        )
        VALUES (:order_id, :promotion_id, :code, :amount)
        """

        db.session.execute(text(sql), {
            "order_id": order_id,
            "promotion_id": promotion_id,
            "code": code,
            "amount": amount
        })


    @staticmethod
    def record_redemption(promotion_id, customer_id, order_id):

        sql = """
        INSERT INTO promotion_redemptions (
            promotion_id,
            customer_id,
            order_id
        )
        VALUES (:promotion_id, :customer_id, :order_id)
        """

        db.session.execute(text(sql), {
            "promotion_id": promotion_id,
            "customer_id": customer_id,
            "order_id": order_id
        })


    @staticmethod
    def get_customer_orders(customer_id):

        sql = """
        SELECT 
            o.order_id,
            o.order_date,
            o.order_subtotal,
            o.order_tax,
            o.order_total,
            o.order_status,

            COALESCE(
                json_agg(
                    json_build_object(
                        'product_name', p.product_name,
                        'quantity', oi.quantity,
                        'price_at_purchase', oi.price_at_purchase
                    )
                ) FILTER (WHERE oi.order_id IS NOT NULL),
                '[]'
            ) AS order_items

        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.product_id
        WHERE o.customer_id = :customer_id
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        """

        result = db.session.execute(
            text(sql),
            {"customer_id": customer_id}
        ).mappings().all()

        print("Fetched Orders:", result)
        return result