from extensions import db

from repositories.PaymentRepository import PaymentRepository

class PaymentService:
    @staticmethod
    def process_payment(customer_id, amount, order_id):
        # Placeholder for payment processing logic
        # In a real implementation, you would integrate with a payment gateway here

        # For this example, we'll just save the payment info to the database
        PaymentRepository.save_payment_info(
            customer_id=customer_id,
            order_id=order_id,
            amount=amount,
            payment_method="card"
        )

        db.session.commit()