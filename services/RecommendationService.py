from ml.inference.recommend import recommend_for_user
from models import Products


def get_user_recommendations(user_id):
    product_ids = recommend_for_user(user_id, top_k=5)

    if not product_ids:
        return []

    # Fetch full product objects
    products = Products.query.filter(
        Products.product_id.in_(product_ids)
    ).all()

    return products