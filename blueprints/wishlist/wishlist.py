from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask_login import current_user, login_required
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

@wishlist_bp.route("/update_wishlist", methods=["POST"])
@login_required
def update_wishlist():

    WishlistService.update_quantities(
        customer_id=current_user.get_id(),
        form_data=request.form
    )

    return redirect(url_for("wishlist.wishlist"))