from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from services.CartService import CartService

cart_bp = Blueprint("cart", __name__, template_folder="templates_cart")

@cart_bp.route("/cart")
def cart():

    if not current_user.is_authenticated:
        return redirect(url_for("login.login"))
    if not current_user.has_role("customer"):
        return redirect(url_for("login.login"))
    
    customer_id = current_user.get_id()

    promo_code = session.get("manual_promo_code")

    cart = CartService.get_cart(customer_id, promo_code)

    if not cart or not cart.get("items"):
        # Either the cart doesn't exist, or it has no items
        return render_template("cart.html", cart=None)

    return render_template(
        "cart.html",
        cartItems=cart["items"],
        subtotal=cart["subtotal"],
        discounts=cart["discounts"],
        tax=cart["tax"],
        total=cart["total"],
        promotions=cart["applied_promotions"]
    )

@cart_bp.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    customer_id = current_user.get_id()
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))

    if not product_id or quantity < 1:
        flash("Invalid product or quantity", "error")
        return redirect(request.referrer or url_for("home.home"))
    try:
        CartService.add_item(customer_id, product_id, quantity)
        flash("Item added to cart", "success")
    except Exception as e:
        flash("Error adding item to cart", "error")

    return redirect(url_for("cart.cart"))

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

@cart_bp.route("/update_cart", methods=["POST"])
@login_required
def update_cart():

    CartService.update_quantities(
        customer_id=current_user.get_id(),
        form_data=request.form
    )

    return redirect(url_for("cart.cart"))