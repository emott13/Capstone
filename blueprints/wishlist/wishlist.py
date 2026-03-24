from flask import Blueprint
from flask import render_template
from flask_login import current_user
from services.WishlistService import WishlistService

wishlist_bp = Blueprint("wishlist", __name__, static_folder="static_wishlist",
                  template_folder="templates_wishlist")

@wishlist_bp.route("/wishlist")
def wishlist():
    if current_user.has_role("customer"):
        customer_id = current_user.get_id()

        # get wishlist items from database using customer_id
        wishlist_items = WishlistService.get_wishlist_items(customer_id)
        print("wishlist items", type(wishlist_items))
        for item in wishlist_items:
            print("item", item)
        return render_template("wishlist.html", wishlists=wishlist_items)
    # customer id
    # get wishlist items from database
    # render wishlist template with items