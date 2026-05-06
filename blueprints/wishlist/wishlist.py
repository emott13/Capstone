from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask_login import current_user, login_required
from services.WishlistService import WishlistService
from services.CartService import CartService
from repositories.WishlistRepository import WishlistRepository
from models import Customers

wishlist_bp = Blueprint("wishlist", __name__, static_folder="static_wishlist",
                  template_folder="templates_wishlist")

@wishlist_bp.route("/wishlist")
@login_required
def wishlist():
    try:
        customer = Customers.query.filter_by(customer_id=current_user.get_id()).first()

        if not customer:
            return redirect(url_for("home.home"))
        customer_id = current_user.get_id()

        # get wishlist items from database using customer_id
        wishlist_items = WishlistService.get_wishlist_items(customer_id)


        if wishlist_items:
            for item in wishlist_items:
                print(f"DEBUG: Item: {item}")
        
        return render_template("wishlist.html", wishlists=wishlist_items)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(url_for("home.home"))

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