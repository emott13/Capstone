from datetime import datetime
from models import Promotion, PromotionTarget, Products
from extensions import db

def get_sale_products():

    now = datetime.utcnow()

    products_on_sale = (
        db.session.query(Products)
        .join(PromotionTarget, Products.product_id == PromotionTarget.product_id)
        .join(Promotion, PromotionTarget.promotion_id == Promotion.promotion_id)
        .filter(
            Promotion.scope_type == 'product',
            Promotion.is_active == True,
            (Promotion.starts_at == None) | (Promotion.starts_at <= now),
            (Promotion.ends_at == None) | (Promotion.ends_at >= now)
        )
        .distinct()
        .all()
    )

    return [p.product_id for p in products_on_sale]