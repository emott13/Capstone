from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask_login import current_user, login_required
from services.WishlistService import WishlistService
from services.CartService import CartService
from repositories.WishlistRepository import WishlistRepository

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

@wishlist_bp.route("/remove_item", methods=["POST"])
@login_required
def remove_item():

    wishlist_item_id = int(request.form.get("remove_item_id"))
    WishlistService.remove_item(wishlist_item_id)

    return redirect(url_for("wishlist.wishlist"))

@wishlist_bp.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    wishlist_item_id = request.form.get("add_to_cart_id")

    if not wishlist_item_id:
        return "Invalid request", 400

    wishlist_item_id = int(wishlist_item_id)

    # Get the wishlist item
    wishlist_item = WishlistRepository.get_wishlist_item(wishlist_item_id)
    if not wishlist_item:
        return "Item not found", 404

    # Add to cart
    CartService.add_item(
        customer_id=current_user.get_id(),
        product_id=wishlist_item.product_id,
        quantity=wishlist_item.quantity
    )

    # Remove from wishlist
    WishlistService.remove_item(wishlist_item_id)

    return redirect(url_for("wishlist.wishlist"))