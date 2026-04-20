from sqlalchemy import func
from extensions import db
from models import OrderItems, Orders

def get_best_selling_products(limit=10):
    results = (
        db.session.query(
            OrderItems.product_id,
            func.sum(OrderItems.quantity).label("total_sold")
        )
        .join(Orders, OrderItems.order_id == Orders.order_id)
        .filter(Orders.order_status == "delivered")
        .group_by(OrderItems.product_id)
        .order_by(func.sum(OrderItems.quantity).desc())
        .limit(limit)
        .all()
    )

    return [r[0] for r in results]