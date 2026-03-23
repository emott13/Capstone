from sqlalchemy import text
from extensions import db

class PaymentRepository:
    @staticmethod
    def save_payment_info(customer_id, order_id, amount, payment_method):
        sql = """
        INSERT INTO payments (
            customer_id,
            order_id,
            amount,
            payment_method,
            paid_at
        )
        VALUES (:customer_id, :order_id, :amount, :payment_method, NOW())
        """

        db.session.execute(text(sql), {
            "customer_id": customer_id,
            "order_id": order_id,
            "amount": amount["total"],
            "payment_method": payment_method,
        })