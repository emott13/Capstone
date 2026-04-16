from sqlalchemy import func
from models import UserInteractions
from extensions import db

def get_popular_products(limit=10):
    results = (
        db.session.query(
            UserInteractions.product_id,
            func.sum(UserInteractions.interaction_value).label("score")
        )
        .group_by(UserInteractions.product_id)
        .order_by(func.sum(UserInteractions.interaction_value).desc())
        .limit(limit)
        .all()
    )

    return [r[0] for r in results]