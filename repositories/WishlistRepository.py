from extensions import db
from sqlalchemy import text
from models import WishlistItems

from models import Wishlists

class WishlistRepository:
    @staticmethod
    def get_wishlists(customer_id):
        wishlists = Wishlists.query.filter_by(customer_id=customer_id).all()
        return wishlists
    
    @staticmethod
    def get_wishlist_item(wishlist_item_id):
        return WishlistItems.query.filter_by(wishlist_item_id=wishlist_item_id).first()
    
    @staticmethod
    def update_quantity(wishlist_item_id, quantity):
        sql = """
        UPDATE wishlist_items
        SET quantity = :quantity
        WHERE wishlist_item_id = :wishlist_item_id
        """

        db.session.execute(
            text(sql),
            {
                "quantity": quantity,
                "wishlist_item_id": wishlist_item_id
            }
        )

    @staticmethod
    def remove_item(wishlist_item_id):
        sql = """
        DELETE FROM wishlist_items
        WHERE wishlist_item_id = :wishlist_item_id
        """

        db.session.execute(
            text(sql),
            {"wishlist_item_id": wishlist_item_id}
        )
