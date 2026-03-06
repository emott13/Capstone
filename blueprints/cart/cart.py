from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from services.CartService import CartService

cart_bp = Blueprint("cart", __name__, template_folder="templates_cart")

@cart_bp.route("/cart")
@login_required
def cart():

    customer_id = current_user.get_id()

    promo_code = session.get("manual_promo_code")

    cart = CartService.get_cart(customer_id, promo_code)

    return render_template(
        "cart.html",
        cartItems=cart["items"],
        subtotal=cart["subtotal"],
        discounts=cart["discounts"],
        tax=cart["tax"],
        total=cart["total"],
        promotions=cart["applied_promotions"]
    )

@cart_bp.route("/apply-promo", methods=["POST"])
@login_required
def apply_promo():

    code = request.form.get("promo_code","").strip().upper()

    if not code:
        flash("Invalid code","error")
        return redirect(url_for("cart.cart"))

    session["manual_promo_code"] = code

    flash("Promo code applied","success")

    return redirect(url_for("cart.cart"))