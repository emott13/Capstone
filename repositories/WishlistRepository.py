from extensions import db
from sqlalchemy import text

from models import Wishlists

class WishlistRepository:
    @staticmethod
    def get_wishlists(customer_id):
        wishlists = Wishlists.query.filter_by(customer_id=customer_id).all()
        return wishlists
